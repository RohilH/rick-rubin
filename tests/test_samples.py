import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent))

from fake_live import FakeLiveServer  # noqa: E402

from ableton_use import Project, Song  # noqa: E402
from fixture_songs import generate  # noqa: E402
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
    p = Project.create(tmp_path / "trk", generate("classic", template="radio", key="F minor", bpm=BPM, seed=3))
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
    names = [Path(c.file_path).name for c in clips]
    assert names[:2] == ["top.wav", "top.0+16.wav"]
    # the drop's filter sweep is rendered into the audio (Live drops envelopes on arrangement audio clips):
    # one cut per pass, no Auto Filter, and the first pass is duller than the second
    assert names[2].startswith("top.0+32.") and names[3].startswith("top.0+32.") and names[2] != names[3]
    assert not any(d.name == "Auto Filter" for d in top.devices) and not any(c.envs for c in clips)
    _, dull = read_audio(clips[2].file_path)
    _, bright = read_audio(clips[3].file_path)
    _, orig = read_audio(clips[0].file_path)
    def hf(v):                                                    # share of energy above 4 kHz
        S = np.abs(np.fft.rfft(v[:, 0])) ** 2
        return float(S[int(4000 * len(v) / SR):].sum() / S.sum())
    assert len(dull) == len(orig) and hf(dull) < 0.5 * hf(bright) and hf(bright) < hf(orig)

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
    p = Project.create(tmp_path / "trk", generate(template="radio", bpm=BPM, seed=1))
    src = _saw(tmp_path / "a1.wav", 110.0, 0.6)
    assert main(["sample", str(p.root), str(src), "--name", "stab", "--oneshot", "--melodic"]) == 0
    out = capsys.readouterr().out
    assert "samples/stab.wav: one-shot, root A1 (45.0" in out and 'sample="samples/stab.wav", sample_root=45.00)' in out
    loop = _clicks(tmp_path / "l.wav", BPM, 2)
    assert main(["sample", str(p.root), str(loop), "--name", "lp", "--loop", "--src-bpm", "130"]) == 0
    out = capsys.readouterr().out
    assert "samples/lp.wav: 2-bar loop (from 130 BPM)" in out and 'audio="samples/lp.wav", bars=2)' in out
    with pytest.raises(SystemExit):
        main(["sample", str(p.root), str(loop), "--name", "lp", "--loop"])


# ---------------------------------------------------------------- transcription (no model needed)
def test_words_snap_to_sound_and_grid(tmp_path):
    from ableton_use.transcribe import HOP_S, _envelope, load_words, sidecar, snap_to_audio, to_grid, words_text
    # three bursts of sound at 120 BPM: beat 1 (0.5 s), beat 2.5 (1.25 s) and beat 4 (2.0 s), 0.2 s each
    x = np.zeros((3 * SR, 1), np.float32)
    for t in (0.5, 1.25, 2.0):
        i = int(t * SR)
        x[i:i + int(0.2 * SR), 0] = 0.5 * np.sin(np.arange(int(0.2 * SR)) * 0.05)
    env = _envelope(x, SR)
    # a model that starts the first word in silence, lets the second run across a gap, and starts the third late
    raw = [("gonna", 0.0, 0.7, 0.9), ("take", 0.7, 1.95, 0.4), ("time", 2.05, 2.6, 0.99)]
    snapped = snap_to_audio(raw, env)
    assert [round(s, 2) for _, s, _, _ in snapped] == [0.5, 1.25, 2.0]
    assert all(abs((e - s) - 0.2) < 4 * HOP_S for _, s, e, _ in snapped)
    words = to_grid(snapped, 120.0)
    assert [w.pos for w in words] == ["1.2.1", "1.3.3", "2.1.1"] and all(abs(w.off_ms) < 6 for w in words)
    assert words_text(words) == ["  words bar 1: 2.1 gonna; 3.3 take?", "  words bar 2: 1.1 time"]
    assert load_words(tmp_path / "none.wav") is None and sidecar("a/b.wav").name == "b.words.json"


# ---------------------------------------------------------------- stereo image
def test_stereo_stats_and_checks(tmp_path):
    from ableton_use.analysis import stereo_issues, stereo_report, stereo_stats
    rng = np.random.default_rng(0)
    n = 3 * SR
    a, b = rng.standard_normal(n) * 0.1, rng.standard_normal(n) * 0.1
    mono = stereo_stats(np.stack([a, a], 1), SR, "mono")
    assert mono.correlation > 0.999 and mono.side_pct < 0.01 and abs(mono.mono_loss_lu) < 0.05 and abs(mono.balance_db) < 0.01
    wide = stereo_stats(np.stack([a, b], 1), SR, "wide")
    assert abs(wide.correlation) < 0.05 and 45 < wide.side_pct < 55 and 2.5 < wide.mono_loss_lu < 3.5
    flipped = stereo_stats(np.stack([a, -a], 1), SR, "flipped")
    assert flipped.correlation < -0.999 and flipped.side_pct > 99.9 and flipped.mono_loss_lu > 20
    left = stereo_stats(np.stack([a, a * 0.5], 1), SR, "left")
    assert 5.9 < left.balance_db < 6.1
    # wide highs over a centred low end is fine; a wide low end is flagged
    from scipy.signal import butter, sosfilt
    lo = sosfilt(butter(4, 120, fs=SR, output="sos"), a) * 4
    hi_l, hi_r = (sosfilt(butter(4, 3000, btype="high", fs=SR, output="sos"), v) for v in (a, b))
    good = stereo_stats(np.stack([lo + hi_l, lo + hi_r], 1), SR, "good")
    assert good.bands["low"][0] < 1 and good.bands["high"][0] > 40
    rules = lambda s: [i.message for i in stereo_issues([s])]  # noqa: E731
    assert not any("low end" in m for m in rules(good)) and any("low end" in m for m in rules(wide))
    assert any("out of phase" in m for m in rules(flipped)) and any("leans left" in m for m in rules(left))
    assert any("effectively mono" in m for m in rules(mono))
    write_wav24(tmp_path / "w.wav", SR, np.stack([lo + hi_l, lo + hi_r], 1))
    assert "| whole file | +" in stereo_report(tmp_path / "w.wav")


# ---------------------------------------------------------------- zoom
def test_zoom_on_bars_and_tracks(sampled, capsys):
    from ableton_use.analysis import measure, section_windows
    p, _ = sampled
    song = p.load()
    # windows: sections cut to the bar range, timed for a file that starts at bar 21
    wins = section_windows(song, (21, 28), file_start_bar=21)
    assert [w[0] for w in wins] == ["groove[21-24]", "breakdown[25-28]"]
    assert wins[0][3] == 0.0 and abs(wins[1][3] - 4 * BAR_S) < 1e-9 and abs(wins[1][4] - 8 * BAR_S) < 1e-9
    assert [w[0] for w in section_windows(song)] == [s.name for s in song.sections]
    # a solo of the kick is silent in the breakdown and present in the groove
    wav, m = p.measure_zoom((21, 28), ["Kick"])
    assert wav.name == "preview_Kick.wav" and [s.name for s in m.sections] == ["groove[21-24]", "breakdown[25-28]"]
    assert m.sections[0].lufs > -30 and m.sections[1].lufs == float("-inf") and not m.issues
    # zoomed score: only those tracks, sections and patterns
    text = pack(song, bars=(21, 28), tracks=["Kick", "Top"])
    assert "zoom: bars 21-28, tracks Kick Top" in text and "| **groove** | groove | 9-24 (16)" in text
    assert "### top" in text and "### kick" in text and "### bass" not in text and "**drop**" not in text and "- Bass" not in text
    assert main(["score", str(p.root), "--tracks", "Bass"]) == 0
    out = capsys.readouterr().out
    assert "tracks Bass" in out and "### bass" in out and "### hats" not in out
    assert "### hats" in p.score_path.read_text()          # score.md itself stays whole
    assert main(["eval", str(p.root), "--bars", "9-16", "--tracks", "Kick", "Bass"]) == 0
    assert "| groove[9-16] | groove |" in capsys.readouterr().out


# ---------------------------------------------------------------- Serum 2 presets
def test_serum_preset_sheet_and_catalog(tmp_path):
    cbor2 = pytest.importorskip("cbor2")
    zstandard = pytest.importorskip("zstandard")
    import json
    import struct
    from ableton_use import serum

    def write(path, name, tags, tree, desc=""):
        meta = json.dumps({"fileType": "SerumPreset", "presetName": name, "presetAuthor": "me", "presetDescription": desc,
                           "tags": tags + ["Preview"]}).encode()
        body = zstandard.ZstdCompressor().compress(cbor2.dumps(tree))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(serum.MAGIC + struct.pack("<Q", len(meta)) + meta + struct.pack("<II", len(body), 2) + body)

    tree = {
        "Oscillator0": {"WTOsc0": {"plainParams": {"kParamTablePos": 128.4}, "relativePathToWT": "S2 Tables/Default Shapes.wav"},
                        "SampleOsc0": {"plainParams": "default"}, "plainParams": {"kParamOctave": -2.0, "kParamUnison": 3.0}},
        "Oscillator1": {"WTOsc1": {"plainParams": "default"}, "plainParams": "default"},
        "Oscillator4": {"SubOsc4": {"plainParams": "default"}, "plainParams": {"kParamEnable": 1.0}},
        "VoiceFilter0": {"plainParams": {"kParamEnable": 1.0, "kParamFreq": 0.49, "kParamType": "LH12"}},
        "Env0": {"plainParams": {"kParamCurve1": 50.0, "kParamRelease": 0.8}}, "Env1": {"plainParams": {"kParamCurve1": 50.0}},
        "LFO0": {"curveData": {}, "pathData": {}, "plainParams": {"kParamRate": 10.66}},
        "FXRack0": {"FX": [{"FXReverb": {"plainParams": {"kParamType": "kHall", "kParamWet": 0.0}}, "type": 3}]},
        "Macro0": {"name": "FILTER", "plainParams": {"kParamValue": 50.0}},
        "ModSlot0": {"destModuleID": 0, "destModuleParamName": "kParamFreq", "destModuleTypeString": "VoiceFilter",
                     "plainParams": {"kParamAmount": 29.4}, "source": [25, 0]},
        "ModSlot1": {"destModuleID": 0, "destModuleParamName": "kParamFine", "destModuleTypeString": "Oscillator",
                     "plainParams": {"kParamAmount": -12.0}, "source": [3, 0]},
        "ModSlot2": {"plainParams": "default"},
        "Global0": {"plainParams": {"kParamMonoToggle": 1.0}},
    }
    write(tmp_path / "Bass" / "Reese.SerumPreset", "BS Reese", ["Wavetable", "Mono"], tree, "growly")
    write(tmp_path / "Pads" / "Warm.SerumPreset", "PD Warm Room", ["Wavetable", "Poly"], {}, "instant warmth")
    (tmp_path / "Pads" / "junk.SerumPreset").write_bytes(b"nope")

    assert [i.name for i in serum.catalog(tmp_path)] == ["BS Reese", "PD Warm Room"]
    assert [i.name for i in serum.catalog(tmp_path, search="warm pad")] == ["PD Warm Room"]
    assert [(i.name, i.folder, i.tags) for i in serum.catalog(tmp_path, tag="mono")] == [("BS Reese", "Bass", ["Wavetable", "Mono"])]
    assert serum.find("reese", tmp_path).name == "Reese.SerumPreset"
    with pytest.raises(FileNotFoundError):
        serum.find("supersaw", tmp_path)
    text = serum.sheet(serum.find("BS Reese", tmp_path))
    assert "# BS Reese — Serum 2 preset" in text and 'tags: Wavetable, Mono · "growly"' in text
    assert "- OSC A ON  wavetable 'Default Shapes' (TablePos 128); Octave -2, Unison 3" in text
    assert "OSC B" not in text and "- SUB ON" in text
    assert "- FILTER 1: Enable 1, Freq 0.49, Type LH12" in text
    assert "- ENV 1: Release 0.8" in text and "ENV 2" not in text and "- LFO 1: Rate 10.7" in text
    assert "- Reverb: Type Hall, Wet 0" in text
    assert "- Macro 1 'FILTER' at 50% → VoiceFilter0.Freq +29" in text
    assert "- source #3 → Oscillator0.Fine -12" in text and text.count("source #") == 1
    assert "- MonoToggle 1" in text
    assert main(["serum", "list", "--root", str(tmp_path), "--folder", "Bass"]) == 0


# ---------------------------------------------------------------- groove
def test_groove_moves_and_accents_notes():
    s = generate("classic", template="radio", seed=1, bpm=120.0)
    hats, clap, kick = s.track("Hats"), s.track("Clap"), s.track("Kick")
    base = {c.track: c for c in s.flatten()[0] if c.section == "groove"}
    ms = lambda beats: beats * 60000.0 / s.bpm  # noqa: E731

    clap.groove = {"timing": [0, 0, 0, 0, 12, 0, 0, 0, 0, 0, 0, 0, 12, 0, 0, 0]}
    kick.groove = {"timing": [-10] + [0] * 15, "accent": [0] * 4 + [-30] + [0] * 11}
    hats.groove = {"swing": 60, "accent": [5, -20, 0, -10] * 4, "gate": 0.5, "humanize": {"ms": 3, "vel": 4, "seed": 2}}
    assert not s.validate()
    new = {c.track: c for c in s.flatten()[0] if c.section == "groove"}
    # claps (beats 2 and 4) sit 12 ms late, everything else on that track untouched
    d = [ms(n.start - o.start) for n, o in zip(new["Clap"].notes, base["Clap"].notes) if o.start % 4 in (1.0, 3.0)]
    assert d and all(abs(x - 12) < 1e-6 for x in d)
    # the kick's downbeat is pushed 10 ms early — except the clip's very first hit, which cannot move before the clip
    k0, k1 = sorted(new["Kick"].notes, key=lambda n: n.start)[0], [n for n in new["Kick"].notes if abs(n.start - (4 - 10 * s.bpm / 60000)) < 1e-6]
    assert k0.start == 0.0 and len(k1) == 1
    assert {n.vel for n in new["Kick"].notes if abs(n.start % 4 - 1.0) < 1e-6} == {70}
    # hats: own swing (60% instead of the song's), shorter notes, velocities shaped, small random drift that is repeatable
    off16 = [n for n in new["Hats"].notes if 0.2 < n.start % 0.5 < 0.4]
    assert off16 and all(abs(ms(n.start % 0.5 - 0.30)) <= 3.001 for n in off16)
    assert all(abs(n.dur - 0.125) < 1e-9 for n in new["Hats"].notes)
    again = {c.track: c for c in s.flatten()[0] if c.section == "groove"}
    assert [(n.start, n.vel) for n in again["Hats"].notes] == [(n.start, n.vel) for n in new["Hats"].notes]
    assert len({round(ms(n.start % 0.5 - 0.30), 3) for n in off16}) > 3
    # round trip, score, validation
    s2 = Song.from_json(s.to_json())
    assert s2.track("Hats").groove == hats.groove and "groove" not in s2.to_json()["tracks"]["Bass"]
    text = pack(s)
    assert "groove timing ms · · · · +12" in text and "groove swing 60%, accent +5 -20 · -10" in text and "humanize ±3 ms ±4 vel" in text
    clap.groove = {"template": "laid_back"}
    kick.groove = {"timing": [1, 2, 3]}
    errs = s.validate()
    assert any("unknown groove keys ['template']" in e for e in errs) and any("needs 16 values" in e for e in errs)


def test_instrument_params_reach_simpler(sampled):
    p, _ = sampled
    p.edit([{"op": "track", "name": "Bass", "set": {"instrument_params": {"Volume": -3, "Nope": 1}}}])
    song = p.load()
    srv = FakeLiveServer()
    with LiveBridge(port=srv.port) as b:
        rep = push_song(song, b)
    simpler = {t.name: t for t in srv.song.tracks}["Bass"].devices[0]
    assert {q.name: q.str_for_value(q.value) for q in simpler.parameters}["Volume"] == "-3.0 dB"
    assert len({t.name: t for t in srv.song.tracks}["Bass"].devices) == 2          # Simpler + sidechain compressor, no second Simpler
    assert rep.tracks["Bass"]["instrument_params"] == "Volume -3.0 dB" and any("no parameter 'Nope'" in w for w in rep.warnings)


# ---------------------------------------------------------------- writing a song in Python
SONG_PY = '''
from ableton_use import Song

song = Song("Hand Made", bpm=126, key="A minor", swing=56)
kick = song.add_track("Kick", "kick", volume_db=-6)
hats = song.add_track("Hats", "hat", volume_db=-16, groove={"swing": 58, "accent": [6, -20, 0, -12] * 4})
bass = song.add_track("Bass", "bass", instrument="Operator", sidechain=True)
keys = song.add_track("Keys", "chords", instrument=["Electric"], volume_db=-12)

four = song.pattern("four", kick, "x...x...x...x...")
gap = four.variant("four_gap", bars={1: "x...x...x......."})
tick = song.pattern("tick", hats, "gxogxogx" * 2)
line = song.pattern("line", bass, ["1.3 A0 0.4; 2.3 A0 0.4 v110; 3.3 A0 0.4; 4.4 G0 0.2",
                                   "1.3 F0 0.4; 2.3 F0 0.4 v110; 3.3 G0 0.4; @3.5 G1 0.2 v80"])
line8 = line.variant("line8", repeat=2, bars={4: "1.3 E0 0.4; 3.1 [E0] 1 v90"}, add={1: "1.1 A1 0.1 v60"})
stab = song.pattern("stab", keys, {1: "1.1 [A2 C3 E3 G3] 0.25 v90; 2.4 A2+C3+E3+G3 0.5", 2: "2.3 [F2 A2 C3 E3] 1.5"})
stab_hi = stab.variant("stab_hi", transpose=12, drop=lambda n: n.start >= 4)

intro = song.add_section("intro", 8, energy=3, parts={kick: four, hats: tick.at(5)}, fills={kick: gap})
drop = song.add_section("drop", 16, kind="drop", energy=9, parts={kick: four, hats: tick, bass: line, keys: stab},
                        fills={kick: gap.every(8)}, automation={keys: {"filter": [0.4, 1.0]}})
drop2 = drop.variant("drop2", energy=10, add={bass: line8, keys: stab_hi.at(9, 16)}, without=[hats], fills={hats: tick})
outro = intro.variant("outro", bars=4, kind="outro", without=kick)
song.arrange(intro, drop, intro, drop2, outro)
'''


def test_song_written_in_python(tmp_path, capsys):
    from ableton_use.compose import bar_events
    assert main(["init", str(tmp_path / "trk"), "--title", "Hand Made", "--bpm", "126", "--key", "A minor"]) == 0
    p = Project(tmp_path / "trk")
    assert p.source_path.exists() and p.load().tracks == [] and p.tempo() == 126       # the skeleton builds: an empty song
    p.source_path.write_text(SONG_PY)
    import os
    os.utime(p.source_path, (p.song_path.stat().st_mtime + 2,) * 2)
    song = p.load()                                                                     # rebuilt because song.py is newer
    assert [s.name for s in song.sections] == ["intro", "drop", "intro (2)", "drop2", "outro"] and song.total_bars == 52
    pat = song.patterns
    assert [n.pitch for n in pat["four"].notes] == [36] * 4 and len(pat["four_gap"].notes) == 3
    assert pat["tick"].notes[0].pitch == 42 and pat["tick"].bars == 1
    line = pat["line"]
    assert line.bars == 2 and (line.notes[0].pitch, line.notes[0].start, line.notes[1].vel) == (33, 0.5, 110)
    assert any(abs(n.start - 7.5) < 1e-9 and n.pitch == 43 for n in line.notes)        # "@3.5" in bar 2
    l8 = pat["line8"]
    assert l8.bars == 4 and len(line.notes) == 8                                        # the original is untouched
    assert [n.pitch for n in l8.notes if n.start >= 12] == [28, 28] and any(n.pitch == 45 and n.start == 0 for n in l8.notes)
    assert [n for n in l8.notes if 4 <= n.start < 12] != []
    assert len([n for n in pat["stab"].notes if n.start < 4]) == 8 and min(n.pitch for n in pat["stab_hi"].notes) == 57 + 12
    assert all(n.start < 4 for n in pat["stab_hi"].notes)
    d2 = song.section("drop2")
    assert d2.parts["Bass"].pattern == "line8" and (d2.parts["Keys"].start, d2.parts["Keys"].end) == (8, 16)
    assert "Hats" not in d2.parts and d2.fills["Hats"].pattern == "tick" and d2.fills["Kick"].every == 8 and d2.energy == 10
    assert song.section("drop").parts["Bass"].pattern == "line" and "Hats" in song.section("drop").parts
    assert "Kick" not in song.section("outro").parts and "Hats" not in song.section("outro").parts   # hats entered at bar 5 of 8; the outro is 4 bars
    assert song.section("intro").parts["Hats"].start == 4 and song.track("Bass").instrument == ["Operator"]
    assert "### line8" in p.score_path.read_text() and not [i for i in lint(song) if i.severity == "error"]
    # the json op path is closed for python projects; a broken song.py says why
    with pytest.raises(ValueError, match="edit that file"):
        p.edit([{"op": "set", "field": "bpm", "value": 120}])
    p.source_path.write_text(SONG_PY.replace("hats: tick.at(5)}", "hats: tick.at(5), 'Nobody': four}"))
    os.utime(p.source_path, (p.song_path.stat().st_mtime + 4,) * 2)
    with pytest.raises(ValueError, match="unknown track 'Nobody'"):
        p.load()
    for bad, msg in (("9.1 A0 1", "outside the bar"), ("1.1 H9 1", "cannot read event"), ("1.1 A0", "cannot read event")):
        with pytest.raises(ValueError, match=msg):
            bar_events(bad)
