"""JSON edit operations on a Song — the agent's write interface.

Every op is a small dict, so an LLM (or a human) can express changes precisely
without rewriting song.json. `apply(song, ops)` mutates in place, validates, and
returns a log of what changed. Ops:

  {"op": "set", "field": "bpm"|"key"|"swing"|"title", "value": ...}
  {"op": "track", "name": "Bass", "set": {"role": "bass", "volume_db": -6, "instrument": ["Operator"], ...}}
  {"op": "remove_track", "name": "Riser"}
  {"op": "pattern", "name": "bass_b", "bars": 4, "track": "Bass", "notes": [["A0", "1.1.3", 0.25, 100], ...]}
  {"op": "pattern", "name": "hats2", "track": "Hats", "pitch": "F#1", "steps": "x.x.x.x.x.x.x.x."}
  {"op": "generate", "what": "bass|chords|pad|lead|hats|perc|roll", "name": "...", "track": "...",
        "options": {"style": "rolling", "progression": [1,6,4,5], "bars_per_chord": 1, "seed": 7}}
  {"op": "transpose_pattern", "name": "lead", "semitones": 12}
  {"op": "humanize", "name": "hats", "velocity": 8}
  {"op": "section", "name": "drop", "set": {"bars": 32, "energy": 9, "kind": "drop", "desc": "..."}}
  {"op": "insert_section", "index": 3, "section": {"name": "break2", "kind": "breakdown", "bars": 8, "parts": {...}}}
  {"op": "remove_section", "name": "bridge"}
  {"op": "move_section", "name": "bridge", "index": 5}
  {"op": "part", "section": "drop", "track": "Lead", "pattern": "lead", "start": 8, "end": null, "transpose": 0}
  {"op": "part", "section": "drop", "track": "Lead", "pattern": null}            # remove
  {"op": "fill", "section": "drop", "track": "Clap", "pattern": "clap_fill", "every": 8}
  {"op": "automation", "section": "build", "track": "Pad", "param": "filter", "points": [0.3, 1.0]}
  {"op": "copy_parts", "from": "drop", "to": "drop2"}
"""
from __future__ import annotations

import random
from . import house
from .model import Fill, Part, Pattern, Section, Song, Track


class EditError(ValueError):
    pass


def apply(song: Song, ops: list[dict] | dict) -> list[str]:
    if isinstance(ops, dict):
        ops = ops.get("ops", [ops])
    log = []
    for i, op in enumerate(ops):
        kind = op.get("op")
        fn = _OPS.get(kind)
        if not fn:
            raise EditError(f"op {i}: unknown op {kind!r}; known: {sorted(_OPS)}")
        try:
            log.append(fn(song, op))
        except (KeyError, ValueError, TypeError, IndexError) as e:
            raise EditError(f"op {i} ({kind}): {e}") from e
    errs = song.validate()
    if errs:
        raise EditError("song invalid after edits:\n  " + "\n  ".join(errs))
    return log


def _set(song: Song, op: dict) -> str:
    f, v = op["field"], op["value"]
    if f not in ("bpm", "key", "swing", "title"):
        raise ValueError(f"cannot set {f!r}")
    setattr(song, f, float(v) if f in ("bpm", "swing") else str(v))
    if f == "key":
        song.key_obj  # validate
        song.key = str(song.key_obj)
    return f"set {f} = {getattr(song, f)}"


def _track(song: Song, op: dict) -> str:
    name, fields = op["name"], dict(op.get("set", {}))
    try:
        t = song.track(name)
        created = False
    except KeyError:
        if "role" not in fields:
            raise ValueError(f"new track {name!r} needs a role")
        t = Track(name, fields["role"], list(house.DEFAULT_INSTRUMENTS.get(fields["role"], [])))
        idx = op.get("index")
        song.tracks.insert(len(song.tracks) if idx is None else int(idx), t)
        created = True
    for k, v in fields.items():
        if k == "instrument" and isinstance(v, str):
            v = [v]
        if k == "name":
            _rename_track(song, t.name, v)
        if not hasattr(t, k):
            raise ValueError(f"track has no field {k!r}")
        setattr(t, k, v)
    return f"{'created' if created else 'updated'} track {t.name}"


def _rename_track(song: Song, old: str, new: str) -> None:
    for s in song.sections:
        for d in (s.parts, s.fills, s.automation):
            if old in d:
                d[new] = d.pop(old)
    for p in song.patterns.values():
        if p.track == old:
            p.track = new


def _remove_track(song: Song, op: dict) -> str:
    t = song.track(op["name"])
    song.tracks.remove(t)
    for s in song.sections:
        s.parts.pop(t.name, None)
        s.fills.pop(t.name, None)
        s.automation.pop(t.name, None)
    return f"removed track {t.name}"


def _pattern(song: Song, op: dict) -> str:
    d = {k: v for k, v in op.items() if k not in ("op", "name")}
    p = Pattern.from_json(op["name"], d)
    existed = op["name"] in song.patterns
    song.patterns[p.name] = p
    return f"{'replaced' if existed else 'added'} pattern {p.name} ({p.bars} bars, {len(p.notes)} notes)"


def _generate(song: Song, op: dict) -> str:
    what, name = op["what"], op["name"]
    o = op.get("options", {})
    rng = random.Random(o.get("seed", hash(name) & 0xFFFF))
    key = song.key_obj
    prog = o.get("progression") or song.meta.get("progression") or [1, 6, 4, 5]
    bpc = int(o.get("bars_per_chord", 1 if len(prog) >= 4 else 2))
    track = op.get("track")
    if what == "bass":
        p = house.bass_pattern(name, track or "Bass", key, prog, bpc, o.get("style", "offbeat"), rng)
    elif what in ("chords", "pad"):
        chords = house.progression_chords(key, prog, int(o.get("size", 4)))
        if what == "pad":
            p = house.pad_pattern(name, track or "Pad", chords, bpc)
        else:
            p = house.chord_pattern(name, track or "Chords", chords, bpc, o.get("style", "stab"), rng)
    elif what == "lead":
        p = house.lead_pattern(name, track or "Lead", key, prog, bpc, rng)
    elif what == "hats":
        p = house.drum(name, "hat", house._HATS[o.get("style", "straight")] * 2, track or "Hats", rng, 6)
    elif what == "perc":
        steps = o.get("steps") or rng.choice(["...x..x....x..x.", "..o..x...o..x.o.", "...x.x.....x..x."])
        p = house.drum(name, o.get("role", "perc"), steps, track or "Perc", rng, 8)
    elif what == "roll":
        p = house.snare_roll(name, track or "Clap", int(o.get("bars", 4)), o.get("role", "clap"))
    else:
        raise ValueError(f"cannot generate {what!r}")
    song.patterns[name] = p
    return f"generated {what} pattern {name} ({p.bars} bars, {len(p.notes)} notes)"


def _transpose(song: Song, op: dict) -> str:
    p = song.patterns[op["name"]]
    st = int(op["semitones"])
    for n in p.notes:
        n.pitch += st
    return f"transposed {p.name} by {st:+d}"


def _humanize(song: Song, op: dict) -> str:
    p = song.patterns[op["name"]]
    rng = random.Random(op.get("seed", 0))
    amt = int(op.get("velocity", 8))
    for n in p.notes:
        n.vel = max(1, min(127, n.vel + rng.randint(-amt, amt)))
    return f"humanized {p.name} velocities ±{amt}"


def _section(song: Song, op: dict) -> str:
    s = song.section(op["name"])
    for k, v in op.get("set", {}).items():
        if k not in ("bars", "energy", "kind", "desc", "name"):
            raise ValueError(f"cannot set section field {k!r}")
        setattr(s, k, int(v) if k in ("bars", "energy") else v)
    return f"updated section {s.name}"


def _insert_section(song: Song, op: dict) -> str:
    sec = Section.from_json(op["section"])
    if any(s.name == sec.name for s in song.sections):
        raise ValueError(f"section {sec.name!r} exists")
    idx = op.get("index", len(song.sections))
    song.sections.insert(int(idx), sec)
    return f"inserted section {sec.name} at {idx}"


def _remove_section(song: Song, op: dict) -> str:
    s = song.section(op["name"])
    song.sections.remove(s)
    return f"removed section {s.name}"


def _move_section(song: Song, op: dict) -> str:
    s = song.section(op["name"])
    song.sections.remove(s)
    song.sections.insert(int(op["index"]), s)
    return f"moved section {s.name} to {op['index']}"


def _part(song: Song, op: dict) -> str:
    s = song.section(op["section"])
    tn = op["track"]
    song.track(tn)
    if op.get("pattern") is None:
        s.parts.pop(tn, None)
        return f"{s.name}: removed {tn}"
    s.parts[tn] = Part(op["pattern"], int(op.get("start", 0)), op.get("end"), int(op.get("transpose", 0)))
    return f"{s.name}: {tn} plays {op['pattern']}"


def _fill(song: Song, op: dict) -> str:
    s = song.section(op["section"])
    tn = op["track"]
    song.track(tn)
    if op.get("pattern") is None:
        s.fills.pop(tn, None)
        return f"{s.name}: removed fill on {tn}"
    s.fills[tn] = Fill(op["pattern"], op.get("every"))
    return f"{s.name}: fill {op['pattern']} on {tn}" + (f" every {op['every']}" if op.get("every") else "")


def _automation(song: Song, op: dict) -> str:
    s = song.section(op["section"])
    tn, prm = op["track"], op.get("param", "filter")
    song.track(tn)
    if op.get("points") is None:
        s.automation.get(tn, {}).pop(prm, None)
        if tn in s.automation and not s.automation[tn]:
            del s.automation[tn]
        return f"{s.name}: cleared {tn}.{prm}"
    s.automation.setdefault(tn, {})[prm] = op["points"]
    return f"{s.name}: automate {tn}.{prm} {op['points']}"


def _copy_parts(song: Song, op: dict) -> str:
    a, b = song.section(op["from"]), song.section(op["to"])
    b.parts = {k: Part(v.pattern, v.start, v.end, v.transpose) for k, v in a.parts.items()}
    b.fills = {k: Fill(v.pattern, v.every) for k, v in a.fills.items()}
    return f"copied parts {a.name} -> {b.name}"


_OPS = {
    "set": _set, "track": _track, "remove_track": _remove_track, "pattern": _pattern, "generate": _generate,
    "transpose_pattern": _transpose, "humanize": _humanize, "section": _section, "insert_section": _insert_section,
    "remove_section": _remove_section, "move_section": _move_section, "part": _part, "fill": _fill,
    "automation": _automation, "copy_parts": _copy_parts,
}
