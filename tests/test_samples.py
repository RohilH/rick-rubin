import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent))

from fake_live import FakeLiveServer  # noqa: E402

from ableton_use import Project, generate  # noqa: E402
from ableton_use import edits  # noqa: E402
from ableton_use.analysis import lint  # noqa: E402
from ableton_use.cli import main  # noqa: E402
from ableton_use.live import LiveBridge, push_song  # noqa: E402
from ableton_use.render.preview import render_preview  # noqa: E402
from ableton_use.samples import SR, conform_loop, detect_pitch, import_sample, read_audio, write_wav24  # noqa: E402
from ableton_use.score import pack  # noqa: E402

needs_ffmpeg = pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg not installed")
BPM = 130.0
BAR_S = 4 * 60.0 / BPM


def _saw(path, hz, secs, amp=0.5):
    t = np.arange(int(secs * SR)) / SR
    write_wav24(path, SR, (amp * (2 * ((t * hz) % 1.0) - 1) * np.exp(-2 * t)).astype(np.float32))
    return path


def _clicks(path, bpm, bars):
    """A loop with a click on every beat."""
    n = int(round(bars * 4 * 60.0 / bpm * SR))
    x = np.zeros(n, dtype=np.float32)
    for b in range(bars * 4):
        i = int(b * 60.0 / bpm * SR)
        x[i:i + 200] = 0.8
    write_wav24(path, SR, x)
    return path


@pytest.fixture
def sampled(tmp_path):
    """A radio-template project at 130 BPM with a sampled kick + bass and an 8-bar
    audio loop that enters 4 bars into the groove."""
    p = Project.create(tmp_path / "trk", subgenre="classic", template="radio", key="F minor", bpm=BPM, seed=3)
    raw = tmp_path / "raw"
    raw.mkdir()
    kick = p.add_sample(_saw(raw / "kick.wav", 55.0, 0.3), "kick")
    bass = p.add_sample(_saw(raw / "bass.wav", 65.406, 0.5), "bass", melodic=True)        # C1 = MIDI 36
    top = p.add_sample(_clicks(raw / "top.wav", BPM, 8), "top", loop=True, src_bpm=BPM, bars=8)
    p.edit([
        {"op": "track", "name": "Kick", "set": {"sample": kick.rel}},
        {"op": "track", "name": "Bass", "set": {"sample": bass.rel, "sample_root": bass.root}},
        {"op": "track", "name": "Top", "set": {"role": "perc", "audio": True, "volume_db": -12}},
        {"op": "pattern", "name": "top", "track": "Top", "audio": top.rel, "bars": 8, "key": "F minor"},
        {"op": "part", "section": "groove", "track": "Top", "pattern": "top", "start": 4},
        {"op": "part", "section": "drop", "track": "Top", "pattern": "top"},
        {"op": "automation", "section": "drop", "track": "Top", "param": "filter", "points": [0.2, 1.0]},
    ])
    return p, bass


# ---------------------------------------------------------------- samples.py
def test_detect_pitch_on_synthetic_saw(tmp_path):
    assert abs(detect_pitch(_saw(tmp_path / "a1.wav", 110.0, 1.0)) - 45.0) < 0.1


def test_write_read_roundtrip_24bit(tmp_path):
    x = np.linspace(-0.9, 0.9, 1000, dtype=np.float32)
    write_wav24(tmp_path / "x.wav", SR, x)
    sr, y = read_audio(tmp_path / "x.wav")
    assert sr == SR and y.shape == (1000, 1) and np.abs(y[:, 0] - x).max() < 1e-4


def test_conform_loop_trims_and_aligns_without_ffmpeg(tmp_path):
    src = _clicks(tmp_path / "src.wav", BPM, 9)       # one bar too long
    assert conform_loop(src, tmp_path / "a.wav", BPM, BPM, bars=8) == 8
    sr, a = read_audio(tmp_path / "a.wav")
    assert len(a) == round(8 * BAR_S * SR)
    # align='end' keeps the tail: its last beat is the source's last beat
    conform_loop(src, tmp_path / "b.wav", BPM, BPM, bars=8, align="end")
    _, b = read_audio(tmp_path / "b.wav")
    _, s = read_audio(src)
    assert len(b) == len(a) and np.allclose(b[1000:-1000], s[-len(b):][1000:-1000], atol=1e-4)
    # end_at: that moment of the source becomes the end; shorter material is padded in front
    conform_loop(src, tmp_path / "e.wav", BPM, BPM, bars=8, align="end", end_at=2 * BAR_S)
    _, e = read_audio(tmp_path / "e.wav")
    n2 = round(2 * BAR_S * SR)
    assert len(e) == len(a) and not e[: len(e) - n2 - 10].any() and np.allclose(e[-n2 + 200:-200], s[200:n2 - 200][-len(e[-n2 + 200:-200]):], atol=1e-4)
    # nearest whole number of bars when bars is omitted
    assert conform_loop(src, tmp_path / "c.wav", BPM, BPM) == 9


@needs_ffmpeg
def test_conform_loop_stretches_to_exact_bars(tmp_path):
    src = _clicks(tmp_path / "src126.wav", 126.0, 4)
    assert conform_loop(src, tmp_path / "out.wav", 126.0, BPM) == 4
    sr, x = read_audio(tmp_path / "out.wav")
    assert sr == SR and abs(len(x) / sr - 4 * BAR_S) < 1 / SR
    # every click moved onto the 130 BPM grid (atempo alone leaves them ~20 ms early)
    m = np.abs(x[:, 0])
    for beat in range(1, 16):
        i = int(beat * 60.0 / BPM * SR)
        w = m[i - 3000:i + 3000]
        assert w.max() > 0.2 and abs(int(np.argmax(w > 0.5 * w.max())) - 3000) < 0.008 * SR, beat


def test_import_sample_needs_tempo_for_loops(tmp_path):
    with pytest.raises(ValueError, match="src_bpm"):
        import_sample(tmp_path, _clicks(tmp_path / "l.wav", BPM, 1), "l", loop=True)


# ---------------------------------------------------------------- model / score / lint
def test_flatten_audio_segments(sampled):
    p, _ = sampled
    song = p.load()
    clips, _ = song.flatten()
    groove = next(c for c in clips if c.track == "Top" and c.section == "groove")
    # groove is bars 9-24; the part starts 4 bars in and runs 12 bars = 1.5 passes of the 8-bar loop
    assert (groove.start, groove.length) == ((8 + 4) * 4, 12 * 4)
    assert groove.audio == "samples/top.wav" and groove.notes == []
    assert groove.segments == [(0, 32, 0), (32, 16, 0)]
    drop = next(c for c in clips if c.track == "Top" and c.section == "drop")
    assert drop.segments == [(0, 32, 0), (32, 32, 0)]


def test_validate_rejects_mixed_audio_and_midi(sampled):
    p, _ = sampled
    song = p.load()
    with pytest.raises(edits.EditError, match="audio pattern 'top' on MIDI track"):
        edits.apply(song, {"op": "part", "section": "drop", "track": "Hats", "pattern": "top"})
    song = p.load()
    with pytest.raises(edits.EditError, match="MIDI pattern 'hats' on audio track"):
        edits.apply(song, {"op": "part", "section": "drop", "track": "Top", "pattern": "hats"})
    song = p.load()
    with pytest.raises(edits.EditError, match="needs sample_root"):
        edits.apply(song, {"op": "track", "name": "Lead", "set": {"sample": "samples/bass.wav"}})
    song = p.load()
    with pytest.raises(edits.EditError, match="not found"):
        edits.apply(song, {"op": "track", "name": "Clap", "set": {"sample": "samples/nope.wav"}})


def test_score_shows_samples_and_loops(sampled):
    p, bass = sampled
    text = pack(p.load())
    assert "- Top (perc) -12 dB, pan +0.0, audio track" in text
    assert "Simpler 'samples/bass.wav' root C1 (%.2f)" % bass.root in text
    assert "Simpler 'samples/kick.wav' one-shot" in text
    assert "audio loop 'samples/top.wav', key F minor — repeats every 8 bars" in text


def test_lint_h14(sampled):
    p, _ = sampled
    song = p.load()
    msgs = [str(i) for i in lint(song)]
    assert any("H14-samples" in m and "groove" in m and "12 bars of the 8-bar loop" in m for m in msgs)
    assert not any("H4-key" in m and "top" in m for m in msgs)
    # relative major is fine, an unrelated key is not
    song.patterns["top"].key = "Ab major"
    assert not any(i.rule == "H4-key" and i.where == "top" for i in lint(song))
    song.patterns["top"].key = "A minor"
    assert any(i.rule == "H4-key" and i.where == "top" and i.severity == "warn" for i in lint(song))
    # notes far from the sample root
    song.track("Bass").sample_root = 84.0
    assert any(i.rule == "H14-samples" and i.where == "Bass" and i.severity == "warn" for i in lint(song))


# ---------------------------------------------------------------- preview
def test_preview_plays_samples(sampled, tmp_path):
    p, _ = sampled
    song = p.load()
    r = render_preview(song, tmp_path / "prev.wav", stems_dir=tmp_path / "stems")
    _, top = read_audio(r.stems["Top"])
    spb = 60.0 / BPM
    at = lambda bar: np.abs(top[int(bar * 4 * spb * SR): int((bar + 1) * 4 * spb * SR)]).max()  # noqa: E731
    assert at(8) == 0 and at(11) == 0          # groove bars 9-12: loop not in yet
    assert at(12) > 0.01 and at(23) > 0.01     # plays from bar 13 to the end of the groove
    assert at(24) == 0                         # breakdown
    _, kick = read_audio(r.stems["Kick"])
    _, bass = read_audio(r.stems["Bass"])
    assert np.abs(kick).max() > 0.05 and np.abs(bass).max() > 0.05
    # the sampled bass sounds at the written pitch: its first note, measured in the stem
    clips, _ = song.flatten()
    c = next(c for c in clips if c.track == "Bass")
    n = min(c.notes, key=lambda n: n.start)
    i = int((c.start + n.start) * spb * SR)
    seg = bass[i: i + int(n.dur * spb * SR), 0].astype(np.float64)
    ac = np.correlate(seg, seg, "full")[len(seg) - 1:]
    lo, hi = int(SR / 400), int(SR / 25)
    f0 = SR / (lo + int(np.argmax(ac[lo:hi])))
    assert abs(69 + 12 * np.log2(f0 / 440.0) - n.pitch) < 0.5


# ---------------------------------------------------------------- push
def test_push_samples_to_fake_live(sampled):
    p, bass_imp = sampled
    song = p.load()
    srv = FakeLiveServer()
    with LiveBridge(port=srv.port) as b:
        rep = push_song(song, b)
    live = {t.name: t for t in srv.song.tracks}
    assert not rep.warnings, rep.warnings

    top = live["Top"]
    assert top.is_audio and rep.tracks["Top"]["instrument"] == "audio track"
    clips = sorted(top.arrangement_clips, key=lambda c: c.start_time)
    # groove: bars 13-20 (full loop) + bars 21-24 (first half, trimmed); drop: 2 full passes
    assert [(c.start_time, round(c.length, 3)) for c in clips] == [(48, 32), (80, 16), (160, 32), (192, 32)]
    assert all(c.warping is False for c in clips)
    assert [Path(c.file_path).name for c in clips] == ["top.wav", "top.0+16.wav", "top.wav", "top.wav"]
    assert clips[0].name.startswith("groove")
    # filter automation on the audio clips of the drop, continuous across the two segments
    flt = next(d for d in top.devices if d.name == "Auto Filter")
    e1 = [v for _, _, v in clips[2].envs[id(flt.parameters[0])].steps]
    e2 = [v for _, _, v in clips[3].envs[id(flt.parameters[0])].steps]
    assert e1[0] < e1[-1] < e2[-1] and abs(e1[-1] - e2[0]) / e2[0] < 0.1

    kick = live["Kick"].devices[0]
    assert kick.name == "Simpler" and kick.sample_path.endswith("samples/kick.wav") and kick.playback_mode == 1
    assert {n[0] for c in live["Kick"].arrangement_clips for n in c.notes} == {60}

    bass = live["Bass"].devices[0]
    assert bass.sample_path.endswith("samples/bass.wav") and bass.playback_mode == 0 and bass.voices == 1
    params = {q.name: q.str_for_value(q.value) for q in bass.parameters}
    semis = round(60 - bass_imp.root)
    assert params["Transpose"] == "%d st" % semis
    assert params["Detune"] == "%d ct" % round((60 - bass_imp.root - semis) * 100)
    # melodic notes keep their written pitch
    want = sorted(n.pitch for c in song.flatten()[0] if c.track == "Bass" for n in c.notes)
    assert sorted(n[0] for c in live["Bass"].arrangement_clips for n in c.notes) == want
    # sidechain compressor sits after the Simpler
    assert [d.name for d in live["Bass"].devices][-1] == "Compressor"


# ---------------------------------------------------------------- cli
def test_cli_sample(tmp_path, capsys):
    p = Project.create(tmp_path / "trk", template="radio", bpm=BPM, seed=1)
    src = _saw(tmp_path / "a1.wav", 110.0, 0.6)
    assert main(["sample", str(p.root), str(src), "--name", "stab", "--oneshot", "--melodic"]) == 0
    out = capsys.readouterr().out
    assert "samples/stab.wav: one-shot, root A1 (45.0" in out and '"sample_root": 45.0' in out
    loop = _clicks(tmp_path / "l.wav", BPM, 2)
    assert main(["sample", str(p.root), str(loop), "--name", "lp", "--loop", "--src-bpm", "130"]) == 0
    out = capsys.readouterr().out
    assert "samples/lp.wav: 2-bar loop (from 130 BPM)" in out and '"audio": "samples/lp.wav"' in out
    with pytest.raises(SystemExit):
        main(["sample", str(p.root), str(loop), "--name", "lp", "--loop"])
