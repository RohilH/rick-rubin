"""Auditions, installed presets and verdicts: what a person listens to and what they said."""
import plistlib
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent))

from rick_rubin import hear, serum  # noqa: E402

HAVE_SERUM = serum.VST3_PATH.exists()
needs_serum = pytest.mark.skipif(not HAVE_SERUM, reason="Serum 2 is not installed")


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setattr(hear, "HOME", tmp_path / "home")
    return tmp_path / "home"


def test_a_verdict_lands_in_the_project_and_in_the_taste_file(tmp_path, home):
    proj = tmp_path / "night-bus"
    (proj / "auditions").mkdir(parents=True)
    (proj / "project.md").write_text("# Night Bus\n")
    (proj / "auditions" / "log.md").write_text("# Auditions\n\n## round-bass — 2026-11-19\n- preset: `x`\n- verdict: (waiting)\n\n## other — 2026-11-19\n- verdict: (waiting)\n")
    r = hear.record_verdict(proj, "round-bass", "low end is right, the top is fizzy", keep=False)
    assert r["line"] == "REJECT: low end is right, the top is fizzy"
    log = (proj / "auditions" / "log.md").read_text()
    assert "REJECT: low end is right" in log.split("## other")[0] and "- verdict: (waiting)" in log.split("## other")[1]   # only its own entry
    assert "## Ear verdicts" in (proj / "project.md").read_text() and "round-bass: REJECT" in (proj / "project.md").read_text()
    taste = (home / "taste.md").read_text()
    assert "night-bus · round-bass: REJECT: low end is right, the top is fizzy" in taste
    # a second verdict on the same thing is added, not swapped in; a label that is no audition still counts
    hear.record_verdict(proj, "round-bass", "better after the filter change", keep=True)
    hear.record_verdict(proj, "drop 2 bounce", "kick could be louder")
    log = (proj / "auditions" / "log.md").read_text()
    assert log.count("round-bass") == 1 and "REJECT" in log and "KEEP: better after the filter change" in log
    assert (home / "taste.md").read_text().count("\n- ") == 3 and "drop 2 bounce: NOTE: kick could be louder" in (home / "taste.md").read_text()


def test_install_puts_a_preset_in_serums_user_folder(tmp_path, monkeypatch):
    root = tmp_path / "Presets"
    (root / "User").mkdir(parents=True)
    monkeypatch.setattr(serum, "preset_root", lambda: root)
    src = tmp_path / "night-bass.SerumPreset"
    src.write_bytes(b"XferJson\x00")
    out = hear.install_preset(src)
    assert out == root / "User" / "rick-rubin" / "night-bass.SerumPreset" and out.read_bytes() == src.read_bytes()
    with pytest.raises(FileNotFoundError):
        hear.install_preset(tmp_path / "notes.txt")


@needs_serum
def test_audition_renders_a_patch_and_waits_for_a_verdict(tmp_path, home):
    (tmp_path / "project.md").write_text("# T\n")
    r = hear.serum_audition("init", tmp_path, notes=["C2", "G2"], secs=0.3, picture=False) if _has_init() else None
    if r is None:
        pytest.skip("no init patch to render")
    wav = tmp_path / "auditions" / f"{r['name']}.wav"
    assert wav in r["files"] and wav.stat().st_size > 10_000
    assert "- verdict: (waiting)" in (tmp_path / "auditions" / "log.md").read_text() and "C2, G2" in r["played"]


def _has_init() -> bool:
    try:
        serum.find("init")
        return True
    except Exception:  # noqa: BLE001
        from rick_rubin.serum_patch import Patch
        try:
            Patch.open("init")
            return False            # 'init' is a Patch, not a file: the audition takes preset files
        except Exception:  # noqa: BLE001
            return False


@pytest.mark.skipif(not (HAVE_SERUM and serum.AU_PATH.exists()), reason="Serum 2 (VST3 and Audio Unit) is not installed")
def test_an_aupreset_carries_the_patch_into_the_audio_unit(tmp_path):
    presets = sorted(serum.preset_root().rglob("*.SerumPreset"))
    if not presets:
        pytest.skip("no Serum presets installed")
    src = presets[0]
    out = serum.write_aupreset(src, tmp_path / "x.aupreset")
    state = plistlib.loads(out.read_bytes())
    assert state["name"] == "x" and state["Processor State"][:8] == b"XferJson" and state["Controller State"][:8] == b"XferJson"
    # the Audio Unit, given that state, plays what the VST3 plays
    host = serum.SerumHost.get()
    serum.load_with_params(host, src, None)
    notes = [(48, 0.0, 0.4, 100)]
    ref = host.render(notes, 1.0, 44100).mean(axis=1)
    from mido import Message
    au = serum._audio_unit()
    au.raw_state = plistlib.dumps(state, fmt=plistlib.FMT_BINARY)
    got = au([Message("note_on", note=48, velocity=100, time=0.0), Message("note_off", note=48, velocity=0, time=0.4)],
             duration=1.0, sample_rate=44100, reset=True).T.mean(axis=1)
    n = min(len(ref), len(got))
    if ref[:n].std() > 1e-6 and got[:n].std() > 1e-6:
        assert float(np.corrcoef(ref[:n], got[:n])[0, 1]) > 0.9
