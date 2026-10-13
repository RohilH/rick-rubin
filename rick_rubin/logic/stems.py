"""Split a recording into stems with Logic Pro's own Stem Splitter (Logic Pro 11 on Apple silicon).

    split_stems("refs/track.wav", "stems/track")   # -> stems/track/vocals.wav, drums.wav, bass.wav, guitar.wav, piano.wav, other.wav

The recording gets a Logic project of its own: a one-track MIDI file Logic opens as a project, saved as
`<out>/logic/<name> stems.logicx`, an audio track, File > Import (the project takes the recording's sample
rate). Right-click > Stem Splitter… on the region then separates it into the stems asked for. The project is named after the output folder (`stems/track` ->
'track stems'). Logic adds a
summing stack with one audio track per stem, mutes the original, and writes the stems into the project's Audio
Files folder while its progress window is up (a 2'43" song takes about 30 s on an M4 Pro). They are copied out
as `<stem>.wav`, 24-bit at the recording's rate, and measured: a stem with nothing in it (no piano in a house
track) comes out near silent, and the report says so.

The project stays open in Logic, so the split can be auditioned there; `close=True` closes it (it is saved
either way). Other open projects are left alone.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import time
from pathlib import Path

import numpy as np

from ..model import Song
from ..samples import read_audio, write_wav24
from .bridge import STEMS, LogicBridge, LogicError
from .client import safe_name
from .smf import export_logic_midi

SILENT_DB = -60.0          # a stem quieter than this (RMS, dBFS) holds nothing worth using


def parse_stems(spec: str | list[str] | tuple[str, ...] | None) -> list[str]:
    """'vocals,drums' / ['Bass'] / 'all' / None (all) -> Logic's names, in the dialog's order."""
    if spec is None or spec == "all" or spec == ["all"]:
        return list(STEMS)
    words = [w.strip().lower() for w in (spec.split(",") if isinstance(spec, str) else spec) if w.strip()]
    unknown = [w for w in words if w.capitalize() not in STEMS]
    if unknown or not words:
        raise ValueError(f"stems are {', '.join(s.lower() for s in STEMS)} or 'all' (not {', '.join(unknown) or 'nothing'})")
    return [s for s in STEMS if s.lower() in words]


def stem_of(path: Path, region: str) -> str | None:
    """Which stem a file Logic wrote holds: '<region>_<Stem>.wav', with '#01'-style suffixes when the name was taken."""
    m = re.fullmatch(re.escape(region) + r"_(\w+?)(?:#\d+)?", path.stem)
    if m and m.group(1).capitalize() in STEMS:
        return m.group(1).capitalize()
    return None


def prepare_source(src: Path, dest: Path, start_s: float | None = None, end_s: float | None = None) -> tuple[Path, int, float]:
    """The recording as a WAV in a folder Logic's file panel can reach, cut to start_s..end_s (seconds).
    Formats other than WAV go through macOS's afconvert. Returns (path, sample rate, seconds)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.suffix.lower() != ".wav":
        r = subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI24", str(src), str(dest)], capture_output=True, text=True, check=False)
        if r.returncode != 0 or not dest.exists():
            raise LogicError(f"cannot read {src.name} (afconvert: {(r.stderr or r.stdout).strip()[-200:]})")
        src = dest
    if start_s is None and end_s is None:
        if src != dest:
            shutil.copyfile(src, dest)
        sr, x = read_audio(dest)
        return dest, sr, len(x) / sr
    sr, x = read_audio(src)
    a = max(0, round((start_s or 0.0) * sr))
    b = len(x) if end_s is None else min(len(x), round(end_s * sr))
    if b <= a:
        raise ValueError(f"empty range {start_s or 0:g}-{end_s} s (the recording is {len(x) / sr:.1f} s)")
    write_wav24(dest, sr, x[a:b])
    return dest, sr, (b - a) / sr


def _close_ours(bridge: LogicBridge, title: str, package: Path) -> None:
    """Close our earlier split into the same folder; refuse to go on beside another project of the same name
    (the bridge finds a project's window by its name)."""
    app = bridge.app
    assert app is not None
    for w in app.project_windows():
        t = app.project_title(w) or ""
        if t not in (title, f"{title}.logicx"):
            continue
        path = app.project_path(w)
        if path is not None and path.resolve() == package.resolve():
            bridge.close_project(t)
        else:
            raise LogicError(f"another project called {t!r} is open in Logic ({path or 'unsaved'}); close it, or split into another folder (--out)")


def _wait_for_stems(bridge: LogicBridge, roots: list[Path], before: dict[Path, float], region: str, want: list[str],
                    seconds: float, timeout: float, say) -> dict[str, Path]:
    """Poll the project's folders until every stem Logic wrote is complete: all there, its progress window gone,
    and the files' sizes unchanged for two seconds."""
    t0 = time.time()
    sizes: dict[Path, int] = {}
    found: dict[str, Path] = {}
    stable_since = None
    told = t0
    while time.time() - t0 < timeout:
        found = {}
        for root in roots:
            for p in root.rglob("*.wav"):
                st = stem_of(p, region)
                if st in want and (p not in before or p.stat().st_mtime > before[p]):
                    found[st] = p
        now = {p: p.stat().st_size for p in found.values()}
        busy = bridge.stem_split_progress() is not None
        if now != sizes or busy or len(found) < len(want):
            sizes, stable_since = now, None
        elif stable_since is None:
            stable_since = time.time()
        elif time.time() - stable_since >= 2.0:
            return found
        if time.time() - told > 10:
            told = time.time()
            say(f"waiting for the stem files ({len(found)}/{len(want)} there, {sum(now.values()) / 1e6:.0f} MB)")
        time.sleep(0.5)
    raise LogicError(f"Logic did not finish writing the stems of a {seconds:.0f} s recording within {timeout:.0f} s "
                     f"(have {sorted(found)}; pending: {bridge.pending_alert()})")


def split_stems(source: str | Path, out_dir: str | Path, stems: list[str] | tuple[str, ...] | str | None = None,
                submix: bool = False, start_s: float | None = None, end_s: float | None = None, close: bool = False,
                bridge: LogicBridge | None = None, progress=None, timeout: float | None = None) -> dict:
    """Separate `source` with Logic's Stem Splitter into `out_dir`/<stem>.wav. `stems`: any of vocals, drums, bass,
    guitar, piano, other (default all six). `submix` adds Logic's mix of the stems not asked for (as submix.wav).
    Returns {"stems": {stem: path}, "levels": {stem: (rms_db, peak_db)}, "silent": [...], "project", "seconds",
    "split_s", "sample_rate"}."""
    say = progress or (lambda *_: None)
    want = parse_stems(stems)
    source = Path(source).expanduser().resolve()
    if not source.exists():
        raise LogicError(f"{source} does not exist")
    out_dir = Path(out_dir).expanduser().resolve()
    name = safe_name(source.stem)
    title = f"{safe_name(out_dir.name)} stems"
    work = out_dir / "logic"
    if bridge is None:
        if any(p.startswith(".") for p in out_dir.parts) or str(out_dir).startswith(("/private/", "/tmp/")):
            raise LogicError(f"{out_dir} is in a hidden folder, which Logic's file panels cannot reach; use a visible folder (e.g. under ~/Documents)")
        from ..live.client import live_lock
        with live_lock(f"split {name}", progress=say), LogicBridge(progress=say, use_mcu=False) as b:
            return split_stems(source, out_dir, want, submix, start_s, end_s, close, b, say, timeout)

    package = work / f"{title}.logicx"
    _close_ours(bridge, title, package)
    if package.exists():
        shutil.rmtree(package)                            # our own earlier split of this recording
    for st in [*STEMS, "submix"]:
        (out_dir / f"{st.lower()}.wav").unlink(missing_ok=True)
    wav, sr, seconds = prepare_source(source, work / f"{name}.wav", start_s, end_s)
    say(f"{source.name}: {seconds:.1f} s at {sr} Hz")

    song = Song(title, bpm=120, key="C major")            # tempo and key do not matter: the region starts at 0:00
    song.add_track("Source", "pad")
    song.add_section("all", max(1, int(np.ceil(seconds / 2.0))), kind="drop", parts={})
    smf = export_logic_midi(song, work / f"{name}.mid")
    say("opening a project for it in Logic")
    bridge.open_midi_project(smf["path"], expect_tracks=1)
    package = bridge.save_project_as(work, title)
    before_tracks = bridge.tracks()
    ti = bridge.add_audio_track()
    say(f"importing {wav.name}")
    bridge.import_audio(ti, wav, 1, keep_file_rate=True)
    region = bridge.select_region(ti)
    roots = [package, work]
    before = {p: p.stat().st_mtime for r in roots for p in r.rglob("*.wav")}
    say(f"Stem Splitter: {', '.join(want)}{' + submix' if submix else ''}")
    t0 = time.time()
    timeout = timeout or 120.0 + 2.0 * seconds
    added = bridge.stem_split(ti, want, submix, timeout, on_progress=lambda f: say(f"splitting: {100 * f:.0f}%"))
    say(f"Logic added {added}")
    files = _wait_for_stems(bridge, roots, before, region, want, seconds, 60.0, say)
    split_s = time.time() - t0
    out: dict[str, Path] = {}
    for st in want:
        dest = out_dir / f"{st.lower()}.wav"
        shutil.copyfile(files[st], dest)
        out[st.lower()] = dest
    if submix:
        known = set(files.values()) | {wav}
        extra = [p for r in roots for p in r.rglob(f"{region}_*.wav") if p not in known and (p not in before or p.stat().st_mtime > before[p])]
        if extra:
            shutil.copyfile(extra[0], out_dir / "submix.wav")
            out["submix"] = out_dir / "submix.wav"
        else:
            say("Logic wrote no submix file")
    bridge.save_project()
    if close:
        bridge.close_project()
    levels, silent = {}, []
    for st, p in out.items():
        _, y = read_audio(p)
        rms = float(20 * np.log10(np.sqrt(np.mean(y.astype(np.float64) ** 2)) + 1e-12))
        levels[st] = (rms, float(20 * np.log10(np.abs(y).max() + 1e-12)))
        if rms < SILENT_DB:
            silent.append(st)
    return {"stems": out, "levels": levels, "silent": silent, "project": package, "seconds": seconds,
            "split_s": split_s, "sample_rate": sr, "tracks_added": added, "tracks_before": before_tracks}
