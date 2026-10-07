import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent))

from ableton_use import Key, Project, Song  # noqa: E402
from fixture_songs import generate  # noqa: E402
from ableton_use import edits  # noqa: E402
from ableton_use.analysis import lint, loudness_lufs, measure  # noqa: E402
from ableton_use.model import Note, Pattern, Section, Part, Track, dumps_compact, fmt_pos, parse_pos, steps_to_notes  # noqa: E402
from ableton_use.render.midi import export_midi, read_midi_notes  # noqa: E402
from ableton_use.render.preview import render_preview  # noqa: E402
from ableton_use.score import pack  # noqa: E402
from ableton_use.theory import chord_name, note, name, voice_lead  # noqa: E402


# ---------------------------------------------------------------- theory
def test_note_names_ableton_convention():
    assert note("C3") == 60 and note("C1") == 36 and note("A-2") == 9 and note("A-1") == 21
    assert name(60) == "C3" and note("Bb2") == 58


@pytest.mark.parametrize("text,root,scale", [("Am", 9, "minor"), ("F#m", 6, "minor"), ("D dorian", 2, "dorian"),
                                             ("Eb", 3, "major"), ("G minor", 7, "minor"), ("Bbm", 10, "minor")])
def test_key_parse(text, root, scale):
    k = Key.parse(text)
    assert (k.root, k.scale) == (root, scale)


def test_diatonic_chords_and_names():
    k = Key.parse("A minor")
    assert chord_name(k.chord(1, 4)) == "Am7"
    assert chord_name(k.chord(6, 4)) == "Fmaj7"
    assert chord_name([57, 60, 64, 67, 71]) == "Am9"


def test_voice_lead_stays_in_range_and_moves_little():
    a = voice_lead(None, [57, 60, 64], 53, 79)
    b = voice_lead(a, [53, 57, 60], 53, 79)
    assert all(53 <= p <= 79 for p in a + b)
    assert sum(abs(x - y) for x, y in zip(sorted(a), sorted(b))) <= 6


# ---------------------------------------------------------------- model
def test_positions():
    assert parse_pos("2.1.3") == 4.5
    assert fmt_pos(4.5) == "2.1.3"
    assert parse_pos(1.25) == 1.25


def test_steps():
    ns = steps_to_notes("x...X.g.|o...", 36)
    assert [n.start for n in ns] == [0, 1.0, 1.5, 2.0]
    assert [n.vel for n in ns] == [100, 127, 45, 72]


@pytest.mark.parametrize("sub,tpl", [("classic", "club"), ("deep", "radio"), ("tech", "dj_tool")])
def test_generate_roundtrip_and_flatten(sub, tpl):
    s = generate(sub, template=tpl, seed=2)
    assert s.validate() == []
    j = s.to_json()
    assert Song.from_json(json.loads(dumps_compact(j))).to_json() == j
    clips, markers = s.flatten()
    assert [m.name for m in markers] == [x.name for x in s.sections]
    for c in clips:
        assert c.length % 4 == 0 and c.start % 4 == 0
        assert all(0 <= n.start < c.length and n.start + n.dur <= c.length + 1e-9 for n in c.notes)


def test_flatten_parts_fills_and_swing():
    s = Song(bpm=124, key="A minor", swing=60)
    s.tracks = [Track("Hats", "hat", swing=True), Track("Clap", "clap")]
    s.add_pattern(Pattern("h", 1, steps_to_notes("xxxxxxxxxxxxxxxx", 42)))
    s.add_pattern(Pattern("c", 1, steps_to_notes("....x.......x...", 39)))
    s.add_pattern(Pattern("f", 1, steps_to_notes("xxxxxxxxxxxxxxxx", 39)))
    s.sections = [Section("a", "groove", 8, parts={"Hats": Part("h", 4)}, fills={"Clap": __import__("ableton_use").Fill("f", 4)})]
    clips, _ = s.flatten()
    hats = next(c for c in clips if c.track == "Hats")
    assert hats.start == 16 and hats.length == 16           # starts at bar 5
    assert abs(hats.notes[1].start - (0.25 + 0.05)) < 1e-9  # 60% swing delays 2nd 16th by 0.05 beat
    clap = next(c for c in clips if c.track == "Clap")
    assert clap.start == 12 and clap.length == 20           # fill-only bars 4 and 8 -> clip spans bars 4-8
    assert len(clap.notes) == 32


def test_validate_catches_errors():
    s = generate(seed=1)
    s.sections[0].parts["Kick"] = Part("nope")
    assert any("unknown pattern" in e for e in s.validate())
    with pytest.raises(ValueError):
        s.flatten()


# ---------------------------------------------------------------- edits
def test_edit_ops():
    s = generate("classic", seed=1)
    log = edits.apply(s, [
        {"op": "set", "field": "key", "value": "Gm"},
        {"op": "pattern", "name": "b2", "track": "Bass", "bars": 1, "notes": [["A0", "1.1.2", 0.2, 100], ["A0", "1.3.4", 0.2, 90]]},
        {"op": "part", "section": "drop2", "track": "Bass", "pattern": "b2"},
        {"op": "part", "section": "bridge", "track": "Pad", "pattern": None},
        {"op": "fill", "section": "drop", "track": "Perc", "pattern": "clap_fill", "every": 8},
        {"op": "automation", "section": "drop", "track": "Chords", "param": "filter", "points": [0.5, 1]},
        {"op": "insert_section", "index": 4, "section": {"name": "break2", "kind": "breakdown", "bars": 8, "parts": {"Pad": "pad"}}},
        {"op": "track", "name": "Bass", "set": {"name": "Sub", "volume_db": -5}},
        {"op": "pattern", "name": "p2", "track": "Perc", "pitch": "D2", "steps": "..x...x...x..x.x"},
    ])
    assert len(log) == 9 and s.key == "G minor"
    assert s.section("drop2").parts["Sub"].pattern == "b2"
    assert "Pad" not in s.section("bridge").parts
    assert s.sections[4].name == "break2"
    with pytest.raises(edits.EditError):
        edits.apply(s, [{"op": "part", "section": "drop", "track": "Lead", "pattern": "missing"}])


# ---------------------------------------------------------------- lint
def test_generated_songs_lint_clean_of_errors():
    for sub in ("classic", "deep", "tech"):
        assert not [i for i in lint(generate(sub, seed=5)) if i.severity == "error"]


def test_lint_rules_fire():
    s = generate("classic", seed=1)
    s.sections[0].bars = 14                                       # H2
    s.sections[0].parts["Bass"] = Part("bass")                    # H3
    s.patterns["chords"].notes.append(Note(40, 0, 1, 90))         # H10
    s.patterns["chords"].notes.append(Note(61, 0, 1, 90))         # H4 (C# not in F minor)
    s.track("Bass").sidechain = False
    s.patterns["bass"].notes = [Note(29, b, 0.5, 100) for b in range(16)]  # on every kick, H6
    rules = {i.rule for i in lint(s)}
    assert {"H2-phrasing", "H3-dj-friendly", "H10-low-end", "H4-key", "H6-kick-bass"} <= rules
    s2 = generate("classic", seed=1)
    s2.sections[5].parts.pop("Kick")
    assert any(i.rule == "H8-energy" and i.severity == "error" for i in lint(s2))


# ---------------------------------------------------------------- renderers
def test_midi_roundtrip(tmp_path):
    s = generate("tech", template="radio", seed=3)
    paths = export_midi(s, tmp_path)
    assert (tmp_path / "song.mid") in paths and len(paths) == len(s.tracks) + 1
    got = read_midi_notes(tmp_path / "song.mid")
    clips, _ = s.flatten()
    assert len(got) == sum(len(c.notes) for c in clips)
    kick = [g for g in got if g[0] == 1]
    assert kick[0][1] == 0.0 and kick[0][3] == 36


def test_preview_and_measure(tmp_path):
    s = generate("classic", template="radio", seed=1)
    r = render_preview(s, tmp_path / "p.wav", sr=22050)
    assert abs(r.duration_s - (s.duration_s + 2)) < 0.1
    m = measure(tmp_path / "p.wav", s)
    by = {x.name: x for x in m.sections}
    assert by["drop"].lufs > by["breakdown"].lufs + 3
    assert by["drop"].bands["sub"] + by["drop"].bands["bass"] > 30


def test_lufs_reference():
    sr = 48000
    t = np.arange(sr * 5) / sr
    x = 10 ** (-20 / 20) * np.sin(2 * np.pi * 1000 * t)   # -20 dBFS 1 kHz sine
    # BS.1770: a -20 dBFS 1 kHz sine on both channels reads ~-20 LUFS
    assert abs(loudness_lufs(np.stack([x, x], 1), sr) - (-20.0)) < 0.5


def test_score_is_compact_and_complete():
    s = generate("deep", seed=4)
    text = pack(s)
    assert len(text) < 12000
    for sec in s.sections:
        assert f"**{sec.name}**" in text
    for p in s.patterns:
        assert f"### {p} " in text


# ---------------------------------------------------------------- project
def test_project_flow(tmp_path):
    p = Project.create(tmp_path / "trk", generate("classic", template="radio", seed=1))
    assert p.score_path.exists()
    p.edit([{"op": "section", "name": "drop", "set": {"energy": 8}}])
    assert p.load().section("drop").energy == 8
    p.undo()
    assert p.load().section("drop").energy == 9
    r = p.evaluate()
    assert r.errors == 0 and p.eval_path.exists() and p.preview_path.exists()
    png = p.view((25, 40))
    assert png.exists() and png.stat().st_size > 10000
    p.remember(strategy="test", decisions="d")
    p.remember(strategy="again")
    assert p.memory().count("## Session") == 2


# ---------------------------------------------------------------- option() choices, A/B, hit levels
OPTION_SONG = '''
from ableton_use import Song, option

GHOST = option("ghost", 60)
song = Song("Opt", bpm=126, key="G minor")
hat = song.add_track("Hats", "hat", volume_db=-10)
h = song.pattern("h", hat, f"1.1 F#1 0.2 v{GHOST}; 1.3 F#1 0.2 v110; 2.3 F#1 0.2 v110; 3.3 F#1 0.2 v110; 4.3 F#1 0.2 v110")
song.add_section("a", 2, energy=5, parts={hat: h})
'''


def test_option_switches_and_rebuilds(tmp_path, monkeypatch):
    from ableton_use import options
    from ableton_use.project import Project
    monkeypatch.delenv(options.ENV, raising=False)
    (tmp_path / "song.py").write_text(OPTION_SONG)
    p = Project(tmp_path)
    assert p.load().meta["options"]["ghost"] == {"default": 60, "value": 60}
    with options.using({"ghost": "20"}):
        assert p.load().meta["options"]["ghost"]["value"] == 20          # stale song.json is rebuilt for the switched choice
    assert p.load().meta["options"]["ghost"]["value"] == 60              # ... and back again without it
    assert "ghost=60" in p.score()
    with options.using({"gost": "20"}):
        with pytest.raises(ValueError, match="no option called gost"):
            p.build()


def test_ab_and_hits(tmp_path, monkeypatch):
    from ableton_use import options
    from ableton_use.analysis import compare_table
    from ableton_use.project import Project
    monkeypatch.delenv(options.ENV, raising=False)
    (tmp_path / "song.py").write_text(OPTION_SONG)
    p = Project(tmp_path)
    files = p.ab([("base", {}), ("loud", {"ghost": "127"})], bars=(1, 2), tracks=["Hats"])
    assert [f.name for _, f in files] == ["base.wav", "loud.wav"]
    table = compare_table(files)
    assert "| LUFS |" in table and "loud" in table.splitlines()[0]
    text = p.hits((1, 2), ["Hats"])
    rows = [ln for ln in text.splitlines() if ln[:1].isdigit() and " dB " in ln and "hits" not in ln]
    assert len(rows) == 2 and "vel" in text
    assert "10 hits" in text                                             # 5 written hits per bar, no tails counted


def test_live_lock_is_exclusive_and_reentrant(tmp_path, monkeypatch):
    import tempfile

    from ableton_use.live.client import BridgeError, live_lock, lock_path
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    with live_lock("a"):
        assert lock_path().exists()
        with live_lock("b"):                                             # same process: free
            pass
        assert lock_path().exists()
    assert not lock_path().exists()
    lock_path().write_text("1 someone else")                             # pid 1 is always alive
    with pytest.raises(BridgeError, match="in use"):
        with live_lock("c", wait_s=0.1):
            pass
    lock_path().write_text("999999999 a dead run")
    with live_lock("d"):
        pass
