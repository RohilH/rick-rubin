import sys
from pathlib import Path

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
