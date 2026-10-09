import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent))

from fake_live import FakeLiveServer  # noqa: E402

from rick_rubin import Project, Song  # noqa: E402
from fixture_songs import generate  # noqa: E402
from rick_rubin import edits  # noqa: E402
from rick_rubin.analysis import lint  # noqa: E402
from rick_rubin.cli import main  # noqa: E402
from rick_rubin.live import LiveBridge, push_song  # noqa: E402
from rick_rubin.render.preview import render_preview  # noqa: E402
from rick_rubin.samples import SR, conform_loop, detect_pitch, import_sample, read_audio, write_wav24  # noqa: E402
from rick_rubin.score import pack  # noqa: E402

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
def _sung(path, sylls, total_s=4.0):
    """A fake vocal: each syllable is 30 ms of quiet hiss (the consonant) then a tone (the vowel)."""
    rng = np.random.default_rng(0)
    x = np.zeros(int(total_s * SR), np.float32)
    for start, cons_s, vowel_s in sylls:
        i, c, v = int(start * SR), int(cons_s * SR), int(vowel_s * SR)
        x[i:i + c] += 0.03 * rng.standard_normal(c).astype(np.float32)
        t = np.arange(v) / SR
        x[i + c:i + c + v] += (0.5 * np.sin(2 * np.pi * 220 * t) * np.minimum(1, t / 0.004)).astype(np.float32)
    write_wav24(path, SR, x)
    return path


def test_syllables_and_attacks(tmp_path):
    from rick_rubin.transcribe import (beat_point, build_words, clean_words, envelope, load_words, save_words, sidecar,
                                        snap_onset, syllabify, table, words_text)
    cut = lambda w: [w[a:b] for a, _, b in syllabify(w)]  # noqa: E731
    assert cut("gonna") == ["gon", "na"] and cut("take") == ["take"] and cut("some") == ["some"] and cut("time") == ["time"]
    assert cut("crisis") == ["cri", "sis"] and cut("table") == ["tab", "le"] and cut("yesterday") == ["yes", "ter", "day"]
    assert cut("i'm") == ["i'm"] and cut("mmm") == ["mmm"] and syllabify("take")[0] == (0, 1, 4)
    assert clean_words("I’m gonna, TAKE... some-time!") == ["i'm", "gonna", "take", "sometime"]

    # 120 BPM: a 16th is 125 ms. "gonna" starts on beat 2, "take" 20 ms late of beat 3 with a 30 ms consonant
    wav = _sung(tmp_path / "v.wav", [(0.5, 0.03, 0.15), (0.75, 0.0, 0.15), (1.02, 0.03, 0.4)])
    _, x = read_audio(wav)
    env = envelope(x, SR)
    assert abs(snap_onset(env, 0.52) - 0.5) < 0.006 and snap_onset(env, 2.5) == 2.5          # nothing rises at 2.5 s
    assert abs(beat_point(env, 0.5, 0.62) - 0.53) < 0.008 and abs(beat_point(env, 0.75, 0.85) - 0.75) < 0.008
    # letters as a CTC aligner gives them: 20 ms frames, placed mid-sound, never exactly on the onset
    letters = [[(0.52, 0.54, 0.9), (0.58, 0.60, 0.9), (0.66, 0.68, 0.9), (0.76, 0.78, 0.8), (0.80, 0.82, 0.8)],
               [(1.04, 1.06, 0.2), (1.10, 1.12, 0.3), (1.28, 1.30, 0.2), (1.32, 1.34, 0.2)]]
    words = build_words(["gonna", "take"], letters, env, 120.0, len(x) / SR)
    assert [w.text for w in words] == ["gonna", "take"] and [s.text for s in words[0].syllables] == ["gon", "na"]
    gon, na = words[0].syllables
    take = words[1].syllables[0]
    assert abs(gon.start_s - 0.5) < 0.006 and abs(gon.vowel_s - 0.53) < 0.008 and gon.pos == "1.2.1" and 20 < gon.off_ms < 40
    assert abs(na.start_s - 0.75) < 0.006 and na.pos == "1.2.3" and abs(na.off_ms) < 8
    assert abs(take.start_s - 1.02) < 0.006 and abs(take.vowel_s - 1.05) < 0.008 and take.pos == "1.3.1" and 40 < take.off_ms < 60
    assert abs(take.end_s - 1.45) < 0.02 and words[1].conf < 0.3 <= words[0].conf
    lines = words_text(words)
    assert lines[0].startswith("  words bar 1: 2.1 gon+") and "; 2.3 -na; 3.1 take?+" in lines[0]
    assert "-na" in table(words) and "(gonna)" in table(words)
    save_words(wav, words, 120.0, "test")
    assert load_words(wav) == words and load_words(tmp_path / "none.wav") is None and sidecar("a/b.wav").name == "b.words.json"


def test_retime_puts_attacks_on_the_grid(tmp_path):
    from rick_rubin.transcribe import beat_point, build_words, envelope, load_words, retime_loop, snap_onset
    # three words, each late by a different amount (120 BPM, 16th = 125 ms)
    wav = _sung(tmp_path / "v.wav", [(0.52, 0.02, 0.2), (1.02, 0.03, 0.3), (2.31, 0.0, 0.3)])
    _, x = read_audio(wav)
    env = envelope(x, SR)
    letters = [[(0.54, 0.56, 0.9), (0.58, 0.60, 0.9)], [(1.04, 1.06, 0.9), (1.09, 1.11, 0.9)], [(2.33, 2.35, 0.9), (2.4, 2.42, 0.9)]]
    words = build_words(["go", "to", "at"], letters, env, 120.0, len(x) / SR)
    assert [round(w.off_ms) for w in words] != [0, 0, 0]
    rows = retime_loop(wav, tmp_path / "q.wav", 120.0, words, grid=16, moves={3: "2.1.3"})
    assert [r["text"] for r in rows] == ["go", "to", "at"] and [r["to_pos"] for r in rows] == ["1.2.1", "1.3.1", "2.1.3"]
    assert rows[0]["shift_ms"] < -30 and rows[2]["to_beat"] == 4.5
    _, y = read_audio(tmp_path / "q.wav")
    assert len(y) == len(x)
    env2 = envelope(y, SR)
    for target in (0.5, 1.0, 2.25):                       # measured again in the new file: attacks sit on the grid
        st = snap_onset(env2, target, before_s=0.08, after_s=0.08)
        assert abs(beat_point(env2, st, st + 0.1) - target) < 0.008
    moved = load_words(tmp_path / "q.wav")
    assert [w.pos for w in moved] == ["1.2.1", "1.3.1", "2.1.3"] and all(abs(w.off_ms) < 1 for w in moved)
    # half strength moves half way; by="syllable" yields one piece per syllable
    half = retime_loop(wav, tmp_path / "h.wav", 120.0, words, strength=0.5)
    assert abs(half[0]["shift_ms"] - rows[0]["shift_ms"] / 2) < 0.6
    assert len(retime_loop(wav, tmp_path / "s.wav", 120.0, words, by="syllable")) == 3


# ---------------------------------------------------------------- stereo image
def test_stereo_stats_and_checks(tmp_path):
    from rick_rubin.analysis import stereo_issues, stereo_report, stereo_stats
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
    from rick_rubin.analysis import measure, section_windows
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
    from rick_rubin import serum

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
from rick_rubin import Song

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
    from rick_rubin.compose import bar_events
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


# ---------------------------------------------------------------- notes inside a sample
def test_notes_inside_a_sample(tmp_path, capsys):
    from rick_rubin import Key
    from rick_rubin.pitch import _tidy, load_notes, notes_text, pitch_at, register, sample_notes, table
    # a sung line at 120 BPM: F3 for a beat, a breath, F3 again, then Ab3 20 cents flat, then E3 (not in F minor)
    def tone(midi, secs):
        f = 440 * 2 ** ((midi - 69) / 12)
        t = np.arange(int(secs * SR)) / SR
        return 0.4 * (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(4 * np.pi * f * t) + 0.25 * np.sin(6 * np.pi * f * t)) * np.minimum(1, t / 0.01)
    gap = np.zeros(int(0.04 * SR))
    x = np.concatenate([np.zeros(int(0.5 * SR)), tone(53, 0.46), gap, tone(53, 0.25), np.zeros(int(0.25 * SR)),
                        tone(55.8, 0.5), tone(52, 0.5), np.zeros(int(0.5 * SR))]).astype(np.float32)
    write_wav24(tmp_path / "v.wav", SR, x)
    notes = sample_notes(tmp_path / "v.wav", 120.0, Key.parse("F minor"))
    assert [n.name for n in notes] == ["F2", "G#2", "E2"]             # the breath did not split the first note
    f, ab, e = notes
    assert abs(f.midi - 53) < 0.1 and abs(f.start_s - 0.5) < 0.03 and abs(f.end_s - 1.25) < 0.04 and f.pos == "1.2.1"
    assert abs(ab.cents + 20) <= 6 and ab.pos == "1.4.1" and abs(ab.beats - 1.0) < 0.12
    assert (f.in_key, ab.in_key, e.in_key) == (True, True, False)
    assert register(notes).startswith("range E2-G#2 (165-20") and "centre F#2" in register(notes)
    lines = notes_text(notes)
    assert lines[0].startswith("  pitch: range E2-G#2") and "2.1 F2 1.5" in lines[1] and "4.1 G#2-" in lines[1]
    assert "E2!" in "".join(lines) and "E2    !" in table(notes)
    assert pitch_at(notes, 1.55, 1.9).name == "G#2" and pitch_at(notes, 3.0, 3.2) is None and load_notes(tmp_path / "v.wav") == notes
    # an octave blip next to a long note is that note; noise has no notes
    assert _tidy([(0.0, 0.5, 53.0), (0.5, 0.58, 65.1), (0.58, 0.9, 53.1)]) == [(0.0, 0.9, pytest.approx(53.04, abs=0.05))]
    write_wav24(tmp_path / "n.wav", SR, (0.3 * np.random.default_rng(1).standard_normal(SR)).astype(np.float32))
    assert sample_notes(tmp_path / "n.wav", 120.0) == [] and "no pitched notes" in register([])


# ---------------------------------------------------------------- exploring: scaffold + audition
def test_init_copies_the_scaffold_and_audition_compares(tmp_path, capsys):
    from rick_rubin.samples import describe_sample
    root = tmp_path / "new song"
    assert main(["init", str(root), "--title", "New Song", "--bpm", "126", "--key", "A minor"]) == 0
    assert {p.name for p in root.iterdir()} >= {"CLAUDE.md", "song.py", "project.md", "samples", ".gitignore"}
    claude = (root / "CLAUDE.md").read_text()
    prefs = [ln[1:] for ln in claude.splitlines() if ln.startswith("@")]
    assert len(prefs) == 1 and Path(prefs[0]).name == "PREFERENCES.md" and "one-shot" in Path(prefs[0]).read_text()
    assert "{" not in claude and "{title}" not in (root / "project.md").read_text()
    import json
    assert json.loads((root / "samples" / "manifest.json").read_text())["song"] == {"title": "New Song", "bpm": 126, "key": "A minor"}
    song = Project(root).load()
    assert (song.title, song.bpm, song.key, song.tracks, song.patterns) == ("New Song", 126, "A minor", [], {})   # nothing pre-written
    with pytest.raises(FileExistsError):
        Project.init(root, "x", 120, "C minor")
    # audition: a long low tone vs a short bright click
    t = np.arange(SR) / SR
    write_wav24(root / "samples" / "raw" / "low.wav", SR, (0.5 * np.sin(2 * np.pi * 55 * t) * np.minimum(1, t / 0.05)).astype(np.float32))
    click = np.zeros(SR // 4, np.float32)
    click[:300] = 0.8 * np.random.default_rng(0).standard_normal(300) * np.linspace(1, 0, 300)
    write_wav24(root / "samples" / "raw" / "click.wav", SR, click)
    low, hi = describe_sample(root / "samples" / "raw" / "low.wav"), describe_sample(root / "samples" / "raw" / "click.wav")
    assert low["pitch"] == "A0" and abs(low["pitch_hz"] - 55) < 1 and low["bands"]["sub"] > 90 and 25 < low["attack_ms"] < 50
    assert hi["pitch"] is None and hi["centroid_hz"] > 3000 and hi["attack_ms"] < 3 and hi["decay_ms"] < 15 and low["decay_ms"] != low["decay_ms"]
    capsys.readouterr()
    assert main(["audition", str(root), "samples/raw/low.wav", "samples/raw/click.wav"]) == 0
    out = capsys.readouterr().out
    assert "| low.wav | 1.00 |" in out and "A0 55 Hz" in out and "sustains" in out and "| click.wav | 0.25 |" in out


# ---------------------------------------------------------------- Serum hosted in-process (needs the plug-in)
_SERUM_OK = Path("/Library/Audio/Plug-Ins/VST3/Serum2.vst3").exists()


@pytest.mark.skipif(not _SERUM_OK, reason="Serum 2 VST3 not installed")
def test_serum_track_is_rendered_through_the_plugin(tmp_path):
    pytest.importorskip("pedalboard")
    from rick_rubin import serum
    presets = serum.catalog()
    if not presets:
        pytest.skip("no Serum presets installed")
    host = serum.SerumHost.get()
    # state container round trip, and a preset really changes the instrument
    comp, cont = serum.split_state(host.init_state)
    assert serum.split_state(serum.join_state(comp, cont)) == (comp, cont)
    assert serum._unpack(comp)[0]["component"] == "processor" and serum._unpack(cont)[0]["component"] == "controller"
    name = host.load(presets[0].path)
    assert serum._unpack(serum.split_state(bytes(host.plugin.raw_state))[1])[0]["presetName"] == name
    with pytest.raises(KeyError, match="no parameter"):
        host.set({"definitely_not_a_param": 1})
    a = host.render([(48, 0.0, 0.5, 100)], 1.0)
    assert a.shape == (44100, 2) and np.abs(a).max() > 0.001

    song = Song("Serum Test", bpm=120, key="A minor")
    kick = song.add_track("Kick", "kick")
    syn = song.add_track("Synth", "lead", serum=str(presets[0].path), serum_params={"macro_1": 30}, sidechain=True)
    four = song.pattern("four", kick, "x...x...x...x...")
    riff = song.pattern("riff", syn, ["1.1 A2 0.5; 2.3 C3 0.5; 3.1 E3 1"])
    song.add_section("a", 4, kind="drop", parts={kick: four, syn: riff}, automation={syn: {"filter": [0.3, 1.0]}})
    song.add_section("b", 4, kind="drop", parts={kick: four})
    p = Project.create(tmp_path / "trk", song)
    song = p.load()
    assert "Serum 2 preset" in pack(song) and "macro_1=30" in pack(song)
    r = render_preview(song, tmp_path / "prev.wav", stems_dir=tmp_path / "stems")
    _, st = read_audio(r.stems["Synth"])
    half = len(st) // 2 - SR
    assert np.abs(st[:half]).max() > 0.001 and np.abs(st[half + 3 * SR:]).max() < np.abs(st[:half]).max() * 0.2   # plays in section a only
    stems = list((p.root / "serum").glob("Synth.*.wav"))
    assert len(stems) == 1
    _, sx = read_audio(stems[0])
    assert abs(len(sx) / SR - song.duration_s) < 0.01                       # exactly the song's length
    render_preview(song, tmp_path / "prev2.wav")
    assert list((p.root / "serum").glob("Synth.*.wav")) == stems           # cached, not re-rendered
    srv = FakeLiveServer()
    with LiveBridge(port=srv.port) as b:
        rep = push_song(song, b)
    live = {t.name: t for t in srv.song.tracks}
    assert live["Synth"].is_audio and "rendered to audio" in rep.tracks["Synth"]["instrument"] and not rep.warnings
    clips = live["Synth"].arrangement_clips
    assert len(clips) == 1 and clips[0].start_time == 0.0 and abs(clips[0].length - 32) < 0.01
    assert clips[0].file_path.endswith(".baked.wav") and [d.name for d in live["Synth"].devices] == ["Compressor"]
    song.track("Synth").sample = "x.wav"
    assert any("cannot also have sample" in e for e in song.validate())


def test_track_delay_shifts_the_whole_track(sampled):
    p, _ = sampled
    song = p.load()
    base = {(c.track, c.section): c.start for c in song.flatten()[0]}
    song.track("Clap").delay_ms = 12
    song.track("Top").delay_ms = -9          # an audio-loop track
    song.track("Kick").delay_ms = -5         # starts at beat 0: cannot go earlier
    clips = song.flatten()[0]
    ms = lambda beats: beats * 60000.0 / song.bpm  # noqa: E731
    for c in clips:
        want = {"Clap": 12, "Top": -9, "Kick": -5}.get(c.track, 0)
        if c.track == "Kick" and base[(c.track, c.section)] == 0:
            assert c.start == 0.0 and min(n.start for n in c.notes) == 0.0 and sorted(n.start for n in c.notes)[1] < 1.0
        else:
            assert abs(ms(c.start - base[(c.track, c.section)]) - want) < 1e-6
    assert "delay +12 ms" in pack(song) and "delay -9 ms" in pack(song)
    assert Song.from_json(song.to_json()).track("Top").delay_ms == -9
    srv = FakeLiveServer()
    with LiveBridge(port=srv.port) as b:
        push_song(song, b)
    live = {t.name: t for t in srv.song.tracks}
    assert abs(ms(min(c.start_time for c in live["Top"].arrangement_clips) - 48) + 9) < 1e-3
    song.track("Clap").delay_ms = 250
    assert any("more than 100 ms" in e for e in song.validate())


# ---------------------------------------------------------------- check: lint + types + build + music lint
def test_check_catches_python_and_music_mistakes(tmp_path, capsys):
    import shutil as _sh
    root = tmp_path / "chk"
    assert main(["init", str(root), "--title", "Chk", "--bpm", "126", "--key", "A minor"]) == 0
    assert (root / "pyproject.toml").exists()
    p = Project(root)
    good = (root / "song.py").read_text() + '''
kick = song.add_track("Kick", "kick", volume_db=-6)
four = song.pattern("four", kick, "x...x...x...x...")
song.add_section("intro", 16, kind="intro", energy=3, parts={kick: four})
song.add_section("drop", 16, kind="drop", energy=9, parts={kick: four})
song.add_section("outro", 16, kind="outro", energy=3, parts={kick: four})
'''
    (root / "song.py").write_text(good)
    stages, errors = p.check()
    assert errors == 0 and [n for n, ok, _ in stages if not ok] == [] and [n for n, _, _ in stages][0] == "syntax"
    have_tools = all((Path(sys.executable).parent / t).exists() or _sh.which(t) for t in ("ruff", "mypy"))
    cases = [("song.add_section('x', 16, parts={kick: fuor})", "ruff" if have_tools else "build", "fuor"),
             ("song.add_track('Bass', 'bass', volume=-6)", "mypy" if have_tools else "build", "volume"),
             ("song.add_section('odd', 6, parts={kick: four})", "music lint", "not a multiple of 4"),
             ("song.add_section('y', 8, parts={'Nobody': four})", "build", "unknown track"),
             ("song.add_section('z', 8, parts={kick: four}", "syntax", "song.py:")]
    for line, stage, needle in cases:
        (root / "song.py").write_text(good + line + chr(10))
        stages, errors = p.check()
        failed = {n: out for n, ok, out in stages if not ok}
        assert errors >= 1 and stage in failed and needle in failed[stage], (line, stages)
    capsys.readouterr()
    assert main(["check", str(root)]) == 1 and "FAIL  syntax" in capsys.readouterr().out


# ---------------------------------------------------------------- character vocabulary and the sample library
def test_character_words_and_project_sample_search(tmp_path, capsys):
    import json
    from rick_rubin.samples import analyse_project_samples, character_words, describe_sample, search_rows, similar
    root = tmp_path / "lib"
    assert main(["init", str(root), "--title", "Lib", "--bpm", "126", "--key", "A minor"]) == 0
    raw = root / "samples" / "raw"
    t = np.arange(SR) / SR
    write_wav24(raw / "sub_drone.wav", SR, (0.5 * np.sin(2 * np.pi * 45 * t) * np.minimum(1, t / 0.2)).astype(np.float32))
    rng = np.random.default_rng(0)
    tick = np.zeros(SR // 8, np.float32)
    tick[:400] = 0.8 * rng.standard_normal(400) * np.linspace(1, 0, 400) ** 2
    write_wav24(raw / "tick.wav", SR, tick)
    wide = np.stack([rng.standard_normal(SR), rng.standard_normal(SR)], 1).astype(np.float32) * 0.2
    write_wav24(raw / "wide_noise.wav", SR, wide)
    sub, tk, wd = (describe_sample(raw / f) for f in ("sub_drone.wav", "tick.wav", "wide_noise.wav"))
    assert {"slow-attack", "sustained", "dark", "subby", "bassy", "mono", "pitched"} <= set(sub["character"])
    assert {"short", "snappy", "tight", "no-low-end", "unpitched", "punchy"} <= set(tk["character"]) and ("bright" in tk["character"] or "airy" in tk["character"])
    assert {"very-wide", "wide-low-end", "unpitched"} <= set(wd["character"]) and character_words(sub) == sub["character"]
    rows = analyse_project_samples(root)
    assert set(rows) == {"samples/raw/sub_drone.wav", "samples/raw/tick.wav", "samples/raw/wide_noise.wav"}
    saved = json.loads((root / "samples" / "manifest.json").read_text())
    assert saved["analysis"]["samples/raw/tick.wav"]["character"] == tk["character"] and saved["song"]["title"] == "Lib"
    assert saved["analysis"]["samples/raw/sub_drone.wav"]["decay_ms"] is None             # NaN stored as null
    assert [k for k, _ in search_rows(rows, ["snappy"])] == ["samples/raw/tick.wav"]
    assert [k for k, _ in search_rows(rows, ["-mono"])] == ["samples/raw/wide_noise.wav"]
    assert [k for k, _ in search_rows(rows, [], "sub")][0] == "samples/raw/sub_drone.wav"
    assert [k for k, _ in search_rows(rows, [], "bright")][-1] == "samples/raw/sub_drone.wav"
    assert similar({k: v for k, v in rows.items() if "tick" not in k}, rows["samples/raw/tick.wav"], 1)[0][0] == "samples/raw/wide_noise.wav"
    capsys.readouterr()
    assert main(["samples", str(root), "subby", "--sort", "sub"]) == 0
    out = capsys.readouterr().out
    assert "samples/raw/sub_drone.wav" in out and "tick.wav" not in out and "1 of 3 samples" in out
    # importing prints and records the character
    assert main(["sample", str(root), str(raw / "tick.wav"), "--name", "tick", "--oneshot"]) == 0
    out = capsys.readouterr().out
    assert "snappy" in out and "samples/tick.wav" in json.loads((root / "samples" / "manifest.json").read_text())["analysis"]


def test_several_parts_for_one_track_are_joined():
    s = Song("J", bpm=120, key="A minor")
    hats = s.add_track("Hats", "hat")
    a = s.pattern("a", hats, "x...x...x...x...")
    b = s.pattern("b", hats, "x.x.x.x.x.x.x.x.|xxxxxxxxxxxxxxxx")
    sec = s.add_section("drop", 8, kind="drop", parts={hats: [a.at(1, 4), b.at(5, 8), a.at(8, 8)]})
    assert sec.parts["Hats"].pattern == "drop/Hats" and s.patterns["drop/Hats"].bars == 8 and not s.validate()
    notes = s.patterns["drop/Hats"].notes
    per_bar = [sum(1 for n in notes if bar * 4 <= n.start < bar * 4 + 4) for bar in range(8)]
    assert per_bar == [4, 4, 4, 4, 8, 16, 8, 16 + 4]            # a, a, a, a, then b's two bars twice, with a layered on the last bar
    v = sec.variant("drop2", add={hats: [b.at(1, 8)]})
    assert s.patterns["drop2/Hats"].bars == 8 and v.parts["Hats"].pattern == "drop2/Hats" and "joined: b[1-8]" in s.patterns["drop2/Hats"].desc


def test_sample_tracks_play_velocity_100_at_file_level(sampled, tmp_path):
    from rick_rubin.model import sample_gain_db, simpler_velocity_db
    # the measured law: 0.4 dB per velocity step at 100 % sensitivity, 0 dB at velocity ~70
    assert abs(simpler_velocity_db(100, 35) - 4.16) < 0.02 and abs(simpler_velocity_db(64, 35) + 0.88) < 0.02
    assert abs(simpler_velocity_db(32, 100) + 15.3) < 0.1 and simpler_velocity_db(90, 0) == 0
    p, _ = sampled
    p.edit([{"op": "track", "name": "Hats", "set": {"sample": "samples/kick.wav", "instrument_params": {"Vol < Vel": 80}}}])
    song = p.load()
    kick, hats = song.track("Kick"), song.track("Hats")
    assert sample_gain_db(kick, 100) == 0 and abs(sample_gain_db(kick, 64) + 5.04) < 0.02 and abs(sample_gain_db(hats, 64) + 11.52) < 0.02
    srv = FakeLiveServer()
    with LiveBridge(port=srv.port) as b:
        push_song(song, b)
    live = {t.name: t for t in srv.song.tracks}
    vol = lambda name: {q.name: q.str_for_value(q.value) for q in live[name].devices[0].parameters}["Volume"]  # noqa: E731
    assert vol("Kick") == "-4.2 dB" and vol("Hats") == "-9.5 dB"       # cancels Simpler's boost at velocity 100
    # offline: a velocity-100 kick is the file itself (times the track fader)
    song.track("Kick").volume_db = 0.0
    r = render_preview(song, tmp_path / "p.wav", stems_dir=tmp_path / "st", tracks=["Kick"], master_peak=1.25 * 0.89)
    _, st = read_audio(r.stems["Kick"])
    _, src = read_audio(song.resolve("samples/kick.wav"))
    assert abs(np.abs(st).max() / np.abs(src).max() - 1.0) < 0.05


# ---------------------------------------------------------------- reference profiles
def test_reference_profile_and_compare(tmp_path):
    from rick_rubin.reference import Profile, compare, estimate_bpm, profile
    rng = np.random.default_rng(0)
    bpm, secs = 125.0, 40
    n = secs * SR
    t = np.arange(n) / SR
    beat = 60 / bpm

    def groove(width=0.0, vary=False, hat_db=-20.0, limit=False):
        L = np.zeros(n)
        R = np.zeros(n)
        k = np.arange(int(0.25 * SR)) / SR
        kick = np.sin(2 * np.pi * 50 * k) * np.exp(-k * 18)
        hat = rng.standard_normal(int(0.05 * SR)) * np.exp(-np.arange(int(0.05 * SR)) / 300)
        for b in range(int(secs / beat) - 1):
            i = int(b * beat * SR)
            L[i:i + len(kick)] += kick
            R[i:i + len(kick)] += kick
            j = i + int(beat / 2 * SR)
            g = 10 ** (hat_db / 20) * (1.0 + (0.8 * np.sin(b / 5.0) if vary else 0.0))
            hl, hr = hat * g, (rng.standard_normal(len(hat)) * np.exp(-np.arange(len(hat)) / 300) * g if width else hat * g)
            L[j:j + len(hat)] += hl
            R[j:j + len(hat)] += hl * (1 - width) + hr * width
        if vary:                                               # a filtered pad that opens and closes
            pad = np.sin(2 * np.pi * 440 * t) * 0.15 * (0.5 + 0.5 * np.sin(2 * np.pi * t / 7.0))
            L += pad
            R += pad
        x = np.stack([L, R], 1)
        x = np.tanh(x * 4) * 0.9 if limit else x * 0.3
        return x.astype(np.float32)

    write_wav24(tmp_path / "flat.wav", SR, groove())
    write_wav24(tmp_path / "alive.wav", SR, groove(width=0.9, vary=True, hat_db=-12, limit=True))
    flat, alive = profile(tmp_path / "flat.wav"), profile(tmp_path / "alive.wav")
    assert abs(estimate_bpm(groove().mean(axis=1), SR) - bpm) < 0.6 and abs(flat.bpm - bpm) < 0.6
    assert alive.drop_lufs > flat.drop_lufs + 6 and alive.crest_db < flat.crest_db - 3          # louder and denser
    assert flat.side_pct < 0.1 and alive.side_bands["high"] > 20 and alive.side_bands["low"] < 1  # wide top, centred low end
    assert alive.movement > flat.movement + 0.3 and flat.repeat_pct > 80 and alive.repeat_pct < flat.repeat_pct
    assert alive.bands_db["high"] > flat.bands_db["high"] + 3 and flat.pump_db < -6
    text = compare(flat, [alive, Profile(**{**alive.__dict__, "name": "alive2", "drop_lufs": alive.drop_lufs + 1, "movement": alive.movement + 0.2})])
    assert "| loudness of the drop |" in text and "BELOW all references" in text
    out = text.split("## Outside the references' range")[1]
    assert "loudness of the drop" in out and "movement in the drop" in out and "stereo: side energy" in out
