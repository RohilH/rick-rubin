"""Logic's Stem Splitter, tested without Logic: the stem names, the source preparation, the split against a fake
bridge that writes stems the way Logic does, and the bridge fixes it needed (which projects are ours to close, where
a new track went). The real Stem Splitter is exercised by hand: see docs/LOGIC.md."""
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

from rick_rubin.logic import bridge as B
from rick_rubin.logic import stems as S
from rick_rubin.samples import read_audio, write_wav24

SR = 44100


def _tone(seconds: float, sr: int = SR) -> np.ndarray:
    t = np.arange(int(seconds * sr)) / sr
    voc = 0.3 * np.sin(2 * np.pi * 440 * t)
    bass = 0.3 * np.sin(2 * np.pi * 55 * t)
    return np.stack([voc + bass, voc + bass], axis=1).astype(np.float32)


def test_stem_names():
    assert S.parse_stems(None) == list(B.STEMS) == S.parse_stems("all")
    assert S.parse_stems("bass, Vocals") == ["Vocals", "Bass"]                 # the dialog's order
    assert S.parse_stems(["drums"]) == ["Drums"]
    with pytest.raises(ValueError, match="stems are"):
        S.parse_stems("vocals,strings")
    assert S.stem_of(Path("song_Vocals.wav"), "song") == "Vocals"
    assert S.stem_of(Path("song_Bass#01.wav"), "song") == "Bass"
    assert S.stem_of(Path("song_Instrumental.wav"), "song") is None            # the submix
    assert S.stem_of(Path("other song_Vocals.wav"), "song") is None


def test_prepare_source_cuts_and_converts(tmp_path):
    src = tmp_path / "in.wav"
    write_wav24(src, SR, _tone(3.0))
    out, sr, secs = S.prepare_source(src, tmp_path / "w" / "a.wav", 0.5, 2.0)
    assert sr == SR and secs == pytest.approx(1.5) and len(read_audio(out)[1]) == int(1.5 * SR)
    out, sr, secs = S.prepare_source(src, tmp_path / "w" / "b.wav")
    assert secs == pytest.approx(3.0) and out.read_bytes() == src.read_bytes()
    with pytest.raises(ValueError, match="empty range"):
        S.prepare_source(src, tmp_path / "w" / "c.wav", 5.0, 6.0)
    if shutil.which("afconvert"):
        aif = tmp_path / "in.aif"
        subprocess.run(["afconvert", "-f", "AIFF", "-d", "BEI16", str(src), str(aif)], check=True)
        out, sr, secs = S.prepare_source(aif, tmp_path / "w" / "d.wav")
        assert out.suffix == ".wav" and sr == SR and secs == pytest.approx(3.0, abs=0.01)


class _App:
    def __init__(self, br):
        self.br = br

    def project_windows(self):
        return list(self.br.open)

    def project_title(self, w=None):
        return w

    def project_path(self, w):
        return self.br.paths.get(w)


class FakeStemBridge:
    """What split_stems sees of Logic: projects, one audio track, and a Stem Splitter that writes
    '<region>_<Stem>.wav' (vocals = the 440 Hz part of the test tone, bass = the 55 Hz part, the rest silent)."""

    def __init__(self, open_projects=()):
        self.open = list(open_projects)
        self.paths: dict[str, Path] = {}
        self.app = _App(self)
        self.project = None
        self.closed: list[str] = []
        self.calls: list[tuple] = []
        self._tracks = ["Source"]

    def close_project(self, title=None, save=False):
        t = title or self.project
        self.open.remove(t)
        self.closed.append(t)
        return True

    def open_midi_project(self, path, expect_tracks=None, close_ours=True, ours=()):
        self.project = "Untitled 1"
        self.open.append(self.project)
        return self.project

    def save_project_as(self, folder, name):
        target = Path(folder) / f"{name}.logicx"
        (target / "Media" / "Audio Files").mkdir(parents=True)
        self.open[self.open.index(self.project)] = self.project = f"{name}.logicx"
        self.package = target
        return target

    def save_project(self):
        self.calls.append(("save",))
        return True

    def tracks(self):
        return list(self._tracks)

    def add_audio_track(self):
        self._tracks.insert(0, "Audio 1")                 # Logic sometimes puts it first
        return 0

    def import_audio(self, ti, path, bar, beat=1, keep_file_rate=False):
        self.calls.append(("import", ti, Path(path).name, keep_file_rate))
        self.source = Path(path)

    def select_region(self, ti, nth=0):
        return self.source.stem

    def stem_split(self, ti, stems, submix=False, timeout=600.0, on_progress=None):
        self.calls.append(("split", ti, tuple(stems), submix))
        sr, x = read_audio(self.source)
        t = np.arange(len(x)) / sr
        parts = {"Vocals": 0.3 * np.sin(2 * np.pi * 440 * t), "Bass": 0.3 * np.sin(2 * np.pi * 55 * t)}
        af = self.package / "Media" / "Audio Files"
        for st in stems:
            y = parts.get(st, np.zeros_like(t))
            write_wav24(af / f"{self.source.stem}_{st}.wav", sr, np.stack([y, y], axis=1))
        if submix:
            rest = sum((parts.get(st, 0 * t) for st in B.STEMS if st not in stems), 0 * t)
            write_wav24(af / f"{self.source.stem}_Instrumental.wav", sr, np.stack([rest, rest], axis=1))
        new = [f"{self.source.stem} (Stems)"] + [f"{self.source.stem} ({st})" for st in stems]
        self._tracks[1:1] = new
        if on_progress:
            on_progress(1.0)
        return new

    def stem_split_progress(self):
        return None

    def pending_alert(self):
        return None


def test_split_stems_against_a_fake_logic(tmp_path):
    src = tmp_path / "refs" / "My Song!.wav"
    src.parent.mkdir()
    write_wav24(src, SR, _tone(4.0))
    out = tmp_path / "stems" / "song"
    out.mkdir(parents=True)
    (out / "guitar.wav").write_bytes(b"stale")                  # from an earlier split: must not survive
    b = FakeStemBridge(open_projects=["Someone Else.logicx", "song stems.logicx"])
    b.paths["song stems.logicx"] = out / "logic" / "song stems.logicx"
    r = S.split_stems(src, out, "vocals,bass,piano", bridge=b)
    assert set(r["stems"]) == {"vocals", "bass", "piano"} and not (out / "guitar.wav").exists()
    assert b.closed == ["song stems.logicx"]                     # our earlier project, not someone else's
    assert "Someone Else.logicx" in b.open
    assert ("import", 0, "My Song_.wav", True) in b.calls        # onto the track Logic actually added
    assert ("split", 0, ("Vocals", "Bass", "Piano"), False) in b.calls
    assert r["silent"] == ["piano"] and r["levels"]["vocals"][0] > -20
    sr, voc = read_audio(r["stems"]["vocals"])
    assert sr == SR and len(voc) == 4 * SR
    assert r["project"] == out / "logic" / "song stems.logicx" and r["seconds"] == pytest.approx(4.0)


def test_split_stems_will_not_close_a_namesake_elsewhere(tmp_path):
    src = tmp_path / "t.wav"
    write_wav24(src, SR, _tone(1.0))
    b = FakeStemBridge(open_projects=["out stems.logicx"])
    b.paths["out stems.logicx"] = tmp_path / "elsewhere" / "out stems.logicx"
    with pytest.raises(B.LogicError, match="another project called"):
        S.split_stems(src, tmp_path / "out", bridge=b)
    assert b.closed == [] and b.calls == []


def test_split_stems_submix_and_range(tmp_path):
    src = tmp_path / "t.wav"
    write_wav24(src, SR, _tone(4.0))
    b = FakeStemBridge()
    r = S.split_stems(src, tmp_path / "out", ["vocals"], submix=True, start_s=1.0, end_s=3.0, bridge=b)
    assert set(r["stems"]) == {"vocals", "submix"} and r["seconds"] == pytest.approx(2.0)
    assert r["levels"]["submix"][0] > -20                          # the bass, which was not asked for
    assert len(read_audio(r["stems"]["submix"])[1]) == 2 * SR


def test_split_refuses_hidden_folders(tmp_path):
    src = tmp_path / "t.wav"
    write_wav24(src, SR, _tone(1.0))
    with pytest.raises(B.LogicError, match="hidden"):
        S.split_stems(src, Path.home() / ".cache" / "stems")              # refused before Logic is reached


def test_new_track_index():
    assert B.first_new_index(["Pad"], ["Audio 1", "Pad"]) == 0
    assert B.first_new_index(["Kick", "Bass"], ["Kick", "Bass", "Audio 1"]) == 2
    assert B.first_new_index(["A", "B"], ["A", "Audio 1", "B"]) == 1


class _AlertApp:
    """Logic asking whether to close the frontmost project before it opens a MIDI file."""

    def __init__(self, current):
        self.current, self.windows_, self.answered = current, [current], []
        self.asking = True

    def project_windows(self):
        return list(self.windows_)

    def project_title(self, w=None):
        return w if w is not None else self.current

    def main_window(self, title=None):
        return title if title in self.windows_ else None

    def alerts(self):
        return ["alert"] if self.asking else []

    def alert_text(self, al):
        return "Do you want to close the current project?"

    def alert_buttons(self, al):
        return ["Close", "Don't Close"]

    def answer(self, al, button):
        button = button.replace("’", "'")
        self.answered.append(button)
        self.asking = False
        if button == "Close":
            self.windows_.remove(self.current)
        self.windows_.append("Untitled 2")
        return True

    def tracks(self, w=None):
        return ["Source"]


@pytest.mark.parametrize("ours", [False, True])
def test_open_midi_project_keeps_the_frontmost_project_unless_ours(monkeypatch, tmp_path, ours):
    monkeypatch.setattr(B.subprocess, "run", lambda *a, **k: None)
    monkeypatch.setattr(B.time, "sleep", lambda *_: None)
    br = B.LogicBridge(use_mcu=False, project="Their Song")       # connect() targets the frontmost project
    br.app = _AlertApp("Their Song")
    if ours:
        br._opened.add("Their Song")                              # a project this bridge opened earlier
    br.open_midi_project(tmp_path / "x.mid", expect_tracks=1)
    assert br.app.answered == (["Close"] if ours else ["Don't Close"])
    assert br.project == "Untitled 2" and "Untitled 2" in br._opened
