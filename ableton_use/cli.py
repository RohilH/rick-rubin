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
    s.add_argument("--no-instruments", action="store_true")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=9877)

    s = sub.add_parser("remember", help="append a session entry to project.md")
    s.add_argument("dir")
    for k in ("strategy", "decisions", "reasoning", "outstanding"):
        s.add_argument(f"--{k}", default="")

    s = sub.add_parser("install-bridge", help="copy the AbletonUse remote script into Live's User Library")
    s.add_argument("--dest", help="Remote Scripts folder (default: your User Library)")

    s = sub.add_parser("status", help="check the Live bridge connection")
    s.add_argument("--port", type=int, default=9877)

    sub.add_parser("templates", help="list subgenres and arrangement templates")

    s = sub.add_parser("agent", help="run the built-in Claude agent on a project")
    s.add_argument("dir")
    s.add_argument("task")
    s.add_argument("--model")
    s.add_argument("--yes", action="store_true", help="auto-approve the plan")

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
        rep = Project(a.dir).push(a.host, a.port, a.replace, not a.no_instruments, progress=lambda m: print("·", m, file=sys.stderr))
        print(rep.text())
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
    elif a.cmd == "agent":
        from .agent import DEFAULT_MODEL, Agent
        confirm = (lambda plan: "approved") if a.yes else (lambda plan: input("\nApprove plan? (enter to approve, or type changes) ") or "approved")
        print(Agent(a.dir, a.task, model=a.model or DEFAULT_MODEL, confirm=confirm).run())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
