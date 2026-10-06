import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent))

from fake_live import FakeLiveServer, Param, _vol_fmt  # noqa: E402
from handlers import _hz, _num, filter_mapper, norm_to_param, set_param_display  # noqa: E402

from ableton_use import Song  # noqa: E402
from fixture_songs import generate  # noqa: E402
from ableton_use.score import pack  # noqa: E402
from ableton_use.live import BridgeError, LiveBridge, push_song  # noqa: E402


def test_param_helpers():
    assert _num("-6.0 dB") == -6.0 and _num("-inf dB") == float("-inf") and _num("4.00 : 1") == 4.0
    p = Param("Vol", 0.0, 1.0, 0.85, _vol_fmt)
    assert set_param_display(p, -12.0) == "-12.0 dB"
    f = Param("Frequency", 20.0, 20000.0, 0, str)
    assert abs(norm_to_param(f, 0.5) - (20 * 1000 ** 0.5)) < 1e-6
    # cutoff automation follows the preview's 60 Hz..18 kHz curve whatever the raw scale is
    assert _hz("632 Hz") == 632.0 and _hz("3.56 kHz") == 3560.0 and _hz("50 %") is None
    af = Param("Frequency", 0.0, 1.0, 1.0, lambda v: "%.3f kHz" % (0.02 * 1000 ** v) if v > 0.57 else "%.1f Hz" % (20 * 1000 ** v))
    m = filter_mapper(af)
    for v in (0.0, 0.3, 0.5, 1.0):
        assert abs(20 * 1000 ** m(v) / (60 * 300 ** v) - 1) < 0.02
    assert filter_mapper(Param("Cutoff", 0.0, 127.0, 0, str))(0.5) == 63.5


def test_plugin_instruments_load_by_name():
    srv = FakeLiveServer()
    s = generate("classic", template="radio", seed=1)
    s.track("Lead").instrument = ["Serum 2"]
    with LiveBridge(port=srv.port) as b:
        rep = push_song(s, b)
    assert rep.tracks["Lead"]["instrument"] == "Serum 2" and not rep.warnings


def test_push_song_end_to_end():
    srv = FakeLiveServer()
    s = generate("classic", template="club", seed=1)
    with LiveBridge(port=srv.port) as b:
        rep = push_song(s, b)
    song = srv.song
    assert song.tempo == s.bpm
    names = [t.name for t in song.tracks]
    assert names[1:] == [t.name for t in s.tracks]
    clips, markers = s.flatten()
    assert rep.clips == len(clips) and not [w for w in rep.warnings if "clip" in w]
    assert sum(len(c.notes) for t in song.tracks for c in t.arrangement_clips) == rep.notes
    assert [c.name for c in song.cue_points] == [m.name for m in markers]
    bass = song.tracks[names.index("Bass")]
    assert bass.mixer_device.volume.str_for_value(bass.mixer_device.volume.value) == "-6.0 dB"
    comp = [d for d in bass.devices if d.name == "Compressor"][0]
    assert comp.input_routing_type["display_name"].endswith("Kick")
    # filter automation became a clip envelope on an inserted Auto Filter
    riser = song.tracks[names.index("Riser")]
    assert any(d.name == "Auto Filter" for d in riser.devices)
    env = next(iter(riser.arrangement_clips[0].envs.values()))
    vals = [v for _, _, v in env.steps]
    assert vals[0] < vals[-1] and len(vals) == 32 * 4


def test_push_refuses_to_clobber_without_replace():
    srv = FakeLiveServer()
    s = generate("tech", template="radio", seed=1)
    with LiveBridge(port=srv.port) as b:
        push_song(s, b, load_instruments=False)
        with pytest.raises(BridgeError):
            push_song(s, b, load_instruments=False)
        push_song(s, b, replace=True, load_instruments=False)
    assert [t.name for t in srv.song.tracks].count("Kick") == 1


def test_unknown_command_errors():
    srv = FakeLiveServer()
    with LiveBridge(port=srv.port) as b:
        with pytest.raises(BridgeError, match="unknown command"):
            b.call("nope")


def test_display_units_and_set_param():
    from handlers import _disp, set_param
    inf = float("inf")
    assert [_disp(x) for x in ("-28.0 dB", "1.00 s", "120 ms", "3.56 kHz", "inf : 1", "4.00 : 1", "1 : 1.15", "-inf dB", "0.71")] == \
        [-28.0, 1000.0, 120.0, 3560.0, inf, 4.0, 1.15, -inf, 0.71]
    srv = FakeLiveServer()
    srv.song.tracks[0].insert_device("Compressor")
    P = {p.name: p for p in srv.song.tracks[0].devices[0].parameters}
    assert set_param(P["Release"], 1500) == "1.50 s" and set_param(P["Attack"], 0.5) == "0.50 ms"
    assert set_param(P["Ratio"], inf) == "inf : 1" and set_param(P["Ratio"], "8 : 1") == "8.00 : 1"
    assert set_param(P["Threshold"], -inf) == "-inf dB" and set_param(P["S/C EQ Freq"], 2000) == "2.00 kHz"
    assert set_param(P["Model"], "peak") == "Peak" and set_param(P["LookAhead"], 10) == "10 ms"
    assert set_param(P["Makeup"], True) == "On" and set_param(P["Makeup"], "off") == "Off"
    with pytest.raises(ValueError, match="no option"):
        set_param(P["Model"], "Opto")


def test_push_effects_chain_and_sidechain():
    srv = FakeLiveServer()
    s = generate("classic", template="radio", seed=1)
    s.track("Bass").effects = [{"device": "Compressor", "sidechain": "Kick", "sidechain_tap": "Pre FX",
                                "params": {"Threshold": -35, "Ratio": 8, "Attack": 0.1, "Release": 90, "Knee": 0,
                                           "Model": "Peak", "LookAhead": "1 ms", "Nope": 1}}]
    s.track("Kick").effects = [{"device": "Compressor", "params": {"Threshold": -12, "Ratio": 2, "Makeup": True}}]
    s.track("Pad").sidechain = True          # shorthand still works next to explicit chains
    assert s.track("Bass").ducked and not s.track("Kick").ducked
    assert "fx Compressor keyed from Kick: Threshold -35, Ratio 8" in pack(s)
    s2 = Song.from_json(s.to_json())
    assert s2.track("Bass").effects == s.track("Bass").effects and "effects" not in s2.to_json()["tracks"]["Clap"]
    with LiveBridge(port=srv.port) as b:
        rep = push_song(s, b)
    live = {t.name: t for t in srv.song.tracks}
    comps = [d for d in live["Bass"].devices if d.name == "Compressor"]
    assert len(comps) == 1                   # the explicit compressor replaces the shorthand one
    shown = {p.name: p.str_for_value(p.value) for p in comps[0].parameters}
    assert shown["Threshold"] == "-35.0 dB" and shown["Ratio"] == "8.00 : 1" and shown["Attack"] == "0.10 ms"
    assert shown["Release"] == "90.00 ms" and shown["Knee"] == "0.0 dB" and shown["Model"] == "Peak"
    assert shown["LookAhead"] == "1 ms" and shown["S/C On"] == "On"
    assert comps[0].input_routing_type["display_name"] == "Kick" and comps[0].input_routing_channel["display_name"] == "Pre FX"
    kick = [d for d in live["Kick"].devices if d.name == "Compressor"][0]
    assert kick.input_routing_type is None and {p.name: p.str_for_value(p.value) for p in kick.parameters}["Makeup"] == "On"
    pad = [d for d in live["Pad"].devices if d.name == "Compressor"][0]
    assert pad.input_routing_type["display_name"] == "Kick"
    assert [w for w in rep.warnings] == [w for w in rep.warnings if "no parameter 'Nope'" in w] and len(rep.warnings) == 1
    assert "fx: Compressor <- Kick (Threshold -35.0 dB" in rep.text()
    # a sidechain source has to be a track of the song
    s.track("Pad").effects = [{"device": "Compressor", "sidechain": "Nobody"}]
    assert any("sidechain source 'Nobody'" in e for e in s.validate())


def test_midi_effects_real_in_live_emulated_offline():
    from ableton_use.analysis import lint
    from ableton_use.midifx import apply, unemulated
    from ableton_use.model import Note
    s = Song("Chordy", bpm=120, key="A minor")
    kick = s.add_track("Kick", "kick")
    keys = s.add_track("Keys", "chords", instrument="Operator", midi_effects=[
        {"device": "Pitch", "params": {"Pitch": 12}},
        {"device": "Chord", "params": {"Shift1": 3, "Shift2": 7, "Shift3": 10, "Velocity3": 50, "Strum": 20}}])
    four = s.pattern("four", kick, "x...x...x...x...")
    one = s.pattern("one_finger", keys, ["1.1 A2 1 v100; 3.1 F2 1 v80"])
    s.add_section("a", 4, kind="drop", parts={kick: four, keys: one})
    assert not s.validate()
    written = [c for c in s.flatten()[0] if c.track == "Keys"][0].notes
    heard = [c for c in s.flatten(sounding=True)[0] if c.track == "Keys"][0].notes
    assert len(written) == 2 * 4 and len(heard) == 4 * len(written)                 # one finger in, four voices out
    first = sorted(heard, key=lambda n: (n.start, n.pitch))[:4]
    assert [n.pitch for n in first] == [57 + 12, 57 + 15, 57 + 19, 57 + 22][:1] + [n.pitch for n in first][1:]
    chord0 = sorted((n for n in heard if n.start < 0.2), key=lambda n: n.pitch)
    assert [n.pitch for n in chord0] == [69, 72, 76, 79] and [n.vel for n in chord0] == [100, 100, 100, 50]
    assert [round(n.start * 60000 / 120) for n in chord0] == [0, 20, 40, 60]          # strummed upward, 20 ms apart
    assert "midi fx Chord: Shift1 3, Shift2 7" in pack(s) and not [i for i in lint(s) if i.rule == "H15-midi-fx"]
    # effects the offline side cannot follow are said out loud
    assert unemulated([{"device": "Arpeggiator"}, {"device": "Chord", "params": {"Chance2": 50}}]) == \
        ["Arpeggiator is not emulated offline", "Chord Chance2 below 100% is random in Live"]
    s.track("Kick").midi_effects = [{"device": "Arpeggiator", "params": {}}]
    assert any(i.rule == "H15-midi-fx" and i.where == "Kick" for i in lint(s))
    s.track("Kick").midi_effects = []
    assert [n.dur for n in apply([Note(60, 0, 2, 90)], [{"device": "Note Length", "params": {"Time Length": 250, "Gate": 50}}], 120)] == [0.25]
    assert [n.vel for n in apply([Note(60, 0, 1, 90), Note(62, 1, 1, 20)], [{"device": "Velocity", "params": {"Out Low": 40, "Out Hi": 80}}], 120)] == [80, 40]

    srv = FakeLiveServer()
    with LiveBridge(port=srv.port) as b:
        rep = push_song(s, b)
    live = {t.name: t for t in srv.song.tracks}
    assert [d.name for d in live["Keys"].devices] == ["Pitch", "Chord", "Operator"]        # in front of the instrument, in order
    chord = live["Keys"].devices[1]
    shown = {q.name: q.str_for_value(q.value) for q in chord.parameters}
    assert (shown["Shift1"], shown["Shift2"], shown["Shift3"], shown["Velocity3"], shown["Strum"]) == ("+3 st", "+7 st", "+10 st", "50 %", "20.00 ms")
    assert sum(len(c.notes) for c in live["Keys"].arrangement_clips) == len(written)        # Live gets the written notes; the device adds the rest
    assert "midi fx: Chord (Shift1 +3 st" in rep.text() and not rep.warnings


def test_returns_sends_and_master_chain(tmp_path):
    from ableton_use.analysis import lint, stereo_stats
    from ableton_use.render.preview import render_preview
    from ableton_use.samples import read_audio
    s = Song("Space", bpm=120, key="A minor")
    kick = s.add_track("Kick", "kick", volume_db=-6)
    clap = s.add_track("Clap", "clap", volume_db=-10, sends={"A": -12, "B": -18})
    s.add_return("A", [{"device": "Reverb", "params": {"Decay Time": 1500, "Dry/Wet": 100}}])
    s.add_return("b", [{"device": "Delay", "params": {"Feedback": 40, "L 16th": 3, "R 16th": 4}}])
    s.master_effects = [{"device": "Limiter", "params": {}}]
    s.pattern("four", kick, "x...x...x...x...")
    s.pattern("two", clap, "....x...........")
    s.add_section("a", 4, kind="drop", parts={"Kick": "four", "Clap": "two"})
    assert not s.validate() and sorted(s.returns) == ["A", "B"]
    s2 = Song.from_json(s.to_json())
    assert s2.returns == s.returns and s2.track("Clap").sends == {"A": -12.0, "B": -18.0} and s2.master_effects == s.master_effects
    text = pack(s)
    assert "sends A -12 dB, B -18 dB" in text and "- return A: Reverb (Decay Time 1500" in text and "- master: Limiter" in text
    # offline: the clap now has a tail and some width; without sends it has neither
    wet = render_preview(s, tmp_path / "wet.wav")
    s.track("Clap").sends = {}
    dry = render_preview(s, tmp_path / "dry.wav")
    s.track("Clap").sends = {"A": -12, "B": -18}
    _, w = read_audio(wet.path)
    _, d = read_audio(dry.path)
    assert stereo_stats(w, 44100).side_pct > stereo_stats(d, 44100).side_pct + 0.01
    gap = slice(int(0.95 * 44100), int(0.99 * 44100))                  # just before the second kick: only tails live here
    assert np.abs(w[gap]).mean() > 3 * np.abs(d[gap]).mean()
    assert any(i.rule == "H16-returns" for i in lint(Song.from_json({**s.to_json(), "returns": {"A": [{"device": "Saturator"}], "B": s.returns["B"]}})))

    srv = FakeLiveServer()
    with LiveBridge(port=srv.port) as b:
        rep = push_song(s, b)
    live = {t.name: t for t in srv.song.tracks}
    ra, rb = srv.song.return_tracks
    assert [d.name for d in ra.devices] == ["Reverb"] and [d.name for d in rb.devices] == ["Delay"]
    assert {q.name: q.str_for_value(q.value) for q in ra.devices[0].parameters}["Decay Time"] == "1500 ms"
    sends = live["Clap"].mixer_device.sends
    assert [q.str_for_value(q.value) for q in sends] == ["-12.0 dB", "-18.0 dB"]
    assert [q.str_for_value(q.value) for q in live["Kick"].mixer_device.sends] == ["-inf dB", "-inf dB"]
    assert [d.name for d in srv.song.master_track.devices] == ["Limiter"]
    assert "sends: A -12.0 dB, B -18.0 dB" in rep.text() and "return A" in rep.text()
    assert [w_ for w_ in rep.warnings if "no parameter" not in w_] == []
    # a return that should hold something else replaces what the set came with
    s.returns["A"] = [{"device": "Delay", "params": {}}]
    srv2 = FakeLiveServer()
    with LiveBridge(port=srv2.port) as b:
        push_song(s, b)
    assert [d.name for d in srv2.song.return_tracks[0].devices] == ["Delay"]
    s.track("Kick").sends = {"C": -6}
    assert any("send C has no return" in e for e in s.validate())
