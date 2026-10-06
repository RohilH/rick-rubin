"""MIDI effects on a track — real devices in Live, emulated offline where that is well defined.

A track's `midi_effects` is an ordered list like its audio `effects`:

    keys = song.add_track("Keys", "chords", instrument="Drift",
                          midi_effects=[{"device": "Chord", "params": {"Shift1": 3, "Shift2": 7, "Shift3": 10, "Velocity3": 70}}])

`push` puts the actual devices in front of the instrument, so in Live you see one-finger notes
going into a Chord device. Offline (score lint, preview, eval, view, Serum renders) the notes that
would *sound* are computed here for the effects whose result is deterministic:

  Chord        Shift1-6 (semitones), Velocity1-6 (%), Strum (ms)
  Pitch        Pitch (semitones)
  Note Length  Time Length (ms) x Gate (%), when Sync is off
  Velocity     Out Low / Out Hi as a clamp, Mode "Fixed" -> Out Hi

Anything else (Arpeggiator, Random, Scale, chance or scale-degree settings) still loads in Live
but is not emulated: `unemulated()` names those so lint can say the offline numbers will differ.
"""
from __future__ import annotations

from .model import Note

EMULATED = {"chord", "pitch", "note length", "velocity"}


def _num(v, default=0.0) -> float:
    if isinstance(v, bool):
        return float(v)
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).split()[0].replace("+", ""))
    except (ValueError, IndexError):
        return default


def _get(params: dict, name: str, default=0.0):
    for k, v in (params or {}).items():
        if k.lower() == name.lower():
            return v
    return default


def unemulated(effects: list[dict]) -> list[str]:
    """Why the offline result will differ from Live, one line per reason (empty = it will not)."""
    out = []
    for e in effects or []:
        dev = str(e.get("device", "")).lower()
        p = e.get("params") or {}
        if dev not in EMULATED:
            out.append(f"{e.get('device')} is not emulated offline")
            continue
        if dev == "chord":
            for i in range(1, 7):
                if _num(_get(p, f"Chance{i}", 100)) < 100:
                    out.append(f"Chord Chance{i} below 100% is random in Live")
                if _num(_get(p, f"Shift{i} Scale Degrees", 0)):
                    out.append(f"Chord Shift{i} Scale Degrees is not emulated offline (use Shift{i} in semitones)")
        if dev == "pitch" and _num(_get(p, "Pitch Scale Degrees", 0)):
            out.append("Pitch Scale Degrees is not emulated offline")
        if dev == "note length" and str(_get(p, "Sync On", "Off")).lower() in ("on", "true", "1", "1.0"):
            out.append("Note Length with Sync on is not emulated offline (use Time Length)")
        if dev == "velocity" and any(_num(_get(p, k, 0)) for k in ("Drive", "Compand", "Random")):
            out.append("Velocity Drive/Compand/Random are not emulated offline")
    return out


def apply(notes: list[Note], effects: list[dict], bpm: float) -> list[Note]:
    """The notes that sound after the chain (times in beats, as given)."""
    for e in effects or []:
        dev = str(e.get("device", "")).lower()
        p = e.get("params") or {}
        if dev == "chord":
            extra = []
            strum = _num(_get(p, "Strum", 0)) * bpm / 60000.0          # ms -> beats, per added voice
            voices = [(i, _num(_get(p, f"Shift{i}", 0)), _num(_get(p, f"Velocity{i}", 100))) for i in range(1, 7)]
            voices = [(i, s, v) for i, s, v in voices if s]
            for n in notes:
                for k, (_, shift, vel) in enumerate(voices, start=1):
                    pitch = n.pitch + int(round(shift))
                    if 0 <= pitch <= 127:
                        t = n.start + (k * strum if strum > 0 else (len(voices) - k + 1) * strum if strum < 0 else 0.0)
                        extra.append(Note(pitch, max(0.0, t), n.dur, int(max(1, min(127, round(n.vel * vel / 100.0))))))
            if strum < 0:                                             # downward strum: the played note comes last
                notes = [Note(n.pitch, n.start + len(voices) * -strum, n.dur, n.vel) for n in notes]
            notes = list(notes) + extra
        elif dev == "pitch":
            st = int(round(_num(_get(p, "Pitch", 0))))
            notes = [Note(n.pitch + st, n.start, n.dur, n.vel) for n in notes if 0 <= n.pitch + st <= 127]
        elif dev == "note length":
            if str(_get(p, "Sync On", "Off")).lower() not in ("on", "true", "1", "1.0"):
                beats = _num(_get(p, "Time Length", 100)) * _num(_get(p, "Gate", 100)) / 100.0 * bpm / 60000.0
                notes = [Note(n.pitch, n.start, max(1 / 64, beats), n.vel) for n in notes]
        elif dev == "velocity":
            lo, hi = _num(_get(p, "Out Low", 1)), _num(_get(p, "Out Hi", 127))
            fixed = str(_get(p, "Mode", "Clip")).lower() == "fixed"
            notes = [Note(n.pitch, n.start, n.dur, int(hi if fixed else max(lo, min(hi, n.vel)))) for n in notes]
    return sorted(notes, key=lambda n: (n.start, n.pitch))
