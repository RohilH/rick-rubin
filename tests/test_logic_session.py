"""Session mode (work inside an open Logic project) against the fake bridge, and the parts of a Logic push
that reach it as rendered audio or as notes with the MIDI effects written in."""
import json
import os
import struct
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent))

from fake_logic import FakeLogicBridge, FakeStrip  # noqa: E402

from rick_rubin import Song  # noqa: E402
from rick_rubin.logic import client as C  # noqa: E402
from rick_rubin.logic import session as S  # noqa: E402
from rick_rubin.logic.bridge import LogicError  # noqa: E402
from rick_rubin.logic.smf import export_logic_midi, key_signature  # noqa: E402
from rick_rubin.render.midi import read_midi_notes  # noqa: E402
from rick_rubin.render.stems import sample_stem  # noqa: E402
from rick_rubin.samples import read_audio, write_wav24  # noqa: E402


@pytest.fixture
def fake(tmp_path, monkeypatch):
    monkeypatch.setattr(S, "HOME", tmp_path / "home")
    b = FakeLogicBridge()
    b.projects, b.project = ["My Song.logicx"], "My Song.logicx"
    b._strips = [FakeStrip("Kick", instrument="Drum Synth"), FakeStrip("Bass", inserts=["Channel EQ", "Compressor", "Compressor"]),
                 FakeStrip("Pad", volume=-12.0, pan=-10), FakeStrip("Pad 2"),
                 FakeStrip("Aux 1", kind="aux", instrument=None, inserts=["ChromaVerb"]),
                 FakeStrip("Stereo Out", kind="output", instrument=None)]
    b.selected = 2
    return b


def test_inspect_reads_the_open_project(fake):
    with S.Session(fake) as s:
        st = s.state()
    assert st["project"] == "My Song.logicx" and st["tempo"] == 124.0 and st["key"] == "Amin"
    assert [t["name"] for t in st["tracks"]] == ["Kick", "Bass", "Pad", "Pad 2"] and [t["n"] for t in st["tracks"]] == [1, 2, 3, 4]
    assert [t["selected"] for t in st["tracks"]] == [False, False, True, False]
    assert st["aux"][0]["inserts"] == ["ChromaVerb"] and st["outputs"][0]["name"] == "Stereo Out"
    text = S.format_state(st)
    assert "| 3* | Pad | -12.0 dB | -10 |" in text and "| aux | Aux 1 |" in text
    assert not fake.selections or fake.selections == [2]          # reading selects nothing but puts the selection back


def test_strips_are_found_by_name_number_or_a_unique_beginning(fake):
    with S.Session(fake) as s:
        assert s.resolve("bass")[0] == 1 and s.resolve("#3")[0] == 2 and s.resolve(1)[0] == 0
        assert s.resolve("Aux 1")[0] == "Aux 1" and s.resolve("stereo")[0] == "Stereo Out"
        assert s.resolve("Pad")[0] == 2                            # an exact name wins over 'Pad 2'
        with pytest.raises(LogicError, match="fits 2 strips"):
            s.resolve("pa")
        with pytest.raises(LogicError, match="no channel strip"):
            s.resolve("Vocal")
        with pytest.raises(LogicError, match="4 tracks"):
            s.resolve("#9")


def test_mix_changes_are_read_back_logged_and_leave_the_selection(fake, tmp_path):
    with S.Session(fake) as s:
        changes = s.mix("Bass", volume=-6, pan=-20, mute=True)
    assert [(c.op, c.before, c.after, c.ok) for c in changes] == [("volume", "0.0 dB", "-6.0 dB", True), ("pan", "0", "-20", True), ("mute", False, True, True)]
    assert fake._strips[1].volume == -6.0 and fake._strips[1].pan == -20 and fake._strips[1].mute
    assert fake.selections[0] == 1 and fake.selections[-1] == 2    # only the target selected for the edit; the person's selection back
    log = [json.loads(x) for x in (tmp_path / "home" / "sessions" / "My Song.logicx.jsonl").read_text().splitlines()]
    assert [e["op"] for e in log] == ["volume", "pan", "mute"] and log[0]["before"] == "0.0 dB" and log[0]["after"] == "-6.0 dB"


def test_a_change_that_does_not_read_back_as_asked_is_reported(fake):
    fake.fader_stop = -3.0
    with S.Session(fake) as s:
        (c,) = s.mix("Bass", volume=-10)
    assert not c.ok and c.after == "-3.0 dB" and "NOT AS ASKED" in c.line()


def test_aux_strips_are_edited_with_one_track_selected(fake):
    with S.Session(fake) as s:
        (c,) = s.mix("Aux 1", volume=-3)
    assert c.ok and fake._strips[4].volume == -3.0 and fake.selections[0] == 2


def test_insert_tweak_and_side_chain(fake):
    with S.Session(fake) as s:
        name, values = s.params("Bass", "Compressor")
        assert name == "Compressor" and values["Thrshld"] == "-20.0 dB"
        c = s.insert("Pad", "Trackspacer 2.5", {"Ratio": 60}, sidechain="Kick")
        assert c.ok and c.after == ["Trackspacer 2.5"] and "Ratio 60" in c.note and "side chain <- Kick" in c.note
        assert fake._strips[2].params[1] == {"Ratio": "60"} and fake._strips[2].side_chains[0] == "Kick"
        c = s.tweak("Bass", "Compressor", {"Threshold": -30}, nth=1)       # the second Compressor is insert 3
        assert c.ok and fake._strips[1].params == {3: {"Threshold": "-30"}}
        c = s.tweak("Bass", "comp", {"Nope": 1})
        assert not c.ok and "no parameter" in c.note
        with pytest.raises(LogicError, match="has no 'Limiter'"):
            s.tweak("Bass", "Limiter", {"Gain": 1})
        with pytest.raises(LogicError, match="no plug-in"):
            s.insert("Pad", "Not A Plug-in")


def test_sends_make_and_remove(fake):
    with S.Session(fake) as s:
        c = s.send("Pad", 2, -14)
        assert c.ok and c.after == ["Bus 2"] and any(x.name == "Aux 2" for x in fake._strips)
        c = s.send("Pad", 2, None)
        assert c.ok and c.after == []
        with pytest.raises(LogicError, match="sends are set on tracks"):
            s.send("Aux 1", 1, -10)


def test_new_tracks_from_audio_midi_and_an_instrument(fake, tmp_path):
    wav = tmp_path / "vocal take.wav"
    write_wav24(wav, 44100, np.zeros((1000, 2), np.float32))
    mid = tmp_path / "line.mid"
    mid.write_bytes(b"MThd" + struct.pack(">IHHH", 6, 1, 1, 480))
    with S.Session(fake) as s:
        c = s.add_audio(wav, bar=9, name="Vocal")
        assert c.ok and fake.imports == [(4, wav, 9, 1)] and fake.tracks()[4] == "Vocal"
        c = s.add_midi(mid, bar=17, names=["Lead"])
        assert c.ok and fake.midi_imports == [(mid, 17)] and "Lead" in fake.tracks()
        c = s.add_instrument("Retro Synth", "Stab", {"Cutoff": 40})
        assert c.ok and fake.tracks()[-1] == "Stab" and fake._strips[len(fake.tracks()) - 1].instrument == "Retro Synth"
        with pytest.raises(LogicError, match="does not exist"):
            s.add_audio(tmp_path / "missing.wav")


def test_bounce_solos_only_for_the_bounce(fake, tmp_path):
    fake._strips[0].solo = True                                   # the person had the kick soloed
    with S.Session(fake) as s:
        r = s.bounce(tmp_path / "bass.wav", bars=(9, 16), tracks=["Bass"])
    assert Path(r["path"]).exists() and r["tracks"] == ["Bass"]
    assert [x.solo for x in fake._strips[:3]] == [True, False, False]


def test_a_session_does_not_start_while_logic_asks_something(fake):
    fake.alert = ("Do you want to save the changes?", ["Save", "Don't Save", "Cancel"])
    with pytest.raises(LogicError, match="never answers"):
        with S.Session(fake):
            pass


def test_backup_copies_the_saved_state_once_per_save(fake, tmp_path):
    pkg = tmp_path / "My Song.logicx"
    (pkg / "Alternatives" / "000").mkdir(parents=True)
    (pkg / "Alternatives" / "000" / "ProjectData").write_bytes(b"state-1")
    (pkg / "Media").mkdir()
    (pkg / "Media" / "big.wav").write_bytes(b"x" * 100)
    fake.path = pkg
    with S.Session(fake) as s:
        s.mix("Bass", volume=-3)
        s.mix("Bass", volume=-4)
    made = sorted((tmp_path / "home" / "backups" / "My Song").glob("*/Alternatives/000/ProjectData"))
    assert len(made) == 1 and made[0].read_bytes() == b"state-1"
    assert not list((tmp_path / "home" / "backups").rglob("big.wav"))          # audio is not copied
    with S.Session(fake) as s:
        s.mix("Bass", volume=-5)
    assert len(list((tmp_path / "home" / "backups" / "My Song").glob("*/info.json"))) == 1    # same saved state: no second copy
    (pkg / "Alternatives" / "000" / "ProjectData").write_bytes(b"state-2")
    os.utime(pkg / "Alternatives" / "000" / "ProjectData", (2_000_000_000, 2_000_000_000))
    assert S.backup(fake) is not None or S.backup(fake, force=True) is not None


def test_projects_are_found_by_a_loose_title():
    b = FakeLogicBridge()
    b.projects = ["Night Shift.logicx", "Untitled 3"]
    assert S.find_project(b.app, "night shift") == "Night Shift.logicx" and S.find_project(b.app, "untitled") == "Untitled 3"
    with pytest.raises(LogicError, match="no open project matches"):
        S.find_project(b.app, "Other")
    b.projects = []
    with pytest.raises(LogicError, match="no project is open"):
        S.find_project(b.app, None)


def test_settings_parse_numbers_switches_and_names():
    assert S.parse_settings(["Threshold=-24", "Auto Gain=Off", "Model=RMS", "On=true"]) == {"Threshold": -24.0, "Auto Gain": False, "Model": "RMS", "On": True}
    assert S.number("−4.5 dB") == -4.5 and S.number("+2,5") == 2.5 and S.number("Off") is None
    with pytest.raises(LogicError):
        S.parse_settings(["Threshold"])


# ------------------------------------------------------------------ parts that reach Logic as audio / written-in notes
def _click(path: Path, sr: int = 44100, stereo: bool = True) -> None:
    x = np.zeros((sr // 10, 2 if stereo else 1), np.float32)
    x[:200, 0] = 0.5
    if stereo:
        x[:200, 1] = 0.25
    write_wav24(path, sr, x)


def test_sample_stem_plays_the_file_at_each_hit_with_the_velocity_law(tmp_path):
    (tmp_path / "samples").mkdir()
    _click(tmp_path / "samples" / "clap.wav")
    s = Song("T", bpm=120, key="A minor")
    s.base_dir = tmp_path
    clap = s.add_track("Clap", "clap", sample="samples/clap.wav")
    hits = s.pattern("hits", clap, ["2.1 C1 0.25 v100; 4.1 C1 0.25 v64"])
    s.arrange(s.add_section("a", 8, kind="drop", energy=5, parts={clap: hits}))
    clips, _ = s.flatten(sounding=True)
    out = sample_stem(s, clap, clips, tmp_path / "stems")
    sr, x = read_audio(out)
    assert x.shape == (int(8 * 4 * 0.5 * sr), 2)                               # the song's length, stereo kept
    first, second = int(0.5 * sr), int(1.5 * sr)                               # beats 2 and 4 at 120 BPM
    assert abs(float(np.abs(x[first:first + 200, 0]).max()) - 0.5) < 0.01 and abs(float(np.abs(x[first:first + 200, 1]).max()) - 0.25) < 0.01
    assert float(np.abs(x[:first - 10]).max()) == 0.0
    drop_db = 20 * np.log10(float(np.abs(x[second:second + 200, 0]).max()) / 0.5)
    assert -5.6 < drop_db < -4.4                                               # velocity 64 is 5 dB under velocity 100 (Simpler at 35 %)
    assert sample_stem(s, clap, clips, tmp_path / "stems") == out              # cached by content


def test_push_places_sample_parts_as_audio_and_writes_midi_effects_into_the_notes(tmp_path):
    (tmp_path / "samples").mkdir()
    _click(tmp_path / "samples" / "kick.wav", stereo=False)
    s = Song("Sampled", bpm=124, key="F dorian")
    s.base_dir = tmp_path
    kick = s.add_track("Kick", "kick", sample="samples/kick.wav", volume_db=-6)
    keys = s.add_track("Keys", "chords", instrument="Retro Synth",
                       midi_effects=[{"device": "Chord", "params": {"Shift1": 3, "Shift2": 7}}])
    arp = s.add_track("Arp", "lead", midi_effects=[{"device": "Arpeggiator", "params": {}}])
    four = s.pattern("four", kick, "x...x...x...x...")
    stab = s.pattern("stab", keys, ["1.1 F3 0.5; 3.1 Eb3 0.5"])
    line = s.pattern("line", arp, ["1.1 F4 1"])
    s.arrange(s.add_section("a", 8, kind="drop", energy=7, parts={kick: four, keys: stab, arp: line}))

    r = export_logic_midi(s, tmp_path / "x.mid")
    data = (tmp_path / "x.mid").read_bytes()
    assert b"\xff\x59\x02\xfd\x00" in data                                    # F dorian: three flats (Eb major), a major-type signature
    by_track: dict[int, list] = {}
    for n in read_midi_notes(r["path"]):
        by_track.setdefault(n[0], []).append(n)
    keys_notes = [n for n in by_track[2] if n[4] > 1]
    assert 8 * 2 * 3 - 3 <= len(keys_notes) <= 8 * 2 * 3                       # each written note became a three-note chord (the test reader merges same-tick pairs)
    assert {n[3] for n in keys_notes} >= {65, 68, 72}                         # F3 with a minor third and a fifth (C3 = 60)

    fake = FakeLogicBridge()
    rep = C.push_song(s, fake, save=False)
    assert fake.tracks() == ["Keys", "Arp", "Kick"]                            # the sample part is an audio track after the MIDI tracks
    ti, path, bar, beat = fake.imports[0]
    assert fake.tracks()[ti] == "Kick" and path.name == "Kick.wav" and (bar, beat) == (1, 1)
    assert "rendered to audio" in rep.tracks["Kick"]["instrument"] and fake._strips[ti].volume == -6.0
    assert "written into the notes: Chord" in rep.tracks["Keys"]["midi_fx"]
    assert any("Arp" in w and "Arpeggiator" in w for w in rep.warnings)        # not emulated: said, not hidden
    assert not any("not yet built" in w for w in rep.warnings)
    assert key_signature("A minor") == (0, 1) and key_signature("F# minor") == (3, 1) and key_signature("nonsense scale") is None


def test_push_can_put_a_live_serum_on_the_track(tmp_path, monkeypatch):
    from rick_rubin import serum
    (tmp_path / "serum" / "presets").mkdir(parents=True)
    (tmp_path / "serum" / "presets" / "round.SerumPreset").write_bytes(b"x")

    def fake_aupreset(src, dst, params=None, root=None):
        Path(dst).parent.mkdir(parents=True, exist_ok=True)
        Path(dst).write_bytes(b"au")
        return Path(dst)
    monkeypatch.setattr(serum, "write_aupreset", fake_aupreset)
    s = Song("Live Serum", bpm=124, key="A minor")
    s.base_dir = tmp_path
    kick = s.add_track("Kick", "kick")
    bass = s.add_track("Bass", "bass", serum="serum/presets/round.SerumPreset", volume_db=-9)
    four = s.pattern("four", kick, "x...x...x...x...")
    line = s.pattern("line", bass, ["1.3 A0 0.35; 2.3 A0 0.35; 3.3 G0 0.35"])
    s.arrange(s.add_section("a", 8, kind="drop", energy=7, parts={kick: four, bass: line}))
    fake = FakeLogicBridge()
    rep = C.push_song(s, fake, save=False, serum_live=True)
    assert fake.tracks() == ["Kick", "Bass"] and not fake.imports                 # MIDI on the track, nothing rendered to audio
    strip = fake._strips[1]
    assert strip.instrument == "Serum 2" and strip.params[0]["setting"] == "Bass" and strip.inserts == [] and strip.volume == -9.0
    assert (tmp_path / "logic" / "presets" / "Bass.aupreset").exists() and "live" in rep.tracks["Bass"]["instrument"]
    notes = [n for n in read_midi_notes(tmp_path / "logic" / "Live Serum.mid") if n[0] == 2 and n[4] > 1]
    assert len(notes) == 8 * 3                                                    # the part is in the MIDI file
    # without the option the part is rendered: an audio track, as before (needs the real plug-in, so only the plan is checked)
    assert C.as_audio(bass) and not C.as_audio(bass, True)


def test_a_serum_patch_goes_onto_a_track_that_holds_serum(fake, tmp_path, monkeypatch):
    from rick_rubin import serum
    pre = tmp_path / "proj" / "serum" / "presets"
    pre.mkdir(parents=True)
    (pre / "round.SerumPreset").write_bytes(b"x")
    monkeypatch.setattr(serum, "write_aupreset", lambda src, dst, params=None, root=None: (Path(dst).parent.mkdir(parents=True, exist_ok=True), Path(dst).write_bytes(b"au"), Path(dst))[2])
    with S.Session(fake) as s:
        with pytest.raises(LogicError, match="not Serum 2"):
            s.serum("Bass", "serum/presets/round.SerumPreset", project_dir=tmp_path / "proj")
        fake._strips[1].instrument = "Serum 2"
        c = s.serum("Bass", "serum/presets/round.SerumPreset", project_dir=tmp_path / "proj")
        assert c.ok and c.after == "round" and (tmp_path / "proj" / "serum" / "aupresets" / "round.aupreset").exists()
        fake._strips[1].instrument = "Serum 2 FX"
        with pytest.raises(LogicError, match="not Serum 2"):
            s.serum("Bass", "serum/presets/round.SerumPreset", project_dir=tmp_path / "proj")
