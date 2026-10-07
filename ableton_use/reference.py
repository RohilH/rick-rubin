"""Measure a finished mix the way a listener judges it — and compare it with reference tracks.

Lint and section loudness answer "is this correct?". They do not answer "does this sound like a record?".
`profile()` measures the things that make a mix feel alive or flat, on any audio file, with no knowledge of
the arrangement: loudness and punch, tonal balance, stereo width per band, how hard the low end pumps against
the kick, how sharp the transients are, and how much the sound *changes* over time. `compare()` puts a mix
next to reference tracks (released music in the genre) and says where it falls outside their range.

Everything is measured on the loudest sustained stretch (the "drop") unless stated, so intros and breakdowns
do not blur the picture; movement is measured over the whole file.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from .analysis import loudness_lufs
from .samples import read_audio

BANDS = [("sub", 20, 60), ("bass", 60, 200), ("lowmid", 200, 800), ("mid", 800, 4000), ("high", 4000, 12000), ("air", 12000, 20000)]


@dataclass
class Profile:
    name: str
    seconds: float
    bpm: float
    lufs: float                      # integrated, whole file
    drop_lufs: float                 # loudest sustained 30 s
    crest_db: float                  # peak / rms in the drop: punch (and how hard it is limited)
    plr_db: float                    # peak to loudness in the drop
    bands_db: dict[str, float]       # level of each band relative to the whole drop (dB)
    tilt_db_oct: float               # spectral slope above 100 Hz, dB per octave (more negative = darker)
    side_pct: float                  # drop: share of energy in the sides
    side_bands: dict[str, float]     # drop: side % per band
    correlation: float
    pump_db: float                   # drop, low band: level on the off-beat minus level on the kick
    transient_db: float              # drop, 2-8 kHz: how far hits stand above the level between them
    hf_flux: float                   # how busy the top end is: average frame-to-frame change above 4 kHz
    loudness_range: float            # whole file: spread of 3 s loudness (p95 - p10)
    movement: float                  # drop: how different each 8-beat block's spectrum is from the previous one (0 = looped)
    repeat_pct: float                # drop: share of 8-beat blocks that are near-copies of the block before
    novelty_per_min: float           # whole file: clear changes of texture per minute
    extra: dict = field(default_factory=dict)


def _bandpass(x: np.ndarray, sr: int, lo: float, hi: float) -> np.ndarray:
    from scipy.signal import butter, sosfilt
    return sosfilt(butter(4, [lo, min(hi, sr / 2 * 0.99)], btype="band", fs=sr, output="sos"), x, axis=0)


def estimate_bpm(mono: np.ndarray, sr: int, lo: float = 110.0, hi: float = 136.0) -> float:
    """Tempo from the low band's onset envelope (dance music: the kick)."""
    low = _bandpass(mono, sr, 30, 150)
    hop = sr // 200
    env = np.sqrt(np.mean(low[: len(low) // hop * hop].reshape(-1, hop) ** 2, axis=1))
    on = np.maximum(0, np.diff(env))
    on = on[: 200 * 90]                                          # 90 s is plenty
    ac = np.correlate(on, on, "full")[len(on) - 1:]
    best, score = 124.0, -1.0
    for bpm in np.arange(lo, hi + 0.01, 0.05):
        lag = 60.0 / bpm * 200
        s = sum(np.interp(lag * k, np.arange(len(ac)), ac) for k in (1, 2, 4, 8))
        if s > score:
            best, score = float(bpm), s
    return round(best, 2)


def _loudest_window(x: np.ndarray, sr: int, seconds: float = 30.0) -> tuple[int, int]:
    m = x.mean(axis=1)
    hop = sr // 2
    p = np.array([np.mean(m[i:i + hop] ** 2) for i in range(0, len(m) - hop, hop)])
    n = int(seconds * 2)
    if len(p) <= n:
        return 0, len(x)
    c = np.convolve(p, np.ones(n), "valid")
    i = int(np.argmax(c))
    return i * hop, (i + n) * hop


def profile(path: str | Path, name: str | None = None, bpm: float | None = None) -> Profile:
    sr, x = read_audio(path)
    if x.shape[1] == 1:
        x = np.repeat(x, 2, axis=1)
    x = x.astype(np.float64)
    mono = x.mean(axis=1)
    bpm = bpm or estimate_bpm(mono, sr)
    a, b = _loudest_window(x, sr)
    d = x[a:b]
    dm = d.mean(axis=1)
    rms = np.sqrt(np.mean(dm ** 2)) + 1e-12
    peak = np.abs(d).max() + 1e-12
    drop_lufs = loudness_lufs(d.astype(np.float32), sr)

    # tonal balance
    n = 1 << 15
    acc = np.zeros(n // 2 + 1)
    k = 0
    for i in range(0, len(dm) - n, n // 2):
        acc += np.abs(np.fft.rfft(dm[i:i + n] * np.hanning(n))) ** 2
        k += 1
    acc /= max(1, k)
    f = np.fft.rfftfreq(n, 1 / sr)
    tot = acc[(f >= 20) & (f < 20000)].sum() + 1e-20
    bands_db = {nm: float(10 * np.log10(acc[(f >= lo) & (f < hi)].sum() / tot + 1e-20)) for nm, lo, hi in BANDS}
    centres = np.geomspace(100, 12800, 22)
    lev = [10 * np.log10(acc[(f >= c / 2 ** (1 / 6)) & (f < c * 2 ** (1 / 6))].mean() + 1e-20) for c in centres]
    tilt = float(np.polyfit(np.log2(centres), lev, 1)[0])

    # width
    L, R = d[:, 0], d[:, 1]
    mid, side = (L + R) / 2, (L - R) / 2
    side_pct = float(100 * (side ** 2).sum() / ((mid ** 2).sum() + (side ** 2).sum() + 1e-20))
    corr = float((L * R).sum() / (np.sqrt((L * L).sum() * (R * R).sum()) + 1e-20))
    side_bands = {}
    for nm, lo, hi in (("low", 20, 150), ("lowmid", 150, 800), ("mid", 800, 4000), ("high", 4000, 16000)):
        mb, sb = _bandpass(mid, sr, lo, hi), _bandpass(side, sr, lo, hi)
        side_bands[nm] = float(100 * (sb ** 2).sum() / ((mb ** 2).sum() + (sb ** 2).sum() + 1e-20))

    # pump: fold the low band's envelope onto one beat; level between kicks vs level on them
    beat = 60.0 / bpm
    hop = max(1, sr // 400)
    low_env = np.sqrt(np.mean(_bandpass(dm, sr, 30, 200)[: len(dm) // hop * hop].reshape(-1, hop) ** 2, axis=1) + 1e-14)
    t = np.arange(len(low_env)) * hop / sr
    best = None
    for phase in np.linspace(0, beat, 24, endpoint=False):       # the grid's phase is unknown: try them, keep the deepest
        ph = ((t - phase) % beat) / beat
        on = low_env[(ph < 0.2)]
        off = low_env[(ph > 0.45) & (ph < 0.7)]
        if len(on) and len(off):
            v = 20 * np.log10(np.mean(off) / np.mean(on))
            best = v if best is None or v < best else best
    pump = float(best if best is not None else 0.0)

    # transients in the presence band: peaks vs the floor between them
    hi_env = np.abs(_bandpass(dm, sr, 2000, 8000))
    hop2 = max(1, sr // 200)
    he = hi_env[: len(hi_env) // hop2 * hop2].reshape(-1, hop2).max(axis=1)
    transient = float(20 * np.log10((np.percentile(he, 95) + 1e-12) / (np.percentile(he, 30) + 1e-12)))

    # top-end activity
    nf, hp = 2048, 1024
    frames = np.array([np.abs(np.fft.rfft(dm[i:i + nf] * np.hanning(nf))) for i in range(0, len(dm) - nf, hp)])
    ff = np.fft.rfftfreq(nf, 1 / sr)
    top = np.log10(frames[:, ff > 4000] + 1e-9)
    hf_flux = float(np.mean(np.maximum(0, np.diff(top, axis=0)).mean(axis=1)) * 100)

    # movement: compare each 8-beat block's spectrum (1/3-octave, level-normalised) with the previous block
    def blocks(sig: np.ndarray, beats: float = 8.0) -> np.ndarray:
        size = int(beats * beat * sr)
        edges = np.geomspace(40, 16000, 28)
        out = []
        for i in range(0, len(sig) - size, size):
            S = np.abs(np.fft.rfft(sig[i:i + size] * np.hanning(size))) ** 2
            fr = np.fft.rfftfreq(size, 1 / sr)
            v = np.array([10 * np.log10(S[(fr >= lo) & (fr < hi)].sum() + 1e-20) for lo, hi in zip(edges[:-1], edges[1:])])
            out.append(v)
        return np.array(out)
    bl = blocks(dm)
    if len(bl) > 2:
        diff = np.sqrt(np.mean(np.diff(bl - bl.mean(axis=1, keepdims=True), axis=0) ** 2, axis=1))      # dB rms change in spectral shape
        movement = float(np.mean(diff))
        repeat = float(100 * np.mean(diff < 0.6))
    else:
        movement, repeat = 0.0, 100.0
    whole = blocks(mono)
    if len(whole) > 2:
        dw = np.sqrt(np.mean(np.diff(whole, axis=0) ** 2, axis=1))                                         # includes level changes
        novelty = float((dw > 3.0).sum() / (len(mono) / sr / 60.0))
    else:
        novelty = 0.0

    # loudness range over the file
    win = int(3 * sr)
    st = [loudness_lufs(x[i:i + win].astype(np.float32), sr) for i in range(0, len(x) - win, win)]
    st = np.array([v for v in st if np.isfinite(v) and v > -50])
    lra = float(np.percentile(st, 95) - np.percentile(st, 10)) if len(st) > 3 else 0.0

    return Profile(name or Path(path).stem, len(x) / sr, bpm, loudness_lufs(x.astype(np.float32), sr), float(drop_lufs),
                   float(20 * np.log10(peak / rms)), float(20 * np.log10(peak) - drop_lufs), bands_db, tilt, side_pct, side_bands, corr,
                   pump, transient, hf_flux, lra, movement, repeat, novelty)


METRICS = [
    # key, label, how to read it, unit
    ("drop_lufs", "loudness of the drop", "LUFS; mastered records sit far above an unmastered mix", "LUFS"),
    ("crest_db", "crest (peak/rms) in the drop", "lower = denser and more limited; much higher = unmastered", "dB"),
    ("bands_db.sub", "sub 20-60 Hz", "share of the drop's energy", "dB"),
    ("bands_db.bass", "bass 60-200 Hz", "", "dB"),
    ("bands_db.lowmid", "low-mid 200-800 Hz", "", "dB"),
    ("bands_db.mid", "mid 0.8-4 kHz", "presence", "dB"),
    ("bands_db.high", "high 4-12 kHz", "bite, hats, click", "dB"),
    ("bands_db.air", "air 12-20 kHz", "", "dB"),
    ("tilt_db_oct", "spectral tilt", "more negative = darker", "dB/oct"),
    ("side_pct", "stereo: side energy", "0 = mono", "%"),
    ("side_bands.lowmid", "side, 150-800 Hz", "", "%"),
    ("side_bands.mid", "side, 0.8-4 kHz", "", "%"),
    ("side_bands.high", "side, 4-16 kHz", "", "%"),
    ("pump_db", "low-end pump (off-beat vs kick)", "more negative = the kick dominates the low end between beats", "dB"),
    ("transient_db", "transient contrast 2-8 kHz", "how far hits stand above what is between them", "dB"),
    ("hf_flux", "top-end activity", "how busy the highs are", ""),
    ("movement", "movement in the drop", "change in spectral shape from one 2-bar block to the next", "dB"),
    ("repeat_pct", "near-identical 2-bar blocks", "share of the drop that is a copy of the 2 bars before", "%"),
    ("novelty_per_min", "texture changes per minute", "whole track", "/min"),
    ("loudness_range", "loudness range", "whole track, 3 s windows, p95-p10", "LU"),
]


def _get(p: Profile, key: str) -> float:
    if "." in key:
        a, b = key.split(".")
        return float(getattr(p, a)[b])
    return float(getattr(p, key))


def compare(mix: Profile, refs: list[Profile]) -> str:
    """A table of `mix` against the references' range, with a verdict per line."""
    L = [f"# {mix.name} against {len(refs)} reference tracks", "",
         "| measure | this mix | references (min – median – max) | verdict | reading |", "|---|---|---|---|---|"]
    out_of_range = []
    for key, label, note, unit in METRICS:
        v = _get(mix, key)
        r = np.array([_get(p, key) for p in refs])
        lo, med, hi = r.min(), np.median(r), r.max()
        span = max(hi - lo, 1e-6)
        if v < lo - 0.1 * span:
            verdict = "BELOW all references"
        elif v > hi + 0.1 * span:
            verdict = "ABOVE all references"
        elif v < lo or v > hi:
            verdict = "at the edge"
        else:
            verdict = "in range"
        if "all" in verdict:
            out_of_range.append((label, v, med, unit))
        L.append(f"| {label} | {v:.1f} {unit} | {lo:.1f} – {med:.1f} – {hi:.1f} | {verdict} | {note} |")
    L += ["", "## Outside the references' range"]
    L += [f"- {label}: {v:.1f} {unit} here, {med:.1f} {unit} typical ({v - med:+.1f})" for label, v, med, unit in out_of_range] or ["nothing"]
    return "\n".join(L) + "\n"


# ============================================================================ a shared shelf of reference profiles
def shelf_path() -> Path:
    """Reference profiles are numbers only (no audio) and shared by every project: <repo>/.cache/references.json."""
    return Path(__file__).resolve().parent.parent / ".cache" / "references.json"


def load_shelf() -> list[Profile]:
    import json
    p = shelf_path()
    if not p.exists():
        return []
    return [Profile(**d) for d in json.loads(p.read_text())]


def add_references(files: list[str | Path], progress=None) -> list[Profile]:
    """Profile audio files (any format ffmpeg reads) and put them on the shelf, replacing same-named entries."""
    import json
    import shutil
    import subprocess
    import tempfile
    from dataclasses import asdict
    shelf = {p.name: p for p in load_shelf()}
    added = []
    for f in files:
        f = Path(f).expanduser()
        if not f.exists():
            raise FileNotFoundError(f)
        if progress:
            progress(f.name)
        if f.suffix.lower() == ".wav":
            prof = profile(f)
        else:
            if not shutil.which("ffmpeg"):
                raise RuntimeError("ffmpeg is needed to read non-WAV references")
            with tempfile.TemporaryDirectory() as td:
                wav = Path(td) / "ref.wav"
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(f), "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", str(wav)], check=True)
                prof = profile(wav, f.stem)
        shelf[prof.name] = prof
        added.append(prof)
    shelf_path().parent.mkdir(parents=True, exist_ok=True)
    shelf_path().write_text(json.dumps([asdict(p) for p in shelf.values()], indent=1) + "\n")
    return added


def summary_row(p: Profile) -> str:
    return (f"| {p.name[:44]} | {p.bpm:.0f} | {p.drop_lufs:.1f} | {p.crest_db:.1f} | {p.bands_db['sub']:.1f} | {p.bands_db['bass']:.1f} | "
            f"{p.bands_db['mid']:.1f} | {p.bands_db['high']:.1f} | {p.side_pct:.1f} | {p.side_bands['high']:.1f} | {p.pump_db:.1f} | "
            f"{p.transient_db:.1f} | {p.movement:.2f} | {p.repeat_pct:.0f} | {p.novelty_per_min:.1f} |")


SUMMARY_HEAD = ("| track | bpm | drop LUFS | crest | sub | bass | mid | high | side % | side % >4k | pump | transients | movement | repeat % | changes/min |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
