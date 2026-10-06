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
    """Fundamental of a one-shot as a fractional MIDI pitch (Ableton numbering: C3 = 60).

    Analyses 150 ms just after the attack with a harmonic product spectrum and
    checks it against autocorrelation. If they disagree by about an octave (a
    common HPS failure), the autocorrelation estimate is used."""
    sr, x = read_audio(path)
    m = x.mean(axis=1).astype(np.float64)
    m /= np.abs(m).max() + 1e-12
    i0 = int(np.argmax(np.abs(m) > 0.3)) + int(0.02 * sr)
    seg = m[i0: i0 + int(0.15 * sr)]
    if len(seg) < int(0.03 * sr):
        seg = m[: int(0.15 * sr)]
    seg = seg * np.hanning(len(seg))
    n = 1 << 18
    S = np.abs(np.fft.rfft(seg, n))
    f = np.fft.rfftfreq(n, 1 / sr)
    hps = S.copy()
    for h in (2, 3, 4):
        d = S[::h]
        hps[: len(d)] *= d
    band = (f > fmin) & (f < fmax)
    f_hps = float(f[band][np.argmax(hps[band])])
    ac = np.correlate(seg, seg, "full")[len(seg) - 1:]
    lo, hi = int(sr / fmax), min(len(ac) - 1, int(sr / fmin))
    lag = lo + int(np.argmax(ac[lo:hi]))
    # parabolic interpolation for sub-sample lag
    if 0 < lag < len(ac) - 1:
        a, b, c = ac[lag - 1], ac[lag], ac[lag + 1]
        lag = lag + 0.5 * (a - c) / (a - 2 * b + c + 1e-12)
    f_ac = sr / lag
    f0 = f_hps if abs(12 * np.log2(f_hps / f_ac)) < 1.0 else f_ac
    # Standard MIDI numbering (60 = 261.6 Hz); Ableton only *names* it C3.
    return float(69 + 12 * np.log2(f0 / 440.0))


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
    """Change duration by 1/ratio keeping pitch (ratio>1 = faster). Needs ffmpeg."""
    if abs(ratio - 1) < 1e-6:
        sr, x = read_audio(src)
        write_wav24(dst, sr, x)
        return
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg is required to tempo-match loops (brew install ffmpeg)")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-filter:a", _atempo_chain(ratio),
                    "-ar", str(SR), "-c:a", "pcm_s24le", str(dst)], check=True)


def conform_loop(src: str | Path, dst: str | Path, src_bpm: float, bpm: float, bars: int | None = None,
                 align: str = "start", fade_ms: float = 2.0) -> int:
    """Tempo-match `src` to `bpm` and cut it to exactly `bars` bars (default: nearest
    whole number of bars). align='end' keeps the tail (for risers). Returns bars."""
    dst = Path(dst)
    tmp = dst.with_suffix(".stretch.wav")
    stretch(src, tmp, bpm / src_bpm)
    sr, x = read_audio(tmp)
    tmp.unlink(missing_ok=True)
    x = _resample(x, sr, SR)
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
                  align: str = "start", melodic: bool = False) -> Imported:
    """Copy/conform a sample into <project>/samples/<name>.wav."""
    project_dir = Path(project_dir)
    out = project_dir / "samples" / f"{name}.wav"
    out.parent.mkdir(parents=True, exist_ok=True)
    rel = str(out.relative_to(project_dir))
    if loop:
        if not (src_bpm and bpm):
            raise ValueError("loops need src_bpm (the sample's tempo) and bpm (the song's)")
        bars = conform_loop(src, out, src_bpm, bpm, bars, align)
        return Imported(out, rel, "loop", bars=bars, src_bpm=src_bpm)
    sr, x = read_audio(src)
    write_wav24(out, SR, _resample(x, sr, SR))
    root = detect_pitch(out) if melodic else None
    return Imported(out, rel, "oneshot", root=root)
