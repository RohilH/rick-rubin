"""Test data only: a deterministic song generator used as a fixture by the test-suite.

The library itself has no generators or templates (see CLAUDE.md) — songs are written by hand in song.py.
This file exists so the tests have full-size songs to flatten, lint, render and push."""
from __future__ import annotations

import random
from dataclasses import dataclass, field

from ableton_use.model import (BEATS_PER_BAR, DRUM_MAP, STEP, Note, Part, Fill, Pattern, Section, Song, Track,
                    steps_to_notes)
from ableton_use.theory import Key, voice_lead

# ============================================================================ profiles
@dataclass
class Profile:
    name: str
    bpm: float
    swing: float
    scale: str
    progressions: list[list[int]]
    bars_per_chord: int
    chord_size: int          # 3 triad, 4 seventh, 5 ninth
    chord_style: str         # stab | held | single
    bass_style: str          # offbeat | rolling | syncopated
    hat_style: str           # straight | shuffle | busy
    lead: bool = True
    pad: bool = True
    instruments: dict[str, list[str]] = field(default_factory=dict)


_DRUM_KIT = ["909 Core Kit", "Kit-Core 909", "808 Core Kit", "Drum Rack"]

PROFILES: dict[str, Profile] = {
    "classic": Profile(
        "classic", 124, 54, "minor",
        progressions=[[1, 6, 7, 5], [1, 4, 6, 5], [1, 7, 6, 7], [6, 7, 1, 1]],
        bars_per_chord=1, chord_size=4, chord_style="stab", bass_style="offbeat", hat_style="straight",
        instruments={"chords": ["Grand Piano", "Wavetable", "Operator"], "lead": ["Drift", "Analog", "Operator"]},
    ),
    "deep": Profile(
        "deep", 121, 57, "dorian",
        progressions=[[1, 4, 1, 4], [1, 7, 4, 5], [2, 5, 1, 1], [1, 6, 4, 4]],
        bars_per_chord=2, chord_size=5, chord_style="held", bass_style="syncopated", hat_style="shuffle",
        instruments={"chords": ["Electric Piano", "Wavetable", "Electric"], "lead": ["Wavetable", "Drift"]},
    ),
    "tech": Profile(
        "tech", 126, 52, "minor",
        progressions=[[1, 1, 1, 1], [1, 1, 6, 7], [1, 1, 4, 4]],
        bars_per_chord=1, chord_size=4, chord_style="single", bass_style="rolling", hat_style="busy",
        lead=False, pad=True,
        instruments={"chords": ["Analog", "Wavetable"], "bass": ["Operator", "Analog"]},
    ),
}

DEFAULT_INSTRUMENTS = {
    "kick": _DRUM_KIT, "clap": _DRUM_KIT, "hat": _DRUM_KIT, "openhat": _DRUM_KIT, "perc": _DRUM_KIT,
    "crash": _DRUM_KIT, "bass": ["Operator", "Analog", "Drift"], "chords": ["Wavetable", "Operator"],
    "pad": ["Wavetable", "Drift", "Analog"], "lead": ["Drift", "Analog", "Operator"], "riser": ["Wavetable", "Operator"],
}

# ============================================================================ drums
_HATS = {
    "straight": "gox.gox.gox.gox.",
    "shuffle":  "g.xog.xog.xog.xo",
    "busy":     "oxgxoxgxoxgxoxgx",
}


def drum(name: str, role: str, steps: str, track: str, rng: random.Random | None = None, humanize: int = 0, desc: str = "") -> Pattern:
    notes = steps_to_notes(steps, DRUM_MAP[role])
    if rng and humanize:
        for n in notes:
            n.vel = max(1, min(127, n.vel + rng.randint(-humanize, humanize)))
    bars = max(1, len(steps.replace("|", "")) // 16)
    return Pattern(name, bars, notes, track, desc)


def snare_roll(name: str, track: str, bars: int = 4, role: str = "clap") -> Pattern:
    """Classic build roll: quarters -> 8ths -> 16ths with a velocity ramp."""
    notes = []
    total = bars * BEATS_PER_BAR
    for b in range(bars):
        div = 1.0 if b < bars - 3 else 0.5 if b == bars - 3 else 0.25
        t = b * BEATS_PER_BAR
        while t < (b + 1) * BEATS_PER_BAR - 1e-9:
            if b == bars - 1 and t >= total - 1:   # last beat silent: 'the gap' before the drop
                break
            vel = int(50 + 77 * (t / total) ** 1.3)
            notes.append(Note(DRUM_MAP[role], t, STEP, vel))
            t += div
    return Pattern(name, bars, notes, track, f"{bars}-bar accelerating roll, last beat silent")


# ============================================================================ harmony helpers
def progression_chords(key: Key, degrees: list[int], size: int) -> list[list[int]]:
    out, prev = [], None
    for d in degrees:
        # add the 9th only where it is a whole step above the root (avoid b9 clashes, e.g. ii in dorian / iii in minor)
        root = key.degree(d, 3)
        ninth_ok = size >= 5 and (key.degree(d + 8, 3) - root) % 12 == 2
        c = key.chord(d, size=min(size, 4), octave=3, extensions=(9,) if ninth_ok else ())
        c = voice_lead(prev, c, lo=53, hi=79)
        out.append(c)
        prev = c
    return out


def bass_root(key: Key, degree: int) -> int:
    """Chord root placed so the fundamental sits in the sub range (E0..D#1 = 28..39, ~41-78 Hz)."""
    p = key.degree(degree, octave=0)
    while p < 28:
        p += 12
    while p > 39:
        p -= 12
    return p


# ============================================================================ melodic generators
def bass_pattern(name: str, track: str, key: Key, degrees: list[int], bpc: int, style: str, rng: random.Random) -> Pattern:
    notes = []
    for i, d in enumerate(degrees):
        root = bass_root(key, d)
        nxt = bass_root(key, degrees[(i + 1) % len(degrees)])
        for b in range(bpc):
            base = (i * bpc + b) * BEATS_PER_BAR
            last_bar_of_chord = b == bpc - 1
            if style == "offbeat":
                for beat in range(4):
                    p = root + (12 if (beat == 3 and rng.random() < 0.35) else 0)
                    notes.append(Note(p, base + beat + 0.5, 0.35, 108 if beat % 2 else 100))
            elif style == "rolling":
                for beat in range(4):
                    for s, v in ((1, 80), (2, 110), (3, 88)):
                        p = root + (12 if s == 2 and beat == 3 else 0)
                        notes.append(Note(p, base + beat + s * STEP, 0.2, v))
            else:  # syncopated deep-house line
                rhythm = rng.choice([
                    [(0.5, 0.75, 0), (1.75, 0.5, 0), (2.5, 0.5, 7), (3.5, 0.25, 12)],
                    [(0.75, 0.5, 0), (1.5, 0.25, 0), (2.5, 0.75, 0), (3.75, 0.25, 12)],
                    [(0.5, 1.0, 0), (2.25, 0.5, 0), (3.0, 0.25, 7), (3.5, 0.5, 0)],
                ])
                for t, dur, iv in rhythm:
                    notes.append(Note(root + iv, base + t, dur, 104))
            if last_bar_of_chord and style != "rolling" and nxt != root and rng.random() < 0.6:
                # approach note into the next chord (in key)
                appr = key.snap(nxt + (1 if nxt < root else -1))
                notes = [n for n in notes if not (base + 3.5 <= n.start < base + 4)]
                notes.append(Note(appr, base + 3.75, 0.2, 96))
    return Pattern(name, len(degrees) * bpc, notes, track, f"{style} bass, roots of {degrees}")


_STAB_RHYTHMS = [
    [(0.5, 0.3), (1.25, 0.3), (2.5, 0.3), (3.25, 0.3)],
    [(0.5, 0.3), (1.5, 0.3), (2.75, 0.3), (3.5, 0.25)],
    [(0.0, 0.25), (0.75, 0.3), (1.5, 0.3), (2.75, 0.5)],
]
_HELD_RHYTHMS = [
    [(0.0, 1.4), (1.75, 1.0), (3.5, 0.45)],
    [(0.0, 2.75), (3.0, 0.75)],
    [(0.5, 1.25), (2.5, 1.25)],
]


def chord_pattern(name: str, track: str, chords: list[list[int]], bpc: int, style: str, rng: random.Random) -> Pattern:
    notes = []
    rhythm = rng.choice(_HELD_RHYTHMS if style == "held" else _STAB_RHYTHMS)
    for i, c in enumerate(chords):
        voicing = c if style != "single" else chords[0]
        for b in range(bpc):
            base = (i * bpc + b) * BEATS_PER_BAR
            r = rhythm if style != "single" else [(0.5, 0.25), (1.5, 0.25), (2.5, 0.25), (3.5, 0.25)]
            for t, dur in r:
                for p in voicing:
                    notes.append(Note(p, base + t, dur, 96 if t % 1 else 88))
    return Pattern(name, len(chords) * bpc, notes, track, f"{style} chords")


def pad_pattern(name: str, track: str, chords: list[list[int]], bpc: int) -> Pattern:
    notes = []
    for i, c in enumerate(chords):
        for p in c:
            notes.append(Note(p - 12 if p > 72 else p, i * bpc * BEATS_PER_BAR, bpc * BEATS_PER_BAR, 70))
    return Pattern(name, len(chords) * bpc, notes, track, "held pad, one chord per change")


_MOTIF_RHYTHMS = [
    [0.0, 0.75, 1.5, 2.5, 3.0],
    [0.5, 1.0, 1.75, 2.5, 3.25],
    [0.0, 0.5, 1.5, 2.0, 2.75, 3.5],
    [0.75, 1.5, 2.25, 3.0],
]


def lead_pattern(name: str, track: str, key: Key, degrees: list[int], bpc: int, rng: random.Random) -> Pattern:
    """Call/response hook built from chord tones of each chord, 2-bar motif repeated
    over the progression with the response bar varied."""
    rhythm = rng.choice(_MOTIF_RHYTHMS)
    # motif as chord-relative scale steps (0 = chord root, 2 = third, 4 = fifth, 7 = octave)
    call = [rng.choice([0, 2, 4, 7, 4]) for _ in rhythm]
    resp = call[:-2] + [rng.choice([2, 4]), rng.choice([0, -1])]
    notes = []
    bar = 0
    for d in degrees:
        for b in range(bpc):
            motif = call if bar % 2 == 0 else resp
            for t, step in zip(rhythm, motif):
                p = key.degree(d + step, octave=4)
                if p > 84:
                    p -= 12
                dur = 0.25 if t % 0.5 else 0.4
                notes.append(Note(p, bar * BEATS_PER_BAR + t, dur, 100 if t % 1 == 0 else 90))
            bar += 1
    return Pattern(name, bar, notes, track, "2-bar call/response hook on chord tones")


# ============================================================================ templates
# Each template: (name, kind, bars, energy, parts, fills, automation, desc)
# parts value: pattern name or (pattern, start, end) or (pattern, start, end, transpose)
TEMPLATES: dict[str, list[dict]] = {
    "club": [
        dict(name="intro", kind="intro", bars=16, energy=2, desc="DJ intro: kick + top loop only",
             parts={"Kick": "kick", "Hats": ("hats", 8, None), "Perc": ("perc", 8, None)},
             fills={"Kick": "kick_gap"}),
        dict(name="groove", kind="groove", bars=16, energy=4, desc="clap + open hat in, filtered bass enters",
             parts={"Kick": "kick", "Clap": "clap", "Hats": "hats", "OpenHat": "openhat", "Perc": "perc",
                    "Bass": ("bass", 8, None), "Crash": ("crash", 0, 1)},
             fills={"Clap": {"pattern": "clap_fill", "every": 8}, "Kick": "kick_gap"},
             automation={"Bass": {"filter": [0.3, 0.65]}}),
        dict(name="main", kind="groove", bars=16, energy=6, desc="chords enter, filter opening",
             parts={"Kick": "kick", "Clap": "clap", "Hats": "hats", "OpenHat": "openhat", "Perc": "perc",
                    "Bass": "bass", "Chords": "chords", "Crash": ("crash", 0, 1)},
             fills={"Clap": {"pattern": "clap_fill", "every": 8}, "Kick": "kick_gap"},
             automation={"Chords": {"filter": [0.45, 0.8]}}),
        dict(name="breakdown", kind="breakdown", bars=16, energy=3, desc="drums & bass out; pad + hook stated",
             parts={"Pad": "pad", "Chords": ("chords", 0, 8), "Lead": ("lead", 8, None), "Hats": ("hats", 8, None),
                    "Crash": ("crash", 0, 1)},
             automation={"Pad": {"filter": [0.35, 0.55]}}),
        dict(name="build", kind="build", bars=8, energy=6, desc="roll + riser, filters open, gap on last beat",
             parts={"Pad": "pad", "Lead": "lead", "Hats": "hats", "Riser": "riser"},
             fills={"Clap": "roll"},
             automation={"Pad": {"filter": [0.55, 1.0]}, "Lead": {"filter": [0.5, 1.0]}, "Riser": {"filter": [0.05, 1.0]}}),
        dict(name="drop", kind="drop", bars=32, energy=9, desc="everything in",
             parts={"Kick": "kick", "Clap": "clap", "Hats": "hats", "OpenHat": "openhat", "Perc": "perc",
                    "Bass": "bass", "Chords": "chords", "Lead": "lead", "Crash": ("crash", 0, 1)},
             fills={"Clap": {"pattern": "clap_fill", "every": 8}, "Kick": {"pattern": "kick_gap", "every": 16}}),
        dict(name="bridge", kind="bridge", bars=8, energy=6, desc="hook & chords out for a breath",
             parts={"Kick": "kick", "Clap": "clap", "Hats": "hats", "Perc": "perc", "Bass": "bass", "Pad": "pad"},
             fills={"Kick": "kick_gap"}),
        dict(name="drop2", kind="drop", bars=32, energy=10, desc="biggest section: lead up an octave + pad layer",
             parts={"Kick": "kick", "Clap": "clap", "Hats": "hats", "OpenHat": "openhat", "Perc": "perc",
                    "Bass": "bass", "Chords": "chords", "Pad": "pad", "Lead": ("lead", 0, None, 12),
                    "Crash": ("crash", 0, 1)},
             fills={"Clap": {"pattern": "clap_fill", "every": 8}, "Kick": {"pattern": "kick_gap", "every": 16}}),
        dict(name="outro", kind="outro", bars=16, energy=3, desc="DJ outro: strip back to drums",
             parts={"Kick": "kick", "Hats": "hats", "Perc": "perc", "Clap": ("clap", 0, 8), "Bass": ("bass", 0, 8),
                    "OpenHat": ("openhat", 0, 8)},
             automation={"Bass": {"filter": [0.65, 0.2]}}),
    ],
    "radio": [
        dict(name="intro", kind="intro", bars=8, energy=3, parts={"Kick": "kick", "Hats": "hats", "Pad": "pad"},
             automation={"Pad": {"filter": [0.3, 0.6]}}, fills={"Kick": "kick_gap"}),
        dict(name="groove", kind="groove", bars=16, energy=5,
             parts={"Kick": "kick", "Clap": "clap", "Hats": "hats", "OpenHat": "openhat", "Bass": "bass",
                    "Chords": "chords", "Crash": ("crash", 0, 1)},
             fills={"Clap": {"pattern": "clap_fill", "every": 8}}),
        dict(name="breakdown", kind="breakdown", bars=8, energy=3, parts={"Pad": "pad", "Lead": "lead"}),
        dict(name="build", kind="build", bars=8, energy=6, parts={"Pad": "pad", "Lead": "lead", "Riser": "riser", "Hats": "hats"},
             fills={"Clap": "roll"}, automation={"Pad": {"filter": [0.5, 1.0]}, "Riser": {"filter": [0.05, 1.0]}}),
        dict(name="drop", kind="drop", bars=16, energy=9,
             parts={"Kick": "kick", "Clap": "clap", "Hats": "hats", "OpenHat": "openhat", "Perc": "perc", "Bass": "bass",
                    "Chords": "chords", "Lead": "lead", "Crash": ("crash", 0, 1)},
             fills={"Clap": {"pattern": "clap_fill", "every": 8}}),
        dict(name="bridge", kind="bridge", bars=8, energy=6,
             parts={"Kick": "kick", "Clap": "clap", "Hats": "hats", "Bass": "bass", "Pad": "pad"}, fills={"Kick": "kick_gap"}),
        dict(name="drop2", kind="drop", bars=16, energy=10,
             parts={"Kick": "kick", "Clap": "clap", "Hats": "hats", "OpenHat": "openhat", "Perc": "perc", "Bass": "bass",
                    "Chords": "chords", "Pad": "pad", "Lead": ("lead", 0, None, 12), "Crash": ("crash", 0, 1)},
             fills={"Clap": {"pattern": "clap_fill", "every": 8}}),
        dict(name="outro", kind="outro", bars=8, energy=3, parts={"Kick": "kick", "Hats": "hats", "Pad": "pad"},
             automation={"Pad": {"filter": [0.6, 0.2]}}),
    ],
    "dj_tool": [
        dict(name="intro", kind="intro", bars=32, energy=2, parts={"Kick": "kick", "Hats": ("hats", 8, None), "Perc": ("perc", 16, None),
             "OpenHat": ("openhat", 24, None)}, fills={"Kick": {"pattern": "kick_gap", "every": 16}}),
        dict(name="groove", kind="groove", bars=32, energy=6,
             parts={"Kick": "kick", "Clap": "clap", "Hats": "hats", "OpenHat": "openhat", "Perc": "perc",
                    "Bass": "bass", "Chords": ("chords", 16, None), "Crash": ("crash", 0, 1)},
             fills={"Clap": {"pattern": "clap_fill", "every": 8}, "Kick": {"pattern": "kick_gap", "every": 16}},
             automation={"Chords": {"filter": [0.3, 0.7]}}),
        dict(name="breakdown", kind="breakdown", bars=16, energy=3, parts={"Pad": "pad", "Chords": "chords", "Perc": "perc"},
             automation={"Chords": {"filter": [0.3, 0.6]}}),
        dict(name="build", kind="build", bars=8, energy=6, parts={"Pad": "pad", "Chords": "chords", "Hats": "hats", "Riser": "riser"},
             fills={"Clap": "roll"}, automation={"Chords": {"filter": [0.6, 1.0]}, "Riser": {"filter": [0.05, 1.0]}}),
        dict(name="drop", kind="drop", bars=32, energy=9,
             parts={"Kick": "kick", "Clap": "clap", "Hats": "hats", "OpenHat": "openhat", "Perc": "perc", "Bass": "bass",
                    "Chords": "chords", "Crash": ("crash", 0, 1)},
             fills={"Clap": {"pattern": "clap_fill", "every": 8}, "Kick": {"pattern": "kick_gap", "every": 16}}),
        dict(name="outro", kind="outro", bars=32, energy=2,
             parts={"Kick": "kick", "Hats": ("hats", 0, 24), "Perc": ("perc", 0, 16), "Clap": ("clap", 0, 8), "Bass": ("bass", 0, 8)}),
    ],
}

# track name -> (role, volume_db, sidechain, swing, color)
TRACK_SPECS = {
    "Kick":    ("kick", -3.0, False, False, 14),
    "Clap":    ("clap", -8.0, False, False, 2),
    "Hats":    ("hat", -13.0, False, True, 5),
    "OpenHat": ("openhat", -14.0, False, False, 5),
    "Perc":    ("perc", -15.0, False, True, 6),
    "Bass":    ("bass", -6.0, True, True, 16),
    "Chords":  ("chords", -11.0, True, False, 25),
    "Pad":     ("pad", -15.0, True, False, 26),
    "Lead":    ("lead", -12.0, True, False, 9),
    "Crash":   ("crash", -16.0, False, False, 13),
    "Riser":   ("riser", -18.0, False, False, 20),
}


def _part(v) -> Part:
    if isinstance(v, str):
        return Part(v)
    v = list(v) + [None] * (4 - len(v))
    return Part(v[0], v[1] or 0, v[2], v[3] or 0)


def generate(subgenre: str = "classic", key: str | None = None, bpm: float | None = None,
             template: str = "club", seed: int = 0, title: str | None = None,
             progression: list[int] | None = None) -> Song:
    """Generate a complete, editable house Song."""
    prof = PROFILES[subgenre]
    rng = random.Random(seed)
    k = Key.parse(key) if key else Key(rng.choice([9, 5, 7, 2, 0]), prof.scale)  # A F G D C
    degrees = progression or rng.choice(prof.progressions)
    song = Song(title=title or f"{subgenre} house {seed}", bpm=bpm or prof.bpm, key=str(k), swing=prof.swing,
                meta={"generator": "ableton_use.house.generate", "subgenre": subgenre, "template": template,
                      "seed": seed, "progression": degrees})

    sections_spec = TEMPLATES[template]
    used = {t for s in sections_spec for t in list(s["parts"]) + list(s.get("fills", {}))}
    for tname, (role, vol, sc, sw, color) in TRACK_SPECS.items():
        if tname not in used:
            continue
        if tname == "Lead" and not prof.lead:
            continue
        inst = prof.instruments.get(role) or DEFAULT_INSTRUMENTS.get(role, [])
        song.tracks.append(Track(tname, role, list(inst), vol, 0.0, sc, sw, color))

    bpc = prof.bars_per_chord
    chords = progression_chords(k, degrees, prof.chord_size)
    hat = _HATS[prof.hat_style]
    P = song.add_pattern
    P(drum("kick", "kick", "x...x...x...x...", "Kick", desc="four on the floor"))
    P(drum("kick_gap", "kick", "x...x...x.......", "Kick", desc="kick drops out on beat 4 to set up the next phrase"))
    P(drum("clap", "clap", "....x.......x...", "Clap", desc="backbeat on 2 & 4"))
    P(drum("clap_fill", "clap", "....x.......x.gx", "Clap", desc="pickup into next phrase"))
    P(snare_roll("roll", "Clap", bars=4))
    P(drum("hats", "hat", hat * 2, "Hats", rng, 6, desc=f"{prof.hat_style} 16ths"))
    P(drum("openhat", "openhat", "..x...x...x...x.", "OpenHat", desc="off-beat open hat"))
    perc = rng.choice(["...x..x....x..x.", "..o..x...o..x.o.", "...x.x.....x..x."])
    P(drum("perc", "perc", perc, "Perc", rng, 8, desc="syncopated rim/perc"))
    P(drum("crash", "crash", "X...............", "Crash", desc="crash on the downbeat"))
    if any(t.name == "Bass" for t in song.tracks):
        P(bass_pattern("bass", "Bass", k, degrees, bpc, prof.bass_style, rng))
    if any(t.name == "Chords" for t in song.tracks):
        P(chord_pattern("chords", "Chords", chords, bpc, prof.chord_style, rng))
    if any(t.name == "Pad" for t in song.tracks):
        P(pad_pattern("pad", "Pad", chords, bpc))
    if any(t.name == "Lead" for t in song.tracks):
        P(lead_pattern("lead", "Lead", k, degrees, bpc, rng))
    if any(t.name == "Riser" for t in song.tracks):
        P(Pattern("riser", 8, [Note(k.tonic(3), 0.0, 8 * BEATS_PER_BAR, 90)], "Riser", "8-bar sustained riser; open its filter"))

    have_tracks = {t.name for t in song.tracks}
    for spec in sections_spec:
        parts = {t: _part(v) for t, v in spec["parts"].items() if t in have_tracks}
        fills = {t: Fill.from_json(v) for t, v in spec.get("fills", {}).items() if t in have_tracks}
        auto = {t: v for t, v in spec.get("automation", {}).items() if t in have_tracks}
        song.sections.append(Section(spec["name"], spec["kind"], spec["bars"], spec["energy"], parts, fills, auto, spec.get("desc", "")))
    errs = song.validate()
    if errs:
        raise RuntimeError("generator produced invalid song: " + "; ".join(errs))
    return song
