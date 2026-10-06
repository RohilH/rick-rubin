import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from fake_live import FakeLiveServer, Param, _vol_fmt  # noqa: E402
from handlers import _num, norm_to_param, set_param_display  # noqa: E402

from ableton_use import generate  # noqa: E402
from ableton_use.live import BridgeError, LiveBridge, push_song  # noqa: E402


def test_param_helpers():
    assert _num("-6.0 dB") == -6.0 and _num("-inf dB") == float("-inf") and _num("4.00 : 1") == 4.0
    p = Param("Vol", 0.0, 1.0, 0.85, _vol_fmt)
    assert set_param_display(p, -12.0) == "-12.0 dB"
    f = Param("Frequency", 20.0, 20000.0, 0, str)
    assert abs(norm_to_param(f, 0.5) - (20 * 1000 ** 0.5)) < 1e-6


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
