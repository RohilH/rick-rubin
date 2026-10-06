"""Project folder = one track's working directory (cf. video-use's <videos_dir>/edit/).

<project>/
├── song.py          ← source of truth: the song, written in Python (ableton_use.Song API)
├── song.json        ← built from song.py (what every other tool reads)
├── score.md         ← packed score, the LLM's primary reading view (regenerated on every save)
├── eval.md          ← latest self-eval report
├── project.md       ← memory: one section appended per session
├── preview.wav      ← offline sketch render
├── stems/           ← optional per-track preview stems
├── midi/            ← song.mid + one .mid per track
├── views/           ← on-demand timeline PNGs
└── history/         ← song.json snapshot before every edit batch (undo)
"""
from __future__ import annotations

import datetime as _dt
import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from . import analysis, edits, score, views
from .model import Song
from .render.midi import export_midi
from .render.preview import render_preview


@dataclass
class EvalResult:
    text: str
    errors: int
    warnings: int
    path: Path


class Project:
    def __init__(self, root: str | Path):
        self.root = Path(root).expanduser().resolve()

    # paths
    @property
    def song_path(self) -> Path: return self.root / "song.json"
    @property
    def score_path(self) -> Path: return self.root / "score.md"
    @property
    def eval_path(self) -> Path: return self.root / "eval.md"
    @property
    def memory_path(self) -> Path: return self.root / "project.md"
    @property
    def preview_path(self) -> Path: return self.root / "preview.wav"

    @property
    def live_path(self) -> Path: return self.root / "live.wav"      # audio recorded from Live's master (`capture`)

    @property
    def source_path(self) -> Path: return self.root / "song.py"

    @classmethod
    def create(cls, root: str | Path, song: Song) -> "Project":
        """A project around an existing Song object (no song.py)."""
        p = cls(root)
        p.root.mkdir(parents=True, exist_ok=True)
        if p.song_path.exists():
            raise FileExistsError(f"{p.song_path} exists — open it with Project(...) instead")
        p.save(song, snapshot=False)
        return p

    @classmethod
    def init(cls, root: str | Path, title: str, bpm: float, key: str) -> "Project":
        """A new project with an empty song.py to write the song in."""
        p = cls(root)
        (p.root / "samples").mkdir(parents=True, exist_ok=True)
        if p.source_path.exists() or p.song_path.exists():
            raise FileExistsError(f"{p.root} already holds a song")
        p.source_path.write_text(SONG_PY.format(title=title, bpm=f"{bpm:g}", key=key))
        return p

    def exists(self) -> bool:
        return self.song_path.exists() or self.source_path.exists()

    def _run_source(self) -> Song:
        import contextlib
        import runpy
        if not self.source_path.exists():
            raise FileNotFoundError(f"{self.source_path} not found — `ableton-use init` creates one")
        with contextlib.chdir(self.root):               # sample paths in song.py are relative to the project
            ns = runpy.run_path(str(self.source_path), run_name="song")
        song = ns.get("song")
        if not isinstance(song, Song):
            raise ValueError(f"{self.source_path} must leave a Song in a variable called `song`")
        song.base_dir = self.root
        return song

    def build(self) -> Song:
        """Run song.py and write song.json + score.md from the `song` it defines."""
        import os
        song = self._run_source()
        errs = song.validate()
        if errs:
            raise ValueError("song.py builds an invalid song:\n  " + "\n  ".join(errs))
        self.save(song, snapshot=False)
        os.utime(self.song_path)
        return song

    def tempo(self) -> float:
        """The song's BPM, readable even while song.py still points at samples that are not imported yet."""
        return (self._run_source() if self.source_path.exists() else self.load()).bpm

    def load(self) -> Song:
        if self.source_path.exists() and (not self.song_path.exists()
                                          or self.source_path.stat().st_mtime > self.song_path.stat().st_mtime):
            return self.build()
        return Song.load(self.song_path)

    def save(self, song: Song, snapshot: bool = True) -> None:
        if snapshot and self.song_path.exists():
            h = self.root / "history"
            h.mkdir(exist_ok=True)
            n = len(list(h.glob("song.*.json")))
            shutil.copy(self.song_path, h / f"song.{n:03d}.json")
        song.save(self.song_path)
        self.score_path.write_text(score.pack(song))

    def undo(self) -> str:
        h = sorted((self.root / "history").glob("song.*.json"))
        if not h:
            raise FileNotFoundError("nothing to undo")
        shutil.copy(h[-1], self.song_path)
        h[-1].unlink()
        self.score_path.write_text(score.pack(self.load()))
        return h[-1].name

    # actions
    def edit(self, ops) -> list[str]:
        if self.source_path.exists():
            raise ValueError(f"this project is written in {self.source_path.name}: edit that file, the next command rebuilds it")
        song = self.load()
        log = edits.apply(song, ops)
        self.save(song)
        return log

    def score(self, bars: tuple[int, int] | None = None, tracks: list[str] | None = None) -> str:
        song = self.load()
        self.score_path.write_text(score.pack(song))
        return score.pack(song, bars=bars, tracks=tracks)

    def preview(self, stems: bool = False):
        return render_preview(self.load(), self.preview_path, stems_dir=self.root / "stems" if stems else None)

    def evaluate(self, audio: bool = True, render: bool = True) -> EvalResult:
        song = self.load()
        issues = analysis.lint(song)
        meas = None
        if audio and not any(i.severity == "error" for i in issues):
            if render or not self.preview_path.exists() or self.preview_path.stat().st_mtime < self.song_path.stat().st_mtime:
                render_preview(song, self.preview_path)
            meas = analysis.measure(self.preview_path, song)
        text = analysis.report(song, issues, meas)
        self.eval_path.write_text(text)
        all_i = issues + (meas.issues if meas else [])
        return EvalResult(text, sum(i.severity == "error" for i in all_i), sum(i.severity == "warn" for i in all_i), self.eval_path)

    def view(self, bars: tuple[int, int] | None = None, tracks: list[str] | None = None,
             wav: str | Path | None = None, wav_start_bar: int = 1) -> Path:
        """Timeline PNG. The audio rows show `wav` if given, else Live's capture if there is one, else the preview."""
        song = self.load()
        b = bars or (1, song.total_bars)
        if wav is None:
            wav = self.live_path if self.live_path.exists() and self.live_path.stat().st_mtime >= self.song_path.stat().st_mtime \
                else self.preview_path if self.preview_path.exists() else None
        name = f"bars_{b[0]:03d}-{b[1]:03d}" + ("_" + "+".join(tracks) if tracks else "") + ("" if wav is None else "_" + Path(wav).stem.split("_")[0])
        return views.timeline_view(song, self.root / "views" / f"{name}.png", b, wav, tracks, wav_start_bar)

    def midi(self) -> list[Path]:
        return export_midi(self.load(), self.root / "midi")

    def push(self, host: str = "127.0.0.1", port: int = 9889, replace: bool = False, load_instruments: bool = True, progress=None, clean: bool = False):
        from .live import LiveBridge, push_song
        with LiveBridge(host, port) as b:
            return push_song(self.load(), b, replace=replace, load_instruments=load_instruments, progress=progress, clean=clean)

    def add_sample(self, src: str | Path, name: str, *, loop: bool = False, src_bpm: float | None = None,
                   bars: int | None = None, align: str = "start", melodic: bool = False, end_at: float | None = None):
        """Copy/conform a sample into <project>/samples/ at the song's tempo."""
        from .samples import import_sample
        return import_sample(self.root, src, name, loop=loop, src_bpm=src_bpm, bpm=self.tempo(), bars=bars,
                             align=align, melodic=melodic, end_at=end_at)

    def zoom_path(self, prefix: str, bars: tuple[int, int] | None, tracks: list[str] | None) -> Path:
        """File name for audio of a bar range and/or a set of tracks, e.g. live_bars_033-048_Bass+Kick.wav."""
        if not bars and not tracks:
            return self.root / f"{prefix}.wav"
        name = prefix + (f"_bars_{bars[0]:03d}-{bars[1]:03d}" if bars else "") + ("_" + "+".join(tracks) if tracks else "")
        return self.root / "zoom" / f"{name}.wav"

    def measure_zoom(self, bars: tuple[int, int] | None = None, tracks: list[str] | None = None):
        """Measure a bar range and/or a subset of tracks of the offline preview."""
        song = self.load()
        wav = self.zoom_path("preview", None, tracks)
        render_preview(song, wav, tracks=tracks)
        return wav, analysis.measure(wav, song, bars=bars)

    def capture(self, bars: tuple[int, int] | None = None, tracks: list[str] | None = None,
                host: str = "127.0.0.1", port: int = 9889, progress=None) -> dict:
        """Record the pushed arrangement from Live's master into live.wav (or zoom/live_bars_...wav)."""
        from .live import LiveBridge, capture_live
        with LiveBridge(host, port) as b:
            return capture_live(self.load(), b, self.zoom_path("live", bars, tracks), bars=bars, tracks=tracks, progress=progress)

    # memory
    def remember(self, strategy: str = "", decisions: str = "", reasoning: str = "", outstanding: str = "") -> None:
        existing = self.memory_path.read_text() if self.memory_path.exists() else f"# {self.load().title} — project memory\n"
        n = existing.count("\n## Session ") + 1
        today = _dt.date.today().isoformat()
        block = [f"\n## Session {n} — {today}\n"]
        for label, val in (("Strategy", strategy), ("Decisions", decisions), ("Reasoning log", reasoning), ("Outstanding", outstanding)):
            if val:
                block.append(f"**{label}:** {val}\n")
        self.memory_path.write_text(existing.rstrip() + "\n" + "\n".join(block))

    def memory(self) -> str:
        return self.memory_path.read_text() if self.memory_path.exists() else ""

    def summary(self) -> dict:
        song = self.load()
        return {"title": song.title, "bpm": song.bpm, "key": song.key, "bars": song.total_bars,
                "duration_s": round(song.duration_s, 1), "tracks": [t.name for t in song.tracks],
                "sections": [f"{s.name}({s.bars})" for s in song.sections]}


SONG_PY = '''"""{title}

The whole song lives in this file. Every other command (score, eval, view, push, capture...)
rebuilds from it. Notation and API: SKILL.md, "Writing a song".
"""
from ableton_use import Song

song = Song("{title}", bpm={bpm}, key="{key}", swing=50)

# tracks    kick = song.add_track("Kick", "kick", sample="samples/kick.wav", volume_db=-7)
# patterns  four = song.pattern("four", kick, "x...x...x...x...")
# sections  intro = song.add_section("intro", 8, energy=3, parts={{kick: four}})
'''


def dump(obj) -> str:
    return json.dumps(obj, indent=2, default=str)
