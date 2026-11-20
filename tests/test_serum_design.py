"""Serum sound design: the producer-facing parameter map, patch editing and saving, sound measurements.

The map and patch tests run anywhere the optional Serum dependencies are installed (they edit preset trees);
tests that render need the Serum 2 plug-in and skip without it."""
import re
import struct
from pathlib import Path

import numpy as np
import pytest
from scipy.signal import butter, sosfilt

from rick_rubin import serum_params as sp
from rick_rubin.sounddesign import delta_text, describe_sound, describe_table

SR = 44100
_SERUM_OK = Path("/Library/Audio/Plug-Ins/VST3/Serum2.vst3").exists()
needs_serum = pytest.mark.skipif(not _SERUM_OK, reason="Serum 2 VST3 not installed")


# ---------------------------------------------------------------- the map
def test_every_plugin_parameter_is_mapped_once_or_ignored_with_a_reason():
    raw_names = sp.tables()["plugin_params"]          # snapshot of SerumHost.params() taken by build_tables()
    assert len(raw_names) > 2500
    mapped = [p.raw for p in sp.all_params().values() if p.raw]
    assert len(mapped) == len(set(mapped)), "a plug-in parameter is mapped by two keys"
    for n in raw_names:
        inside = n in mapped
        why = sp.ignored_reason(n)
        assert inside != bool(why), f"{n}: {'mapped and ignored' if inside else 'neither mapped nor ignored'}"
    assert not set(mapped) - set(raw_names)


def test_map_groups_views_and_lookup():
    g = sp.groups()
    for name in ("osc", "noise", "sub", "filter", "routing", "env", "lfo", "mod", "macro", "global", "random", "arp"):
        assert g[name], name
    text = sp.view("filter")
    assert "| filter_1.cutoff_hz | Hz | 8..22050 | 425 |" in text and len(text.splitlines()) < 40
    assert "lfo_1 .. lfo_10" in sp.view("lfo") and "mod_1.amount" in sp.view("mod")
    assert "distortion" in sp.view("fx") and "reverb" in sp.view("fx")
    assert sp.lookup("filter_1_freq_hz").key == "filter_1.cutoff_hz"          # plug-in names resolve too
    with pytest.raises(KeyError, match="filter_1 has"):
        sp.lookup("filter_1.cutof")


def test_converters_invert_and_match_serums_display_curves():
    for key, value in (("filter_1.cutoff_hz", 800.0), ("osc_a.level_db", -5.0), ("env_1.sustain_db", -12.0), ("env_2.sustain_pct", 25.0),
                       ("filter_1.level_db", 3.0), ("global.volume_db", -9.0), ("global.direct_db", 0.0), ("env_2.attack_ms", 40.0)):
        c = sp.lookup(key).conv
        assert c.from_tree(c.to_tree(value)) == pytest.approx(value, rel=1e-9, abs=1e-9), key
    # the points Serum itself shows (read off the hosted plug-in): tree value -> display
    assert sp.HZ.from_tree(0.5) == pytest.approx(420, rel=0.02)        # Serum: 425 Hz (its display grid)
    assert sp.HZ.from_tree(0.9) == pytest.approx(10025, rel=0.005)
    assert sp.GAIN.from_tree(0.5625) == pytest.approx(-5.0, abs=0.01)  # 75 % = -5.0 dB
    assert sp.SUSTAIN_DB.from_tree(0.5) == pytest.approx(-12.04, abs=0.01)
    assert sp.PCT2.from_tree(0.5) == pytest.approx(25.0)
    assert sp.FILTER_OUT.from_tree(1.0) == pytest.approx(12.0) and sp.MASTER.from_tree(1.0) == pytest.approx(3.0)
    assert sp.lookup("filter_1.type").conv.to_tree("MG Low 24") == "MgL24" and sp.lookup("filter_1.type").conv.to_tree("MG Low 12") is None
    assert sp.lookup("lfo_1.rate").conv.to_tree("1/8") == pytest.approx(10.662, rel=1e-3) and sp.lookup("lfo_1.rate").conv.to_tree(3) == 3.0
    with pytest.raises(ValueError, match="not one of"):
        sp.lookup("sub.shape").conv.to_tree("Wobble")


def test_mod_sources_and_destination_ids():
    assert sp.mod_source("lfo_1") == 6 and sp.mod_source("env_2") == 3 and sp.mod_source("macro_8") == 32 and sp.mod_source("#40") == 40
    assert sp.mod_source_name([16, 0]) == "velocity" and sp.mod_source_name(59) == "#59"
    assert sp.mod_param_id("VoiceFilter", "kParamFreq") == 3 and sp.mod_param_id("WTOsc", "kParamTablePos") == 6
    with pytest.raises(KeyError):
        sp.mod_source("lfo_11")


# ---------------------------------------------------------------- patches (no plug-in needed)
def _tiny_patch():
    from rick_rubin.serum_patch import Patch
    tree = {"Oscillator0": {"WTOsc0": {"plainParams": "default", "relativePathToWT": "S2 Tables/Default Shapes.wav"}, "plainParams": {}},
            "Oscillator4": {"SubOsc4": {"plainParams": {}}, "plainParams": {}},
            "VoiceFilter0": {"plainParams": {}}, "Env0": {"plainParams": {}}, "Env1": {"plainParams": {}},
            "LFO0": {"curveData": {}, "pathData": {}, "plainParams": {}}, "Macro0": {"plainParams": {}},
            **{f"ModSlot{i}": {"plainParams": {}} for i in range(64)},
            "FXRack0": {"FX": [], "displayName": "", "plainParams": "default"}, "Global0": {"plainParams": {}},
            "presetName": "tiny", "fileType": "SerumPreset"}
    return Patch({"fileType": "SerumPreset", "presetName": "tiny", "product": "Serum2", "productVersion": "2.0.12", "version": 5.0}, tree)


def test_patch_edit_save_read_round_trip(tmp_path):
    pytest.importorskip("cbor2")
    pytest.importorskip("zstandard")
    from rick_rubin import serum
    from rick_rubin.serum_patch import Patch, parse_assignments, parse_mod
    p = _tiny_patch()
    edits = {"osc_a.detune": 0.18, "osc_a.unison": 5, "filter_1.on": "on", "filter_1.cutoff_hz": 800, "filter_1.type": "MG Low 24",
             "env_2.attack_ms": 40, "env_2.sustain_pct": 50, "env_1.sustain_db": -6, "sub.shape": "Saw", "lfo_1.rate": "1/8",
             "global.mono": "on", "global.glide_ms": 30, "macro_1.value": 40, "macro_1.name": "CUTOFF", "lfo_1.shape": "0:0,0.5:1,1:0"}
    p.apply(edits)
    label = p.add_fx("distortion", params={"drive": 35, "mode": "TapeSat"})
    assert label == "fx.distortion" and p.add_fx("distortion") == "fx.distortion#2"
    p.set("fx.distortion#2.drive", 70)
    p.remove_fx("fx.distortion#2")
    slot = p.add_mod("lfo_1", "filter_1.cutoff_hz", 25)
    p.add_mod("macro_1", "fx.distortion.drive", 50)
    out = p.save(tmp_path / "serum" / "presets" / "designed", name="designed", author="agent", description="round trip")
    assert out.name == "designed.SerumPreset"
    raw = out.read_bytes()
    n = struct.unpack("<Q", raw[9:17])[0]
    import hashlib
    import json
    head = json.loads(raw[17:17 + n])
    assert head["hash"] == hashlib.md5(raw[17 + n + 8:]).hexdigest() and head["presetName"] == "designed" and head["fileType"] == "SerumPreset"
    q = Patch.open(out)
    got = q.read()
    for k, v in edits.items():
        if k == "lfo_1.shape":
            assert got[k] == "Custom"
        elif isinstance(v, (int, float)):
            assert got[k] == pytest.approx(v, rel=1e-6), k
        else:
            assert str(got[k]).lower() == str(v).lower(), k
    assert [(lab, prm) for lab, _, _, prm in q.fx()] == [("fx.distortion", {"drive": 35.0, "mode": "kTapeSat"})]
    mods = q.mods()
    assert mods[0] == {"slot": slot, "source": "lfo_1", "aux": None, "dest": "filter_1.cutoff_hz", "amount": 25.0, "bipolar": False}
    assert mods[1]["dest"] == "fx.distortion.drive" or mods[1]["dest"].startswith("fx.distortion")
    assert q.remove_mod("filter_1.cutoff_hz") == 1 and len(q.mods()) == 1
    curve = q.tree["LFO0"]["curveData"]
    assert curve["numPoints"] == 3 and curve["yVals"][:3] == [1.0, 0.0, 1.0]       # Serum's y axis: 0 = top
    text = serum.sheet(out)
    assert "# designed — Serum 2 preset" in text and "Distortion: Drive 35, Mode TapeSat" in text
    # errors that say what to do
    with pytest.raises(KeyError, match="add it first"):
        q.set("fx.reverb.wet", 30)
    with pytest.raises(ValueError, match="out of range"):
        q.set("osc_a.pan", 80)
    assert parse_assignments(["osc_a.detune=0.18 filter_1.type=MG Low 24", "env_2.attack_ms=40"]) == {
        "osc_a.detune": 0.18, "filter_1.type": "MG Low 24", "env_2.attack_ms": 40.0}
    assert parse_mod("lfo_1:filter_1.cutoff_hz:-20") == ("lfo_1", "filter_1.cutoff_hz", -20.0)


# ---------------------------------------------------------------- measurements on synthetic sounds
def _note(kind, held=1.2, secs=1.8, f0=110.0):
    t = np.arange(int(secs * SR)) / SR
    env = np.where(t < held, 1.0, np.exp(-(t - held) / 0.05)) * np.minimum(1, t / 0.004)
    saw = 2 * ((t * f0) % 1.0) - 1
    if kind == "saw":
        x = 0.5 * saw * env
    elif kind == "dark":
        x = sosfilt(butter(2, 500, "low", fs=SR, output="sos"), 0.5 * saw * env)
    elif kind == "square":
        x = 0.4 * np.sign(np.sin(2 * np.pi * f0 * t)) * env
    elif kind == "noise":
        x = np.random.default_rng(3).standard_normal(len(t)) * 0.3 * np.exp(-t / 0.06)
    elif kind == "tremolo":
        x = 0.3 * saw * env * (1 + 0.8 * np.sin(2 * np.pi * 2.0 * t))
    elif kind == "pluck":
        x = 0.5 * saw * np.exp(-t / 0.08) * np.minimum(1, t / 0.002)
    return x.astype(np.float32)[:, None]


def test_describe_reads_synthetic_sounds():
    d = {k: describe_sound(SR, _note(k), k, 1.2 if k not in ("noise", "pluck") else None, bpm=120) for k in
         ("saw", "dark", "square", "noise", "tremolo", "pluck")}
    saw, dark, sq, noise, trem, pluck = (d[k] for k in ("saw", "dark", "square", "noise", "tremolo", "pluck"))
    assert saw["pitch_txt"].startswith("A1") and abs(saw["odd_even_db"]) < 4 and saw["harmonics"] >= 15 and "rich" in saw["character"]
    assert dark["centroid_early_hz"] < 0.6 * saw["centroid_early_hz"] and dark["harmonics"] < saw["harmonics"] and dark["tilt_db_oct"] < saw["tilt_db_oct"] - 4
    assert sq["odd_even_db"] > 15 and "odd-heavy" in sq["character"]
    assert noise["pitch"] is None and "unpitched" in noise["character"] and "plucky" in noise["character"]
    assert trem["rate_hz"] == pytest.approx(2.0, rel=0.05) and trem["rate_beats"] == pytest.approx(1.0, rel=0.05) and "moving" in trem["character"]
    assert "plucky" in pluck["character"] and pluck["sustain_db"] < -20
    assert saw["release_ms"] < 400 and saw["attack_ms"] < 10 and saw["sustain_db"] > -1
    table = describe_table([saw, dark])
    assert table.count("\n| ") == 2 and "changes against saw" in table and "bright early -" in table
    assert "words +dark" in delta_text(saw, dark)


# ---------------------------------------------------------------- through the plug-in
@needs_serum
def test_patch_renders_as_saved_and_serum_reads_the_edits(tmp_path):
    pytest.importorskip("pedalboard")
    from rick_rubin import serum
    from rick_rubin.serum_patch import Patch
    host = serum.SerumHost.get()
    p = Patch.init()
    p.apply({"osc_a.detune": 0.18, "osc_a.unison": 3, "filter_1.on": "on", "filter_1.cutoff_hz": 800, "filter_1.type": "MG Low 24",
             "env_2.attack_ms": 40, "env_1.sustain_db": -6, "osc_a.level_db": -3, "global.volume_db": -6, "lfo_1.rate": "1/8"})
    out = p.save(tmp_path / "x.SerumPreset")
    host.load(out)
    shown = {n: v for n, v, _ in host.params()}
    assert shown["a_uni_detune"] == "0.18" and shown["filter_1_type"] == "MG Low 24" and shown["env_2_attack"] == "40 ms"
    assert shown["env_1_sustain"] == "-6.0 dB" and shown["a_level"].endswith("[-3.0 dB]") and shown["main_vol"].endswith("[-6.0 dB]")
    assert shown["lfo_1_rate"] == "1/8" and 790 <= float(shown["filter_1_freq_hz"]) <= 815
    a = host.render([(48, 0.0, 0.5, 100)], 1.0)
    host.load_patch(p)
    b = host.render([(48, 0.0, 0.5, 100)], 1.0)
    assert np.allclose(a, b, atol=1e-4)
    # a few mapped plug-in parameters land where the map says
    assert sp.check_paths(host, ["filter_1.cutoff_hz", "osc_b.detune", "env_3.release_ms", "lfo_4.rate", "macro_5.value", "sub.shape", "noise.pitch"]) == []


@needs_serum
def test_synced_lfo_plays_at_the_song_tempo():
    pytest.importorskip("pedalboard")
    from rick_rubin import serum
    from rick_rubin.serum_patch import Patch

    def rate(audio):
        m = np.abs(audio.mean(axis=1))
        e = m[: len(m) // 44 * 44].reshape(-1, 44).max(axis=1)[100:]
        e = e - e.mean()
        spec = np.abs(np.fft.rfft(e * np.hanning(len(e)), 1 << 17))
        f = np.fft.rfftfreq(1 << 17, 1 / 1000)
        sel = (f > 0.2) & (f < 30)
        return f[sel][np.argmax(spec[sel])]
    p = Patch.init()
    p.apply({"osc_a.level_db": -120, "lfo_1.rate": "1/4"})
    p.add_mod("lfo_1", "osc_a.level_db", 100)
    _, a120 = serum.render_preset(p, [(48, 0.0, 4.0, 100)], 4.0)
    _, a126 = serum.render_preset(p, [(48, 0.0, 4.0, 100)], 4.0, bpm=126)
    assert rate(a120) == pytest.approx(2.0, rel=0.01)           # Serum offline: 120 BPM
    assert rate(a126) == pytest.approx(2.1, rel=0.01)
    changed = serum.at_tempo(p.copy(), 126)
    assert changed == ["LFO 1 1/4 -> 2.100 Hz free"]


@needs_serum
def test_cli_set_saves_a_designed_patch(tmp_path, capsys):
    pytest.importorskip("pedalboard")
    from rick_rubin.cli import main
    assert main(["serum", "set", "init", "osc_a.unison=4", "osc_a.detune=0.2", "filter_1.on=on", "filter_1.cutoff_hz=900",
                 "--mod", "env_2:filter_1.cutoff_hz:30", "--fx-add", "distortion", "--save", "wide-saw", "--project", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "changed: +fx.distortion; osc_a.unison=4.0" in out and "| before (Init) |" in out and "| after |" in out
    saved = tmp_path / "serum" / "presets" / "wide-saw.SerumPreset"
    assert saved.exists() and 'serum="serum/presets/wide-saw.SerumPreset"' in out
    assert main(["serum", "patch", str(saved)]) == 0
    text = capsys.readouterr().out
    assert "osc_a.unison=4" in text and "env_2 → filter_1.cutoff_hz +30" in text and "fx.distortion" in text
    assert main(["serum", "ab", str(saved), "--try", "filter_1.cutoff_hz=300", "--try", "osc_a.unison=1"]) == 0
    text = capsys.readouterr().out
    assert "| filter_1.cutoff_hz=300 |" in text and re.search(r"- filter_1.cutoff_hz=300: .*bright", text)


# ---------------------------------------------------------------- matching a reference
def _phrase(f0s, gap=0.1, note=0.4, cutoff=None):
    t = np.arange(int(SR * (len(f0s) * (note + gap) + 0.3))) / SR
    x = np.zeros_like(t)
    for i, f0 in enumerate(f0s):
        a = i * (note + gap)
        sel = (t >= a) & (t < a + note)
        tt = t[sel] - a
        x[sel] = 0.5 * (2 * ((tt * f0) % 1.0) - 1) * np.minimum(1, tt / 0.003) * np.minimum(1, (note - tt) / 0.005)
    if cutoff:
        x = sosfilt(butter(2, cutoff, "low", fs=SR, output="sos"), x)
    return np.stack([x, x], axis=1).astype(np.float32)


def test_target_notes_split_repeated_notes_at_their_onsets(tmp_path):
    from rick_rubin.samples import write_wav24
    from rick_rubin.soundmatch import target_notes
    write_wav24(tmp_path / "p.wav", SR, _phrase([87.31, 87.31, 103.83, 77.78]))
    notes = target_notes(tmp_path / "p.wav")
    assert [n[0] for n in notes] == [41, 41, 44, 39]
    assert [n[1] for n in notes] == pytest.approx([0.0, 0.5, 1.0, 1.5], abs=0.012)
    assert all(abs(n[2] - 0.4) < 0.04 for n in notes)


def test_isolate_band_passes_the_bass_out_of_a_mix(tmp_path):
    from rick_rubin.isolate import isolate
    from rick_rubin.samples import read_audio, write_wav24
    bass = _phrase([55.0, 55.0, 65.41, 49.0] * 2)
    hats = np.random.default_rng(0).standard_normal(bass.shape).astype(np.float32) * 0.2
    hats = sosfilt(butter(4, 6000, "high", fs=SR, output="sos"), hats, axis=0).astype(np.float32)
    write_wav24(tmp_path / "mix.wav", SR, bass + hats)
    r = isolate(tmp_path / "mix.wav", tmp_path / "ref_bass.wav", "bass", start_s=2.0, end_s=4.0, method="bandpass")
    sr, y = read_audio(r["path"])
    assert r["method"] == "bandpass" and "band-passed" in r["warning"] and abs(len(y) / sr - 2.0) < 0.01
    spec = np.abs(np.fft.rfft(y[:, 0]))
    f = np.fft.rfftfreq(len(y), 1 / sr)
    assert spec[f > 4000].sum() < 0.01 * spec[f < 400].sum()          # the hats are gone
    assert [n.name for n in r["notes"]][:3] == ["A0", "C1", "G0"]          # the note table (a repeated pitch reads as one)
    from rick_rubin.soundmatch import target_notes
    assert [n[0] for n in target_notes(r["path"])][:4] == [33, 33, 36, 31]    # onsets split them for the fit
    with pytest.raises(RuntimeError, match="demucs"):
        isolate(tmp_path / "mix.wav", tmp_path / "d.wav", "drums", method="bandpass")


def test_distance_is_zero_for_the_same_sound_and_names_what_differs():
    from rick_rubin.soundmatch import distance, features
    a = features(SR, _phrase([87.31] * 3, cutoff=800))
    same, parts0 = distance(a, features(SR, _phrase([87.31] * 3, cutoff=800)))
    darker, parts = distance(a, features(SR, _phrase([87.31] * 3, cutoff=250)))
    louder, _ = distance(a, features(SR, 3 * _phrase([87.31] * 3, cutoff=800)))
    assert same < 1e-6 and louder < 0.05                            # level is a fader, not a sound
    assert darker > 1.0 and parts["spectrum"] > 3 and parts["brightness"] > 0.3


@needs_serum
def test_fit_moves_the_chosen_keys_towards_the_target(tmp_path):
    pytest.importorskip("pedalboard")
    from rick_rubin import serum
    from rick_rubin.samples import write_wav24
    from rick_rubin.serum_patch import Patch
    from rick_rubin.soundmatch import fit
    target = Patch.init().apply({"filter_1.on": "on", "filter_1.cutoff_hz": 600, "global.mono": "on"})
    _, audio = serum.render_preset(target, [(41, 0.0, 0.4, 100), (44, 0.5, 0.4, 100)], 1.3)
    write_wav24(tmp_path / "t.wav", SR, audio)
    start = Patch.init().apply({"filter_1.on": "on", "filter_1.cutoff_hz": 3000, "global.mono": "on"})
    r = fit(start, tmp_path / "t.wav", ["filter_1.cutoff_hz"], iters=14)
    assert r.best < r.start / 3 and 450 < r.patch.get("filter_1.cutoff_hz") < 800 and r.renders <= 16
    assert r.patch.get("global.mono") == "on"                      # nothing else moved
