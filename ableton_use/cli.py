"""ableton-use command line. Every command takes a project folder."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import house
from .project import Project


def _bars(s: str) -> tuple[int, int]:
    a, _, b = s.partition("-")
    return int(a), int(b or a)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="ableton-use", description="Agentic house-music production rendered to Ableton Live.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("new", help="create a project with a generated house track")
    s.add_argument("dir")
    s.add_argument("--subgenre", default="classic", choices=sorted(house.PROFILES))
    s.add_argument("--template", default="club", choices=sorted(house.TEMPLATES))
    s.add_argument("--key")
    s.add_argument("--bpm", type=float)
    s.add_argument("--seed", type=int, default=0)
    s.add_argument("--title")
    s.add_argument("--progression", help="scale degrees, e.g. '1 6 4 5'")

    for name, hlp in (("score", "print the packed score (and refresh score.md)"),
                      ("midi", "export song.mid + per-track .mid"),
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

    s = sub.add_parser("remember", help="append a session entry to project.md")
    s.add_argument("dir")
    for k in ("strategy", "decisions", "reasoning", "outstanding"):
        s.add_argument(f"--{k}", default="")

    s = sub.add_parser("install-bridge", help="copy the AbletonUse remote script into Live's User Library")
    s.add_argument("--dest", help="Remote Scripts folder (default: your User Library)")

    s = sub.add_parser("status", help="check the Live bridge connection")
    s.add_argument("--port", type=int, default=9889)

    sub.add_parser("templates", help="list subgenres and arrangement templates")

    a = ap.parse_args(argv)

    if a.cmd == "new":
        prog = [int(x) for x in a.progression.split()] if a.progression else None
        p = Project.create(a.dir, subgenre=a.subgenre, template=a.template, key=a.key, bpm=a.bpm, seed=a.seed,
                           title=a.title, progression=prog)
        print(f"created {p.song_path}\n")
        print(p.score_path.read_text())
    elif a.cmd == "score":
        print(Project(a.dir).score())
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
        if r.kind == "loop":
            hint = [{"op": "track", "name": "<Track>", "set": {"role": "perc", "audio": True}},
                    {"op": "pattern", "name": a.name, "track": "<Track>", "audio": r.rel, "bars": r.bars},
                    {"op": "part", "section": "<section>", "track": "<Track>", "pattern": a.name}]
        else:
            fields = {"sample": r.rel}
            if r.root is not None:
                fields["sample_root"] = round(r.root, 2)
            hint = [{"op": "track", "name": "<Track>", "set": fields}]
        print("use it with:  " + json.dumps({"ops": hint}))
    elif a.cmd == "width":
        from .analysis import stereo_report
        p = Project(a.dir)
        if a.wav:
            wav = Path(a.wav) if Path(a.wav).exists() else p.root / a.wav
            full_mix = wav.resolve() in (p.live_path.resolve(), p.preview_path.resolve())
        else:
            wav, full_mix = (p.live_path if p.live_path.exists() else p.preview_path), True
            if wav == p.preview_path:
                print("(no Live capture yet — this is the offline sketch, whose stems are mono; width only reflects panning)\n")
        text = stereo_report(wav, p.load() if full_mix else None)
        if full_mix:
            (p.root / "width.md").write_text(text)
        print(text)
    elif a.cmd == "transcribe":
        from .transcribe import transcribe
        p = Project(a.dir)
        song = p.load()
        words = transcribe(song.resolve(a.sample), a.bpm or song.bpm, a.model, a.language)
        print(f"{a.sample} at {a.bpm or song.bpm:g} BPM — {len(words)} words")
        print("pos (bar.beat.16th)  offset   time            conf  word")
        for w in words:
            print(f"{w.pos:<20} {w.off_ms:+6.0f}ms {w.start_s:6.2f}-{w.end_s:5.2f}s   {w.conf:.2f}  {w.text}")
        p.score()
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
    elif a.cmd == "templates":
        for n, pr in house.PROFILES.items():
            print(f"subgenre {n:8s} {pr.bpm:g} BPM, {pr.scale}, bass={pr.bass_style}, chords={pr.chord_style}, hats={pr.hat_style}")
        for n, t in house.TEMPLATES.items():
            print(f"template {n:8s} " + " ".join(f"{s['name']}:{s['bars']}" for s in t) + f"  = {sum(s['bars'] for s in t)} bars")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
