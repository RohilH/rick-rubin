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
        """A new song project copied from the scaffold in <repo>/project-template: CLAUDE.md (which imports
        the shared PREFERENCES.md), an empty song.py, project.md and a sample manifest. No musical content."""
        p = cls(root)
        if p.source_path.exists() or p.song_path.exists():
            raise FileExistsError(f"{p.root} already holds a song")
        repo = Path(__file__).resolve().parent.parent
        tpl = repo / "project-template"
        prefs = repo / "PREFERENCES.md"
        fill = {"title": title, "bpm": f"{bpm:g}", "key": key, "repo": str(repo), "prefs": str(prefs), "cli": "ableton-use"}
        (p.root / "samples" / "raw").mkdir(parents=True, exist_ok=True)
        if not tpl.is_dir():                                # installed without the repo around it: bare minimum
            p.source_path.write_text(SONG_PY.format(**fill))
            return p
        for src in sorted(tpl.rglob("*")):
            if src.is_dir() or src.name == ".gitkeep":
                continue
            dst = p.root / src.relative_to(tpl)
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists():
                continue
            text = src.read_text()
            if src.name == "manifest.json" or src.suffix not in (".md", ".py"):
                for k, v in fill.items():                   # json/other: plain replacement, braces are literal there
                    text = text.replace("{" + k + "}", v)
            else:
                text = text.format(**fill)
            dst.write_text(text)
        return p

    def exists(self) -> bool:
        return self.song_path.exists() or self.source_path.exists()

    def _run_source(self) -> Song:
        import contextlib
        import runpy
        if not self.source_path.exists():
            raise FileNotFoundError(f"{self.source_path} not found — `ableton-use init` creates one")
        from . import options
        options.begin()
        with contextlib.chdir(self.root):               # sample paths in song.py are relative to the project
            ns = runpy.run_path(str(self.source_path), run_name="song")
        song = ns.get("song")
        if not isinstance(song, Song):
            raise ValueError(f"{self.source_path} must leave a Song in a variable called `song`")
        if options.unknown():
            raise ValueError(f"song.py has no option called {', '.join(options.unknown())} "
                             f"(it declares: {', '.join(options.declared()) or 'none'})")
        song.meta.pop("options", None)
        song.meta.pop("options_set", None)
        if options.declared():
            song.meta["options"] = options.declared()
        if options.active():
            song.meta["options_set"] = options.active()
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

    def check(self, audio: bool = False) -> tuple[list[tuple[str, bool, str]], int]:
        """Everything that can be wrong with a song project before listening to it, in order:
        Python syntax, ruff (undefined names, likely bugs), mypy (wrong arguments to the API), building
        song.py (structure, missing samples), and the music lint. Returns ([(stage, passed, output)], errors)."""
        import ast
        import shutil as _sh
        import subprocess
        import sys
        stages: list[tuple[str, bool, str]] = []
        errors = 0
        src = self.source_path
        if src.exists():
            try:
                ast.parse(src.read_text(), filename=str(src))
                stages.append(("syntax", True, "ok"))
            except SyntaxError as e:
                stages.append(("syntax", False, f"{src.name}:{e.lineno}: {e.msg}\n    {(e.text or '').rstrip()}"))
                return stages, 1
            bindir = Path(sys.executable).parent
            import os
            env = dict(os.environ)
            # let mypy see the library's own type hints even when it is installed in editable mode
            env["MYPYPATH"] = os.pathsep.join(x for x in (str(Path(__file__).resolve().parent.parent), env.get("MYPYPATH", "")) if x)
            for tool, args in (("ruff", ["check", "--quiet", src.name]),
                               ("mypy", ["--no-error-summary", "--follow-imports=silent", src.name])):
                exe = bindir / tool if (bindir / tool).exists() else _sh.which(tool)
                if not exe:
                    stages.append((tool, True, f"not installed — pip install \"ableton-use[check]\""))
                    continue
                r = subprocess.run([str(exe), *args], cwd=self.root, capture_output=True, text=True, env=env)
                out = (r.stdout + r.stderr).strip()
                stages.append((tool, r.returncode == 0, out or "ok"))
                errors += r.returncode != 0
        try:
            song = self.build() if src.exists() else self.load()
            stages.append(("build", True, f"{len(song.tracks)} tracks, {len(song.patterns)} patterns, {song.total_bars} bars"))
        except Exception as e:  # noqa: BLE001
            stages.append(("build", False, f"{type(e).__name__}: {e}"))
            return stages, errors + 1
        issues = analysis.lint(song)
        n_err = sum(i.severity == "error" for i in issues)
        n_warn = sum(i.severity == "warn" for i in issues)
        stages.append(("music lint", n_err == 0, "\n".join(str(i) for i in issues) or "clean"))
        errors += n_err
        if audio:
            r = self.evaluate()
            stages.append(("audio checks", r.errors == 0, r.text.split("## Audio checks", 1)[-1].strip()))
        _ = n_warn
        return stages, errors

    def tempo(self) -> float:
        """The song's BPM, readable even while song.py still points at samples that are not imported yet."""
        return (self._run_source() if self.source_path.exists() else self.load()).bpm

    def load(self) -> Song:
        if self.source_path.exists() and (not self.song_path.exists()
                                          or self.source_path.stat().st_mtime > self.song_path.stat().st_mtime):
            return self.build()
        song = Song.load(self.song_path)
        if self.source_path.exists():
            from . import options
            if song.meta.get("options_set", {}) != options.active():   # built with other choices switched than this run's
                return self.build()
        return song

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
        from .live.client import live_lock
        with live_lock(f"push {self.root.name}", progress=progress), LiveBridge(host, port) as b:
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
        from .live.client import live_lock
        with live_lock(f"capture {self.root.name}", progress=progress), LiveBridge(host, port) as b:
            return capture_live(self.load(), b, self.zoom_path("live", bars, tracks), bars=bars, tracks=tracks, progress=progress)

    def ab(self, variants: list[tuple[str, dict[str, str]]], bars: tuple[int, int] | None = None,
           tracks: list[str] | None = None, live: bool = False, host: str = "127.0.0.1", port: int = 9889,
           progress=None) -> list[tuple[str, Path]]:
        """Render candidates of the song side by side. Each variant is (label, {option: value}) — the
        `option()` choices in song.py to switch; {} is the song as it stands. Offline (the preview) by default;
        live=True pushes each one to Live and records it, after which Live is left holding the song as it stands.
        Files go to <project>/ab/<label>.wav; song.json is not touched."""
        from . import options
        from .samples import read_audio, write_wav24
        say = progress or (lambda *_: None)
        if not self.source_path.exists():
            raise ValueError("ab needs a song.py with option() choices")
        out: list[tuple[str, Path]] = []
        (self.root / "ab").mkdir(exist_ok=True)
        spbar = 240.0 / self.tempo()

        def build(values):
            with options.using(values):
                song = self._run_source()
            errs = song.validate()
            if errs:
                raise ValueError(f"{values}: song.py builds an invalid song:\n  " + "\n  ".join(errs))
            return song

        if live:
            from .live import LiveBridge, capture_live, push_song
            from .live.client import live_lock
            with live_lock(f"ab {self.root.name}", progress=progress), LiveBridge(host, port) as b:
                last = None
                for label, values in variants:
                    say(f"{label}: push")
                    rep = push_song(build(values), b, replace=True, clean=True)
                    for w in rep.warnings:
                        say(f"{label}: ! {w}")
                    last = values
                    dst = self.root / "ab" / f"{label}.wav"
                    capture_live(build(values), b, dst, bars=bars, tracks=tracks, progress=lambda m, label=label: say(f"{label}: {m}"))
                    out.append((label, dst))
                if last:                                   # leave Live holding the song as it stands
                    say("restoring the song as it stands in Live")
                    push_song(build({}), b, replace=True, clean=True)
            return out
        for label, values in variants:
            say(f"{label}: render")
            dst = self.root / "ab" / f"{label}.wav"
            render_preview(build(values), dst, tracks=tracks)
            if bars:
                sr, x = read_audio(dst)
                write_wav24(dst, sr, x[int((bars[0] - 1) * spbar * sr): int(bars[1] * spbar * sr)])
            out.append((label, dst))
        return out

    def hits(self, bars: tuple[int, int] | None = None, tracks: list[str] | None = None, wav: str | Path | None = None,
             live: bool = False, grid: int = 16, wav_start_bar: int | None = None, progress=None) -> str:
        """Level of every grid step, bar by bar — are the accents and ghost notes that were written the ones
        that come out? Source: `wav` (a file starting on the downbeat of `wav_start_bar`), else a Live capture of
        `tracks` soloed (live=True), else the offline preview of those tracks. With one track, its written
        velocities are printed under each bar."""
        from .model import BEATS_PER_BAR
        from .samples import read_audio
        song = self.load()
        b0, b1 = bars or (1, min(song.total_bars, 8))
        if wav is not None:
            path = Path(wav) if Path(wav).exists() else self.root / wav
            start_bar = wav_start_bar or 1
            src = path.name
        elif live:
            r = self.capture((b0, b1), tracks, progress=progress)
            path, start_bar, src = r["path"], b0, "Live capture"
        else:
            path = self.zoom_path("preview", None, tracks)
            render_preview(song, path, tracks=tracks)
            start_bar, src = 1, "offline preview"
        sr, x = read_audio(path)
        spbar = 240.0 / song.bpm
        a = int(max(0, b0 - start_bar) * spbar * sr)
        seg = x[a: a + int((b1 - b0 + 1) * spbar * sr)]
        levels = analysis.hit_levels(seg, sr, song.bpm, grid)
        vel = None
        if tracks and len(tracks) == 1:
            vel = [[None] * grid for _ in range(b1 - b0 + 1)]
            step = BEATS_PER_BAR / grid
            for c in song.flatten(sounding=True)[0]:
                if c.track != tracks[0]:
                    continue
                for n in c.notes:
                    k = int(round((c.start + n.start) / step)) - (b0 - 1) * grid
                    if 0 <= k < grid * len(vel):
                        cur = vel[k // grid][k % grid]
                        vel[k // grid][k % grid] = max(cur or 0, int(n.vel))
        what = ", ".join(x_ for x_ in (f"bars {b0}-{b1}", "solo " + " ".join(tracks) if tracks else "full mix") if x_)
        return f"# Hit levels — {what} ({src}), 1/{grid} steps, peak dBFS\n" + analysis.hits_text(levels, b0, vel)

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
