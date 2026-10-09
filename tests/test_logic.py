"""The Logic Pro render target, tested without Logic: the MIDI file it opens, the readings of the Mackie Control
emulation, the number parsing, and a whole push against a fake bridge. (The real bridge is exercised by hand:
see docs/LOGIC.md.)"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from fake_logic import FakeLogicBridge  # noqa: E402
from fixture_songs import generate  # noqa: E402

from rick_rubin import Song  # noqa: E402
from rick_rubin.logic import bridge as B  # noqa: E402
from rick_rubin.logic import client as C  # noqa: E402
from rick_rubin.logic.ax import disp_number  # noqa: E402
from rick_rubin.logic.mcu import SurfaceState  # noqa: E402
from rick_rubin.logic.smf import GM_PROGRAM_BY_ROLE, cc7_for_db, export_logic_midi  # noqa: E402
from rick_rubin.render.midi import read_midi_notes  # noqa: E402


def test_logic_midi_file_round_trips_notes_and_names(tmp_path):
    s = generate("classic", template="club", seed=1)
    s.base_dir = tmp_path
    r = export_logic_midi(s, tmp_path / "x.mid")
    clips, markers = s.flatten()
    assert r["markers"] == len(markers) and [t["name"] for t in r["tracks"]] == [t.name for t in s.tracks]
    notes = read_midi_notes(r["path"])
    # one MTrk per song track after the conductor; every written note is there
    want = sum(len(c.notes) for c in clips if not s.track(c.track).audio)
    assert want - 2 <= sum(1 for n in notes if not (n[4] == 1 and n[3] == 0)) <= want   # the test reader merges a same-tick off/on pair
    drums = [t for t in r["tracks"] if s.track(t["name"]).is_drum]
    assert drums and all(t["channel"] == 10 for t in drums)
    bass = next(t for t in r["tracks"] if s.track(t["name"]).role == "bass")
    assert bass["program"] == GM_PROGRAM_BY_ROLE["bass"] and bass["channel"] != 10
    assert cc7_for_db(0) == 90 and cc7_for_db(6) == 127 and cc7_for_db(-6) < 90


def test_logic_midi_keeps_silent_tracks_in_order(tmp_path):
    s = Song("Quiet", bpm=120, key="A minor")
    kick = s.add_track("Kick", "kick")
    s.add_track("Pad", "pad")                       # never plays
    s.pattern("four", kick, "x...x...x...x...")
    s.add_section("a", 4, kind="drop", parts={kick: "four"})
    r = export_logic_midi(s, tmp_path / "q.mid")
    assert [t["name"] for t in r["tracks"]] == ["Kick", "Pad"] and r["tracks"][1]["notes"] == 0


def test_display_numbers_and_abbreviations():
    inf = float("inf")
    assert [disp_number(x) for x in ("-6.0 dB", "3.56 kHz", "120 ms", "1.2 s", "51.0ms", "2.1:1", "-oo dB", "60 %", "7040.0", "Off")] == \
        [-6.0, 3560.0, 120.0, 1200.0, 51.0, 2.1, -inf, 60.0, 7040.0, None]
    assert B.abbrev_matches("Thrs", "Threshold") and B.abbrev_matches("Rel", "Release") and B.abbrev_matches("AutRel", "Auto Release")
    assert B.abbrev_matches("MakeUp", "Make Up") and B.abbrev_matches("CirTyp", "Circuit Type") and B.abbrev_matches("Ratio", "Ratio")
    assert not B.abbrev_matches("Rel", "Ratio") and not B.abbrev_matches("Attack", "Threshold")
    F = B.LogicBridge.fader_for_db
    assert F(0.0) == 4251 and F(-90) == -8192 and F(-12.0) == -1014
    assert F(-1.0) > F(-2.0)


def test_surface_state_reads_lcd_and_clock():
    st = SurfaceState()
    text = "Kick   Hats   PulsBs ThFiLe St Out Master               "
    for i, ch in enumerate(text):
        st.lcd[i] = ch
    assert st.cells(0)[:4] == ["Kick", "Hats", "PulsBs", "ThFiLe"]
    for i, ch in enumerate(reversed(" 10 2 2 88")):
        st.time_digits[i] = ch
    assert st.position() == (10, 2, 2, 88)
    assert abs(st.beats() - ((9 * 4) + 1 + 0.25 + 88 / 240 * 0.25)) < 1e-9


def test_push_song_into_fake_logic(tmp_path):
    s = Song("Fake Push", bpm=124, key="A minor")
    s.base_dir = tmp_path
    kick = s.add_track("Kick", "kick", volume_db=-4)
    hat = s.add_track("Hats", "hat", volume_db=-14, pan=0.25, sends={"A": -16})
    bass = s.add_track("Bass", "bass", volume_db=-8, sidechain=True, effects=[{"device": "Channel EQ"}])
    chords = s.add_track("Chords", "chords", instrument="Retro Synth", volume_db=-12, sends={"A": -10},
                         effects=[{"device": "Compressor", "params": {"Threshold": -20, "Ratio": 3, "Nope": 1}}])
    pad = s.add_track("Pad", "pad", instrument=["Deep House Pad", "Alchemy"])
    s.add_return("A", [{"device": "ChromaVerb", "params": {"Decay": 2000}}])
    s.master_effects = [{"device": "Limiter"}]
    s.pattern("four", kick, "x...x...x...x...")
    s.pattern("off", hat, "..x...x...x...x.")
    s.pattern("line", bass, "1.3 A0 0.4; 2.3 A0 0.4")
    s.pattern("stab", chords, "1.3 [A2 C3 E3] 0.4")
    s.pattern("hold", pad, "1.1 [A2 E3] 4")
    s.add_section("intro", 8, kind="intro", parts={kick: "four", hat: "off"}, automation={hat: {"volume": [0.3, 1.0]}})
    s.add_section("drop", 8, kind="drop", parts={kick: "four", hat: "off", bass: "line", chords: "stab", pad: "hold"})
    fake = FakeLogicBridge()
    rep = C.push_song(s, fake, replace=True)
    assert fake.opened and fake.opened[0].name == "Fake Push.mid" and fake.saved[0].name == "Fake Push.logicx"
    assert fake.tracks() == ["Kick", "Hats", "Bass", "Chords", "Pad"]            # Logic's patch names replaced by ours
    k, h, b, c, p = fake._strips[:5]
    assert (k.volume, h.volume, b.volume, c.volume) == (-4.0, -14.0, -8.0, -12.0) and h.pan == 16
    assert b.inserts == ["Channel EQ", "Compressor"] and b.side_chains == {0: "Kick"}      # the `sidechain: true` shorthand
    assert c.instrument == "Retro Synth" and c.inserts == ["Compressor"] and c.params[1]["Threshold"] == "-20"
    assert p.instrument == "Alchemy" and fake.patches == [(4, "Deep House Pad")]     # a Library search, first match
    assert h.sends == {1: -16} and c.sends == {1: -10}
    aux = next(x for x in fake._strips if x.kind == "aux")
    assert aux.name == "Aux 1" and aux.inserts == ["ChromaVerb"]
    out = next(x for x in fake._strips if x.kind == "output")
    assert out.inserts == ["Limiter"]
    text = rep.text()
    assert "Pushed to Logic Pro" in text and "Compressor <- Kick" in text and "sends: A (Bus 1)" in text
    assert any("no parameter 'Nope'" in w for w in rep.warnings) and any("automation" in w for w in rep.warnings)
    assert (tmp_path / "logic" / ".logic-push.json").exists()
    # a second push closes our earlier project first
    rep2 = C.push_song(s, fake, replace=True)
    assert "Fake Push" in fake.closed and rep2.clips == rep.clips


def test_capture_is_a_bounce(tmp_path):
    s = Song("Bounce Me", bpm=120, key="A minor")
    s.base_dir = tmp_path
    kick = s.add_track("Kick", "kick")
    s.pattern("four", kick, "x...x...x...x...")
    s.add_section("a", 8, kind="drop", parts={kick: "four"})
    fake = FakeLogicBridge()
    C.push_song(s, fake)
    r = C.capture_logic(s, fake, tmp_path / "live.wav", bars=(3, 6))
    assert r["path"].exists() and r["bars"] == (3, 6) and r["seconds"] > 0
    with pytest.raises(B.LogicError):
        C.capture_logic(s, fake, tmp_path / "x.wav", tracks=["Nobody"])
