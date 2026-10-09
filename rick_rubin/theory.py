"""Music theory primitives.

Pitch convention follows Ableton Live: MIDI 60 = C3 (not C4), MIDI 36 = C1.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

SCALES: dict[str, list[int]] = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],          # natural minor / aeolian
    "dorian": [0, 2, 3, 5, 7, 9, 10],          # deep house favourite
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "minor_pentatonic": [0, 3, 5, 7, 10],
    "major_pentatonic": [0, 2, 4, 7, 9],
}
_SCALE_ALIASES = {
    "m": "minor", "min": "minor", "aeolian": "minor", "": "major", "maj": "major",
    "ionian": "major", "dor": "dorian", "phr": "phrygian", "mix": "mixolydian",
}


def pc_of(name: str) -> int:
    """Pitch class of a note name like 'F#' or 'Bb'."""
    name = name.strip()
    pc = _PC[name[0].upper()]
    for ch in name[1:]:
        if ch == "#":
            pc += 1
        elif ch in "b♭":
            pc -= 1
    return pc % 12


def note(name: str) -> int:
    """'C3' -> 60 (Ableton convention), 'A1' -> 45, 'F#-1' -> 18."""
    m = re.fullmatch(r"([A-Ga-g][#b♭]*)(-?\d+)", name.strip())
    if not m:
        raise ValueError(f"bad note name {name!r}")
    return pc_of(m.group(1)) + (int(m.group(2)) + 2) * 12


def name(pitch: int) -> str:
    """60 -> 'C3'."""
    return f"{NOTE_NAMES[pitch % 12]}{pitch // 12 - 2}"


@dataclass(frozen=True)
class Key:
    root: int            # pitch class 0-11
    scale: str = "minor"

    @classmethod
    def parse(cls, text: str) -> "Key":
        """Accepts 'Am', 'F#m', 'C', 'D dorian', 'G minor', 'Eb:minor'."""
        t = text.strip().replace(":", " ")
        m = re.fullmatch(r"([A-Ga-g][#b♭]?)\s*([A-Za-z_]*)", t.replace(" ", "")) if " " not in t else None
        if m:
            root, mode = m.group(1), m.group(2).lower()
        else:
            parts = t.split()
            root, mode = parts[0], "_".join(parts[1:]).lower()
        mode = _SCALE_ALIASES.get(mode, mode)
        if mode == "minor" or mode in SCALES:
            return cls(pc_of(root), mode)
        raise ValueError(f"unknown scale {mode!r} in key {text!r}")

    def __str__(self) -> str:
        return f"{NOTE_NAMES[self.root]} {self.scale}"

    @property
    def intervals(self) -> list[int]:
        return SCALES[self.scale]

    def contains(self, pitch: int) -> bool:
        return (pitch - self.root) % 12 in self.intervals

    def degree(self, deg: int, octave: int = 3) -> int:
        """Pitch of 1-based scale degree (negative/large values wrap octaves).
        octave is Ableton octave of the tonic (3 -> tonic near C3)."""
        n = len(self.intervals)
        d = deg - 1
        oct_shift, idx = divmod(d, n)
        return self.root + (octave + 2 + oct_shift) * 12 + self.intervals[idx]

    def tonic(self, octave: int) -> int:
        return self.degree(1, octave)

    def snap(self, pitch: int) -> int:
        """Nearest in-key pitch (ties go down)."""
        for off in (0, -1, 1, -2, 2):
            if self.contains(pitch + off):
                return pitch + off
        return pitch

    def chord(self, deg: int, size: int = 4, octave: int = 3, extensions: tuple[int, ...] = ()) -> list[int]:
        """Diatonic stacked-thirds chord on a scale degree. size=3 triad, 4 seventh, 5 ninth.
        extensions adds extra stacked-third indexes (e.g. (9,) adds the 9th)."""
        idxs = [0, 2, 4, 6, 8, 10, 12][:size]
        for e in extensions:
            idxs.append(e - 1)
        return sorted({self.degree(deg + i, octave) for i in idxs})


# ----------------------------------------------------------------------------- chords
_CHORD_SHAPES = {
    (0, 4, 7): "", (0, 3, 7): "m", (0, 3, 6): "dim", (0, 4, 8): "aug",
    (0, 5, 7): "sus4", (0, 2, 7): "sus2",
    (0, 4, 7, 11): "maj7", (0, 3, 7, 10): "m7", (0, 4, 7, 10): "7", (0, 3, 6, 10): "m7b5",
    (0, 2, 3, 7, 10): "m9", (0, 2, 4, 7, 11): "maj9", (0, 2, 4, 7, 10): "9",
    (0, 2, 3, 7): "madd9", (0, 2, 4, 7): "add9", (0, 3, 5, 7, 10): "m11", (0, 2, 3, 5, 7, 10): "m11",
    (0, 3, 7, 9): "m6", (0, 4, 7, 9): "6", (0, 3, 10): "m7(no5)", (0, 4, 11): "maj7(no5)",
    (0, 2, 3, 10): "m9(no5)", (0, 2, 4, 11): "maj9(no5)", (0, 7): "5",
}


def chord_name(pitches: list[int]) -> str:
    """Best-effort chord symbol for a set of pitches, e.g. 'Am9'. Falls back to note list."""
    if not pitches:
        return "-"
    pcs = sorted({p % 12 for p in pitches})
    bass = min(pitches) % 12
    best = None
    for root in pcs:
        shape = tuple(sorted((p - root) % 12 for p in pcs))
        if shape in _CHORD_SHAPES:
            score = (root == bass, -len(shape))
            if best is None or score > best[0]:
                best = (score, f"{NOTE_NAMES[root]}{_CHORD_SHAPES[shape]}", root)
    if best:
        sym, root = best[1], best[2]
        return sym if root == bass else f"{sym}/{NOTE_NAMES[bass]}"
    return "+".join(NOTE_NAMES[p] for p in pcs)


def voice_lead(prev: list[int] | None, chord: list[int], lo: int = 52, hi: int = 79) -> list[int]:
    """Choose an inversion/octave placement of `chord` (keeping its pitch classes)
    that minimises total movement from `prev` while staying inside [lo, hi].
    Defaults keep chords in the E2..G4 'stab' register so they don't fight the bass."""
    pcs = [p % 12 for p in chord]
    n = len(pcs)
    candidates = []
    base_sorted = sorted(chord)
    for inv in range(n):
        v = base_sorted[inv:] + [p + 12 for p in base_sorted[:inv]]
        for shift in range(-48, 49, 12):
            c = [p + shift for p in v]
            if min(c) >= lo and max(c) <= hi:
                candidates.append(c)
    if not candidates:
        return chord
    if not prev:
        centre = (lo + hi) / 2
        return min(candidates, key=lambda c: abs(sum(c) / len(c) - centre))
    pc = sum(prev) / len(prev)
    return min(candidates, key=lambda c: (sum(min(abs(a - b) for b in prev) for a in c), abs(sum(c) / len(c) - pc)))


def parse_progression(key: Key, text: str) -> list[int]:
    """'1 6 4 5' or 'i VI iv v' -> list of scale degrees."""
    romans = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7}
    out = []
    for tok in re.split(r"[\s,\-|]+", text.strip()):
        if not tok:
            continue
        core = re.sub(r"[^ivIV0-9]", "", tok.split("7")[0].split("9")[0]) or tok
        if core.isdigit():
            out.append(int(core))
        else:
            out.append(romans[core.lower()])
    return out
