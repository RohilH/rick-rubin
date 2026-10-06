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

    @property
    def length(self) -> float:
        return self.bars * BEATS_PER_BAR

    @property
    def is_audio(self) -> bool:
        return self.audio is not None

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

    @property
    def is_drum(self) -> bool:
        return self.role in DRUM_ROLES

    def to_json(self) -> dict:
        d = asdict(self)
        d.pop("name")
        return {k: v for k, v in d.items() if v not in (None, False, [], 0.0) or k == "role"}

    @classmethod
    def from_json(cls, name: str, d: dict) -> "Track":
        inst = d.get("instrument", [])
        return cls(name=name, role=d["role"], instrument=[inst] if isinstance(inst, str) else list(inst),
                   volume_db=float(d.get("volume_db", 0)), pan=float(d.get("pan", 0)),
                   sidechain=bool(d.get("sidechain", False)), swing=bool(d.get("swing", False)),
                   color=d.get("color"), mute=bool(d.get("mute", False)), sample=d.get("sample"),
                   sample_root=None if d.get("sample_root") is None else float(d["sample_root"]),
                   audio=bool(d.get("audio", False)))


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

    # ---- serialization
    def to_json(self) -> dict:
        return {
            "format": "ableton-use/song@1",
            "title": self.title, "bpm": self.bpm, "key": self.key, "swing": self.swing,
            "meta": self.meta,
            "tracks": {t.name: t.to_json() for t in self.tracks},
            "patterns": {k: p.to_json() for k, p in self.patterns.items()},
            "sections": [s.to_json() for s in self.sections],
        }

    @classmethod
    def from_json(cls, d: dict) -> "Song":
        return cls(
            title=d.get("title", "Untitled"), bpm=float(d.get("bpm", 124)), key=d.get("key", "A minor"),
            swing=float(d.get("swing", 50)), meta=d.get("meta", {}),
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
    def _swing_offset(self, t: float) -> float:
        if self.swing <= 50:
            return 0.0
        # delay the 2nd 16th of every 8th-note pair
        pos_in_8th = t % 0.5
        if abs(pos_in_8th - 0.25) < 1e-6:
            return self.swing / 100.0 * 0.5 - 0.25
        return 0.0

    def flatten(self) -> tuple[list[ArrangementClip], list[Marker]]:
        """Expand sections into one arrangement clip per (section, track)."""
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
                for b, (pat, pbar, tr) in sorted(bar_src.items()):
                    lo, hi = pbar * BEATS_PER_BAR, (pbar + 1) * BEATS_PER_BAR
                    for n in pat.notes:
                        if lo <= n.start < hi:
                            t = (b - first) * BEATS_PER_BAR + (n.start - lo)
                            if trk.swing:
                                t += self._swing_offset(n.start - lo)
                            notes.append(Note(n.pitch + tr, t, n.dur, n.vel))
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
