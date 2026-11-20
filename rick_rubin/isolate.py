"""Cut one part out of a reference recording, so a synth can be matched against it.

    isolate("refs/track.wav", "samples/raw/ref_bass.wav", part="bass", bars=(33, 36), bpm=124)

The time range is cut first (bars at the reference's tempo, or seconds). Then the part is separated:

* with demucs (`pip install "rick-rubin[separate]"`, heavy: PyTorch and a model download on first use), the
  htdemucs model splits drums / bass / vocals / other; lead, pad, chords and keys come from "other";
* without it, a band-pass is the fallback: bass 30-250 Hz, lead 300 Hz-8 kHz, pad 150 Hz-6 kHz. That keeps
  whatever else sits in the band (the kick under a bass, hats over a lead), so say so when you use it;
* `stem=` takes a stem you already have (from the artist, or another separator) and only cuts it.

The result is a 24-bit wav plus the notes it plays (`pitch.sample_notes`), so the match can render the same notes.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

from .samples import read_audio, write_wav24

PARTS = {"bass": ("bass", (30.0, 250.0)), "drums": ("drums", None), "vocals": ("vocals", (120.0, 9000.0)),
         "lead": ("other", (300.0, 8000.0)), "pad": ("other", (150.0, 6000.0)), "chords": ("other", (150.0, 6000.0)),
         "keys": ("other", (150.0, 6000.0)), "other": ("other", (150.0, 8000.0))}


def have_demucs() -> bool:
    try:
        import demucs  # noqa: F401
        return True
    except ImportError:
        return False


def _cut(x: np.ndarray, sr: int, start_s: float, end_s: float | None) -> np.ndarray:
    a = max(0, int(round(start_s * sr)))
    b = len(x) if end_s is None else min(len(x), int(round(end_s * sr)))
    if b <= a:
        raise ValueError(f"empty range {start_s:g}-{end_s} s (the file is {len(x) / sr:.1f} s)")
    y = x[a:b].copy()
    f = min(len(y) // 4, int(0.003 * sr))
    if f:
        ramp = np.linspace(0, 1, f, dtype=np.float32)[:, None]
        y[:f] *= ramp
        y[-f:] *= ramp[::-1]
    return y


def _demucs(src: Path, stem: str, workdir: Path) -> Path:
    cmd = [sys.executable, "-m", "demucs.separate", "-n", "htdemucs", "-o", str(workdir), str(src)]
    if stem != "drums":
        cmd[4:4] = [f"--two-stems={stem}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"demucs failed: {(r.stderr or r.stdout).strip()[-400:]}")
    hits = list(workdir.rglob(f"{stem}.wav"))
    if not hits:
        raise RuntimeError(f"demucs wrote no {stem}.wav under {workdir}")
    return hits[0]


def isolate(src: str | Path, out: str | Path, part: str = "bass", bars: tuple[int, int] | None = None, bpm: float | None = None,
            start_s: float | None = None, end_s: float | None = None, method: str = "auto", stem: str | Path | None = None,
            note_bpm: float | None = None) -> dict:
    """Cut `src` (or a ready `stem`) to the range and separate `part`. Returns {"path", "method", "start_s", "end_s",
    "bpm", "notes", "warning"}. method: auto (demucs when installed, else band-pass) | demucs | bandpass | none."""
    from . import pitch
    from .reference import estimate_bpm
    if part not in PARTS:
        raise ValueError(f"part is one of: {', '.join(PARTS)}")
    sr, x = read_audio(stem or src)
    if bars is not None:
        if bpm is None:
            bpm = estimate_bpm(x.mean(axis=1), sr)
        bar_s = 4 * 60.0 / bpm
        start_s, end_s = (bars[0] - 1) * bar_s, bars[1] * bar_s
    start_s = start_s or 0.0
    y = _cut(x, sr, start_s, end_s)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    warning = None
    used = "stem" if stem else method
    if not stem:
        name, band = PARTS[part]
        if method == "auto":
            used = "demucs" if have_demucs() else "bandpass"
        if used == "demucs":
            with tempfile.TemporaryDirectory() as td:
                cut = Path(td) / "cut.wav"
                write_wav24(cut, sr, y)
                sep = _demucs(cut, name, Path(td) / "sep")
                ssr, y = read_audio(sep)
                if ssr != sr:
                    from .samples import _resample
                    y = _resample(y, ssr, sr)
                if part in ("lead", "pad", "chords", "keys") and band:
                    warning = f"demucs puts every melodic part that is not bass or vocals in 'other'; the {part} shares it with them"
        elif used == "bandpass":
            if band is None:
                raise RuntimeError("drums cannot be band-passed out of a mix: install demucs (pip install \"rick-rubin[separate]\") or pass stem=")
            from scipy.signal import butter, sosfiltfilt
            lo, hi = band
            sos = butter(4, [lo, min(hi, sr / 2 * 0.95)], btype="band", fs=sr, output="sos")
            y = sosfiltfilt(sos, y, axis=0).astype(np.float32)
            warning = (f"band-passed {lo:g}-{hi:g} Hz (demucs is not installed): anything else in that band is still in it"
                       + (" — the kick, for a bass" if part == "bass" else ""))
        elif used != "none":
            raise ValueError("method is auto, demucs, bandpass or none")
    peak = float(np.abs(y).max())
    if peak > 0.99:
        y = y * (0.99 / peak)
    write_wav24(out, sr, y)
    notes = pitch.sample_notes(out, note_bpm or bpm or 120.0, fmin=25.0 if part == "bass" else 65.0)
    return {"path": out, "method": used, "start_s": start_s, "end_s": start_s + len(y) / sr, "bpm": bpm, "notes": notes, "warning": warning}

