"""Session mode: work inside a Logic project that is already open.

`push` builds a new project from a song.py. A session does the other job: it reads the project a person is
working in, makes one change at a time in it, and reads every change back. The rules it keeps:

  * it never opens, closes or saves a project, and never answers a question Logic is asking (it stops and
    says what Logic asks);
  * before its first change it copies the project's saved state (ProjectData of every alternative, a few MB)
    to ~/.rick-rubin/backups/<project>/<time>/, and every change is appended to
    ~/.rick-rubin/sessions/<project>.jsonl with the value before and after;
  * exactly one track is selected before a channel-strip edit (Logic applies strip edits to every selected
    strip), and the selection the person had is put back afterwards;
  * a Mixer window it had to open is closed again;
  * changes bring Logic to the front (its Save commands and Aux / Stereo Out strips only answer there), but
    only once the keyboard and mouse have been still for a moment, and the app that was in front gets the
    front back.

Everything here talks to a LogicBridge through its public methods, so the tests run it against the fake one.
"""
from __future__ import annotations

import json
import re
import shutil
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from .bridge import LogicError

HOME = Path.home() / ".rick-rubin"
DEVICES_CACHE = Path(__file__).resolve().parent.parent.parent / ".cache" / "logic-devices.json"


@dataclass
class Change:
    op: str
    target: str
    before: Any = None
    after: Any = None
    ok: bool = True
    note: str = ""

    def line(self) -> str:
        mark = "ok" if self.ok else "NOT AS ASKED"
        tail = f"  — {self.note}" if self.note else ""
        if self.before is None and self.after is None:
            return f"[{mark}] {self.op} {self.target}{tail}"
        return f"[{mark}] {self.op} {self.target}: {self.before} -> {self.after}{tail}"


def number(text: Any) -> float | None:
    """The number in what Logic displays ('-4.0 dB', '+2.5', '−12')."""
    m = re.search(r"[-+−]?\d+(?:[.,]\d+)?", str(text))
    return float(m.group(0).replace("−", "-").replace(",", ".")) if m else None


def parse_value(text: str) -> Any:
    low = text.strip().lower()
    if low in ("on", "true", "yes"):
        return True
    if low in ("off", "false", "no"):
        return False
    try:
        return float(text)
    except ValueError:
        return text


def parse_settings(items: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for it in items:
        if "=" not in it:
            raise LogicError(f"expected KEY=VALUE, got {it!r}")
        k, v = it.split("=", 1)
        out[k.strip()] = parse_value(v)
    return out


def find_project(app, wanted: str | None) -> str:
    """The title of the open project to work in: `wanted` (with or without '.logicx', any case, or a unique part
    of the title), else the front one."""
    titles = [t for t in (app.project_title(w) for w in app.project_windows()) if t]
    if not titles:
        raise LogicError("no project is open in Logic")
    if wanted is None:
        return app.project_title() or titles[0]
    want = wanted.lower().removesuffix(".logicx")
    exact = [t for t in titles if t.lower().removesuffix(".logicx") == want]
    part = exact or [t for t in titles if want in t.lower()]
    if len(part) != 1:
        raise LogicError(f"{'no' if not part else 'more than one'} open project matches {wanted!r} (open: {titles})")
    return part[0]


class Session:
    """`with Session(bridge) as s:` — the bridge is connected and points at the project to work in."""

    def __init__(self, bridge, backups: bool = True, log: bool = True):
        self.b = bridge
        self.backups = backups
        self.log = log
        self.changes: list[Change] = []
        self._backed_up = False
        self._selection: list[int] = []
        self._had_mixer = True

    # ------------------------------------------------------------------ entering and leaving
    def __enter__(self) -> Session:
        pend = self.b.pending_alert() if hasattr(self.b, "pending_alert") else None
        if pend:
            raise LogicError(f"Logic is asking {pend[0][:160]!r} [{', '.join(pend[1])}]. Answer it in Logic first: a session never "
                             "answers a question it did not cause")
        app = self.b.app
        try:
            self._selection = list(app.selected_tracks(self.b.main))
        except (AttributeError, LogicError):
            self._selection = []
        try:
            self._had_mixer = app.mixer_window(self.b.project) is not None
        except AttributeError:
            self._had_mixer = True
        return self

    def __exit__(self, *exc) -> None:
        try:
            if hasattr(self.b, "close_plugin_windows"):
                self.b.close_plugin_windows()
            if hasattr(self.b, "leave_global_view"):
                self.b.leave_global_view()
            if len(self._selection) == 1:
                self.b.select_track(self._selection[0])
            if not self._had_mixer:
                self._close_mixer_window()
        except Exception:  # noqa: BLE001  — tidying up must not hide the real error
            pass

    def _close_mixer_window(self) -> None:
        from . import ax as AX
        w = self.b.app.mixer_window(self.b.project)
        if w is not None:
            AX.press(AX.find(w, lambda e: AX.attr(e, "AXSubrole") == "AXCloseButton", 1))
            self.b._mixer = None

    # ------------------------------------------------------------------ reading
    def state(self, regions: bool = True) -> dict:
        b, app = self.b, self.b.app
        names = b.tracks()
        strips = b.strips()
        try:
            w = b.main
            path = app.project_path(w)
            selected = list(app.selected_tracks(w))
        except AttributeError:
            path, selected = None, []
        st: dict[str, Any] = {
            "project": b.project, "path": str(path) if path else None, "saved": path is not None,
            "tempo": _try(b.tempo), "key": _try(lambda: b.control_text("Key Signature")),
            "time_signature": _try(lambda: b.control_text("Time Signature")),
            "playhead": _try(lambda: b.playhead()), "playing": _try(lambda: b.is_playing()),
            "other_projects": [t for t in (app.project_title(x) for x in app.project_windows()) if t and t != b.project],
            "tracks": [], "aux": [], "outputs": [],
        }
        for s in strips:
            row = {"name": s.name, "volume": s.volume, "pan": s.pan, "mute": s.mute, "solo": s.solo, "instrument": s.instrument,
                   "inserts": list(s.inserts), "sends": list(s.sends), "output": s.output, "automation": s.automation}
            if s.kind == "track" and s.index < len(names):
                row = {"n": s.index + 1, **row, "selected": s.index in selected}
                if regions and hasattr(b, "track_regions"):
                    from . import ax as AX
                    row["regions"] = [AX.desc(r) for r in b.track_regions(s.index)]
                st["tracks"].append(row)
            elif s.kind == "aux":
                st["aux"].append(row)
            else:
                st["outputs"].append({**row, "kind": s.kind})
        return st

    def params(self, ref: str, plugin: str | None = None, nth: int = 0, max_pages: int = 40) -> tuple[str, dict[str, str]]:
        """The displayed parameters of an insert on a strip (or of a track's instrument when `plugin` is None)."""
        target, info = self.resolve(ref)
        self._single(target)
        if plugin is None:
            if not isinstance(target, int):
                raise LogicError(f"{info.name!r} has no instrument")
            return info.instrument or "instrument", self.b.read_instrument_params(target, max_pages)
        slot, shown = self._slot(info, plugin, nth)
        name, values = self.b.read_plugin_params(target, slot, max_pages)
        return name or shown, values

    # ------------------------------------------------------------------ finding things
    def resolve(self, ref: str | int):
        """A strip by '#3' / 3 (track number, 1-based) or by name (any case; a unique beginning will do). Returns
        (what the bridge takes: a track index, or the name for Aux / Stereo Out / Master; its StripInfo)."""
        strips = self.b.strips()
        n_tracks = len(self.b.tracks())
        if isinstance(ref, int) or re.fullmatch(r"#?\d+", str(ref).strip()):
            i = int(str(ref).strip().lstrip("#")) - 1
            if not 0 <= i < n_tracks:
                raise LogicError(f"no track #{i + 1}: the project has {n_tracks} tracks")
            return i, strips[i]
        want = str(ref).strip().lower()
        hits = [s for s in strips if s.name.lower() == want] or [s for s in strips if s.name.lower().startswith(want)]
        if not hits:
            raise LogicError(f"no channel strip called {ref!r} (have {[s.name for s in strips]})")
        if len(hits) > 1:
            raise LogicError(f"{ref!r} fits {len(hits)} strips ({[f'#{s.index + 1} {s.name}' for s in hits]}): give the track number, e.g. '#{hits[0].index + 1}'")
        s = hits[0]
        return (s.index if s.kind == "track" and s.index < n_tracks else s.name), s

    def _slot(self, info, plugin: str, nth: int = 0) -> tuple[int, str]:
        want = plugin.strip().lower()
        hits = [(i, n) for i, n in enumerate(info.inserts) if n.lower() == want] or \
               [(i, n) for i, n in enumerate(info.inserts) if n.lower().startswith(want) or want.startswith(n.lower()) or want in n.lower()]
        if nth >= len(hits):
            raise LogicError(f"{info.name!r} has no {'second ' if nth else ''}{plugin!r} (inserts: {info.inserts})")
        return hits[nth][0] + 1, hits[nth][1]

    def _single(self, target) -> None:
        """One track selected, and only one: the target when it is a track, else the one the person had (or the first).
        Nothing is changed unless Logic shows exactly that selection: it applies strip edits to every selected strip."""
        index = target if isinstance(target, int) else (self._selection[0] if self._selection else 0)
        self.b.select_track(index)
        check = getattr(self.b, "only_selected", None)
        if check is not None and not check(index):
            raise LogicError(f"track #{index + 1} could not be selected on its own, so nothing was changed. Click on Logic's window and run it again")

    # ------------------------------------------------------------------ the record
    def _begin(self) -> None:
        if self.backups and not self._backed_up:
            self._backed_up = True
            try:
                where = backup(self.b)
                if where is not None:
                    self.b.say(f"saved state backed up to {where}")
            except OSError as e:
                self.b.say(f"no backup made ({e})")

    def _done(self, c: Change) -> Change:
        self.changes.append(c)
        if self.log:
            try:
                p = HOME / "sessions" / f"{_safe(self.b.project or 'project')}.jsonl"
                p.parent.mkdir(parents=True, exist_ok=True)
                with p.open("a") as f:
                    f.write(json.dumps({"at": datetime.now().isoformat(timespec="seconds"), **asdict(c)}, default=str) + "\n")
            except OSError:
                pass
        return c

    # ------------------------------------------------------------------ changes
    def mix(self, ref: str, volume: float | None = None, pan: float | None = None, mute: bool | None = None,
            solo: bool | None = None) -> list[Change]:
        """Fader (dB), pan (Logic's -64..63), mute, solo of one strip."""
        target, info = self.resolve(ref)
        self._begin()
        self._single(target)
        out = []
        if volume is not None:
            self.b.set_volume(target, float(volume))
            after = self.b.strip_info(target).volume
            got = number(after)
            out.append(self._done(Change("volume", info.name, info.volume, after, got is not None and abs(got - float(volume)) <= 0.2)))
        if pan is not None:
            self.b.set_pan(target, max(-64.0, min(63.0, float(pan))) / 64.0)
            after = self.b.strip_info(target).pan
            got = number(after)
            out.append(self._done(Change("pan", info.name, info.pan, after, got is not None and abs(got - float(pan)) <= 1.0)))
        if mute is not None:
            now = self.b.set_mute(target, bool(mute))
            out.append(self._done(Change("mute", info.name, info.mute, now, now == bool(mute))))
        if solo is not None:
            now = self.b.set_solo(target, bool(solo))
            out.append(self._done(Change("solo", info.name, info.solo, now, now == bool(solo))))
        return out

    def insert(self, ref: str, plugin: str, params: dict | None = None, sidechain: str | None = None) -> Change:
        """A plug-in in the strip's first free insert slot, then its parameters and side chain."""
        from .client import _nth
        target, info = self.resolve(ref)
        self._begin()
        self._single(target)
        got = self.b.insert_plugin(target, plugin)
        inserts = list(self.b.strip_info(target).inserts)
        slot = len(inserts)
        notes = []
        ok = len(inserts) == len(info.inserts) + 1
        if params:
            self._single(target)
            rep = self.b.set_plugin_params(target, slot, params)
            notes.append(", ".join(f"{k} {v}" for k, v in rep.set.items()))
            if rep.errors:
                ok = False
                notes.append("; ".join(rep.errors))
        if sidechain:
            _, src = self.resolve(sidechain)
            self._single(target)
            shown = self.b.set_side_chain(target, got, src.name, nth=_nth(inserts, got, slot))
            notes.append(f"side chain <- {shown}")
        return self._done(Change("insert", info.name, list(info.inserts), inserts, ok, "; ".join(n for n in notes if n)))

    def tweak(self, ref: str, plugin: str, params: dict, nth: int = 0) -> Change:
        """Parameters of a plug-in that is already on the strip, by displayed value."""
        target, info = self.resolve(ref)
        slot, shown = self._slot(info, plugin, nth)
        self._begin()
        self._single(target)
        rep = self.b.set_plugin_params(target, slot, params)
        return self._done(Change("params", f"{info.name} / {shown}", dict(params), dict(rep.set), not rep.errors, "; ".join(rep.errors)))

    def instrument_params(self, ref: str, params: dict) -> Change:
        target, info = self.resolve(ref)
        if not isinstance(target, int):
            raise LogicError(f"{info.name!r} has no instrument")
        self._begin()
        self._single(target)
        rep = self.b.set_instrument_params(target, params, info.instrument or "")
        return self._done(Change("instrument params", info.name, dict(params), dict(rep.set), not rep.errors, "; ".join(rep.errors)))

    def side_chain(self, ref: str, plugin: str, source: str, nth: int = 0) -> Change:
        target, info = self.resolve(ref)
        _, src = self.resolve(source)
        _slot, shown = self._slot(info, plugin, nth)
        self._begin()
        self._single(target)
        got = self.b.set_side_chain(target, shown, src.name, nth=nth)
        return self._done(Change("side chain", f"{info.name} / {shown}", None, got, True))

    def send(self, ref: str, bus: int, db: float | None) -> Change:
        """A send from a track to 'Bus <bus>' at `db` (None removes it). Logic makes the Aux for a new bus itself."""
        target, info = self.resolve(ref)
        if not isinstance(target, int):
            raise LogicError("sends are set on tracks; give a track name or number")
        want = f"Bus {bus}"
        slot = info.sends.index(want) + 1 if want in info.sends else len(info.sends) + 1
        self._begin()
        self._single(target)
        shown = self.b.set_send(target, bus, db, slot=slot)
        after = list(self.b.strip_info(target).sends)
        ok = (want in after) if db is not None else (want not in after)
        return self._done(Change("send", f"{info.name} -> {want}", list(info.sends), after, ok, shown))

    def instrument(self, ref: str, name: str, params: dict | None = None) -> Change:
        """Load a Logic instrument or Audio Unit by name, or (any other text) the first Library patch a search finds."""
        from .client import is_logic_instrument
        target, info = self.resolve(ref)
        if not isinstance(target, int):
            raise LogicError(f"{info.name!r} is not a track")
        self._begin()
        self._single(target)
        if is_logic_instrument(name):
            got = self.b.load_instrument(target, name)
            ok = True
        else:
            r = self.b.load_patch(target, name)
            got, ok = f"patch {name!r} -> {r['instrument']}", bool(r["loaded"])
        note = ""
        if params and ok:
            self._single(target)
            rep = self.b.set_instrument_params(target, params, name)
            note = ", ".join(f"{k} {v}" for k, v in rep.set.items()) + ("; " + "; ".join(rep.errors) if rep.errors else "")
            ok = ok and not rep.errors
        return self._done(Change("instrument", info.name, info.instrument, got, ok, note))

    def add_instrument(self, instrument: str, name: str | None = None, params: dict | None = None) -> Change:
        """A new software-instrument track at the bottom with `instrument` on it."""
        self._begin()
        before = len(self.b.tracks())
        ti = self.b.add_instrument_track()
        label = self.b.tracks()[ti]
        if name:
            label = self.b.rename_track(ti, name)
        c = self._done(Change("add track", label, f"{before} tracks", f"{len(self.b.tracks())} tracks", True, f"software instrument, track #{ti + 1}"))
        if instrument:
            self.instrument(f"#{ti + 1}", instrument, params)
        return c

    def add_audio(self, file: str | Path, bar: int = 1, name: str | None = None) -> Change:
        """A new audio track at the bottom holding `file`, its region starting on bar `bar` (Logic places an imported
        file on the bar line). A file at another sample rate is converted: the project's rate stays."""
        path = Path(file).expanduser().resolve()
        if not path.exists():
            raise LogicError(f"{path} does not exist")
        self._begin()
        before = len(self.b.tracks())
        ti = self.b.add_audio_track()
        self.b.import_audio(ti, path, int(bar), 1)
        label = self.b.rename_track(ti, name) if name else self.b.tracks()[ti]
        return self._done(Change("add audio", label, f"{before} tracks", f"{len(self.b.tracks())} tracks", True,
                                 f"{path.name} at bar {bar}, track #{ti + 1}"))

    def add_midi(self, file: str | Path, bar: int = 1, names: list[str] | None = None) -> Change:
        """The tracks of a MIDI file as new software-instrument tracks, regions starting on bar `bar`."""
        path = Path(file).expanduser().resolve()
        self._begin()
        before = len(self.b.tracks())
        added = self.b.import_midi(path, int(bar))
        labels = []
        for k, ti in enumerate(added):
            labels.append(self.b.rename_track(ti, names[k]) if names and k < len(names) else self.b.tracks()[ti])
        return self._done(Change("add midi", ", ".join(labels), f"{before} tracks", f"{len(self.b.tracks())} tracks", bool(added),
                                 f"{path.name} at bar {bar}, track{'s' if len(added) != 1 else ''} {', '.join('#' + str(i + 1) for i in added)}"))

    def rename(self, ref: str, name: str) -> Change:
        target, info = self.resolve(ref)
        if not isinstance(target, int):
            raise LogicError(f"{info.name!r} is not a track")
        self._begin()
        got = self.b.rename_track(target, name)
        return self._done(Change("rename", f"#{target + 1}", info.name, got, got == name))

    def bounce(self, out: str | Path, bars: tuple[int, int] | None = None, tracks: list[str] | None = None) -> dict:
        """An offline bounce of the project (or bars A-B, or just some tracks soloed) to a 24-bit WAV. Solo states
        are put back as they were."""
        out = Path(out).expanduser().resolve()
        strips = self.b.strips()
        was = {s.name: s.solo for s in strips}
        targets = [self.resolve(t) for t in tracks or []]
        try:
            if targets:
                for s in strips:
                    if s.solo:
                        self.b.set_solo(s.name if s.kind != "track" else s.index, False)
                for target, _info in targets:
                    self.b.set_solo(target, True)
            b0, b1 = bars or (1, 9999)                      # the bridge stops at the project's end
            path = self.b.bounce(out, b0, b1)
        finally:
            for s in self.b.strips():
                if s.solo != was.get(s.name, False):
                    self.b.set_solo(s.name if s.kind != "track" else s.index, was.get(s.name, False))
        return {"path": str(path), "bars": list(bars) if bars else None, "tracks": [i.name for _t, i in targets]}


def _try(fn):
    try:
        return fn()
    except Exception:  # noqa: BLE001
        return None


def _safe(s: str) -> str:
    return "".join(ch if ch.isalnum() or ch in " -_()." else "_" for ch in s).strip() or "project"


# ---------------------------------------------------------------------- backups
def backup(bridge, force: bool = False) -> Path | None:
    """Copy the saved state of the bridge's project — every alternative's ProjectData and plists, not the audio —
    to ~/.rick-rubin/backups/<project>/<time>/. Nothing is copied when the project was never saved, or when the
    newest backup already holds this saved state (same modification time). To go back: close the project in Logic
    and copy the backup's Alternatives folder over the one in the .logicx package."""
    try:
        path = bridge.app.project_path(bridge.main)
    except AttributeError:
        return None
    if path is None or not (path / "Alternatives").is_dir():
        return None
    data = sorted((path / "Alternatives").glob("*/ProjectData"))
    stamp = max((p.stat().st_mtime for p in data), default=0.0)
    root = HOME / "backups" / _safe(path.stem)
    latest = sorted(root.glob("*/info.json"))
    if latest and not force:
        try:
            if abs(json.loads(latest[-1].read_text()).get("saved_at", 0) - stamp) < 1.0:
                return None
        except ValueError:
            pass
    dest = root / datetime.now().strftime("%Y%m%d-%H%M%S")
    for alt in sorted((path / "Alternatives").iterdir()):
        if not alt.is_dir():
            continue
        (dest / "Alternatives" / alt.name).mkdir(parents=True, exist_ok=True)
        for f in alt.iterdir():
            if f.is_file() and f.stat().st_size < 400_000_000:
                shutil.copy2(f, dest / "Alternatives" / alt.name / f.name)
    (dest / "info.json").write_text(json.dumps({"project": str(path), "saved_at": stamp, "made": datetime.now().isoformat(timespec="seconds")}, indent=1) + "\n")
    return dest


# ---------------------------------------------------------------------- what a plug-in offers
def load_device_maps() -> dict:
    try:
        return json.loads(DEVICES_CACHE.read_text()) if DEVICES_CACHE.exists() else {}
    except ValueError:
        return {}


def map_plugins(names: list[str], progress=None, refresh: bool = False, max_pages: int = 40) -> dict:
    """Read each plug-in's parameters (names as the control surface shows them, and their displayed defaults) by
    inserting it on an audio track of a scratch project, which is closed without saving. Results are kept in
    .cache/logic-devices.json, so later calls answer without Logic."""
    from .bridge import LogicBridge
    say = progress or (lambda *_: None)
    known = load_device_maps()
    todo = [n for n in names if refresh or n.lower() not in {k.lower() for k in known}]
    if todo:
        import mido
        scratch = HOME / "scratch"
        scratch.mkdir(parents=True, exist_ok=True)
        mid = mido.MidiFile(type=1, ticks_per_beat=480)
        meta = mido.MidiTrack()
        meta.append(mido.MetaMessage("set_tempo", tempo=500000, time=0))
        mid.tracks.append(meta)
        tr = mido.MidiTrack()
        tr.append(mido.MetaMessage("track_name", name="scratch", time=0))
        tr.append(mido.Message("note_on", note=60, velocity=80, time=0))
        tr.append(mido.Message("note_off", note=60, velocity=0, time=480))
        mid.tracks.append(tr)
        smf = scratch / "plug-in map.mid"
        mid.save(str(smf))
        with LogicBridge(progress=say, front="start") as b:
            title = b.open_midi_project(smf, expect_tracks=1, close_ours=False)
            try:
                ti = b.add_audio_track()
                for n in todo:
                    if len(b.strip_info(ti).inserts) >= 8:
                        ti = b.add_audio_track()
                    b.select_track(ti)
                    try:
                        say(f"reading {n}")
                        shown = b.insert_plugin(ti, n)
                        slot = len(b.strip_info(ti).inserts)
                        b.select_track(ti)
                        header, values = b.read_plugin_params(ti, slot, max_pages)
                        known[n] = {"name": header or shown, "shown_as": shown, "params": values,
                                    "read": datetime.now().strftime("%Y-%m-%d"), "pages_read": -(-len(values) // 8)}
                    except LogicError as e:
                        known[n] = {"error": str(e), "read": datetime.now().strftime("%Y-%m-%d")}
            finally:
                b.close_project(title)
        DEVICES_CACHE.parent.mkdir(parents=True, exist_ok=True)
        DEVICES_CACHE.write_text(json.dumps(known, indent=1, sort_keys=True) + "\n")
    low = {k.lower(): k for k in known}
    return {n: known[low[n.lower()]] for n in names if n.lower() in low}


# ---------------------------------------------------------------------- text
def format_state(st: dict) -> str:
    head = f"# {st['project']}" + ("" if st.get("saved") else "  (never saved)")
    facts = [f"{st['tempo']:g} BPM" if st.get("tempo") else None, st.get("key"), st.get("time_signature"),
             f"playhead {st['playhead'][0]}.{st['playhead'][1]}" if st.get("playhead") else None, "playing" if st.get("playing") else None]
    lines = [head, " · ".join(str(f) for f in facts if f)]
    if st.get("path"):
        lines.append(st["path"])
    if st.get("other_projects"):
        lines.append(f"also open: {', '.join(st['other_projects'])}")

    def row(r: dict, first: str) -> str:
        flags = "".join(x for x, on in (("M", r["mute"]), ("S", r["solo"])) if on)
        return (f"| {first} | {r['name']} | {r['volume']} | {r['pan']} | {flags} | {r.get('instrument') or ''} | {', '.join(r['inserts'])} | "
                f"{', '.join(r['sends'])} | {r.get('output') or ''} | {', '.join(r.get('regions', []))} |")
    lines += ["", "| # | strip | fader | pan | M/S | instrument | inserts | sends | output | regions |", "|---|---|---|---|---|---|---|---|---|---|"]
    lines += [row(t, f"{t['n']}{'*' if t.get('selected') else ''}") for t in st["tracks"]]
    lines += [row(a, "aux") for a in st["aux"]]
    lines += [row(o, o.get("kind", "out")) for o in st["outputs"]]
    lines.append("\n`*` = the selected track. Name a strip by its name or as `#n`.")
    return "\n".join(lines)


def format_params(name: str, values: dict[str, str], cols: int = 4) -> str:
    items = [f"{k} = {v}" for k, v in values.items()]
    width = max((len(i) for i in items), default=0) + 3
    rows = ["".join(i.ljust(width) for i in items[r:r + cols]).rstrip() for r in range(0, len(items), cols)]
    return f"# {name} — {len(values)} parameters (names as the control surface shows them)\n" + "\n".join(rows)


# ---------------------------------------------------------------------- the command line: `rick-rubin logic ...`
ACTIONS = {
    "inspect": "the open project: tempo, key, tracks, strips, inserts, sends, regions",
    "params": "TRACK [PLUGIN] — displayed parameters of an insert (or of the track's instrument)",
    "set": "TRACK volume=-6 pan=-20 mute=on solo=off — fader (dB), pan (-64..63), mute, solo",
    "insert": "TRACK PLUGIN [KEY=VALUE ...] [--sidechain TRACK] — a plug-in in the first free slot",
    "tweak": "TRACK PLUGIN KEY=VALUE ... — parameters of a plug-in already on the strip",
    "sidechain": "TRACK PLUGIN SOURCE — the plug-in's side chain input",
    "send": "TRACK BUS DB|off — a send to a bus",
    "instrument": "TRACK NAME [KEY=VALUE ...] — load an instrument, Audio Unit or Library patch on a track",
    "add-instrument": "NAME [KEY=VALUE ...] [--name TRACK] — a new software-instrument track",
    "add-audio": "FILE [--bar N] [--name TRACK] — a new audio track holding the file",
    "add-midi": "FILE [--bar N] [--name TRACK ...] — the file's tracks as new instrument tracks",
    "rename": "TRACK NAME",
    "bounce": "OUT.wav [--bars A-B] [--tracks T ...] — offline bounce",
    "backup": "copy the project's saved state to ~/.rick-rubin/backups now",
    "devices": "PLUGIN ... [--refresh] — a plug-in's parameters, read in a scratch project and remembered",
}
READ_ONLY = {"inspect"}
NEEDS_SURFACE = {"params", "insert", "tweak", "sidechain", "send", "instrument", "add-instrument", "devices"}


def add_parser(sub) -> None:
    s = sub.add_parser("logic", help="work inside the Logic project that is open: read it (inspect, params) and make single changes "
                                     "(set, insert, tweak, send, instrument, add-audio, add-midi, bounce)",
                       description="\n".join(f"  {k:15s} {v}" for k, v in ACTIONS.items()), formatter_class=_raw_help())
    s.add_argument("action", choices=sorted(ACTIONS))
    s.add_argument("args", nargs="*")
    s.add_argument("--project", help="the open project to work in (default: the front one)")
    s.add_argument("--json", action="store_true", help="inspect/params/devices: print JSON")
    s.add_argument("--bar", type=int, default=1, help="add-audio/add-midi: the bar the region starts on")
    s.add_argument("--name", action="append", default=[], help="add-*: the new track's name (repeat for several MIDI tracks)")
    s.add_argument("--bars", help="bounce: A-B")
    s.add_argument("--tracks", nargs="+", help="bounce: only these strips (soloed for the bounce)")
    s.add_argument("--sidechain", help="insert: the track that keys the plug-in")
    s.add_argument("--nth", type=int, default=1, help="tweak/params/sidechain: which one when the strip holds the plug-in more than once (1 = first)")
    s.add_argument("--pages", type=int, default=40, help="params/devices: how many pages of eight parameters to read at most")
    s.add_argument("--refresh", action="store_true", help="devices: read again even when remembered")
    s.add_argument("--no-backup", action="store_true", help="do not back up the saved state before the first change")
    s.add_argument("--background", action="store_true", help="leave Logic where it is (Save commands and Aux / Stereo Out strips need it in front)")


def _raw_help():
    import argparse
    return argparse.RawDescriptionHelpFormatter


def run(a, say=None) -> int:
    """Carry out one `rick-rubin logic ...` command. Prints what was read or what changed (before -> after)."""
    from .bridge import LogicBridge
    say = say or (lambda *_: None)
    act, args = a.action, list(a.args)

    def need(n: int, usage: str) -> None:
        if len(args) < n:
            raise LogicError(f"usage: rick-rubin logic {act} {usage}")

    if act == "devices":
        need(1, "PLUGIN ...")
        maps = map_plugins(args, progress=say, refresh=a.refresh, max_pages=a.pages)
        if a.json:
            print(json.dumps(maps, indent=1))
        else:
            for n, m in maps.items():
                print(f"# {n}: {m['error']}" if "error" in m else format_params(f"{n} ({m['name']})", m["params"]))
                print()
        return 0

    with LogicBridge(progress=say, use_mcu=act in NEEDS_SURFACE or act == "set", front=act not in READ_ONLY and act != "backup" and not a.background) as b:
        b.project = find_project(b.app, a.project)
        b._mixer = None
        if act == "backup":
            where = backup(b, force=True)
            print(f"backed up to {where}" if where else "nothing to back up: the project has never been saved")
            return 0
        with Session(b, backups=not a.no_backup) as s:
            if act == "inspect":
                st = s.state()
                print(json.dumps(st, indent=1, default=str) if a.json else format_state(st))
                return 0
            if act == "params":
                need(1, "TRACK [PLUGIN]")
                name, values = s.params(args[0], args[1] if len(args) > 1 else None, a.nth - 1, a.pages)
                print(json.dumps({"plugin": name, "params": values}, indent=1) if a.json else format_params(name, values))
                return 0
            changes: list[Change] = []
            if act == "set":
                need(2, "TRACK volume=-6 pan=-20 mute=on solo=off")
                kv = parse_settings(args[1:])
                unknown = set(kv) - {"volume", "pan", "mute", "solo"}
                if unknown:
                    raise LogicError(f"set takes volume, pan, mute, solo (got {sorted(unknown)}); plug-in parameters are `tweak`")
                changes = s.mix(args[0], kv.get("volume"), kv.get("pan"), kv.get("mute"), kv.get("solo"))
            elif act == "insert":
                need(2, "TRACK PLUGIN [KEY=VALUE ...] [--sidechain TRACK]")
                changes = [s.insert(args[0], args[1], parse_settings(args[2:]), a.sidechain)]
            elif act == "tweak":
                need(3, "TRACK PLUGIN KEY=VALUE ...")
                changes = [s.tweak(args[0], args[1], parse_settings(args[2:]), a.nth - 1)]
            elif act == "sidechain":
                need(3, "TRACK PLUGIN SOURCE")
                changes = [s.side_chain(args[0], args[1], args[2], a.nth - 1)]
            elif act == "send":
                need(3, "TRACK BUS DB|off")
                bus = int(re.sub(r"\D", "", args[1]) or 0)
                if bus < 1:
                    raise LogicError(f"BUS is a bus number (1, 2, ... or 'Bus 1'), got {args[1]!r}")
                changes = [s.send(args[0], bus, None if args[2].lower() in ("off", "none", "remove") else float(args[2]))]
            elif act == "instrument":
                need(2, "TRACK NAME [KEY=VALUE ...]")
                changes = [s.instrument(args[0], args[1], parse_settings(args[2:]))]
            elif act == "add-instrument":
                need(1, "NAME [KEY=VALUE ...] [--name TRACK]")
                changes = [s.add_instrument(args[0], a.name[0] if a.name else None, parse_settings(args[1:]))] + s.changes[1:]
            elif act == "add-audio":
                need(1, "FILE [--bar N] [--name TRACK]")
                changes = [s.add_audio(args[0], a.bar, a.name[0] if a.name else None)]
            elif act == "add-midi":
                need(1, "FILE [--bar N] [--name TRACK ...]")
                changes = [s.add_midi(args[0], a.bar, a.name)]
            elif act == "rename":
                need(2, "TRACK NAME")
                changes = [s.rename(args[0], args[1])]
            elif act == "bounce":
                need(1, "OUT.wav [--bars A-B] [--tracks T ...]")
                bars = None
                if a.bars:
                    m = re.fullmatch(r"(\d+)-(\d+)", a.bars)
                    if not m:
                        raise LogicError(f"--bars is A-B, got {a.bars!r}")
                    bars = (int(m.group(1)), int(m.group(2)))
                t0 = time.time()
                r = s.bounce(args[0], bars, a.tracks)
                print(f"bounced {r['path']}" + (f" (bars {bars[0]}-{bars[1]})" if bars else "") + (f", soloed {r['tracks']}" if r["tracks"] else "")
                      + f" in {time.time() - t0:.0f} s")
                return 0
            for c in changes:
                print(c.line())
            print(f"project: {b.project} (not saved by rick-rubin: save it in Logic when you are happy)")
            return 0 if all(c.ok for c in changes) else 1
