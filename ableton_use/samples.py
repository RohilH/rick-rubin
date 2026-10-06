"""Sample import: one-shots (Simpler instruments) and loops (audio tracks).

Splice (or any) samples come in at their own tempo and pitch. Before they enter
a song they are *conformed*, so the arrangement stays deterministic:

* **Loops** are time-stretched to the song tempo (pitch preserved, via ffmpeg's
  `atempo`), then trimmed or padded to an exact number of bars, with 2 ms edge
  fades. In Live they sit unwarped on audio tracks, so N bars of file = N bars
  of arrangement. To change the song tempo later, re-import the loops at the new
  tempo or turn Warp on in Live.
* **Risers / FX** can be conformed with `align="end"`. That keeps the *end* of
  the file, so the peak lands exactly on the downbeat that follows.
* **One-shots** are copied as-is. Melodic ones get their pitch measured
  (harmonic product spectrum + autocorrelation) so Simpler can be tuned and the
  preview can play them at the right pitch.

All files land in `<project>/samples/` as 24-bit/44.1 kHz WAV.
"""
from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.io import wavfile

from .model import BEATS_PER_BAR
from .theory import name as pitch_name

SR = 44100


# ============================================================================ io
def read_audio(path: str | Path) -> tuple[int, np.ndarray]:
    """Float32 (n, ch) in [-1, 1]. Handles 16/24/32-bit PCM and float WAV."""
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sr, x = wavfile.read(str(path))
    if x.dtype == np.int16:
        x = x.astype(np.float32) / 32768.0
    elif x.dtype == np.int32:
        x = x.astype(np.float32) / 2147483648.0
    elif x.dtype == np.uint8:
        x = (x.astype(np.float32) - 128) / 128.0
    else:
        x = x.astype(np.float32)
    if x.ndim == 1:
        x = x[:, None]
    return sr, x


def write_wav24(path: str | Path, sr: int, x: np.ndarray) -> None:
    """24-bit PCM WAV (scipy has no 24-bit writer, so pack by hand)."""
    x = np.clip(np.asarray(x, dtype=np.float64), -1, 1)
    if x.ndim == 1:
        x = x[:, None]
    ints = np.round(x * 8388607).astype(np.int32)
    b = ints.astype("<i4").view(np.uint8).reshape(-1, 4)[:, :3].tobytes()
    ch = x.shape[1]
    hdr = b"RIFF" + (36 + len(b)).to_bytes(4, "little") + b"WAVEfmt " + (16).to_bytes(4, "little")
    hdr += (1).to_bytes(2, "little") + ch.to_bytes(2, "little") + sr.to_bytes(4, "little")
    hdr += (sr * ch * 3).to_bytes(4, "little") + (ch * 3).to_bytes(2, "little") + (24).to_bytes(2, "little")
    hdr += b"data" + len(b).to_bytes(4, "little")
    Path(path).write_bytes(hdr + b)


def _resample(x: np.ndarray, sr_in: int, sr_out: int) -> np.ndarray:
    if sr_in == sr_out:
        return x
    from scipy.signal import resample_poly
    from math import gcd
    g = gcd(sr_in, sr_out)
    return resample_poly(x, sr_out // g, sr_in // g, axis=0).astype(np.float32)


# ============================================================================ pitch
def detect_pitch(path: str | Path, fmin: float = 25.0, fmax: float = 2000.0) -> float:
    """Fundamental of a one-shot as a fractional MIDI pitch (Ableton numbering: C3 = 60): the pitch of
    its longest steady stretch, from the same tracker `ableton-use notes` uses (so the two always agree).
    Raises ValueError when the sample has no steady pitch (noise, a drum hit, a chord)."""
    from .pitch import segment_notes, track_pitch
    sr, x = read_audio(path)
    times, midi = track_pitch(x, sr, fmin=fmin, fmax=fmax)
    notes = segment_notes(times, midi, min_s=0.03)
    if not notes:
        raise ValueError(f"{Path(path).name}: no steady pitch found — not a single-note sample? (check with `ableton-use notes`)")
    a, b, p = max(notes, key=lambda n: n[1] - n[0])
    sel = (times >= a) & (times <= b) & ~np.isnan(midi)
    return float(np.median(midi[sel])) if sel.any() else float(p)


# ============================================================================ conform
@dataclass
class Imported:
    path: Path            # absolute path of the conformed file
    rel: str              # project-relative path (what song.json stores)
    kind: str             # loop | oneshot
    bars: int | None = None
    root: float | None = None
    src_bpm: float | None = None

    def describe(self) -> str:
        if self.kind == "loop":
            return f"{self.rel}: {self.bars}-bar loop (from {self.src_bpm:g} BPM)"
        return f"{self.rel}: one-shot" + (f", root {pitch_name(round(self.root))} ({self.root:.2f})" if self.root is not None else "")


def _atempo_chain(ratio: float) -> str:
    parts = []
    while ratio > 2.0:
        parts.append("atempo=2.0")
        ratio /= 2.0
    while ratio < 0.5:
        parts.append("atempo=0.5")
        ratio /= 0.5
    parts.append(f"atempo={ratio:.6f}")
    return ",".join(parts)


def stretch(src: str | Path, dst: str | Path, ratio: float) -> None:
    """Change duration by 1/ratio keeping pitch (ratio>1 = faster). Needs ffmpeg.

    atempo swallows ~20 ms while its window fills, which would leave everything
    after the first transient early. So the input is padded with a second of
    silence on both sides and the output is trimmed by the padding *minus*
    whatever went missing, which keeps onsets within a few ms of the grid."""
    sr, x = read_audio(src)
    if abs(ratio - 1) < 1e-6:
        write_wav24(dst, sr, x)
        return
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg is required to tempo-match loops (brew install ffmpeg)")
    dst = Path(dst)
    tmp_in, tmp_out = dst.with_suffix(".pad.wav"), dst.with_suffix(".atempo.wav")
    pad = np.zeros((sr, x.shape[1]), np.float32)
    write_wav24(tmp_in, sr, np.concatenate([pad, x, pad]))
    try:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp_in), "-filter:a", _atempo_chain(ratio),
                        "-c:a", "pcm_s24le", str(tmp_out)], check=True)
        _, y = read_audio(tmp_out)
    finally:
        tmp_in.unlink(missing_ok=True)
        tmp_out.unlink(missing_ok=True)
    lost = max(0, int(round((len(x) + 2 * sr) / ratio)) - len(y))
    start = max(0, int(round(sr / ratio)) - lost)
    write_wav24(dst, sr, y[start: start + int(round(len(x) / ratio))])


def conform_loop(src: str | Path, dst: str | Path, src_bpm: float, bpm: float, bars: int | None = None,
                 align: str = "start", fade_ms: float = 2.0, end_at: float | None = None) -> int:
    """Tempo-match `src` to `bpm` and cut it to exactly `bars` bars (default: nearest
    whole number of bars). align='end' keeps the tail (for risers). `end_at` (seconds
    into the conformed audio) drops everything after that moment first — with
    align='end' it puts a riser's peak, rather than the end of its tail, on the
    downbeat that follows. Returns bars."""
    dst = Path(dst)
    tmp = dst.with_suffix(".stretch.wav")
    stretch(src, tmp, bpm / src_bpm)
    sr, x = read_audio(tmp)
    tmp.unlink(missing_ok=True)
    x = _resample(x, sr, SR)
    if end_at is not None:
        x = x[: int(round(end_at * SR))]
    bar_s = BEATS_PER_BAR * 60.0 / bpm
    if bars is None:
        bars = max(1, int(round(len(x) / SR / bar_s)))
    n = int(round(bars * bar_s * SR))
    if align == "end":
        x = x[-n:] if len(x) >= n else np.concatenate([np.zeros((n - len(x), x.shape[1]), np.float32), x])
    else:
        x = x[:n] if len(x) >= n else np.concatenate([x, np.zeros((n - len(x), x.shape[1]), np.float32)])
    f = max(1, int(fade_ms / 1000 * SR))
    ramp = np.linspace(0, 1, f, dtype=np.float32)[:, None]
    x = x.copy()
    x[:f] *= ramp
    x[-f:] *= ramp[::-1]
    write_wav24(dst, SR, x)
    return bars


def import_sample(project_dir: str | Path, src: str | Path, name: str, *, loop: bool = False,
                  src_bpm: float | None = None, bpm: float | None = None, bars: int | None = None,
                  align: str = "start", melodic: bool = False, end_at: float | None = None) -> Imported:
    """Copy/conform a sample into <project>/samples/<name>.wav."""
    project_dir = Path(project_dir)
    out = project_dir / "samples" / f"{name}.wav"
    out.parent.mkdir(parents=True, exist_ok=True)
    rel = str(out.relative_to(project_dir))
    if loop:
        if not (src_bpm and bpm):
            raise ValueError("loops need src_bpm (the sample's tempo) and bpm (the song's)")
        bars = conform_loop(src, out, src_bpm, bpm, bars, align, end_at=end_at)
        return Imported(out, rel, "loop", bars=bars, src_bpm=src_bpm)
    sr, x = read_audio(src)
    write_wav24(out, SR, _resample(x, sr, SR))
    root = detect_pitch(out) if melodic else None
    return Imported(out, rel, "oneshot", root=root)


# ============================================================================ audition
def describe_sample(path: str | Path) -> dict:
    """What a sample is, in numbers — so candidates can be compared without listening:
    length, level, how fast it hits and dies, where its energy sits, its pitch and octave, its width,
    plus `character`: the same facts as plain words (see `character_words`)."""
    sr, x = read_audio(path)
    return describe_audio(sr, x, Path(path).name)


def describe_audio(sr: int, x: np.ndarray, name: str = "") -> dict:
    """describe_sample for audio already in memory (float, shape (n, channels))."""
    from .analysis import BANDS, loudness_lufs, stereo_stats
    from .pitch import hz, segment_notes, track_pitch
    from .theory import name as pitch_name
    m = x.mean(axis=1).astype(np.float64)
    peak = float(np.abs(m).max() + 1e-12)
    rms = float(np.sqrt(np.mean(m * m)) + 1e-12)
    # envelope at 1 ms: attack = 10% -> 90% of peak, decay = peak -> -20 dB
    k = max(1, sr // 1000)
    env = np.abs(m[: len(m) // k * k]).reshape(-1, k).max(axis=1)
    ip = int(np.argmax(env))
    pre = env[: ip + 1]
    a10 = int(np.argmax(pre >= 0.1 * env[ip]))
    a90 = int(np.argmax(pre >= 0.9 * env[ip]))
    tail = np.maximum.accumulate(env[ip:][::-1])[::-1]              # level never rises again after this point
    under = np.flatnonzero(tail < 0.1 * env[ip])
    spec = np.abs(np.fft.rfft(m * np.hanning(len(m)))) ** 2
    f = np.fft.rfftfreq(len(m), 1 / sr)
    tot = spec[(f >= 20) & (f < 20000)].sum() + 1e-12
    times, midi = track_pitch(x, sr, fmin=30.0)
    notes = segment_notes(times, midi)
    main = max(notes, key=lambda n: n[1] - n[0]) if notes else None
    lufs = loudness_lufs(x, sr) if len(x) >= 0.5 * sr else float("nan")
    st = stereo_stats(x, sr)
    d = {
        "file": name, "seconds": len(x) / sr, "peak_db": float(20 * np.log10(peak)), "rms_db": float(20 * np.log10(rms)),
        "lufs": float(lufs), "crest_db": float(20 * np.log10(peak / rms)), "attack_ms": float(a90 - a10),
        "decay_ms": float(under[0]) if len(under) else float("nan"),
        "centroid_hz": float((f * spec).sum() / (spec.sum() + 1e-12)),
        "bands": {nm: float(100 * spec[(f >= lo) & (f < hi)].sum() / tot) for nm, lo, hi in BANDS},
        "pitch": pitch_name(int(round(main[2]))) if main else None, "pitch_hz": float(hz(main[2])) if main else None,
        "cents": float(round((main[2] - round(main[2])) * 100)) if main else None,
        "n_notes": len(notes), "side_pct": float(st.side_pct), "correlation": float(st.correlation),
        "low_side_pct": float(st.bands["low"][0]),
    }
    d["character"] = character_words(d)
    return d


def character_words(d: dict) -> list[str]:
    """A sound's measured character as plain words — one shared vocabulary for samples and synth presets,
    so they can be searched and compared the same way. Thresholds are deliberately coarse.

    length:      short (< 0.3 s) · long (> 2 s)
    attack:      snappy (< 5 ms) · soft-attack (30-120 ms) · slow-attack (> 120 ms)
    decay:       tight (< 120 ms to -20 dB) · ringing (> 600 ms) · sustained (does not fall 20 dB while it lasts)
    brightness:  dark (centroid < 400 Hz) · warm (400-1200) · bright (1200-4000) · airy (> 4000)
    low end:     subby (> 35% of energy below 60 Hz) · bassy (> 60% below 200 Hz) · no-low-end (< 3% below 200 Hz)
    width:       mono (side < 1%) · wide (> 15%) · very-wide (> 30%) · wide-low-end (> 10% side below 150 Hz)
    pitch:       pitched · unpitched · melodic (several notes)
    dynamics:    punchy (crest > 14 dB) · dense (crest < 8 dB)"""
    w = []
    sec, att, dec, cen = d["seconds"], d["attack_ms"], d["decay_ms"], d["centroid_hz"]
    b = d["bands"]
    if sec < 0.3:
        w.append("short")
    elif sec > 2.0:
        w.append("long")
    w.append("snappy" if att < 5 else "slow-attack" if att > 120 else "soft-attack" if att >= 30 else "")
    w.append("sustained" if dec is None or dec != dec else "tight" if dec < 120 else "ringing" if dec > 600 else "")
    w.append("dark" if cen < 400 else "warm" if cen < 1200 else "bright" if cen < 4000 else "airy")
    low = b["sub"] + b["bass"]
    w.append("subby" if b["sub"] > 35 else "")
    w.append("bassy" if low > 60 else "no-low-end" if low < 3 else "")
    w.append("mono" if d["side_pct"] < 1 else "very-wide" if d["side_pct"] > 30 else "wide" if d["side_pct"] > 15 else "")
    if d["low_side_pct"] > 10:
        w.append("wide-low-end")
    w.append("melodic" if d["n_notes"] > 2 else "pitched" if d["pitch"] else "unpitched")
    w.append("punchy" if d["crest_db"] > 14 else "dense" if d["crest_db"] < 8 else "")
    return [x for x in w if x]


def _has(v) -> bool:
    return v is not None and v == v and v != float("-inf")


def feature_row(r: dict, label: str | None = None) -> str:
    b = r["bands"]
    loud = f"{r['lufs']:.1f} LUFS" if _has(r.get("lufs")) else f"{r['rms_db']:.1f} rms"
    pitch = f"{r['pitch']} {r['pitch_hz']:.0f} Hz {r['cents']:+.0f}c" if r.get("pitch") else "—"
    decay = f"{r['decay_ms']:.0f} ms" if _has(r.get("decay_ms")) else "sustains"
    return (f"| {label or r['file']} | {r['seconds']:.2f} | {r['peak_db']:.1f} | {loud} | {r['crest_db']:.1f} | {r['attack_ms']:.0f} ms | {decay} | "
            f"{r['centroid_hz']:.0f} Hz | {b['sub']:.0f} | {b['bass']:.0f} | {b['lowmid']:.0f} | {b['mid']:.0f} | {b['high']:.0f} | {b['air']:.1f} | "
            f"{pitch} | {r['side_pct']:.1f} ({r['low_side_pct']:.1f}) | {' '.join(r.get('character', []))} |")


FEATURE_HEAD = ("| name | sec | peak | loud | crest | attack | decay | centroid | sub% | bass% | lowmid% | mid% | high% | air% | pitch | side% (low) | character |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")


def audition_table(paths: list[str | Path]) -> str:
    """Candidates side by side. Columns: length, peak, loudness (LUFS, or RMS for short hits), crest,
    attack (10-90%), decay (to -20 dB), spectral centroid, energy by band, main pitch with octave,
    stereo side %, and the character words (see `character_words`)."""
    return FEATURE_HEAD + "\n" + "\n".join(feature_row(describe_sample(p)) for p in paths)


def jsonable(d: dict) -> dict:
    """describe_* output with NaN/inf replaced by None, for JSON."""
    return {k: (None if isinstance(v, float) and (v != v or v in (float("inf"), float("-inf"))) else v) for k, v in d.items()}


# ============================================================================ a project's sample library
def analyse_project_samples(project_dir: str | Path) -> dict[str, dict]:
    """Measured character of every wav under <project>/samples (raw downloads and imports), cached in
    samples/manifest.json under "analysis" and refreshed when a file changes."""
    import json
    project_dir = Path(project_dir)
    mpath = project_dir / "samples" / "manifest.json"
    manifest = json.loads(mpath.read_text()) if mpath.exists() else {}
    cache = manifest.get("analysis", {})
    out: dict[str, dict] = {}
    changed = False
    for wav in sorted((project_dir / "samples").rglob("*.wav")):
        if "cuts" in wav.parts:
            continue
        rel = str(wav.relative_to(project_dir))
        mt = round(wav.stat().st_mtime, 3)
        hit = cache.get(rel)
        if hit and hit.get("mtime") == mt:
            out[rel] = hit
            continue
        d = jsonable(describe_sample(wav))
        d["mtime"] = mt
        out[rel] = d
        changed = True
    if changed or set(cache) != set(out):
        manifest["analysis"] = out
        mpath.parent.mkdir(parents=True, exist_ok=True)
        mpath.write_text(json.dumps(manifest, indent=1) + "\n")
    return out


SORT_KEYS = {
    "attack": lambda d: d["attack_ms"], "decay": lambda d: d["decay_ms"] if _has(d.get("decay_ms")) else 1e9,
    "bright": lambda d: -d["centroid_hz"], "dark": lambda d: d["centroid_hz"], "sub": lambda d: -d["bands"]["sub"],
    "bass": lambda d: -(d["bands"]["sub"] + d["bands"]["bass"]), "wide": lambda d: -d["side_pct"], "loud": lambda d: -d["rms_db"],
    "length": lambda d: d["seconds"],
}


def search_rows(rows: dict[str, dict], words: list[str] | None = None, sort: str | None = None,
                extra: dict[str, str] | None = None) -> list[tuple[str, dict]]:
    """Filter analysed sounds by words — each must appear in the name, the character words, or `extra[name]`
    (tags, description...). A word starting with '-' excludes. sort: attack decay bright dark sub bass wide loud length."""
    out = []
    for name, d in rows.items():
        words_of = set(d.get("character", []))                                  # character words match whole ("bass" is not "bassy")
        text = " ".join([name.lower(), (extra or {}).get(name, "").lower()])     # names, folders, tags, descriptions match anywhere
        ok = True
        for w in words or []:
            w = w.lower()
            neg = w.startswith("-") and len(w) > 1
            hit = (w[1:] if neg else w) in words_of or (w[1:] if neg else w) in text
            ok = ok and (not hit if neg else hit)
        if ok:
            out.append((name, d))
    if sort:
        if sort not in SORT_KEYS:
            raise ValueError(f"sort by one of: {', '.join(SORT_KEYS)}")
        out.sort(key=lambda kv: SORT_KEYS[sort](kv[1]))
    return out


def similar(rows: dict[str, dict], target: dict, n: int = 10) -> list[tuple[str, dict, float]]:
    """The `n` sounds in `rows` whose measured character is closest to `target` (attack, decay, brightness,
    low-end share, width, crest)."""
    def vec(d):
        dec = d["decay_ms"] if _has(d.get("decay_ms")) else 4000.0
        return np.array([np.log10(d["attack_ms"] + 1.0) / 2.5, np.log10(dec + 1.0) / 3.6, np.log10(max(d["centroid_hz"], 20.0)) / 4.3,
                         d["bands"]["sub"] / 100.0, (d["bands"]["sub"] + d["bands"]["bass"]) / 100.0, d["side_pct"] / 50.0, d["crest_db"] / 24.0])
    t = vec(target)
    scored = [(name, d, float(np.linalg.norm(vec(d) - t))) for name, d in rows.items()]
    return sorted(scored, key=lambda x: x[2])[:n]
