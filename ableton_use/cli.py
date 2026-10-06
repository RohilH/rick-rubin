"""ableton-use command line. Every command takes a project folder."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .project import Project


def _bars(s: str) -> tuple[int, int]:
    a, _, b = s.partition("-")
    return int(a), int(b or a)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="ableton-use", description="Agentic house-music production rendered to Ableton Live.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="start a project: an empty song.py to write the song in")
    s.add_argument("dir")
    s.add_argument("--title", required=True)
    s.add_argument("--bpm", type=float, required=True)
    s.add_argument("--key", required=True, help='e.g. "F minor", "D dorian"')

    s = sub.add_parser("build", help="run song.py and refresh song.json + score.md (other commands do this automatically)")
    s.add_argument("dir")

    def zoom(sp):
        sp.add_argument("--bars", type=_bars, help="zoom in on a bar range, e.g. 33-48")
        sp.add_argument("--tracks", nargs="*", help="zoom in on these tracks only")

    s = sub.add_parser("score", help="print the packed score (and refresh score.md); --bars/--tracks print a zoomed score")
    s.add_argument("dir")
    zoom(s)

    s = sub.add_parser("capture", help="record the pushed arrangement from Live's own output (real time) and measure it")
    s.add_argument("dir")
    zoom(s)
    s.add_argument("--port", type=int, default=9889)

    for name, hlp in (("midi", "export song.mid + per-track .mid"),
                      ("undo", "revert the last edit batch"),
                      ("info", "one-line JSON summary")):
        sub.add_parser(name, help=hlp).add_argument("dir")

    s = sub.add_parser("edit", help="apply JSON edit ops from a file or '-' (stdin)")
    s.add_argument("dir")
    s.add_argument("ops")

    s = sub.add_parser("preview", help="render preview.wav")
    s.add_argument("dir")
    s.add_argument("--stems", action="store_true")

    s = sub.add_parser("eval", help="lint + render + measure -> eval.md")
    s.add_argument("dir")
    s.add_argument("--no-audio", action="store_true")
    s.add_argument("--live", action="store_true", help="measure live.wav (from `capture`) instead of rendering the preview")
    zoom(s)

    s = sub.add_parser("view", help="timeline PNG for a bar range, e.g. --bars 65-80")
    s.add_argument("dir")
    s.add_argument("--bars", type=_bars)
    s.add_argument("--tracks", nargs="*")

    s = sub.add_parser("push", help="render into Ableton Live via the bridge")
    s.add_argument("dir")
    s.add_argument("--replace", action="store_true", help="delete same-named tracks first")
    s.add_argument("--clean", action="store_true", help="also remove the set's untouched empty tracks (Live Intro/Lite have a 16/8-track limit)")
    s.add_argument("--no-instruments", action="store_true")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=9889)

    s = sub.add_parser("sample", help="import a one-shot or loop into <dir>/samples/ (loops are conformed to the song tempo)")
    s.add_argument("dir")
    s.add_argument("src")
    s.add_argument("--name", required=True)
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--loop", action="store_true", help="tempo-match and cut to whole bars; plays on an audio track")
    g.add_argument("--oneshot", action="store_true", help="copy as-is; plays in a Simpler")
    s.add_argument("--src-bpm", type=float, help="tempo of the source loop")
    s.add_argument("--bars", type=int, help="loop length in bars (default: nearest whole bar)")
    s.add_argument("--align", default="start", choices=["start", "end"], help="'end' keeps the tail (risers)")
    s.add_argument("--end-at", type=float, help="seconds into the loop to cut at first; with --align end, puts that moment (a riser's peak) on the next downbeat")
    s.add_argument("--melodic", action="store_true", help="measure the one-shot's pitch (sample_root)")

    s = sub.add_parser("transcribe", help="words of a vocal sample with their bar.beat.sixteenth positions (cached; shown in score.md)")
    s.add_argument("dir")
    s.add_argument("sample", help="project-relative path, e.g. samples/vocal.wav")
    s.add_argument("--bpm", type=float, help="tempo to map onto (default: the song's — right for conformed loops)")
    s.add_argument("--model", default="small.en", help="Whisper model: tiny.en, base.en, small.en, medium.en, or multilingual names")
    s.add_argument("--language")

    s = sub.add_parser("width", help="stereo image report: correlation, side %, mono loss, per band and per section")
    s.add_argument("dir")
    s.add_argument("wav", nargs="?", help="file to analyse (default: live.wav if captured, else preview.wav); a sample path gets a whole-file report")
    s.add_argument("--bars", type=_bars, help="zoom in on a bar range of the mix")

    s = sub.add_parser("serum", help="read Serum 2 presets: `serum list` to find one, `serum show NAME` for its patch sheet")
    s.add_argument("action", choices=["list", "show"])
    s.add_argument("name", nargs="?", help="show: preset name, words from it, or a .SerumPreset path")
    s.add_argument("--search", help="list: words that must appear in the name, description, author or folder")
    s.add_argument("--tag", help="list: Wavetable | Poly | Mono | Multisample | Sample | Granular | Spectral | Arp | Clip")
    s.add_argument("--folder", help="list: e.g. Pads, Bass, Leads")
    s.add_argument("--root", help="preset folder (default: Serum 2's own)")

    s = sub.add_parser("remember", help="append a session entry to project.md")
    s.add_argument("dir")
    for k in ("strategy", "decisions", "reasoning", "outstanding"):
        s.add_argument(f"--{k}", default="")

    s = sub.add_parser("install-bridge", help="copy the AbletonUse remote script into Live's User Library")
    s.add_argument("--dest", help="Remote Scripts folder (default: your User Library)")

    s = sub.add_parser("status", help="check the Live bridge connection")
    s.add_argument("--port", type=int, default=9889)

    a = ap.parse_args(argv)

    if a.cmd == "init":
        p = Project.init(a.dir, a.title, a.bpm, a.key)
        print(f"created {p.source_path}\nWrite the song there (SKILL.md, 'Writing a song'), then: ableton-use score {a.dir}")
    elif a.cmd == "build":
        p = Project(a.dir)
        song = p.build()
        print(f"built {p.song_path.name}: {len(song.tracks)} tracks, {len(song.patterns)} patterns, {song.total_bars} bars")
    elif a.cmd == "score":
        print(Project(a.dir).score(a.bars, a.tracks))
    elif a.cmd == "info":
        print(json.dumps(Project(a.dir).summary()))
    elif a.cmd == "midi":
        for path in Project(a.dir).midi():
            print(path)
    elif a.cmd == "undo":
        print("restored", Project(a.dir).undo())
    elif a.cmd == "edit":
        raw = sys.stdin.read() if a.ops == "-" else Path(a.ops).read_text()
        for line in Project(a.dir).edit(json.loads(raw)):
            print(line)
    elif a.cmd == "preview":
        r = Project(a.dir).preview(stems=a.stems)
        print(f"{r.path} ({r.duration_s:.1f}s)" + (f", {len(r.stems)} stems" if r.stems else ""))
    elif a.cmd == "capture":
        from .analysis import measure, measurement_table, stereo_report
        p = Project(a.dir)
        r = p.capture(a.bars, a.tracks, port=a.port, progress=lambda m: print("·", m, file=sys.stderr))
        song = p.load()
        m = measure(r["path"], song, bars=a.bars, file_start_bar=r["bars"][0])
        what = ", ".join(x for x in (f"bars {r['bars'][0]}-{r['bars'][1]}", "solo " + " ".join(a.tracks) if a.tracks else "") if x)
        print(f"# Live capture — {what}\n{r['path']}  ({r['seconds']:.1f} s, {m.integrated_lufs:.1f} LUFS, peak {m.peak_db:.1f} dBFS, "
              f"{m.clipped_samples} clipped samples)\n")
        print("\n".join(measurement_table(m)))
        print("\n".join(str(i) for i in m.issues))
        print()
        print(stereo_report(r["path"], song, a.bars, r["bars"][0]))
        print("view:", p.view(a.bars, a.tracks, wav=r["path"], wav_start_bar=r["bars"][0]))
    elif a.cmd == "eval" and (a.bars or a.tracks or a.live):
        from .analysis import measure, measurement_table
        p = Project(a.dir)
        if a.live:
            if a.tracks:
                ap.error("--live measures Live's full mix; use `capture --tracks ...` to record a solo")
            wav, m = p.live_path, measure(p.live_path, p.load(), bars=a.bars)
        else:
            wav, m = p.measure_zoom(a.bars, a.tracks)
        what = ", ".join(x for x in (f"bars {a.bars[0]}-{a.bars[1]}" if a.bars else "", "tracks " + " ".join(a.tracks) if a.tracks else "") if x) or "whole song"
        print(f"# Measured — {what} ({'Live capture' if a.live else 'offline preview'}: {wav.name})")
        print(f"{m.integrated_lufs:.1f} LUFS, peak {m.peak_db:.1f} dBFS\n")
        print("\n".join(measurement_table(m)))
        print("\n".join(str(i) for i in m.issues))
    elif a.cmd == "eval":
        r = Project(a.dir).evaluate(audio=not a.no_audio)
        print(r.text)
        return 1 if r.errors else 0
    elif a.cmd == "view":
        print(Project(a.dir).view(a.bars, a.tracks))
    elif a.cmd == "push":
        rep = Project(a.dir).push(a.host, a.port, a.replace, not a.no_instruments, clean=a.clean, progress=lambda m: print("·", m, file=sys.stderr))
        print(rep.text())
    elif a.cmd == "sample":
        if a.loop and not a.src_bpm:
            ap.error("--loop needs --src-bpm (the tempo the loop was recorded at)")
        r = Project(a.dir).add_sample(a.src, a.name, loop=a.loop, src_bpm=a.src_bpm, bars=a.bars, align=a.align, melodic=a.melodic, end_at=a.end_at)
        print(r.describe())
        var = "".join(ch if ch.isalnum() else "_" for ch in a.name)
        if r.kind == "loop":
            print("in song.py:")
            print(f'  {var}_trk = song.add_track("{a.name.title()}", "perc", audio=True)')
            print(f'  {var} = song.pattern("{a.name}", {var}_trk, audio="{r.rel}", bars={r.bars})')
        else:
            root = f", sample_root={r.root:.2f}" if r.root is not None else ""
            print(f'in song.py:  song.add_track("{a.name.title()}", "<role>", sample="{r.rel}"{root})')
    elif a.cmd == "serum":
        from . import serum
        if a.action == "show":
            if not a.name:
                ap.error("serum show needs a preset name")
            print(serum.sheet(serum.find(a.name, a.root)))
        else:
            rows = serum.catalog(a.root, a.search or a.name, a.tag, a.folder)
            for r in rows:
                print(f"{r.folder + '/' if r.folder else ''}{r.name}  [{', '.join(r.tags)}]" + (f"  — {r.description}" if r.description else ""))
            print(f"{len(rows)} presets")
    elif a.cmd == "remember":
        Project(a.dir).remember(a.strategy, a.decisions, a.reasoning, a.outstanding)
        print("ok")
    elif a.cmd == "install-bridge":
        from .live import install_bridge
        t = install_bridge(a.dest)
        print(f"installed to {t}\nRestart Live, then Settings > Link, Tempo & MIDI > Control Surface: AbletonUse")
    elif a.cmd == "status":
        from .live import LiveBridge
        with LiveBridge(port=a.port) as b:
            print(json.dumps(b.call("ping")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
