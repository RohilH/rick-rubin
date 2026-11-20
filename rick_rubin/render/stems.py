"""One track of a song as an audio file, for render targets that take the part as audio.

Logic has no Simpler to hand a one-shot to from a script, so a `sample=` track goes into Logic the way a
Serum track does: its part rendered offline (the same notes, velocity law and attack the preview and Live
use) and imported on an audio track. The file is the dry part at the sample's own level: fader, pan,
effects, sends and side chain stay in the DAW.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from ..model import Song, Track, sample_gain_db


def sample_stem(song: Song, track: Track, clips, out_dir: str | Path, sr: int = 44100) -> Path:
    """Every note of `track` in `clips` (pass the sounding notes: `song.flatten(sounding=True)`) played from
    the track's sample: the whole file per hit for drum roles (Simpler's One-Shot), repitched from
    `sample_root` and cut at note-off for melodic roles (Classic). Stereo samples stay stereo. The file is
    the song's length and cached by content."""
    from ..samples import _resample, read_audio, write_wav24
    src = Path(song.resolve(track.sample))
    spb = 60.0 / song.bpm
    notes = sorted((round((c.start + n.start) * spb, 6), n.pitch, round(n.dur * spb, 6), n.vel)
                   for c in clips if c.track == track.name for n in c.notes)
    attack_ms = float(track.instrument_params.get("Ve Attack", 0) or 0) if track.instrument_params else 0.0
    sig = hashlib.sha1(json.dumps([str(src), src.stat().st_mtime, notes, song.bpm, song.total_bars, track.sample_root, track.is_drum,
                                   attack_ms, track.instrument_params.get("Vol < Vel") if track.instrument_params else None, sr, "v1"],
                                  default=str).encode()).hexdigest()[:10]
    out_dir = Path(out_dir)
    out = out_dir / f"{_safe(track.name)}.{sig}.wav"
    if out.exists():
        return out
    sr0, x = read_audio(src)
    x = _resample(x, sr0, sr).astype(np.float32)
    if x.ndim == 1:
        x = x[:, None]
    if x.shape[1] == 1:
        x = np.repeat(x, 2, axis=1)
    total = int(round(song.total_bars * 4 * spb * sr))
    buf = np.zeros((total + len(x) + sr, 2), dtype=np.float32)
    pitched: dict[tuple, np.ndarray] = {}
    for t0, pitch, dur, vel in notes:
        if track.is_drum:
            w = x
        else:
            key = (pitch, dur)
            if key not in pitched:
                ratio = 2 ** ((pitch - (track.sample_root or 60)) / 12)
                n_out = max(1, int(len(x) / ratio))
                pos = np.arange(n_out) * ratio
                y = np.stack([np.interp(pos, np.arange(len(x)), x[:, ch]) for ch in range(2)], axis=1).astype(np.float32)
                hold, rel = int(dur * sr), int(0.05 * sr)
                if hold < len(y):
                    y = y[: hold + rel].copy()
                    tail = len(y) - hold
                    if tail > 0:
                        y[hold:] *= np.linspace(1, 0, tail, dtype=np.float32)[:, None]
                pitched[key] = y
            w = pitched[key]
        if attack_ms > 0.5:
            k = min(len(w), int(attack_ms / 1000.0 * sr))
            w = w.copy()
            w[:k] *= np.linspace(0, 1, k, dtype=np.float32)[:, None]
        i = int(round(t0 * sr))
        j = min(len(buf), i + len(w))
        if j > i >= 0:
            buf[i:j] += w[: j - i] * (10 ** (sample_gain_db(track, vel) / 20))
    buf = buf[:total]
    f = min(len(buf), int(0.005 * sr))
    if f:
        buf[-f:] *= np.linspace(1, 0, f, dtype=np.float32)[:, None]
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob(f"{_safe(track.name)}.*.wav"):               # one current stem per track
        if not old.name.endswith(".baked.wav"):
            old.unlink()
    write_wav24(out, sr, buf)
    return out


def _safe(s: str) -> str:
    return "".join(ch if ch.isalnum() or ch in " -_()" else "_" for ch in s).strip() or "track"
