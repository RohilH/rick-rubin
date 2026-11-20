"""Things for a person to listen to, and what they said about them.

The agent measures; it does not hear. So a sound it designs is not finished until a person has listened:
`serum audition` writes a short render of a patch (a few notes, or a track's own part for some bars) next
to a picture of the patch, `serum install` puts a designed preset where Serum's own browser shows it, and
`verdict` records what the person said — in the project's log and in a taste file every later session reads
(~/.rick-rubin/taste.md).
"""
from __future__ import annotations

import re
import shutil
import subprocess
from datetime import date
from pathlib import Path

HOME = Path.home() / ".rick-rubin"
INSTALL_FOLDER = "rick-rubin"


def taste_path() -> Path:
    return HOME / "taste.md"


def slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", text.strip()).strip("-") or "sound"


# ---------------------------------------------------------------------- Serum presets where Serum shows them
def install_dir() -> Path:
    """Serum 2 lists every folder under its Presets folder; designed sounds go in Presets/User/rick-rubin."""
    from . import serum
    return serum.preset_root() / "User" / INSTALL_FOLDER


def install_preset(preset: str | Path) -> Path:
    """Copy a .SerumPreset into Serum's user presets (outside the project: only when its owner asked)."""
    src = Path(preset).expanduser()
    if not src.is_file() or src.suffix.lower() != ".serumpreset":
        raise FileNotFoundError(f"{src} is not a .SerumPreset file")
    dest = install_dir()
    dest.mkdir(parents=True, exist_ok=True)
    out = dest / src.name
    shutil.copy2(src, out)
    return out


# ---------------------------------------------------------------------- a render to listen to
def _notes_of_track(project_dir: Path, track: str, bars: tuple[int, int] | None):
    """(song, track object, [(pitch, start s, length s, velocity)] from bar A, seconds) for a track's part."""
    from .project import Project
    song = Project(project_dir).load()
    trk = song.track(track)
    clips, _ = song.flatten(sounding=True)
    spb = 60.0 / song.bpm
    b0, b1 = bars or (1, song.total_bars)
    lo, hi = (b0 - 1) * 4.0, b1 * 4.0
    notes = sorted((n.pitch, round((c.start + n.start - lo) * spb, 6), round(n.dur * spb, 6), n.vel)
                   for c in clips if c.track == trk.name for n in c.notes if lo <= c.start + n.start < hi)
    return song, trk, notes, (hi - lo) * spb


def serum_audition(preset: str, project_dir: str | Path, notes: list[str] | None = None, secs: float = 1.0,
                   track: str | None = None, bars: tuple[int, int] | None = None, bpm: float | None = None,
                   name: str | None = None, settings: dict | None = None, picture: bool = True) -> dict:
    """Render `preset` (a name, a path, or a designed preset in the project) to <project>/auditions/<name>.wav
    (+ .mp3 when ffmpeg is there, + a picture of the patch), playing either `notes` one after another for `secs`
    each, or `track`'s own part over `bars` of the project's song. Logged in auditions/log.md awaiting a verdict."""
    from . import serum
    from .samples import write_wav24
    from .sounddesign import describe_sound, describe_table
    from .theory import note as parse_note
    project_dir = Path(project_dir)
    path = project_dir / preset if (project_dir / preset).is_file() else serum.find(preset)
    label = slug(name or Path(path).stem)
    out_dir = project_dir / "auditions"
    out_dir.mkdir(parents=True, exist_ok=True)
    if track:
        song, _trk, seq, total = _notes_of_track(project_dir, track, bars)
        if not seq:
            raise ValueError(f"{track!r} plays nothing in bars {bars[0]}-{bars[1]}" if bars else f"{track!r} has no notes")
        bpm = bpm or song.bpm
        what = f"{track}'s part, bars {bars[0]}-{bars[1]}" if bars else f"{track}'s whole part"
        total += 1.0
    else:
        names = notes or ["C2"]
        gap = 0.25
        seq = [(parse_note(n), i * (secs + gap), secs, 100) for i, n in enumerate(names)]
        total = len(names) * (secs + gap) + 1.5
        what = f"{', '.join(names)} for {secs:g} s each"
    _, audio = serum.render_preset(path, seq, total, settings or None, bpm=bpm)
    wav = out_dir / f"{label}.wav"
    write_wav24(wav, 44100, audio)
    files = [wav]
    if shutil.which("ffmpeg"):
        mp3 = wav.with_suffix(".mp3")
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-b:a", "256k", str(mp3)], capture_output=True)
        if r.returncode == 0:
            files.append(mp3)
    if picture:
        try:
            from .pictures import serum_png
            files.append(Path(serum_png(str(path), out_dir / f"{label}.png", seq[0][0], settings or None)))
        except Exception as e:  # noqa: BLE001 — the picture is extra; the audio is the point
            files.append(Path(f"(no picture: {e})"))
    # the numbers are of the first note alone: the measures are made for one note, and a phrase would read as pitch drift
    a = int(max(0.0, seq[0][1]) * 44100)
    nxt = min((n[1] for n in seq[1:] if n[1] > seq[0][1]), default=None)
    b = int((nxt if nxt is not None else seq[0][1] + seq[0][2] + 1.0) * 44100)
    row = describe_sound(44100, audio[a:b], f"{label} (first note)", min(seq[0][2], (b - a) / 44100), bpm)
    table = describe_table([row])
    log = out_dir / "log.md"
    if not log.exists():
        log.write_text("# Auditions\n\nSounds rendered for a person to listen to. Record what they said with `rick-rubin verdict`.\n")
    with log.open("a") as f:
        f.write(f"\n## {label} — {date.today().isoformat()}\n- preset: `{path}`" + (f" with {settings}" if settings else "")
                + f"\n- played: {what}" + (f" at {bpm:g} BPM" if bpm else "") + f"\n- file: `{wav.name}`\n- verdict: (waiting)\n")
    return {"name": label, "files": files, "played": what, "table": table, "preset": path}


# ---------------------------------------------------------------------- what the person said
def record_verdict(project_dir: str | Path, what: str, words: str, keep: bool | None = None) -> dict:
    """Write down what the person heard: under the audition's entry when `what` names one, in the project's
    project.md, and in ~/.rick-rubin/taste.md, which every session reads before making sound decisions."""
    project_dir = Path(project_dir)
    today = date.today().isoformat()
    mark = "KEEP" if keep else ("REJECT" if keep is False else "NOTE")
    line = f"{mark}: {words.strip()}"
    where = []
    log = project_dir / "auditions" / "log.md"
    if log.exists():
        text = log.read_text()
        head = re.search(rf"^## {re.escape(slug(what))} — .*$", text, re.M)
        if head:
            end = text.find("\n## ", head.end())
            block = text[head.start(): end if end >= 0 else len(text)]
            new = block.replace("- verdict: (waiting)", f"- verdict ({today}): {line}") if "- verdict: (waiting)" in block \
                else block.rstrip("\n") + f"\n- verdict ({today}): {line}\n"
            log.write_text(text[: head.start()] + new + (text[end:] if end >= 0 else ""))
            where.append(log)
    memo = project_dir / "project.md"
    if memo.exists():
        text = memo.read_text()
        if "## Ear verdicts" not in text:
            text = text.rstrip("\n") + "\n\n## Ear verdicts\nWhat a person said after listening (newest last).\n"
        memo.write_text(text.rstrip("\n") + f"\n- {today} · {what}: {line}\n")
        where.append(memo)
    taste = taste_path()
    taste.parent.mkdir(parents=True, exist_ok=True)
    if not taste.exists():
        taste.write_text("# Taste\n\nWhat the person at this Mac said after listening, across all projects (newest last). Read before making\n"
                         "sound, mix or arrangement decisions; a pattern in these lines outranks a general rule.\n\n")
    with taste.open("a") as f:
        f.write(f"- {today} · {project_dir.resolve().name} · {what}: {line}\n")
    where.append(taste)
    return {"line": line, "written": where}
