"""Project folder = one track's working directory (cf. video-use's <videos_dir>/edit/).

<project>/
├── song.json        ← source of truth (the 'EDL')
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

from . import analysis, edits, house, score, views
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

    @classmethod
    def create(cls, root: str | Path, song: Song | None = None, **gen_kwargs) -> "Project":
        p = cls(root)
        p.root.mkdir(parents=True, exist_ok=True)
        if p.song_path.exists():
            raise FileExistsError(f"{p.song_path} exists — open it with Project(...) instead")
        p.save(song or house.generate(**gen_kwargs), snapshot=False)
        return p

    def exists(self) -> bool:
        return self.song_path.exists()

    def load(self) -> Song:
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
        song = self.load()
        log = edits.apply(song, ops)
        self.save(song)
        return log

    def score(self) -> str:
        song = self.load()
        text = score.pack(song)
        self.score_path.write_text(text)
        return text

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

    def view(self, bars: tuple[int, int] | None = None, tracks: list[str] | None = None) -> Path:
        song = self.load()
        b = bars or (1, song.total_bars)
        wav = self.preview_path if self.preview_path.exists() else None
        return views.timeline_view(song, self.root / "views" / f"bars_{b[0]:03d}-{b[1]:03d}.png", b, wav, tracks)

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
        return import_sample(self.root, src, name, loop=loop, src_bpm=src_bpm, bpm=self.load().bpm, bars=bars,
                             align=align, melodic=melodic, end_at=end_at)

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


def dump(obj) -> str:
    return json.dumps(obj, indent=2, default=str)
