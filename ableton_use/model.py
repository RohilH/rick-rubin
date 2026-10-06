"""Song model — the single source of truth (the 'EDL' of ableton-use).

A Song is a set of Tracks, a library of short looping Patterns, and an ordered
list of Sections that say which pattern each track plays. Rendering (MIDI, audio
preview, Ableton Live) always goes through `Song.flatten()`, which expands that
compact description into concrete arrangement clips. Live is a *render target*:
edits happen here, then get re-pushed.

Time units: beats (quarter notes). 4/4 only (house).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

from .theory import Key, name as pitch_name, note as parse_note

BEATS_PER_BAR = 4
STEPS_PER_BAR = 16
STEP = BEATS_PER_BAR / STEPS_PER_BAR  # 0.25 beat

DRUM_ROLES = {"kick", "clap", "snare", "hat", "openhat", "perc", "shaker", "ride", "crash", "drums", "fx", "tom"}
MELODIC_ROLES = {"bass", "sub", "chords", "stab", "pad", "lead", "arp", "pluck", "vocal", "keys", "organ"}

# Ableton Drum Rack default pad layout (C1 = 36), GM-compatible.
DRUM_MAP = {
    "kick": 36, "rim": 37, "snare": 38, "clap": 39, "tom": 41, "hat": 42, "openhat": 46,
    "perc": 50, "crash": 49, "ride": 51, "shaker": 70, "fx": 49,
}

_VEL_CHARS = {"x": 100, "X": 127, "o": 72, "g": 45}

def resolve_groove(g: dict) -> dict:
    return dict(g or {})


# ============================================================================ notes & patterns
@dataclass
class Note:
    pitch: int
    start: float        # beats from pattern/clip start
    dur: float = STEP
    vel: int = 100

    def to_json(self) -> list:
        return [pitch_name(self.pitch), round(self.start, 4), round(self.dur, 4), int(self.vel)]

    @classmethod
    def from_json(cls, v: Any) -> "Note":
        if isinstance(v, dict):
            v = [v["pitch"], v["start"], v.get("dur", STEP), v.get("vel", 100)]
        p, s = v[0], v[1]
        dur = v[2] if len(v) > 2 else STEP
        vel = v[3] if len(v) > 3 else 100
        return cls(parse_note(p) if isinstance(p, str) else int(p), parse_pos(s), float(dur), int(vel))


def parse_pos(s: Any) -> float:
    """Beats from a float or an Ableton-style 'bar.beat.sixteenth' string (1-based): '2.1.3' -> 4.5."""
    if isinstance(s, (int, float)):
        return float(s)
    parts = [float(x) for x in str(s).split(".")] + [1, 1]
    bar, beat, six = parts[:3]
    return (bar - 1) * BEATS_PER_BAR + (beat - 1) + (six - 1) * STEP


def fmt_pos(beats: float) -> str:
    bar, rem = divmod(beats, BEATS_PER_BAR)
    beat, rem = divmod(rem, 1)
    six = rem / STEP
    six_s = f"{six + 1:g}" if abs(six - round(six)) > 1e-6 else f"{int(round(six)) + 1}"
    return f"{int(bar) + 1}.{int(beat) + 1}.{six_s}"


def steps_to_notes(steps: str, pitch: int, dur: float = STEP) -> list[Note]:
    """'x...x...X.o.' -> notes on a 16th grid. '.' or '-' rest, '|' and spaces ignored,
    x=100 X=127 o=72 g=45 (ghost), digits 1-9 -> vel 14..127."""
    clean = steps.replace("|", "").replace(" ", "")
    out = []
    for i, ch in enumerate(clean):
        if ch in ".-_":
            continue
        if ch in _VEL_CHARS:
            vel = _VEL_CHARS[ch]
        elif ch.isdigit():
            vel = max(1, min(127, int(ch) * 14 + 1))
        else:
            raise ValueError(f"bad step char {ch!r} in {steps!r}")
        out.append(Note(pitch, i * STEP, dur, vel))
    return out


def notes_to_steps(notes: list[Note], bars: int) -> str:
    grid = ["."] * (bars * STEPS_PER_BAR)
    for n in notes:
        i = int(round(n.start / STEP))
        if 0 <= i < len(grid):
            v = n.vel
            grid[i] = "X" if v >= 120 else "x" if v >= 90 else "o" if v >= 60 else "g"
    s = "".join(grid)
    return "|".join(s[i:i + 16] for i in range(0, len(s), 16))


@dataclass
class Pattern:
    name: str
    bars: int = 1
    notes: list[Note] = field(default_factory=list)
    track: str | None = None      # owning track (informational)
    desc: str = ""
    audio: str | None = None      # audio loop file (path relative to the project), conformed to exactly `bars` at song tempo
    key: str | None = None        # musical key of an audio loop, if any (metadata for lint)

    _song: Any = field(default=None, repr=False, compare=False)   # set when created through Song.pattern()

    @property
    def length(self) -> float:
        return self.bars * BEATS_PER_BAR

    @property
    def is_audio(self) -> bool:
        return self.audio is not None

    # ---- placing a pattern in a section
    def at(self, first: int = 1, last: int | None = None, transpose: int = 0) -> "Part":
        """This pattern on bars `first`..`last` of a section (1-based, inclusive; last=None = to the end)."""
        return Part(self.name, first - 1, last, transpose)

    def up(self, semitones: int) -> "Part":
        """This pattern transposed, for the whole section."""
        return Part(self.name, 0, None, semitones)

    def every(self, bars: int | None = None) -> "Fill":
        """This pattern as a fill at the end of every `bars`-bar phrase (None = once, at the end of the section)."""
        return Fill(self.name, bars)

    # ---- deriving a new pattern from this one
    def variant(self, name: str, *, bars: dict | None = None, add: Any = None, drop: Any = None, repeat: int = 1,
                transpose: int = 0, length: int | None = None, mono: bool = False, desc: str = "") -> "Pattern":
        """A new pattern built from this one — the original is untouched.

        repeat=2            play it twice (4 bars -> 8) before the changes below
        length=6            cut or pad to that many bars
        bars={4: "..."}     replace whole bars (1-based) with new event text or a step string ("" empties the bar)
        add={2: "..."}      add events to bars, keeping what is there (or one event string for bar 1, or Notes)
        drop=lambda n: ...  remove the notes for which the function is true
        transpose=12        shift every note by semitones
        mono=True           cut each note where the next one starts (basslines, leads)"""
        from .compose import to_notes, to_notes_bar
        if self.is_audio:
            raise ValueError("audio patterns have no notes to vary; import another loop or cut it with at()")
        pitch = self.notes[0].pitch if self.notes else None
        notes = [Note(n.pitch, n.start + r * self.length, n.dur, n.vel) for r in range(max(1, repeat)) for n in self.notes]
        nbars = self.bars * max(1, repeat)
        if length is not None:
            nbars = int(length)
        if bars:
            nbars = max(nbars, max(int(b) for b in bars))
        if isinstance(add, dict) and add:
            nbars = max(nbars, max(int(b) for b in add))
        notes = [n for n in notes if n.start < nbars * BEATS_PER_BAR]
        for b, text in (bars or {}).items():
            lo = (int(b) - 1) * BEATS_PER_BAR
            notes = [n for n in notes if not lo <= n.start < lo + BEATS_PER_BAR]
            notes += to_notes_bar(text, int(b) - 1, pitch)
        if add is not None:
            notes += to_notes(add, pitch)[0]
        if drop is not None:
            notes = [n for n in notes if not drop(n)]
        if transpose:
            notes = [Note(n.pitch + transpose, n.start, n.dur, n.vel) for n in notes]
        notes = sorted(notes, key=lambda n: (n.start, n.pitch))
        if mono:
            for a, b in zip(notes, notes[1:]):
                if b.start > a.start:
                    a.dur = min(a.dur, b.start - a.start)
        p = Pattern(name, nbars, notes, self.track, desc or self.desc, _song=self._song)
        if self._song is not None:
            self._song.patterns[name] = p
        return p

    def then(self, other: "Pattern", name: str, desc: str = "") -> "Pattern":
        """This pattern followed by another, as one new pattern."""
        notes = [Note(n.pitch, n.start, n.dur, n.vel) for n in self.notes]
        notes += [Note(n.pitch, n.start + self.length, n.dur, n.vel) for n in other.notes]
        p = Pattern(name, self.bars + other.bars, notes, self.track, desc, _song=self._song)
        if self._song is not None:
            self._song.patterns[name] = p
        return p

    def is_steppable(self) -> bool:
        if not self.notes:
            return True
        pitches = {n.pitch for n in self.notes}
        return len(pitches) == 1 and all(abs(n.start / STEP - round(n.start / STEP)) < 1e-6 and abs(n.dur - STEP) < 1e-6 for n in self.notes)

    def to_json(self) -> dict:
        d: dict[str, Any] = {"bars": self.bars}
        if self.track:
            d["track"] = self.track
        if self.desc:
            d["desc"] = self.desc
        if self.audio is not None:
            d["audio"] = self.audio
            if self.key:
                d["key"] = self.key
            return d
        if self.notes and self.is_steppable():
            d["pitch"] = pitch_name(self.notes[0].pitch)
            d["steps"] = notes_to_steps(self.notes, self.bars)
        else:
            d["notes"] = [n.to_json() for n in sorted(self.notes, key=lambda n: (n.start, n.pitch))]
        return d

    @classmethod
    def from_json(cls, name: str, d: dict) -> "Pattern":
        bars = int(d.get("bars", 1))
        if "steps" in d:
            p = d["pitch"]
            pitch = parse_note(p) if isinstance(p, str) else int(p)
            notes = steps_to_notes(d["steps"], pitch, float(d.get("dur", STEP)))
            if "bars" not in d:
                bars = max(1, -(-len(d["steps"].replace("|", "").replace(" ", "")) // STEPS_PER_BAR))
        else:
            notes = [Note.from_json(n) for n in d.get("notes", [])]
        return cls(name, bars, notes, d.get("track"), d.get("desc", ""), d.get("audio"), d.get("key"))


# ============================================================================ tracks & sections
@dataclass
class Track:
    name: str
    role: str
    instrument: list[str] = field(default_factory=list)  # Live browser queries, first match wins
    volume_db: float = 0.0
    pan: float = 0.0          # -1..1
    sidechain: bool = False   # duck against the kick (preview + note for Live)
    swing: bool = False       # apply Song.swing to 16th offbeats
    color: int | None = None  # Live color index 0-69
    mute: bool = False
    sample: str | None = None         # one-shot played by Simpler (path relative to the project) instead of `instrument`
    sample_root: float | None = None  # MIDI pitch the sample sounds at (melodic samples; fractional = cents)
    audio: bool = False               # audio track holding audio-loop patterns
    # Live audio effects after the instrument, in order. Each: {"device": "Compressor", "params": {name: displayed
    # value}, "sidechain": "<track name>", "sidechain_tap": "Post FX"}. Parameter names and units are Live's own.
    effects: list[dict] = field(default_factory=list)
    # Send levels in dB to the return tracks, by letter: {"A": -14, "B": -20}. Unlisted sends are off.
    sends: dict = field(default_factory=dict)
    # MIDI effects in front of the instrument, in order: {"device": "Chord", "params": {"Shift1": 3, "Shift2": 7}}.
    # Real devices in Live; emulated offline where deterministic (see midifx.py).
    midi_effects: list[dict] = field(default_factory=list)
    # Feel, baked into the notes by flatten(). Keys (all optional): "swing" % (overrides Song.swing for this track),
    # "timing" 16 offsets in ms, one per 16th of the bar (+ late / - early), "accent" 16 velocity offsets,
    # "gate" note-length multiplier, "humanize" {"ms": n, "vel": n, "seed": n}.
    groove: dict = field(default_factory=dict)
    # Track delay in ms, like Ableton's Track Delay: + plays the whole track late, - early. Applied by shifting the
    # track's clips (Live does not let scripts set its own Track Delay), so it shows in the arrangement.
    delay_ms: float = 0.0
    # A Serum 2 preset (name, words from it, or a .SerumPreset path) to play this track's notes. The part is rendered
    # through the real plug-in offline and reaches Live as audio; serum_params sets Serum parameters by name
    # ({"macro_1": 60, "filter_1_freq_hz": 900}) — see `ableton-use serum params`.
    serum: str | None = None
    serum_params: dict = field(default_factory=dict)
    # Parameters of the track's instrument by displayed value, e.g. Simpler {"Ve Attack": 4, "Ve Release": 60, "Vol < Vel": 70}
    instrument_params: dict = field(default_factory=dict)

    def __hash__(self) -> int:          # tracks are used as dict keys when writing sections: {kick: four, bass: line}
        return id(self)

    @property
    def is_drum(self) -> bool:
        return self.role in DRUM_ROLES

    @property
    def ducked(self) -> bool:
        """Does anything on this track duck it against another track?"""
        return self.sidechain or any(e.get("sidechain") for e in self.effects)

    def to_json(self) -> dict:
        d = asdict(self)
        d.pop("name")
        return {k: v for k, v in d.items() if v not in (None, False, [], {}, 0.0) or k == "role"}

    @classmethod
    def from_json(cls, name: str, d: dict) -> "Track":
        inst = d.get("instrument", [])
        return cls(name=name, role=d["role"], instrument=[inst] if isinstance(inst, str) else list(inst),
                   volume_db=float(d.get("volume_db", 0)), pan=float(d.get("pan", 0)),
                   sidechain=bool(d.get("sidechain", False)), swing=bool(d.get("swing", False)),
                   color=d.get("color"), mute=bool(d.get("mute", False)), sample=d.get("sample"),
                   sample_root=None if d.get("sample_root") is None else float(d["sample_root"]),
                   audio=bool(d.get("audio", False)), effects=[dict(e) for e in d.get("effects", [])],
                   groove=dict(d.get("groove") or {}), instrument_params=dict(d.get("instrument_params") or {}),
                   serum=d.get("serum"), serum_params=dict(d.get("serum_params") or {}),
                   delay_ms=float(d.get("delay_ms", 0) or 0), midi_effects=[dict(e) for e in d.get("midi_effects", [])],
                   sends={str(k).upper(): float(v) for k, v in (d.get("sends") or {}).items()})


@dataclass
class Part:
    pattern: str
    start: int = 0              # bar offset inside section
    end: int | None = None      # bar offset (exclusive); None = section end
    transpose: int = 0

    def to_json(self) -> Any:
        if self.start == 0 and self.end is None and self.transpose == 0:
            return self.pattern
        d: dict[str, Any] = {"pattern": self.pattern}
        if self.start:
            d["start"] = self.start
        if self.end is not None:
            d["end"] = self.end
        if self.transpose:
            d["transpose"] = self.transpose
        return d

    @classmethod
    def from_json(cls, v: Any) -> "Part":
        if isinstance(v, str):
            return cls(v)
        return cls(v["pattern"], int(v.get("start", 0)), v.get("end"), int(v.get("transpose", 0)))


@dataclass
class Fill:
    pattern: str
    every: int | None = None    # place at the end of every N-bar phrase; None = end of section only

    def to_json(self) -> Any:
        return self.pattern if self.every is None else {"pattern": self.pattern, "every": self.every}

    @classmethod
    def from_json(cls, v: Any) -> "Fill":
        return cls(v) if isinstance(v, str) else cls(v["pattern"], v.get("every"))


@dataclass
class Section:
    name: str
    kind: str                   # intro | groove | breakdown | build | drop | bridge | outro
    bars: int
    energy: int = 5             # 0-10, the intended energy curve
    parts: dict[str, Part] = field(default_factory=dict)
    fills: dict[str, Fill] = field(default_factory=dict)
    # automation[track][param] = [v0, v1] (linear over section) or [[frac, v], ...]; values 0..1
    automation: dict[str, dict[str, list]] = field(default_factory=dict)
    desc: str = ""

    _song: Any = field(default=None, repr=False, compare=False)

    def variant(self, name: str, *, bars: int | None = None, kind: str | None = None, energy: int | None = None,
                add: dict | None = None, without: Any = (), fills: dict | None = None, automation: dict | None = None,
                desc: str = "") -> "Section":
        """A new section built from this one — reuse a block and extend it:

            drop2 = drop.variant("drop2", energy=10, add={pad: pad_chords, lead: hook.up(12)}, without=[perc])

        `add` sets or replaces parts, `without` removes tracks (parts, fills and automation),
        `fills` / `automation` are merged over the original's. The new section is appended
        to the song; use song.arrange(...) to set the order."""
        sec = Section(name, kind or self.kind, bars or self.bars, self.energy if energy is None else energy,
                      {k: Part(v.pattern, v.start, v.end, v.transpose) for k, v in self.parts.items()},
                      {k: Fill(v.pattern, v.every) for k, v in self.fills.items()},
                      {k: dict(v) for k, v in self.automation.items()}, desc or self.desc, _song=self._song)
        for t in ([without] if isinstance(without, (str, Track)) else list(without)):
            tn = getattr(t, "name", t)
            sec.parts.pop(tn, None)
            sec.fills.pop(tn, None)
            sec.automation.pop(tn, None)
        sec.parts.update(_as_parts(add))
        sec.fills.update(_as_fills(fills))
        for tn, d in _as_automation(automation).items():
            sec.automation.setdefault(tn, {}).update(d)
        if sec.bars != self.bars:                      # parts that ran to an explicit end may not fit any more
            for tn, part in list(sec.parts.items()):
                if part.start >= sec.bars:
                    del sec.parts[tn]
                elif part.end is not None and part.end > sec.bars:
                    part.end = None
        if self._song is not None:
            self._song.sections.append(sec)
        return sec

    def to_json(self) -> dict:
        d: dict[str, Any] = {"name": self.name, "kind": self.kind, "bars": self.bars, "energy": self.energy}
        if self.desc:
            d["desc"] = self.desc
        d["parts"] = {k: v.to_json() for k, v in self.parts.items()}
        if self.fills:
            d["fills"] = {k: v.to_json() for k, v in self.fills.items()}
        if self.automation:
            d["automation"] = self.automation
        return d

    @classmethod
    def from_json(cls, d: dict) -> "Section":
        return cls(name=d["name"], kind=d.get("kind", d["name"]), bars=int(d["bars"]), energy=int(d.get("energy", 5)),
                   parts={k: Part.from_json(v) for k, v in d.get("parts", {}).items() if v},
                   fills={k: Fill.from_json(v) for k, v in d.get("fills", {}).items() if v},
                   automation=d.get("automation", {}), desc=d.get("desc", ""))


def _as_part(v: Any) -> Part:
    if isinstance(v, Part):
        return v
    if isinstance(v, Pattern):
        return Part(v.name)
    if isinstance(v, (tuple, list)):
        head = v[0].name if isinstance(v[0], Pattern) else v[0]
        rest = list(v[1:]) + [None] * (3 - len(v[1:]))
        return Part(head, int(rest[0] or 0), rest[1], int(rest[2] or 0))
    return Part.from_json(v)


def _as_parts(d: dict | None) -> dict[str, Part]:
    return {getattr(k, "name", k): _as_part(v) for k, v in (d or {}).items() if v is not None}


def _as_fills(d: dict | None) -> dict[str, Fill]:
    out = {}
    for k, v in (d or {}).items():
        if v is None:
            continue
        out[getattr(k, "name", k)] = v if isinstance(v, Fill) else Fill(v.name) if isinstance(v, Pattern) else Fill.from_json(v)
    return out


def _as_automation(d: dict | None) -> dict[str, dict]:
    return {getattr(k, "name", k): dict(v) for k, v in (d or {}).items()}


# ============================================================================ flattened output
@dataclass
class ArrangementClip:
    track: str
    name: str
    start: float                 # beats from song start
    length: float                # beats
    notes: list[Note]            # times relative to clip start
    envelopes: dict[str, list[tuple[float, float]]] = field(default_factory=dict)  # param -> [(beat_in_clip, value)]
    section: str = ""
    audio: str | None = None     # audio file for audio clips
    # audio clips: [(start_in_clip, length, offset_into_file)] in beats; one Live clip per segment
    segments: list[tuple[float, float, float]] = field(default_factory=list)


@dataclass
class Marker:
    name: str
    start: float


# ============================================================================ song
@dataclass
class Song:
    title: str = "Untitled"
    bpm: float = 124.0
    key: str = "A minor"
    swing: float = 54.0          # MPC-style %, 50 = straight, 66.7 = triplet
    tracks: list[Track] = field(default_factory=list)
    patterns: dict[str, Pattern] = field(default_factory=dict)
    sections: list[Section] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)
    # Return tracks by letter, each an effect chain like a track's `effects`: {"A": [{"device": "Reverb", "params": {...}}]}.
    # Tracks feed them with `sends`. One shared reverb or delay instead of one per track.
    returns: dict[str, list[dict]] = field(default_factory=dict)
    # Effects on the master track, in order (e.g. a Limiter).
    master_effects: list[dict] = field(default_factory=list)
    base_dir: Path | None = field(default=None, repr=False, compare=False)   # project folder (not serialized)

    def resolve(self, rel: str) -> Path:
        """Absolute path of a project-relative sample path."""
        p = Path(rel).expanduser()
        if p.is_absolute() or self.base_dir is None:
            return p
        return (self.base_dir / p).resolve()

    # ---- access
    @property
    def key_obj(self) -> Key:
        return Key.parse(self.key)

    def track(self, name: str) -> Track:
        for t in self.tracks:
            if t.name == name:
                return t
        raise KeyError(f"no track {name!r}; have {[t.name for t in self.tracks]}")

    def section(self, ref: str | int) -> Section:
        if isinstance(ref, int):
            return self.sections[ref]
        for s in self.sections:
            if s.name == ref:
                return s
        raise KeyError(f"no section {ref!r}; have {[s.name for s in self.sections]}")

    def section_starts(self) -> list[int]:
        """Start bar (0-based) of each section."""
        out, b = [], 0
        for s in self.sections:
            out.append(b)
            b += s.bars
        return out

    @property
    def total_bars(self) -> int:
        return sum(s.bars for s in self.sections)

    @property
    def duration_s(self) -> float:
        return self.total_bars * BEATS_PER_BAR * 60.0 / self.bpm

    def add_pattern(self, p: Pattern) -> Pattern:
        self.patterns[p.name] = p
        return p

    # ---- writing a song in Python (see compose.py for the notations)
    def add_track(self, name: str, role: str, **fields: Any) -> Track:
        """A new track. role: kick clap snare hat openhat perc crash fx (drums) · bass chords pad lead keys vocal ...
        fields: sample, sample_root, audio, serum, serum_params, instrument, instrument_params, volume_db, pan,
        delay_ms, swing, groove, sidechain, effects, midi_effects, sends, color."""
        if any(t.name == name for t in self.tracks):
            raise ValueError(f"track {name!r} already exists")
        inst = fields.pop("instrument", [])
        t = Track(name, role, [inst] if isinstance(inst, str) else list(inst), **fields)
        self.tracks.append(t)
        return t

    def pattern(self, name: str, track: Track | str, content: Any = None, *, bars: int | None = None,
                pitch: int | str | None = None, dur: float | None = None, audio: str | None = None,
                key: str | None = None, desc: str = "") -> Pattern:
        """A named pattern for a track — a reusable variable.

        content: a step string ("x...x...x...x..."), a list with one event string per bar
        (["1.3 F0 0.35; 2.3 F0 0.35 v108", ...]), a dict {bar: events}, or Notes / (pitch, start, length, vel) tuples.
        Drum tracks take their step pitch from their role; pass pitch= to override.
        audio="samples/loop.wav" (with bars=N) makes it an audio loop for an audio track."""
        from .compose import to_notes
        trk = self.track(track) if isinstance(track, str) else track
        if audio is not None:
            if not bars:
                raise ValueError("an audio pattern needs bars= (the length of the conformed loop)")
            p = Pattern(name, int(bars), [], trk.name, desc, audio, key, _song=self)
        else:
            if pitch is None and trk.is_drum:
                pitch = DRUM_MAP.get(trk.role, 60)
            notes, implied = to_notes(content, pitch, dur) if content is not None else ([], None)
            n = int(bars or implied or max(1, -(-int(max((x.start for x in notes), default=0) + 1) // BEATS_PER_BAR)))
            p = Pattern(name, n, sorted(notes, key=lambda x: (x.start, x.pitch)), trk.name, desc, _song=self)
        self.patterns[name] = p
        return p

    def add_section(self, name: str, bars: int, *, kind: str | None = None, energy: int = 5, parts: dict | None = None,
                    fills: dict | None = None, automation: dict | None = None, desc: str = "") -> Section:
        """A section, appended to the arrangement. parts: {track: pattern | pattern.at(9, 16) | pattern.up(12)},
        fills: {track: pattern | pattern.every(8)}, automation: {track: {"filter": [0.3, 1.0]}} (0..1 over the section,
        or [[fraction, value], ...])."""
        if any(s.name == name for s in self.sections):
            raise ValueError(f"section {name!r} already exists")
        sec = Section(name, kind or name, int(bars), int(energy), _as_parts(parts), _as_fills(fills),
                      _as_automation(automation), desc, _song=self)
        self.sections.append(sec)
        return sec

    def add_return(self, letter: str, effects: list[dict]) -> str:
        """A return track (Ableton's A, B, ...) with an effect chain, e.g.
        song.add_return("A", [{"device": "Reverb", "params": {"Decay Time": 1800, "Dry/Wet": 100}}]).
        Feed it from tracks with sends={"A": -14} (dB). Returns the letter."""
        letter = letter.upper()
        self.returns[letter] = [dict(e) for e in effects]
        return letter

    def arrange(self, *sections: Section) -> None:
        """Set the order of the arrangement. A section listed twice plays twice (the repeat is named 'name (2)')."""
        out: list[Section] = []
        seen: dict[str, int] = {}
        for sec in (sections[0] if len(sections) == 1 and isinstance(sections[0], (list, tuple)) else sections):
            k = seen.get(sec.name, 0) + 1
            seen[sec.name] = k
            if k > 1:
                sec = sec.variant(f"{sec.name} ({k})")
                self.sections.remove(sec)
            out.append(sec)
        self.sections = out

    # ---- serialization
    def to_json(self) -> dict:
        return {
            "format": "ableton-use/song@1",
            "title": self.title, "bpm": self.bpm, "key": self.key, "swing": self.swing,
            "meta": self.meta,
            **({"returns": self.returns} if self.returns else {}),
            **({"master_effects": self.master_effects} if self.master_effects else {}),
            "tracks": {t.name: t.to_json() for t in self.tracks},
            "patterns": {k: p.to_json() for k, p in self.patterns.items()},
            "sections": [s.to_json() for s in self.sections],
        }

    @classmethod
    def from_json(cls, d: dict) -> "Song":
        return cls(
            title=d.get("title", "Untitled"), bpm=float(d.get("bpm", 124)), key=d.get("key", "A minor"),
            swing=float(d.get("swing", 50)), meta=d.get("meta", {}),
            returns={str(k).upper(): [dict(e) for e in v] for k, v in (d.get("returns") or {}).items()},
            master_effects=[dict(e) for e in d.get("master_effects", [])],
            tracks=[Track.from_json(k, v) for k, v in d.get("tracks", {}).items()],
            patterns={k: Pattern.from_json(k, v) for k, v in d.get("patterns", {}).items()},
            sections=[Section.from_json(s) for s in d.get("sections", [])],
        )

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(dumps_compact(self.to_json()) + "\n")
        return path

    @classmethod
    def load(cls, path: str | Path) -> "Song":
        s = cls.from_json(json.loads(Path(path).read_text()))
        s.base_dir = Path(path).resolve().parent
        return s

    # ---- integrity
    def validate(self) -> list[str]:
        """Structural errors only (things that would make rendering wrong). Musical
        checks live in `analysis.lint`."""
        errs = []
        names = [t.name for t in self.tracks]
        if len(set(names)) != len(names):
            errs.append("duplicate track names")
        try:
            self.key_obj
        except Exception as e:  # noqa: BLE001
            errs.append(f"bad key: {e}")
        for s in self.sections:
            for tname, part in s.parts.items():
                if tname not in names:
                    errs.append(f"section {s.name}: unknown track {tname!r}")
                if part.pattern not in self.patterns:
                    errs.append(f"section {s.name}: unknown pattern {part.pattern!r}")
                end = s.bars if part.end is None else part.end
                if not (0 <= part.start < end <= s.bars):
                    errs.append(f"section {s.name}/{tname}: bad part range {part.start}-{end} (section has {s.bars} bars)")
            for tname, fill in s.fills.items():
                if tname not in names:
                    errs.append(f"section {s.name}: fill on unknown track {tname!r}")
                if fill.pattern not in self.patterns:
                    errs.append(f"section {s.name}: unknown fill pattern {fill.pattern!r}")
            for tname in s.automation:
                if tname not in names:
                    errs.append(f"section {s.name}: automation on unknown track {tname!r}")
        letters = "ABCDEFGHIJKL"
        for letter, chain in self.returns.items():
            if len(letter) != 1 or letter not in letters:
                errs.append(f"return {letter!r}: returns are named by letter (A, B, ...)")
            for e in chain:
                if not isinstance(e, dict) or not e.get("device"):
                    errs.append(f"return {letter}: each effect needs a 'device' name (got {e!r})")
        for e in self.master_effects:
            if not isinstance(e, dict) or not e.get("device"):
                errs.append(f"master: each effect needs a 'device' name (got {e!r})")
        for t in self.tracks:
            for letter, db in t.sends.items():
                if letter not in self.returns:
                    errs.append(f"track {t.name}: send {letter} has no return — define it with song.add_return({letter!r}, [...])")
                elif db > 0:
                    errs.append(f"track {t.name}: send {letter} is {db:g} dB; sends go from -inf to 0 dB")
        tracks = {t.name: t for t in self.tracks}
        for s in self.sections:
            for tname, part in list(s.parts.items()) + [(k, v) for k, v in s.fills.items()]:
                pat = self.patterns.get(part.pattern)
                trk = tracks.get(tname)
                if pat is None or trk is None:
                    continue
                if pat.is_audio and not trk.audio:
                    errs.append(f"section {s.name}: audio pattern {pat.name!r} on MIDI track {tname!r} (set the track's audio=true)")
                if trk.audio and not pat.is_audio:
                    errs.append(f"section {s.name}: MIDI pattern {pat.name!r} on audio track {tname!r}")
        for t in self.tracks:
            g = t.groove
            for key in ("timing", "accent"):
                if key in g and (not isinstance(g[key], list) or len(g[key]) != STEPS_PER_BAR):
                    errs.append(f"track {t.name}: groove {key} needs {STEPS_PER_BAR} values, one per 16th of the bar")
            bad = set(g) - {"swing", "timing", "accent", "gate", "humanize"}
            if bad:
                errs.append(f"track {t.name}: unknown groove keys {sorted(bad)}")
            for e in t.midi_effects:
                if not isinstance(e, dict) or not e.get("device"):
                    errs.append(f"track {t.name}: each MIDI effect needs a 'device' name (got {e!r})")
            if t.midi_effects and t.audio:
                errs.append(f"track {t.name}: MIDI effects need a MIDI track, not an audio-loop track")
            for e in t.effects:
                if not isinstance(e, dict) or not e.get("device"):
                    errs.append(f"track {t.name}: each effect needs a 'device' name (got {e!r})")
                elif e.get("sidechain") and e["sidechain"] not in names:
                    errs.append(f"track {t.name}: {e['device']} sidechain source {e['sidechain']!r} is not a track")
                elif e.get("sidechain") == t.name:
                    errs.append(f"track {t.name}: {e['device']} cannot be sidechained from its own track")
            if abs(t.delay_ms) > 100:
                errs.append(f"track {t.name}: delay_ms {t.delay_ms:g} is more than 100 ms — that is a different rhythm, not a track delay")
            if t.serum and (t.sample or t.audio):
                errs.append(f"track {t.name}: a Serum track cannot also have sample= or audio=True")
            if t.sample and not t.is_drum and t.sample_root is None:
                errs.append(f"track {t.name}: melodic sample needs sample_root (run `ableton-use sample ... --oneshot` to detect it)")
            if t.sample and self.base_dir is not None and not self.resolve(t.sample).exists():
                errs.append(f"track {t.name}: sample file not found: {t.sample}")
        for p in self.patterns.values():
            if p.is_audio and self.base_dir is not None and not self.resolve(p.audio).exists():
                errs.append(f"pattern {p.name}: audio file not found: {p.audio}")
            for n in p.notes:
                if not (0 <= n.pitch <= 127):
                    errs.append(f"pattern {p.name}: pitch {n.pitch} out of range")
                if n.dur <= 0:
                    errs.append(f"pattern {p.name}: non-positive duration at {n.start}")
                if n.start < 0 or n.start >= p.length:
                    errs.append(f"pattern {p.name}: note at {n.start} outside {p.bars}-bar pattern")
        return errs

    # ---- expansion
    def _swing_offset(self, t: float, swing: float | None = None) -> float:
        swing = self.swing if swing is None else swing
        if swing <= 50:
            return 0.0
        # delay the 2nd 16th of every 8th-note pair
        pos_in_8th = t % 0.5
        if abs(pos_in_8th - 0.25) < 1e-6:
            return swing / 100.0 * 0.5 - 0.25
        return 0.0

    def _groove_note(self, trk: Track, g: dict, pos_in_bar: float, abs_bar: int, pitch: int, dur: float, vel: int):
        """(time offset in beats, duration, velocity) for a note at `pos_in_bar` on a grooved track."""
        off = 0.0
        if trk.swing or "swing" in g:
            off += self._swing_offset(pos_in_bar, g.get("swing"))
        step_f = pos_in_bar / STEP
        step = int(round(step_f))
        if abs(step_f - step) < 1e-3 and 0 <= step < STEPS_PER_BAR:      # on the 16th grid
            if "timing" in g:
                off += g["timing"][step] * self.bpm / 60000.0
            if "accent" in g:
                vel += g["accent"][step]
        h = g.get("humanize")
        if h:
            import random
            rng = random.Random(f"{h.get('seed', 0)}|{trk.name}|{abs_bar}|{round(pos_in_bar, 4)}|{pitch}")
            off += rng.uniform(-1, 1) * float(h.get("ms", 0)) * self.bpm / 60000.0
            vel += round(rng.uniform(-1, 1) * float(h.get("vel", 0)))
        return off, dur * float(g.get("gate", 1.0)), int(max(1, min(127, vel)))

    def flatten(self, sounding: bool = False) -> tuple[list[ArrangementClip], list[Marker]]:
        """Expand sections into one arrangement clip per (section, track).

        sounding=False gives the notes as written — what goes into Live's clips, in front of any MIDI
        effects. sounding=True gives the notes after each track's `midi_effects` (a Chord device's
        added voices, a Pitch shift...) — what is actually heard, for lint, preview and views."""
        errs = self.validate()
        if errs:
            raise ValueError("song invalid:\n  " + "\n  ".join(errs))
        clips: list[ArrangementClip] = []
        markers: list[Marker] = []
        for sec, sbar in zip(self.sections, self.section_starts()):
            markers.append(Marker(sec.name, sbar * BEATS_PER_BAR))
            tracks_here = set(sec.parts) | set(sec.fills)
            for tname in [t.name for t in self.tracks if t.name in tracks_here]:
                trk = self.track(tname)
                part = sec.parts.get(tname)
                fill = sec.fills.get(tname)
                # bar -> (pattern, bar index within pattern, transpose)
                bar_src: dict[int, tuple[Pattern, int, int]] = {}
                if part:
                    pat = self.patterns[part.pattern]
                    end = sec.bars if part.end is None else part.end
                    for b in range(part.start, end):
                        bar_src[b] = (pat, (b - part.start) % pat.bars, part.transpose)
                if fill:
                    fp = self.patterns[fill.pattern]
                    every = fill.every or sec.bars
                    for phrase_end in range(every, sec.bars + 1, every):
                        for i in range(fp.bars):
                            b = phrase_end - fp.bars + i
                            if b >= 0:
                                bar_src[b] = (fp, i, part.transpose if part else 0)
                if not bar_src:
                    continue
                first, last = min(bar_src), max(bar_src) + 1
                notes: list[Note] = []
                groove = resolve_groove(trk.groove)
                for b, (pat, pbar, tr) in sorted(bar_src.items()):
                    lo, hi = pbar * BEATS_PER_BAR, (pbar + 1) * BEATS_PER_BAR
                    for n in pat.notes:
                        if lo <= n.start < hi:
                            t = (b - first) * BEATS_PER_BAR + (n.start - lo)
                            off, dur, vel = self._groove_note(trk, groove, n.start - lo, sbar + b, n.pitch, n.dur, n.vel)
                            # a hit pushed ahead of the clip's first beat stays on it (the clip cannot start earlier)
                            notes.append(Note(n.pitch + tr, max(0.0, t + off), dur, vel))
                length = (last - first) * BEATS_PER_BAR
                # clip notes to clip end so nothing rings past the clip
                notes = [Note(n.pitch, n.start, min(n.dur, length - n.start), n.vel) for n in notes if n.start < length]
                notes = _no_same_pitch_overlap(notes)
                env = {}
                for param, spec in sec.automation.get(tname, {}).items():
                    env[param] = _expand_env(spec, sec.bars * BEATS_PER_BAR, first * BEATS_PER_BAR, length)
                name = "+".join(sorted({src[0].name for src in bar_src.values()}))
                clip = ArrangementClip(tname, f"{sec.name} · {name}", (sbar + first) * BEATS_PER_BAR, length, notes, env, sec.name)
                if trk.audio:
                    clip.notes = []
                    audio_pats = {src[0].audio for src in bar_src.values()}
                    if len(audio_pats) != 1:
                        raise ValueError(f"section {sec.name}/{tname}: one audio file per section clip (got {sorted(map(str, audio_pats))})")
                    clip.audio = audio_pats.pop()
                    # contiguous runs of bars that read the file in order -> one Live clip each
                    segs: list[list[float]] = []
                    prev = None
                    for b in range(first, last):
                        src = bar_src.get(b)
                        if src is None:
                            prev = None
                            continue
                        pat, pbar, _ = src
                        if prev is not None and prev[0] is pat and pbar == prev[1] + 1:
                            segs[-1][1] += BEATS_PER_BAR
                        else:
                            segs.append([(b - first) * BEATS_PER_BAR, BEATS_PER_BAR, pbar * BEATS_PER_BAR])
                        prev = (pat, pbar)
                    clip.segments = [tuple(x) for x in segs]
                if sounding and trk.midi_effects and clip.notes:
                    from .midifx import apply as _midifx
                    clip.notes = _no_same_pitch_overlap(_midifx(clip.notes, trk.midi_effects, self.bpm))
                if trk.delay_ms:
                    start = clip.start + trk.delay_ms * self.bpm / 60000.0
                    if start < 0:                     # nothing can start before the song does: only the notes move
                        clip.notes = [Note(n.pitch, max(0.0, n.start + start), n.dur, n.vel) for n in clip.notes]
                        start = 0.0
                    clip.start = start
                clips.append(clip)
        return clips, markers


def _no_same_pitch_overlap(notes: list[Note]) -> list[Note]:
    """Truncate a note that would still be sounding when the same pitch restarts
    (Live and most synths would cut or merge it anyway). Drops exact duplicates."""
    out: list[Note] = []
    last: dict[int, Note] = {}
    for n in sorted(notes, key=lambda n: (n.start, n.pitch)):
        prev = last.get(n.pitch)
        if prev is not None:
            if abs(prev.start - n.start) < 1e-9:
                continue
            if prev.start + prev.dur > n.start:
                prev.dur = max(1 / 64, n.start - prev.start)
        out.append(n)
        last[n.pitch] = n
    return out


def _expand_env(spec: list, sec_len: float, clip_off: float, clip_len: float) -> list[tuple[float, float]]:
    if spec and not isinstance(spec[0], (list, tuple)):
        pts = [(0.0, float(spec[0])), (1.0, float(spec[-1]))]
    else:
        pts = [(float(f), float(v)) for f, v in spec]
    out = []
    for f, v in pts:
        t = f * sec_len - clip_off
        out.append((max(0.0, min(clip_len, t)), max(0.0, min(1.0, v))))
    return out


def dumps_compact(obj: Any) -> str:
    """JSON with small arrays kept on one line — readable for humans and LLMs."""
    text = json.dumps(obj, indent=2)
    # collapse innermost arrays of scalars onto a single line
    pat = re.compile(r"\[\s*((?:[^\[\]{}]|\n)*?)\s*\]")
    return pat.sub(lambda m: "[" + ", ".join(x.strip() for x in m.group(1).split(",\n")) + "]" if "\n" in m.group(0) else m.group(0), text)
