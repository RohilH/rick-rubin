"""Notation helpers for writing music in Python.

Two small notations, both the same ones `score.md` prints, so what an agent reads
is what it writes:

* **Step strings** for one-pitch rhythms — one character per 16th, `|` between bars:
  `x`=100 `X`=127 `o`=72 `g`=45 (ghost) `1`-`9` scaled velocity, `.` rest.
      "x...x...x...x..."

* **Event lines** for anything pitched — one string per bar, events separated by `;`:
      "<beat>.<sixteenth> <pitch or [chord]> <length in beats> [vVELOCITY]"
      "1.3 F0 0.35; 2.3 F0 0.35 v108; 4.4 [D#3 G3 A#3] 0.5 v90"
  Positions are 1-based like Ableton's (`2.3` = beat 2, third 16th). For anything
  off the 16th grid write the position as `@<beats from the bar start>`: `@0.333`.

Nothing here invents notes. Loops, functions and your own helpers in song.py are
the way to build bigger things.
"""
from __future__ import annotations

from typing import Any, Iterable

from .model import BEATS_PER_BAR, STEP, Note, steps_to_notes
from .theory import note as parse_pitch

STEP_CHARS = set("xXog.-_|123456789 ")


def is_step_string(s: str) -> bool:
    return bool(s.strip()) and set(s) <= STEP_CHARS


def steps(pattern: str, pitch: int | str, dur: float = STEP) -> list[Note]:
    """Notes from a step string at one pitch."""
    return steps_to_notes(pattern, parse_pitch(pitch) if isinstance(pitch, str) else int(pitch), dur)


def _pos(tok: str) -> float:
    if tok.startswith("@"):
        return float(tok[1:])
    parts = tok.split(".")
    if not 1 <= len(parts) <= 2:
        raise ValueError(f"bad position {tok!r}: use beat.sixteenth (e.g. 2.3) or @beats (e.g. @1.333)")
    beat = float(parts[0])
    six = float(parts[1]) if len(parts) > 1 else 1.0
    if not (1 <= beat < BEATS_PER_BAR + 1 and 1 <= six < 5):
        raise ValueError(f"position {tok!r} is outside the bar (beats 1-4, sixteenths 1-4)")
    return (beat - 1) + (six - 1) * STEP


def bar_events(text: str, bar: int = 0) -> list[Note]:
    """Notes from one bar of event text (see module docstring). `bar` is 0-based."""
    out: list[Note] = []
    for ev in text.replace("\n", ";").split(";"):
        ev = ev.strip()
        if not ev:
            continue
        try:
            pos_tok, rest = ev.split(None, 1)
            vel = 100
            if rest.rsplit(None, 1)[-1][:1] == "v" and rest.rsplit(None, 1)[-1][1:].isdigit():
                rest, v = rest.rsplit(None, 1)
                vel = int(v[1:])
            body, dur = rest.rsplit(None, 1)
            body = body.strip()
            pitches = body.strip("[]").replace("+", " ").split()
            if not pitches:
                raise ValueError("no pitch")
            start = bar * BEATS_PER_BAR + _pos(pos_tok)
            for p in pitches:
                out.append(Note(parse_pitch(p), start, float(dur), max(1, min(127, vel))))
        except (ValueError, IndexError, KeyError) as e:
            raise ValueError(f"cannot read event {ev!r} — expected '<beat.sixteenth> <pitch|[chord]> <beats> [vVEL]' ({e})") from e
    return out


def to_notes(content: Any, pitch: int | str | None = None, dur: float | None = None) -> tuple[list[Note], int | None]:
    """Notes from any accepted pattern content, plus the bar count it implies (None if it does not say).

    content: a step string · a list with one event string (or step string) per bar ·
    a dict {bar number (1-based): event string} · a list of Note / (pitch, start_beats, length[, velocity])."""
    def step_pitch():
        if pitch is None:
            raise ValueError("a step string needs a pitch (drum tracks get theirs from their role)")
        return pitch

    if isinstance(content, str):
        if is_step_string(content):
            ns = steps(content, step_pitch(), dur or STEP)
            n16 = len(content.replace("|", "").replace(" ", ""))
            return ns, max(1, -(-n16 // 16))
        return bar_events(content), 1
    if isinstance(content, dict):
        out: list[Note] = []
        for b, text in content.items():
            out += to_notes_bar(text, int(b) - 1, pitch, dur)
        return out, (max(int(b) for b in content) if content else None)
    items = list(content)
    if items and all(isinstance(x, str) for x in items):
        out = []
        for b, text in enumerate(items):
            out += to_notes_bar(text, b, pitch, dur)
        return out, len(items)
    out = []
    for x in items:
        if isinstance(x, Note):
            out.append(Note(x.pitch, x.start, x.dur, x.vel))
        else:
            out.append(Note.from_json(list(x)))
    return out, None


def to_notes_bar(text: str, bar: int, pitch: int | str | None = None, dur: float | None = None) -> list[Note]:
    """One bar of content (event text, or a one-bar step string) placed at 0-based `bar`."""
    if not text or not text.strip():
        return []
    if is_step_string(text):
        if pitch is None:
            raise ValueError("a step string needs a pitch")
        ns = steps(text, pitch, dur or STEP)
        if any(n.start >= BEATS_PER_BAR for n in ns):
            raise ValueError(f"step string {text!r} is longer than one bar")
        return [Note(n.pitch, n.start + bar * BEATS_PER_BAR, n.dur, n.vel) for n in ns]
    return bar_events(text, bar)


def flatten_names(items: Iterable) -> list[str]:
    return [getattr(x, "name", x) for x in items]
