"""The notes inside a sample — a reading view of what a pitch editor shows as blobs.

`track_pitch()` follows the fundamental through a single-voice recording (a vocal,
a bassline, a lead) with the YIN method; `sample_notes()` cuts that curve into
notes and says, for each one: which pitch, how many cents sharp or flat, where it
starts on the song grid and how long it lasts. With that an agent can tell what
melody a vocal loop sings, whether it fits the key, and which chord tones to put
under which word.

Single-voice only: chords or several instruments in one file need a polyphonic
transcriber, which this is not. Results are cached next to the sample as
`<name>.notes.json` and printed in `score.md`.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from .model import STEP, fmt_pos
from .samples import read_audio
from .theory import name as pitch_name

HOP_S = 0.010


@dataclass
class SampleNote:
    name: str            # nearest pitch, Ableton naming (C3 = 60)
    midi: float          # measured pitch (fractional)
    cents: float         # deviation from that pitch: + sharp, - flat
    start_s: float
    end_s: float
    beat: float          # start, in beats from the start of the file
    pos: str             # bar.beat.sixteenth of the nearest 16th
    beats: float         # length in beats
    in_key: bool | None = None


def sidecar(path: str | Path) -> Path:
    return Path(path).with_suffix(".notes.json")


def track_pitch(x: np.ndarray, sr: int, fmin: float = 65.0, fmax: float = 1000.0, threshold: float = 0.15,
                floor_db: float = -40.0) -> tuple[np.ndarray, np.ndarray]:
    """(times, midi) every HOP_S; midi is NaN where there is no clear pitch (silence, noise, consonants).
    YIN: the lag at which the signal best matches a shifted copy of itself."""
    m = (x.mean(axis=1) if x.ndim > 1 else x).astype(np.float64)
    peak = np.abs(m).max() + 1e-12
    hop, tau_min, tau_max = int(HOP_S * sr), int(sr / fmax), int(sr / fmin)
    W = max(int(0.03 * sr), 2 * tau_max)                       # at least two periods of the lowest pitch
    n = W + tau_max
    nfft = 1 << int(np.ceil(np.log2(n + W)))
    times, out = [], []
    taus = np.arange(1, tau_max + 1)
    for i in range(0, max(1, len(m) - n), hop):
        frame = m[i:i + n]
        times.append((i + W / 2) / sr)
        a = frame[:W]
        if np.sqrt(np.mean(a * a)) < peak * 10 ** (floor_db / 20):
            out.append(np.nan)
            continue
        corr = np.fft.irfft(np.fft.rfft(frame, nfft) * np.conj(np.fft.rfft(a, nfft)), nfft)[: tau_max + 1]
        cs = np.concatenate([[0.0], np.cumsum(frame * frame)])
        energy = cs[W:W + tau_max + 1] - cs[: tau_max + 1]     # energy of the window shifted by tau
        d = energy[0] + energy - 2 * corr
        cm = np.ones(tau_max + 1)
        cm[1:] = d[1:] * taus / np.maximum(np.cumsum(d[1:]), 1e-12)
        seg = cm[tau_min:]
        below = np.flatnonzero(seg < threshold)
        if len(below):
            t = int(below[0])
            while t + 1 < len(seg) and seg[t + 1] < seg[t]:    # walk down to the bottom of that dip
                t += 1
        else:
            t = int(np.argmin(seg))
            if seg[t] > 0.35:                                  # nothing periodic here
                out.append(np.nan)
                continue
        tau = t + tau_min
        if 1 <= tau < tau_max:                                 # parabolic refinement between samples
            y0, y1, y2 = cm[tau - 1], cm[tau], cm[tau + 1]
            den = y0 - 2 * y1 + y2
            tau = tau + (0.5 * (y0 - y2) / den if abs(den) > 1e-12 else 0.0)
        out.append(69 + 12 * np.log2(sr / tau / 440.0))
    return np.array(times), np.array(out)


def segment_notes(times: np.ndarray, midi: np.ndarray, min_s: float = 0.06, split_semitones: float = 0.8,
                  bridge_s: float = 0.03) -> list[tuple[float, float, float]]:
    """(start_s, end_s, pitch) runs of steady pitch. A new note starts when the pitch moves more than
    `split_semitones` from the current note's centre and stays there, or after an unvoiced gap."""
    notes: list[tuple[float, float, float]] = []
    cur: list[int] = []
    gap = 0

    def close():
        if cur and times[cur[-1]] - times[cur[0]] + HOP_S >= min_s:
            notes.append((float(times[cur[0]] - HOP_S / 2), float(times[cur[-1]] + HOP_S / 2), float(np.median(midi[cur]))))

    for i, p in enumerate(midi):
        if np.isnan(p):
            gap += 1
            if cur and gap * HOP_S > bridge_s:
                close()
                cur = []
            continue
        gap = 0
        if cur and abs(p - np.median(midi[cur])) > split_semitones:
            # a jump: only a new note if the next frames agree with it (not a one-frame glitch)
            ahead = midi[i:i + 3]
            ahead = ahead[~np.isnan(ahead)]
            if len(ahead) >= 2 and abs(np.median(ahead) - p) < split_semitones:
                close()
                cur = []
            else:
                continue
        cur.append(i)
    close()
    return _tidy(notes)


def _tidy(notes: list[tuple[float, float, float]], blip_s: float = 0.12, join_gap_s: float = 0.07) -> list[tuple[float, float, float]]:
    """Fix the two things a pitch tracker gets wrong on real voices: a short blip exactly an
    octave away from the note next to it is that note (an octave error), and one held note
    broken by a consonant or a breath is still one note."""
    fixed = []
    for i, (a, b, p) in enumerate(notes):
        if b - a < blip_s:
            # the longest proper note within half a second decides which octave a blip belongs to
            near = [n for j, n in enumerate(notes) if j != i and n[1] - n[0] >= blip_s and n[0] < b + 0.5 and n[1] > a - 0.5]
            if near:
                ref = max(near, key=lambda n: n[1] - n[0])[2]
                d = p - ref
                if abs(abs(d) - 12) < 0.7:
                    p -= 12 * np.sign(d)
        fixed.append((a, b, float(p)))
    out: list[tuple[float, float, float]] = []
    for a, b, p in fixed:
        if out and a - out[-1][1] < join_gap_s and abs(p - out[-1][2]) < 0.5:
            la, lb, lp = out[-1]
            out[-1] = (la, b, (lp * (lb - la) + p * (b - a)) / ((lb - la) + (b - a)))
        else:
            out.append((a, b, p))
    return out


def sample_notes(path: str | Path, bpm: float, key=None, save: bool = True, **track_kw) -> list[SampleNote]:
    """The notes of a single-voice sample, on the grid at `bpm`. `key` (a theory.Key) marks each note in or out of key."""
    sr, x = read_audio(path)
    times, midi = track_pitch(x, sr, **track_kw)
    out = []
    for a, b, p in segment_notes(times, midi):
        near = int(round(p))
        beat = a * bpm / 60.0
        out.append(SampleNote(pitch_name(near), round(p, 2), round((p - near) * 100, 0), round(a, 3), round(b, 3), round(beat, 3),
                              fmt_pos(round(beat / STEP) * STEP), round((b - a) * bpm / 60.0, 2),
                              None if key is None else bool(key.contains(near))))
    if save:
        sidecar(path).write_text(json.dumps({"file": Path(path).name, "bpm": bpm, "notes": [asdict(n) for n in out]}, indent=1) + "\n")
    return out


def load_notes(path: str | Path) -> list[SampleNote] | None:
    p = sidecar(path)
    if not p.exists():
        return None
    return [SampleNote(**n) for n in json.loads(p.read_text())["notes"]]


def pitch_at(notes: list[SampleNote], t0: float, t1: float) -> SampleNote | None:
    """The note that covers most of the time span t0..t1 (e.g. a syllable), if any."""
    best, cover = None, 0.0
    for n in notes:
        c = min(n.end_s, t1) - max(n.start_s, t0)
        if c > cover:
            best, cover = n, c
    return best


def hz(midi: float) -> float:
    return 440.0 * 2 ** ((midi - 69) / 12)


def register(notes: list[SampleNote]) -> str:
    """One line on where the sample sits: lowest-highest note with octaves and Hz, and its centre."""
    if not notes:
        return "no pitched notes found (noise, drums, or several voices at once)"
    lo, hi = min(notes, key=lambda n: n.midi), max(notes, key=lambda n: n.midi)
    w = np.array([n.end_s - n.start_s for n in notes])
    centre = float(np.sum(np.array([n.midi for n in notes]) * w) / w.sum())
    return (f"range {lo.name}-{hi.name} ({hz(lo.midi):.0f}-{hz(hi.midi):.0f} Hz), centre {pitch_name(round(centre))} "
            f"({hz(centre):.0f} Hz), {len(notes)} notes; octaves are Ableton's (C3 = middle C = 261.6 Hz)")


def _label(n: SampleNote) -> str:
    return n.name + (f"{n.cents:+.0f}c" if abs(n.cents) >= 15 else "") + ("!" if n.in_key is False else "")


def notes_text(notes: list[SampleNote]) -> list[str]:
    """Lines for score.md, one per bar: 'beat.sixteenth PITCH[±cents] length'. '!' marks a note outside the song's key;
    cents are shown from 15 up."""
    by_bar: dict[str, list[str]] = {}
    for n in notes:
        bar, rest = n.pos.split(".", 1)
        by_bar.setdefault(bar, []).append(f"{rest} {_label(n)} {n.beats:g}")
    return [f"  pitch: {register(notes)}"] + [f"  notes bar {bar}: " + "; ".join(v) for bar, v in by_bar.items()]


def table(notes: list[SampleNote], words=None) -> str:
    """Notes as a table; with `words` (from transcribe) each note shows the syllable sung on it."""
    L = [register(notes), "", "pos (bar.beat.16th)  pitch      Hz   cents   length   time             " + ("syllable" if words else "")]
    sylls = [(s, w) for w in (words or []) for s in w.syllables]
    for n in notes:
        said = ""
        if sylls:
            hit = [s.text for s, _ in sylls if min(s.end_s, n.end_s) - max(s.start_s, n.start_s) > 0.02]
            said = " ".join(hit)
        L.append(f"{n.pos:<20} {n.name:<6}{'!' if n.in_key is False else ' '} {hz(n.midi):5.0f}  {n.cents:+5.0f}   {n.beats:5.2f} b  {n.start_s:6.2f}-{n.end_s:5.2f}s   {said}")
    return "\n".join(L)
