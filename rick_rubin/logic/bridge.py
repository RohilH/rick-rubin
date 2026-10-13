"""The Logic Pro bridge: everything a push or capture needs Logic to do, as plain method calls.

Logic Pro has no scripting API for its arrangement, so this bridge drives the app from the outside with
three mechanisms, each used where it is the most reliable:

  * a Standard MIDI File (smf.py) that Logic opens as a new project — tempo, markers, tracks, regions,
    notes, and a General MIDI program per track that Logic turns into one of its own patches;
  * the macOS accessibility API (ax.py) — the Mixer (faders, pan, mute, insert slots, sends, output), plug-in
    windows (side chain, whatever parameters they expose), the menu bar, dialogs (bounce, save, open, alerts)
    and the control bar (tempo, playhead). Keystrokes for Logic's own pop-up menus are posted to Logic's
    process only (keys.py); the person at the Mac keeps their keyboard and mouse;
  * a Mackie Control emulated on a virtual MIDI port (mcu.py), which Logic detects on its own — transport,
    the bar/beat clock, track selection, sends, and plug-in parameters by their displayed values.

Nothing here knows about songs: client.py turns a Song into calls on this class, the way live/client.py
turns one into bridge commands for Ableton.
"""
from __future__ import annotations

import json
import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from collections.abc import Callable

from ..live.client import BridgeError
from . import ax as AX
from . import keys as K
from . import mcu as M

LOGIC_APP = "Logic Pro"
# Logic's own software instruments (so `instrument="Retro Synth"` goes to the instrument slot menu, not the Library)
LOGIC_INSTRUMENTS = ["Alchemy", "Drum Kit Designer", "Drum Machine Designer", "Drum Synth", "EFM1", "ES E", "ES M", "ES P", "ES1", "ES2",
                     "EVOC 20 PS", "External Instrument", "Klopfgeist", "Quick Sampler", "Retro Synth", "Sample Alchemy", "Sampler",
                     "Sculpture", "Studio Bass", "Studio Horns", "Studio Piano", "Studio Strings", "Ultrabeat", "Vintage B3 Organ",
                     "Vintage Clav", "Vintage Electric Piano"]
# the stems Logic Pro 11.2's Stem Splitter separates (its dialog's check boxes, in order)
STEMS = ("Vocals", "Drums", "Bass", "Guitar", "Piano", "Other")
# how Logic abbreviates parameter names on a Mackie Control LCD, for the plug-ins a house track reaches for.
# Anything not listed is matched by abbreviation (see `abbrev_matches`); the LCD name itself always works too.
LCD_NAMES = {
    "Compressor": {"Threshold": "Thrs", "Ratio": "Ratio", "Attack": "Attack", "Release": "Rel", "Auto Release": "AutRel",
                   "Make Up": "MakeUp", "Makeup": "MakeUp", "Auto Gain": "AutGai", "Knee": "Knee", "Peak/RMS": "Peak/S",
                   "Limiter": "LimrOn", "Limiter Threshold": "LimThr", "Distortion": "Distrt", "Mix": "Mix", "Circuit Type": "CirTyp",
                   "Side Chain Detection": "SiChDe", "Side Chain Filter": "State", "Filter Mode": "Mode", "Filter Frequency": "Freq",
                   "Filter Q": "Q", "Filter Gain": "Gain"},
    "ChromaVerb": {"Dry": "Dry", "Wet": "Wet", "Room Type": "RooTyp", "Decay": "DcTime", "Decay Time": "DcTime", "Predelay": "Predly",
                   "Pre-delay": "Predly", "Freeze": "Freeze"},
    "Limiter": {"Gain": "Gain", "Release": "Releas", "Output Level": "OutLev", "Lookahead": "LookAh"},
    "AutoFilter": {"Cutoff": "Cutoff", "Resonance": "Reso", "Drive": "Drive", "Filter Type": "FltTyp"},
}


class LogicError(BridgeError):
    pass


def logic_running() -> bool:
    return AX.logic_pid() is not None


def logic_version() -> str | None:
    try:
        out = subprocess.run(["defaults", "read", f"/Applications/{LOGIC_APP}.app/Contents/Info.plist", "CFBundleShortVersionString"],
                             capture_output=True, text=True, timeout=5)
        return out.stdout.strip() or None
    except Exception:  # noqa: BLE001
        return None


def abbrev_matches(abbrev: str, name: str) -> bool:
    """Does the LCD abbreviation `abbrev` ('Thrs', 'AutRel', 'MakeUp') stand for `name` ('Threshold')?
    Exact (case-insensitive) or the abbreviation's letters appear in order in the name, starting with its first."""
    a = re.sub(r"[^a-z0-9/]", "", abbrev.lower())
    n = re.sub(r"[^a-z0-9/]", "", name.lower())
    if not a or not n:
        return False
    if a == n or n.startswith(a):
        return True
    if a[0] != n[0]:
        return False
    i = 0
    for ch in n:
        if i < len(a) and ch == a[i]:
            i += 1
    return i == len(a)


def first_new_index(before: list[str], after: list[str]) -> int:
    """Where a track was added: the first position at which the track lists differ (the end when they agree)."""
    return next((i for i, name in enumerate(after) if i >= len(before) or name != before[i]), len(after) - 1)


@dataclass
class TrackRef:
    index: int            # 0-based position among the project's tracks (= Mixer strip order)
    name: str


@dataclass
class ParamReport:
    set: dict = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


class LogicBridge:
    """Connect once per command; `with LogicBridge() as b:`. Methods raise LogicError with a message a person can act on."""

    def __init__(self, progress: Callable[[str], None] | None = None, use_mcu: bool = True, project: str | None = None):
        self.say = progress or (lambda *_: None)
        self.use_mcu = use_mcu
        self.app: AX.LogicApp | None = None
        self.mcu: M.MackieControl | None = None
        self.project = project               # title prefix of the project window this bridge works in
        self._mixer: AX.Mixer | None = None
        self._opened: set[str] = set()       # projects this bridge opened itself (the only ones it closes unasked)
        self._bank = 0
        self._view = "tracks"

    # ------------------------------------------------------------------ lifecycle
    def connect(self) -> LogicBridge:
        if not logic_running():
            self.say("launching Logic Pro")
            subprocess.run(["open", "-a", LOGIC_APP], check=False)
            if AX.wait_for(logic_running, 150.0, 1.0) is None:
                raise LogicError("Logic Pro did not start (it takes a minute or two on a cold start)")
            time.sleep(6.0)
        try:
            self.app = AX.LogicApp()
        except AX.AXError as e:
            raise LogicError(str(e)) from e
        if self.use_mcu:
            try:
                self.mcu = M.MackieControl(log=self.say).open()
            except Exception as e:  # noqa: BLE001
                raise LogicError(f"cannot open the virtual MIDI port for the Mackie Control emulation ({e}); "
                                 "pip install mido python-rtmidi") from e
            # Logic finds the surface by itself and mirrors its state within a second; it also opens its
            # Control Surface Setup window the first time, which is closed again here
            if AX.wait_for(lambda: self.mcu.state.last_change > 0, 3.0, 0.05) is None:
                self.say("Logic has not answered the Mackie Control port yet (Logic Pro > Control Surfaces > Setup shows it once detected)")
            time.sleep(0.4)
            self._close_setup_window()
        if self.project is None:
            self.project = self.app.project_title()
        return self

    def close(self) -> None:
        if self.mcu is not None:
            self.mcu.close()
            self.mcu = None

    def __enter__(self):
        return self.connect() if self.app is None else self

    def __exit__(self, *a):
        self.close()

    def _close_setup_window(self) -> None:
        for w in self.app.windows():
            if AX.title(w) == "Control Surface Setup":
                AX.press(AX.find(w, lambda e: AX.attr(e, "AXSubrole") == "AXCloseButton", 1))

    def pause_mcu(self):
        """Context manager: disconnect the Mackie Control for a step, then reconnect. Logic 11.2 crashed when a
        plug-in window's side chain was chosen while the surface was linked to that window."""
        bridge = self

        class _Paused:
            def __enter__(self_):
                if bridge.mcu is not None:
                    bridge.mcu.close()
                    bridge.mcu = None
                    bridge._mcu_paused = True
                    time.sleep(0.8)
                return self_

            def __exit__(self_, *a):
                if getattr(bridge, "_mcu_paused", False) and bridge.use_mcu:
                    bridge.mcu = M.MackieControl(log=bridge.say).open()
                    AX.wait_for(lambda: bridge.mcu.state.last_change > 0, 4.0, 0.05)
                    time.sleep(0.5)
                    bridge._close_setup_window()
                    bridge._view = "tracks"
                    bridge._mcu_paused = False
        return _Paused()

    def ping(self) -> dict:
        return {"logic_version": logic_version(), "mcu": bool(self.mcu and self.mcu.state.last_change > 0),
                "project": self.project, "projects": [self.app.project_title(w) for w in self.app.project_windows()]}

    # ------------------------------------------------------------------ windows
    @property
    def main(self):
        w = self.app.main_window(self.project)
        if w is None and self.project:
            # a Save As renames the window: '<title>' becomes '<title>.logicx'-less saved name, or vice versa
            for cand in self.app.project_windows():
                t = self.app.project_title(cand) or ""
                if t.startswith(self.project) or self.project.startswith(t) or t.endswith(self.project):
                    self.project = t
                    self._mixer = None
                    return cand
        if w is None:
            raise LogicError(f"the project window {self.project!r} is not open in Logic any more")
        return w

    def mixer(self) -> AX.Mixer:
        if self._mixer is None:
            self._mixer = AX.Mixer(self.app, self.project)
        return self._mixer

    def focus(self) -> None:
        """Make our project window Logic's key window (menu commands act on it)."""
        self.clear_popups()
        self.app.make_key(self.main)

    def _answer_alert(self, wanted: list[str], contains: str | None = None, timeout: float = 2.0) -> str | None:
        """Press the first of `wanted` buttons on an alert (whose text contains `contains`, if given)."""
        t_end = time.time() + timeout
        while time.time() < t_end:
            for al in self.app.alerts():
                text = self.app.alert_text(al)
                if contains and contains.lower() not in text.lower():
                    continue
                for b in wanted:
                    if self.app.answer(al, b):
                        time.sleep(0.3)
                        return b
            time.sleep(0.1)
        return None

    def pending_alert(self) -> tuple[str, list[str]] | None:
        for al in self.app.alerts():
            return self.app.alert_text(al), self.app.alert_buttons(al)
        return None

    # ------------------------------------------------------------------ projects
    def open_midi_project(self, path: str | Path, expect_tracks: int | None = None, close_ours: bool = True,
                          ours: tuple[str, ...] = ()) -> str:
        """Open `path` (an SMF) as a new Logic project and make it this bridge's project. When another project
        is open Logic asks whether to close it first: a project of ours (title in `ours`, or one this bridge
        opened earlier) is closed without saving, anyone else's is left open — including the project that was
        frontmost when the bridge connected, which is only the bridge's default *target*, not ours to discard."""
        before = {self.app.project_title(w) for w in self.app.project_windows()}
        subprocess.run(["open", "-a", LOGIC_APP, str(path)], check=False)
        t_end = time.time() + 40.0
        new_title = None
        while time.time() < t_end:
            pend = self.pending_alert()
            if pend:
                text, buttons = pend
                low = text.lower()
                if "close the current project" in low:
                    cur = self.app.project_title()
                    mine = close_ours and cur is not None and (cur in ours or cur in self._opened)
                    self._answer_alert(["Close"] if mine else ["Don’t Close", "Don't Close"], "close the current project")
                elif "want to save" in low:
                    self._answer_alert(["Don’t Save", "Don't Save"], "want to save")
                elif buttons:
                    self.say(f"Logic asks: {text} [{', '.join(buttons)}] — answering {buttons[-1]!r}")
                    self._answer_alert([buttons[-1]])
            titles = {self.app.project_title(w) for w in self.app.project_windows()} - before
            if titles:
                new_title = sorted(titles)[0]
                if expect_tracks is None or len(self.app.tracks(self.app.main_window(new_title))) >= expect_tracks:
                    break
            time.sleep(0.25)
        if new_title is None:
            raise LogicError(f"Logic did not open {Path(path).name} as a project (pending: {self.pending_alert()})")
        time.sleep(0.8)
        self.project = new_title
        self._opened.add(new_title)
        self._mixer = None
        return new_title

    def close_project(self, title: str | None = None, save: bool = False) -> bool:
        """Close a project window (ours by default) without saving."""
        w = self.app.main_window(title or self.project)
        if w is None:
            return False
        self.app.make_key(w)
        if not self.app.menu("File", "Close Project"):
            return False
        self._answer_alert(["Save"] if save else ["Don’t Save", "Don't Save"], "want to save", timeout=3.0)
        AX.wait_for(lambda: self.app.main_window(title or self.project) is None, 10.0)
        if (title or self.project) == self.project:
            self._mixer = None
        return True

    def save_project_as(self, folder: str | Path, name: str) -> Path:
        """File > Save As into `folder` (an existing, visible folder) as '<name>.logicx' (a package)."""
        folder = Path(folder).expanduser().resolve()
        folder.mkdir(parents=True, exist_ok=True)
        self.focus()
        if not self.app.menu("File", "Save As…"):
            raise LogicError("File > Save As is not available")
        panel = AX.wait_for(lambda: next((d for d in self.app.dialogs() if AX.find(d, lambda e: AX.attr(e, "AXIdentifier") == "saveAsNameTextField", 3)), None), 8.0)
        if panel is None:
            raise LogicError("the Save panel did not open")
        self._panel_navigate(panel, folder)
        for cb_title in ("Include Apple Sound Library Content",):
            cb = AX.find(panel, lambda e, t=cb_title: AX.role(e) == "AXCheckBox" and AX.title(e) == t, 6)
            if cb is not None:
                AX.set_checkbox(cb, False)
        tf = AX.find(panel, lambda e: AX.attr(e, "AXIdentifier") == "saveAsNameTextField", 3)
        AX.set_value(tf, name)
        btn = AX.find(panel, lambda e: AX.role(e) == "AXButton" and AX.attr(e, "AXIdentifier") == "OKButton", 3) or \
            AX.find(panel, lambda e: AX.role(e) == "AXButton" and AX.title(e) == "Save", 3)
        AX.press(btn)
        time.sleep(1.0)
        self._answer_alert(["Replace"], "already exists", timeout=1.5)
        self._answer_alert(["Cancel"], "download", timeout=1.0)
        target = folder / f"{name}.logicx"
        if AX.wait_for(lambda: target.exists(), 20.0, 0.5) is None:
            raise LogicError(f"Logic did not write {target} (pending: {self.pending_alert()})")
        new_title = AX.wait_for(lambda: next((self.app.project_title(w) for w in self.app.project_windows()
                                             if (self.app.project_title(w) or "").startswith(name)), None), 8.0)
        if new_title:
            if self.project in self._opened:
                self._opened.add(new_title)
            self.project = new_title
            self._mixer = None
        return target

    def save_project(self) -> bool:
        self.focus()
        ok = self.app.menu("File", "Save")
        time.sleep(0.5)
        self._answer_alert(["Cancel"], "download", timeout=1.0)
        return ok

    # ---- file panels (NSOpenPanel / NSSavePanel): sidebar + column browser, no typing needed
    def _panel_columns(self, panel) -> list:
        br = AX.find(panel, lambda e: AX.role(e) == "AXBrowser", 5)
        if br is None:
            return []
        outer = next((c for c in AX.children(br) if AX.role(c) == "AXScrollArea"), None)
        return [c for c in AX.children(outer) if AX.role(c) == "AXScrollArea"] if outer is not None else []

    @staticmethod
    def _column_items(col) -> list[tuple[object, str]]:
        lst = AX.find(col, lambda e: AX.role(e) == "AXList", 2)
        out = []
        for g in AX.children(lst) if lst is not None else []:
            tf = AX.find(g, lambda e: AX.role(e) == "AXTextField" or AX.role(e) == "AXStaticText", 2)
            out.append((g, str(AX.attr(tf, "AXValue") or "") if tf is not None else AX.title(g)))
        return out

    def _panel_column_view(self, panel) -> None:
        if AX.find(panel, lambda e: AX.role(e) == "AXBrowser", 5) is not None:
            return
        vo = AX.find(panel, lambda e: AX.attr(e, "AXIdentifier") == "View Options", 3)
        if vo is None:
            return
        try:
            menu = AX.popup_menu(vo)
            AX.choose_in_menu(menu, "Columns", allow_sub=False)
        except AX.AXError:
            pass
        AX.wait_for(lambda: AX.find(panel, lambda e: AX.role(e) == "AXBrowser", 5), 3.0)

    def _panel_navigate(self, panel, folder: Path, select_file: str | None = None) -> None:
        """Walk the panel's column browser to `folder` (and select `select_file` in it) starting from the
        'Macintosh HD' sidebar item. Hidden folders cannot be reached this way."""
        self._panel_column_view(panel)
        side = AX.find(panel, lambda e: AX.role(e) == "AXOutline" and AX.desc(e) == "sidebar", 5)
        rows = [r for r in AX.children(side) if AX.role(r) == "AXRow"] if side is not None else []

        def row_title(r):
            t = AX.find(r, lambda e: AX.role(e) == "AXStaticText", 3)
            return str(AX.attr(t, "AXValue") or "")
        parts = [p for p in folder.parts if p != "/"]
        home = Path.home()
        start_row, skip = None, 0
        for r in rows:
            if row_title(r) == "Macintosh HD":
                start_row = r
        # a favourite that is a prefix of the path saves columns (Documents, Desktop, Downloads)
        for fav in ("Documents", "Desktop", "Downloads"):
            if folder == home / fav or (home / fav) in folder.parents:
                for r in rows:
                    if row_title(r) == fav:
                        start_row, skip = r, len((home / fav).parts) - 1
        if start_row is None:
            raise LogicError("the file panel has no 'Macintosh HD' in its sidebar")
        AX.set_attr(start_row, "AXSelected", True)
        time.sleep(0.6)
        todo = parts[skip:] + ([select_file] if select_file else [])
        for depth, want in enumerate(todo):
            cols = self._panel_columns(panel)
            if not cols:
                raise LogicError("the file panel shows no columns")
            col = cols[min(depth, len(cols) - 1)]
            items = AX.wait_for(lambda col=col: [(g, n) for g, n in self._column_items(col) if n], 3.0) or []
            if not any(n == want for _, n in items):
                # a folder made a moment ago reaches the panel's listing a little later
                def listing(col=col, want=want):
                    it = [(g, n) for g, n in self._column_items(col) if n]
                    return it if any(n == want for _, n in it) else None
                items = AX.wait_for(listing, 4.0, 0.3) or items
            hit = next((g for g, n in items if n == want), None)
            if hit is None:
                names = [n for _, n in items]
                raise LogicError(f"{want!r} is not in {'/'.join(parts[:skip + depth]) or '/'} (the panel shows {names[:12]}{'…' if len(names) > 12 else ''})")
            lst = AX.find(col, lambda e: AX.role(e) == "AXList", 2)
            if not AX.set_attr(lst, "AXSelectedChildren", [hit]):
                AX.press(hit)
            time.sleep(0.45)

    # ------------------------------------------------------------------ tracks
    def tracks(self) -> list[str]:
        return self.app.tracks(self.main)

    def tempo(self) -> float | None:
        return self.app.tempo(self.main)

    def name_tracks_by_regions(self) -> list[str]:
        """Logic names an imported track after the patch it chose; the region keeps the MIDI track's name.
        Tracks area > Functions > 'Name Track by Region/Cell Name' on all regions puts the song's names back."""
        self.focus()
        self.app.menu("Edit", "selectAll:")
        time.sleep(0.3)
        fn = self.app.tracks_functions_menu(self.main)
        if fn is None:
            raise LogicError("the Tracks area has no Functions menu")
        AX.press(fn)
        menu = AX.wait_for(lambda: next((c for c in AX.children(fn) if AX.role(c) == "AXMenu"), None), 2.0)
        if menu is None:
            raise LogicError("the Functions menu did not open")
        try:
            AX.choose_in_menu(menu, "Name Track by Region/Cell Name", allow_sub=False)
        except AX.AXError as e:
            raise LogicError(str(e)) from e
        time.sleep(0.6)
        self._mixer = None
        self.select_track(0)                                 # one track selected again: Logic applies strip edits to every selected strip
        return self.tracks()

    def select_track(self, index: int) -> None:
        """Select exactly this track (edits to a Mixer strip apply to all selected strips, so keep it to one)."""
        self.app.select_track(index, self.main)
        time.sleep(0.1)

    def add_audio_track(self) -> int:
        """Track > New Tracks… > Audio > Create, below the selected track. Returns its index (found by comparing
        the track list before and after: when the selection does not take, Logic puts the track elsewhere)."""
        before = self.tracks()
        n = len(before)
        self.select_track(n - 1)
        self.focus()
        self.app.menu("Track", "New Tracks…")
        sheet = AX.wait_for(lambda: next((c for c in AX.children(self.main) if AX.role(c) == "AXSheet"), None), 5.0)
        if sheet is None:
            raise LogicError("the New Tracks sheet did not open")
        grp = AX.find(sheet, lambda e: AX.role(e) == "AXGroup" and AX.desc(e).startswith("Audio"), 6)
        rb = AX.find(grp, lambda e: AX.role(e) == "AXRadioButton", 3) if grp is not None else None
        AX.press(rb)
        time.sleep(0.2)
        count = AX.find(sheet, lambda e: AX.role(e) == "AXTextField" and "Number of tracks" in AX.desc(e), 4)
        if count is not None:
            AX.set_value(count, "1")
        AX.press(AX.find(sheet, lambda e: AX.role(e) == "AXButton" and AX.title(e) == "Create", 3))
        if AX.wait_for(lambda: len(self.tracks()) > n, 8.0) is None:
            raise LogicError("Logic did not add an audio track")
        self._mixer = None
        return first_new_index(before, self.tracks())

    def import_audio(self, track_index: int, path: str | Path, bar: int, beat: int = 1, keep_file_rate: bool = False) -> bool:
        """File > Import > Audio File… onto `track_index` at bar.beat (Logic places it at the playhead). When the file's
        sample rate is not the project's, Logic asks: the file is converted, or with `keep_file_rate` the project
        is switched to the file's rate (right for a project that holds only this file)."""
        path = Path(path).expanduser().resolve()
        if not path.exists():
            raise LogicError(f"{path} does not exist")
        self.select_track(track_index)
        self.set_playhead(bar, beat)
        self.focus()
        self.app.menu("File", "Import", "Audio File…")
        panel = AX.wait_for(lambda: next((d for d in self.app.dialogs() if AX.attr(d, "AXIdentifier") == "open-panel"), None), 8.0)
        if panel is None:
            raise LogicError("the Import Audio File panel did not open (is an audio track selected?)")
        self._panel_navigate(panel, path.parent, select_file=path.name)
        btn = AX.find(panel, lambda e: AX.attr(e, "AXIdentifier") == "OKButton", 3)
        AX.press(btn)
        time.sleep(0.8)
        # Logic may ask about the file's tempo, and (a 44.1 kHz file in a 48 kHz project) about the sample rate
        rate_answer = "Change Project" if keep_file_rate else "Convert File"
        t_end = time.time() + 4.0
        while time.time() < t_end:
            if self._answer_alert([rate_answer], "sample rate", timeout=0.3) or \
                    self._answer_alert(["Don’t Import", "Don't Import", "OK", "Import"], "tempo", timeout=0.3):
                t_end = time.time() + 1.5
        if AX.wait_for(lambda: not any(AX.attr(d, "AXIdentifier") == "open-panel" for d in self.app.dialogs()), 10.0) is None:
            raise LogicError("the Import Audio File panel stayed open")
        left = self.pending_alert()
        if left:
            raise LogicError(f"Logic is asking {left[0][:120]!r} ({', '.join(left[1])}) after the import")
        return True

    # ------------------------------------------------------------------ regions and the Stem Splitter
    def track_regions(self, track_index: int) -> list:
        """The region elements on a track's lane in the Tracks area (lanes follow the track order)."""
        cont = AX.find(self.main, lambda e: AX.desc(e) == "Tracks contents", 10)
        lanes = [k for k in AX.children(cont) if AX.role(k) == "AXLayoutArea"] if cont is not None else []
        if track_index >= len(lanes):
            return []
        return [r for r in AX.children(lanes[track_index]) if AX.role(r) == "AXLayoutItem"]

    def select_region(self, track_index: int, nth: int = 0) -> str:
        """Make the nth region of the track the selected one and return its name. Focusing a region selects it
        (setting AXSelected does not stick)."""
        regions = AX.wait_for(lambda: self.track_regions(track_index), 10.0) or []
        if len(regions) <= nth:
            raise LogicError(f"track {track_index + 1} has no region {nth + 1} (it has {len(regions)})")
        AX.set_attr(regions[nth], "AXFocused", True)
        if AX.wait_for(lambda: AX.attr(self.track_regions(track_index)[nth], "AXSelected"), 2.0) is None:
            raise LogicError(f"could not select the region {AX.desc(regions[nth])!r}")
        return AX.desc(regions[nth])

    def region_menu(self, track_index: int, nth: int = 0):
        """Right-click a region: its context menu (Stem Splitter…, Bounce in Place…, Edit, Export …), or None.
        Logic opens it on AXShowMenu (which reports failure) as an AXMenu in the window's tree."""
        regions = self.track_regions(track_index)
        if len(regions) <= nth:
            return None
        AX.do(regions[nth], "AXShowMenu")
        return AX.wait_for(lambda: AX.find(self.track_regions(track_index)[nth], lambda e: AX.role(e) == "AXMenu", 3)
                           or AX.find(self.main, lambda e: AX.role(e) == "AXMenu", 12), 2.0)

    def _tracks_menu(self, name: str):
        """Open the Tracks area's own Edit / Functions / View menu and return it (press an item, or AXCancel it)."""
        button = AX.find(self.main, lambda e: AX.role(e) == "AXMenuButton" and AX.desc(e) == name, 8)
        if button is None:
            raise LogicError(f"the Tracks area has no {name} menu")
        AX.press(button)
        menu = AX.wait_for(lambda: next((c for c in AX.children(button) if AX.role(c) == "AXMenu"), None), 2.0)
        if menu is None:
            raise LogicError(f"the Tracks area's {name} menu did not open")
        return menu

    def _stem_sheet(self):
        return next((s for s in AX.children(self.main) if AX.role(s) == "AXSheet"
                     and AX.find(s, lambda e: AX.role(e) == "AXHeading" and AX.desc(e) == "Stem Splitter", 4) is not None), None)

    def stem_split(self, track_index: int, stems: tuple[str, ...] | list[str] = STEMS, submix: bool = False,
                   timeout: float = 600.0, on_progress: Callable[[float], None] | None = None) -> list[str]:
        """Right-click > Stem Splitter… on the track's first region (Functions > Stem Splitter… if the context menu
        does not open), with `stems` ticked (any of STEMS)
        and the Submix of the unticked stems on or off, and wait for it. Logic writes the stems into the project's
        Audio Files folder under a progress window (`stem_split_progress`, passed to `on_progress`), then adds a
        summing stack holding one audio track per stem and mutes the original region (an unsaved project gets the
        tracks at once). Returns the names of the tracks added."""
        want = {s.strip().capitalize() for s in stems}
        unknown = want - set(STEMS)
        if unknown or not want:
            raise LogicError(f"Logic's Stem Splitter has the stems {', '.join(STEMS)} (asked for {sorted(unknown) or 'none'})")
        self.focus()
        self.select_region(track_index)
        before = self.tracks()

        def splitter_item(menu):
            return next((i for i in AX.children(menu) if AX.title(i).rstrip("…") == "Stem Splitter"), None) if menu is not None else None
        # the region's right-click menu, as a person would; the Tracks area's Functions menu has the same command
        menu = self.region_menu(track_index)
        item = splitter_item(menu)
        via = "the region's right-click menu"
        if item is None or not AX.attr(item, "AXEnabled"):
            if menu is not None:
                AX.do(menu, "AXCancel")
            menu = self._tracks_menu("Functions")
            item = splitter_item(menu)
            via = "the Tracks area's Functions menu"
        self.say(f"Stem Splitter… from {via}")
        if item is None or not AX.attr(item, "AXEnabled"):
            AX.do(menu, "AXCancel")
            raise LogicError("Stem Splitter is not available: it needs Logic Pro 11 on a Mac with Apple silicon, "
                             "and an audio region selected" if item is None else "Stem Splitter is disabled (no audio region selected)")
        AX.press(item)
        sheet = AX.wait_for(self._stem_sheet, 5.0)
        if sheet is None:
            raise LogicError("the Stem Splitter sheet did not open")

        def box(name):
            return AX.find(sheet, lambda e: AX.role(e) == "AXCheckBox" and AX.desc(e) == name, 8)
        try:
            for s in STEMS:
                if box(s) is None:
                    if s in want:                            # Logic 11.0/11.1 split vocals, drums, bass and other only
                        raise LogicError(f"this Logic's Stem Splitter has no {s} stem")
                elif AX.set_checkbox(box(s), s in want) != (s in want):
                    raise LogicError(f"could not set the Stem Splitter's {s} box")
            if box("Submix") is not None:
                AX.set_checkbox(box("Submix"), submix)
        except Exception:
            AX.press(AX.find(sheet, lambda e: AX.role(e) == "AXButton" and AX.desc(e) == "Cancel", 3))
            raise
        AX.press(AX.find(sheet, lambda e: AX.role(e) == "AXButton" and AX.desc(e) == "Apply", 3))
        if AX.wait_for(lambda: self._stem_sheet() is None, 5.0) is None:
            raise LogicError("the Stem Splitter sheet did not close after Apply")
        t_end, last = time.time() + timeout, -1.0
        while True:
            frac = self.stem_split_progress()
            if frac is not None and on_progress is not None and frac - last >= 0.1:
                on_progress(frac)
                last = frac
            if frac is None and len(self.tracks()) > len(before):
                break
            if time.time() > t_end:
                raise LogicError(f"the Stem Splitter did not finish in {timeout:.0f} s (progress {frac}, pending: {self.pending_alert()})")
            time.sleep(0.5)
        self._mixer = None
        added = list(self.tracks())
        for name in before:
            if name in added:
                added.remove(name)
        return added

    def stem_split_progress(self) -> float | None:
        """The Stem Splitter's progress (0..1) while its progress window (a dialog called 'Logic Pro') is up, else None."""
        for d in self.app.dialogs():
            if AX.title(d) == LOGIC_APP and AX.desc(d) != "alert":
                bar = AX.find(d, lambda e: AX.role(e) == "AXProgressIndicator", 2)
                if bar is not None:
                    return float(AX.attr(bar, "AXValue") or 0.0)
        return None

    # ------------------------------------------------------------------ transport
    def set_playhead(self, bar: int, beat: int = 1) -> tuple[int, int] | None:
        return self.app.set_playhead(bar, beat, self.main)

    def playhead(self) -> tuple[int, int] | None:
        return self.app.playhead(self.main)

    def is_playing(self) -> bool:
        if self.mcu is not None and self.mcu.state.leds.get(M.PLAY) is not None:
            return bool(self.mcu.state.leds.get(M.PLAY))
        return bool(self.app.is_playing(self.main))

    def play(self) -> None:
        if self.mcu is not None:
            self.mcu.press(M.PLAY)
        else:
            self.app.toggle("Play", True, self.main)

    def stop(self) -> None:
        if self.mcu is not None:
            self.mcu.press(M.STOP)
        else:
            self.app.toggle("Play", False, self.main)

    def position_beats(self) -> float | None:
        """Playhead in beats from bar 1 (MCU clock, 1/960-beat resolution; falls back to the control bar's bar.beat)."""
        if self.mcu is not None:
            b = self.mcu.state.beats()
            if b is not None:
                return b
        p = self.playhead()
        return None if p is None else (p[0] - 1) * 4.0 + (p[1] - 1)

    # ------------------------------------------------------------------ mixer (accessibility)
    # A strip is referred to by its position (int, the track order) or its name (str, e.g. "Aux 1", "Stereo Out");
    # the accessibility element is looked up afresh on every call, because Logic rebuilds the Mixer view often.
    def leave_global_view(self) -> None:
        """After working on aux/output strips through the surface, show the tracks again (Logic's Mixer follows
        the surface's Global View, which hides the other strips from the accessibility tree)."""
        if self._view != "tracks" and self.mcu is not None and self.mcu.state.last_change > 0:
            self.mcu_select(0, "tracks")

    def strip(self, ref):
        if isinstance(ref, str):
            s = self.mixer().strip(ref)
            if s is None:
                raise LogicError(f"no channel strip called {ref!r} (have {[i.name for i in self.mixer().all_info()]})")
            return s
        strips = self.mixer().strips()
        if ref >= len(strips):
            raise LogicError(f"the Mixer shows {len(strips)} strips, no #{ref + 1}")
        return strips[ref]

    def strip_named(self, name: str):
        return self.strip(name)

    def strips(self) -> list[AX.StripInfo]:
        return self.mixer().all_info()

    def strip_info(self, ref) -> AX.StripInfo:
        return self.mixer().info(self.strip(ref))

    def set_volume(self, ref, db: float) -> str:
        return self.mixer().set_volume(self.strip(ref), db)

    def set_pan(self, ref, pan: float) -> str:
        return self.mixer().set_pan(self.strip(ref), pan)

    def set_mute(self, ref, on: bool) -> bool:
        return self.mixer().set_mute(self.strip(ref), on)

    def set_solo(self, ref, on: bool) -> bool:
        return self.mixer().set_solo(self.strip(ref), on)

    # ---- inserts: Logic's plug-in menu has a search field, so a plug-in is inserted by typing its name
    def _popup_open(self, timeout: float = 1.5) -> bool:
        """Is one of Logic's own pop-up menus (not in the accessibility tree) on screen?"""
        import Quartz
        t_end = time.time() + timeout
        while time.time() < t_end:
            for w in Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID):
                if w.get("kCGWindowOwnerName") == LOGIC_APP and w.get("kCGWindowLayer", 0) == 101:
                    return True
            time.sleep(0.05)
        return False

    def clear_popups(self) -> None:
        """Dismiss any of Logic's pop-up menus left open (pressing a menu while one is open can crash Logic)."""
        for _ in range(3):
            if not self._popup_open(0.05):
                return
            K.key(self.app.pid, "escape")
            time.sleep(0.25)

    def _menu_type_and_pick(self, button, text: str, down: int = 1) -> bool:
        self.clear_popups()
        self.app.make_key(self.mixer().window())          # posted keystrokes go to Logic's key window
        AX.press(button)                                  # reports failure, but the menu opens
        if not self._popup_open():
            return False
        time.sleep(0.25)
        K.type_text(self.app.pid, text)
        time.sleep(0.45)
        for _ in range(down):
            K.key(self.app.pid, "down")
        K.key(self.app.pid, "return")
        return True

    @staticmethod
    def _presel_text(row: str, col: int) -> str:
        """The preselected name Logic writes over the LCD row from V-Pot `col`'s column rightwards (up to two spaces)."""
        text = row.ljust(56)[col * 7:]
        cut = text.find("  ")
        return (text if cut < 0 else text[:cut]).strip()

    def _plugin_name(self, text: str) -> str:
        return text.split(" (")[0].strip().lower()

    @staticmethod
    def _catalog_path(kind: str) -> Path:
        return Path(__file__).resolve().parent.parent.parent / ".cache" / f"logic-{kind}.json"

    def _catalog(self, kind: str) -> list[str]:
        p = self._catalog_path(kind)
        try:
            return list(json.loads(p.read_text())) if p.exists() else []
        except ValueError:
            return []

    def _remember(self, kind: str, order: list[str]) -> None:
        """Keep the order of a list as seen, so the next scroll can jump most of the way."""
        if len(order) < 2:
            return
        p = self._catalog_path(kind)
        p.parent.mkdir(parents=True, exist_ok=True)
        old = self._catalog(kind)
        if order[: len(old)] != old[: len(order)] or len(order) > len(old):
            p.write_text(json.dumps(order if len(order) >= len(old) else old, indent=0) + "\n")

    def _scroll_list(self, vpot: int, read: Callable[[], str], match: Callable[[str], bool], what: str, max_steps: int = 320,
                     kind: str = "plugins") -> str:
        """Turn a V-Pot through one of Logic's preselection lists (plug-ins, instruments): back to the '--' entry at
        the start, then forward until `match`. A list order remembered from an earlier scroll (.cache/) lets it jump
        most of the way with unverified detents; the last few are verified one by one, and whatever is seen is
        remembered for next time. Returns the matching text."""
        cur = read()
        seen: list[str] = []
        for _ in range(max_steps):
            if cur.startswith("--") or not cur:
                break
            seen.append(cur)
            cur = self._step_until_change(vpot, -1, read)
            if len(seen) > 3 and seen[-3:] == [cur] * 3:
                break
        order: list[str] = ["--"]
        known = self._catalog(kind)
        target_i = next((i for i, n in enumerate(known) if match(n)), None)
        if target_i is not None and target_i > 4:
            self._tick(vpot, target_i - 3, spacing=0.03)      # fast, unverified: dropped detents only leave us short
            self._need_mcu().settle(0.15, 1.0)
            cur = read()
            if cur not in known or known.index(cur) > target_i:
                # overshot (or landed on something the catalog has not seen): walk back until the target or the start
                for _ in range(max_steps):
                    if match(cur) or cur.startswith("--"):
                        break
                    nxt = self._step_until_change(vpot, -1, read)
                    if nxt == cur:
                        break
                    cur = nxt
                    if cur in known and known.index(cur) <= target_i:
                        break
            order = known[: known.index(cur) + 1] if cur in known else ["--"]
        for _ in range(max_steps):
            if match(cur):
                if order and order[-1] != cur:
                    order.append(cur)
                self._remember(kind, order)
                return cur
            seen.append(cur)
            nxt = self._step_until_change(vpot, 1, read)
            if nxt == cur:
                break                                      # end of the list
            cur = nxt
            if order and order[-1] != cur:
                order.append(cur)
        self._remember(kind, order)
        raise LogicError(f"no {what} in Logic's list (last shown {cur!r}; the list goes {seen[-5:]})")

    def insert_plugin(self, ref, name: str, view: str = "tracks", index: int | None = None) -> str:
        """Insert audio effect `name` ("Compressor", "Channel EQ", "AutoFilter"...) in the first empty insert slot of
        strip `ref`, through the Mackie Control's Plug-in Channel view: the strip is selected on the surface
        (`index` within `view`: tracks, aux or outputs), the slot's V-Pot scrolls Logic's plug-in list to the name
        and a press inserts it. Returns the name as the Mixer shows it."""
        before = self.strip_info(ref).inserts
        slot = len(before)
        if slot >= 8:
            raise LogicError(f"no free insert slot within the first 8 on {self.strip_info(ref).name!r}")
        self.close_plugin_windows()
        self.mcu_select(self._strip_index(ref) if index is None else index)
        self.mcu_view(M.PLUGIN)
        row0, row1 = self._lcd()
        if not re.search(r"Ins[1-7]Pl Ins[2-8]Pl", row0 + row1):
            raise LogicError(f"the surface is not in the Plug-in Channel view (LCD {row0!r} / {row1!r})")
        u = self._need_mcu()

        def read():
            self._stable_lcd(0.2, 1.0)
            return self._presel_text(u.state.line(1), slot)
        want = name.strip().lower()
        self._scroll_list(slot, read, lambda t: self._plugin_name(t) == want or (len(want) > 3 and self._plugin_name(t).startswith(want)), f"plug-in {name!r}")
        self._press(M.VPOT_PUSH + slot, settle=0.8)                        # inserts it (and opens its window)
        time.sleep(0.5)
        got = AX.wait_for(lambda: (lambda cur: cur if len(cur) > len(before) else None)(self.strip_info(ref).inserts), 6.0, 0.25)
        if not got:
            raise LogicError(f"{name!r} was preselected but Logic did not insert it")
        self.close_plugin_windows()
        return got[slot] if len(got) > slot else got[-1]

    def load_instrument(self, ref, name: str, index: int | None = None) -> str:
        """Put software instrument `name` ("Retro Synth", "Alchemy", "Serum 2"...) in the instrument slot of track
        strip `ref`, through the Mackie Control's Instrument view (the strip's V-Pot scrolls the instrument list)."""
        before = self.strip_info(ref).instrument
        idx = self._strip_index(ref) if index is None else index
        self.close_plugin_windows()
        self.mcu_select(idx)
        # the Track button's Channel view: V-Pot 1 volume, 2 pan, 3 instrument (its preselection text has the
        # room of the whole right half of the LCD), 4-5 inserts 1-2, 6-8 sends
        for _ in range(5):
            self._press(M.TRACK, settle=0.5)
            self._stable_lcd(0.5, 2.5)
            row0 = self._lcd()[0]
            # Channel view: 'Volume Pan Inst ...' (Value mode) or 'Track 3 "Hats"  Channel Strip parameters' (Name mode)
            if (row0.startswith("Volume") and "parameter:" not in row0) or bool(re.match(r'^Track \d+ "', row0)):
                break
        else:
            raise LogicError(f"the surface is not in the Track Channel view (LCD {self._lcd()[0]!r})")
        self._value_mode()                                                  # names above, instrument name below
        u = self._need_mcu()
        col = 2

        def read():
            self._stable_lcd(0.2, 1.0)
            return self._presel_text(u.state.line(1), col)
        want = name.strip().lower()

        def match(t: str) -> bool:
            low = t.lower()
            if low.startswith(want + " stereo") or low == want or low.startswith(want + " (") and "stereo" in low:
                return True
            return low.startswith(want) and "mono" not in low and "multi" not in low and "legacy" not in low
        self._scroll_list(col, read, match, f"instrument {name!r}", kind="instruments")
        self._press(M.VPOT_PUSH + col, settle=1.0)
        time.sleep(1.0)
        self.close_plugin_windows()
        # back in the Track Channel view the 'Inst' cell names the loaded instrument (abbreviated); the Mixer's
        # strip calls some instruments 'input', so it is the LCD that confirms
        for _ in range(3):
            self._stable_lcd(0.4, 2.0)
            if self._lcd()[0].startswith("Volume Pan"):
                break
            self._press(M.TRACK, settle=0.5)
        cell = u.state.cells(1)[2] if self._lcd()[0].startswith("Volume Pan") else ""
        shown = self.strip_info(ref).instrument
        if cell and (abbrev_matches(cell, name.replace(" ", "")) or name.lower().startswith(cell.lower()[:4])):
            return f"{name} ({cell})"
        if shown and shown != before and shown != "input":
            return shown
        raise LogicError(f"{name!r} was preselected but Logic did not load it (surface shows {cell!r}, Mixer {shown!r})")

    def load_patch(self, track_index: int, query: str) -> dict:
        """Load the first Library patch matching `query` on the track (Logic's Library search; results in order)."""
        self.select_track(track_index)
        w = self.main
        self.app.make_key(w)
        lib_btn = self.app.control("Library", w)
        if lib_btn is not None and not AX.is_on(lib_btn):
            AX.press(lib_btn)
            time.sleep(0.8)
        lib = AX.wait_for(lambda: AX.find(self.main, lambda e: AX.desc(e) == "Library" and AX.role(e) == "AXGroup", 4), 4.0)
        sf = AX.find(lib, lambda e: AX.attr(e, "AXSubrole") == "AXSearchField", 8) if lib is not None else None
        if sf is None:
            raise LogicError("the Library has no search field (is the Library open?)")
        before = self.strip_info(track_index)
        AX.set_attr(sf, "AXFocused", True)
        K.key(self.app.pid, "a", "cmd")
        K.type_text(self.app.pid, query)
        K.key(self.app.pid, "return")
        time.sleep(1.2)
        K.key(self.app.pid, "tab")
        time.sleep(0.2)
        K.key(self.app.pid, "down")
        time.sleep(0.2)
        K.key(self.app.pid, "return")
        changed = AX.wait_for(lambda: (lambda cur: cur if (cur.instrument, cur.inserts) != (before.instrument, before.inserts) else None)(
            self.strip_info(track_index)), 8.0, 0.3)
        after = changed or self.strip_info(track_index)
        return {"query": query, "loaded": changed is not None, "instrument": after.instrument, "inserts": after.inserts,
                "track": self.tracks()[track_index] if track_index < len(self.tracks()) else None}

    # ---- plug-in windows (side chain, exposed parameters)
    def close_plugin_windows(self) -> None:
        for w in self.app.plugin_windows():
            AX.PluginWindow(w).close()
        time.sleep(0.2)

    def plugin_window(self, ref, name: str, nth: int = 0) -> AX.PluginWindow:
        """Open (fresh) the window of insert `name` on strip `ref`. The 'open' button toggles, so any plug-in
        window that is already open is closed first."""
        self.clear_popups()
        self.close_plugin_windows()
        try:
            return AX.PluginWindow(self.mixer().open_plugin(self.strip(ref), name, nth))
        except AX.AXError as e:
            raise LogicError(str(e)) from e

    def set_side_chain(self, ref, plugin: str, source: str, nth: int = 0) -> str:
        """Choose the side chain source of insert `plugin` on strip `ref` in its window's header pop-up.
        The surface is taken out of the Plug-in Edit view first (its link to the plug-in window and the
        pop-up's action did not get on together on Logic 11.2)."""
        if self.mcu is not None and self.mcu.state.last_change > 0:
            self._press(M.PAN)                                 # leave the Plug-in Edit view
            time.sleep(0.3)
        with self.pause_mcu():
            pw = self.plugin_window(ref, plugin, nth)
            try:
                got = pw.set_side_chain(source)
            except AX.AXError as e:
                raise LogicError(str(e)) from e
            self.clear_popups()
            time.sleep(1.0)
            pw.close()
            time.sleep(1.5)
            if not logic_running():
                raise LogicError("Logic Pro crashed while the side chain was being set")
        return got

    # ------------------------------------------------------------------ Mackie Control: selection, sends, parameters
    def _need_mcu(self) -> M.MackieControl:
        if self.mcu is None:
            raise LogicError("this needs the Mackie Control emulation (use_mcu=True)")
        if self.mcu.state.last_change == 0:
            raise LogicError("Logic has not connected to the Mackie Control port: open Logic Pro > Control Surfaces > Setup, "
                             "and if 'Mackie Control' is missing choose New > Install… > Mackie Control with the 'rick-rubin MCU' ports")
        return self.mcu

    def _lcd(self) -> tuple[str, str]:
        st = self._need_mcu().state
        return st.line(0), st.line(1)

    def _press(self, note: int, settle: float = 0.25) -> None:
        u = self._need_mcu()
        before = time.time()
        u.press(note)
        u.wait_lcd(before, 0.5)
        u.settle(0.12, settle + 0.6)

    def _tick(self, vpot: int, steps: int, spacing: float = 0.012) -> None:
        import mido
        u = self._need_mcu()
        d = 0x40 if steps < 0 else 0x00
        for _ in range(abs(int(steps))):
            u.send(mido.Message("control_change", channel=0, control=0x10 + vpot, value=d | 1))
            time.sleep(spacing)

    def _strip_index(self, ref) -> int:
        """Position of strip `ref` (int or name) in the Mixer's Tracks view — which is also its channel on the
        surface's Arrange view: tracks, then the Aux strips, Stereo Out, Master."""
        if isinstance(ref, int):
            return ref
        names = [i.name for i in self.strips()]
        if ref not in names:
            raise LogicError(f"no channel strip called {ref!r} (have {names})")
        return names.index(ref)

    def _bank_start(self, index: int) -> int:
        """Where the surface's bank begins for channel `index`: banks move by 8, but Logic clamps the last one so
        that all 8 faders are in use."""
        n = len(self.strips())
        return min((index // 8) * 8, max(0, n - 8))

    def mcu_select(self, index: int, view: str = "tracks") -> None:
        """Select channel strip `index` (its position in the Mixer's Tracks view) on the surface."""
        u = self._need_mcu()
        _ = view
        if u.state.leds.get(M.GLOBAL_VIEW):
            self._press(M.GLOBAL_VIEW)                        # always the Arrange view: every strip is a channel there
        self._view = "tracks"
        infos = self.strips()
        n = len(infos)
        start = self._bank_start(index)
        ch = index - start
        if not 0 <= ch < 8:
            raise LogicError(f"strip {index + 1} is not on the surface's bank (start {start + 1}, {n} strips)")
        n_tracks = len(self.tracks())
        for attempt in range(3):
            for _ in range(max(1, -(-n // 8))):
                self._press(M.BANK_LEFT, 0.05)
            for _ in range(index // 8):
                self._press(M.BANK_RIGHT, 0.05)
            self._press(M.SELECT + ch, settle=0.4)
            # check: a track's header takes the focus in the Tracks area; other strips echo their name on the LCD
            if index < n_tracks:
                focused = self._focused_track()
                if focused == index:
                    break
                self.say(f"mcu: select hit track {focused} instead of {index}, trying again")
            else:
                echo = u.state.cells(1)[ch] if ch < 8 else ""
                want = infos[index].name.replace(" ", "")
                if not echo or abbrev_matches(echo, want) or want.lower().startswith(echo.lower()[:4]):
                    break
                self.say(f"mcu: select echoed {echo!r} instead of {infos[index].name!r}, trying again")
        self._selected = index

    def _focused_track(self) -> int | None:
        for i, h in enumerate(self.app.track_headers(self.main)):
            f = next((k for k in AX.children(h) if AX.desc(k) == "Has Focus"), None)
            if f is not None and AX.is_on(f):
                return i
        return None

    def _mixer_names_view(self, button: int) -> list[str]:
        """Press an assignment button until the LCD's upper row shows the channel names (the Mixer view of that
        assignment); returns the names. From an Edit or Channel view one or two presses are needed."""
        known = [i.name for i in self.strips()]
        for _ in range(4):
            cells = [c for c in self._need_mcu().state.cells(0) if c]
            hits = sum(1 for c in cells if any(abbrev_matches(c, k.replace(" ", "")) or k.startswith(c) for k in known))
            if hits >= min(2, len(known)):
                return cells
            self._press(button, settle=0.5)
            self._stable_lcd(0.4, 2.0)
        return [c for c in self._need_mcu().state.cells(0) if c]

    def mcu_view(self, button: int, channel_view: bool = True) -> None:
        """Enter an assignment view; press again for the Channel view (the selected strip's parameters).
        Each press toggles Mixer view <-> Channel view, so the LCD is read (once stable) after every press."""
        def chan(row0, row1):
            both = row0 + row1
            return bool(re.match(r'^(Track|Aux|Output|Stereo|Master|Bus)\b.*"', row0)) or bool(re.search(r"Ins[1-7]Pl Ins[2-8]Pl", both)) \
                or bool(re.search(r"Sen\d", both))
        for _ in range(3):
            self._press(button, settle=0.5)
            self._stable_lcd(0.4, 2.0)
            row0, row1 = self._lcd()
            if not channel_view or chan(row0, row1):
                self._value_mode()                          # labels above, contents below: what the readers expect
                return
        self.say(f"mcu: not in channel view after three presses (LCD {row0!r} / {row1!r})")

    # ---- sends
    def set_send(self, track_index: int, bus: int, db: float | None, slot: int = 1) -> str:
        """Send `slot` (1..) of track `track_index` to 'Bus <bus>' at `db` (None = remove). Logic creates an Aux
        for a new bus by itself. Uses the Send Channel view: V-Pot 1/5 destination, 2/6 level."""
        u = self._need_mcu()
        self.mcu_select(track_index)
        self.mcu_view(M.SEND)
        if slot > 2:
            for _ in range((slot - 1) // 2):
                self._press(M.CURSOR_RIGHT)
        dest_pot, level_pot = (0, 1) if slot % 2 == 1 else (4, 5)
        col = dest_pot
        want = "--" if db is None else f"Bus {bus}"

        def dest_text():
            return u.state.line(1)[col * 7:col * 7 + 14].strip()
        cur = dest_text()
        seen: list[str] = []
        direction = -1 if db is None else 1
        for _ in range(140):
            if cur.startswith(want):
                break
            if cur in seen and direction == 1 and seen.count(cur) > 2:
                direction = -1                               # went past the end: the list does not wrap
            seen.append(cur)
            cur = self._step_until_change(dest_pot, direction, dest_text)
        else:
            raise LogicError(f"could not find {want!r} among the send destinations (last shown {cur!r}, seen {seen[-6:]})")
        self._press(M.VPOT_PUSH + dest_pot)                 # confirm the destination
        if db is None:
            return "off"
        time.sleep(0.3)

        def level_text():
            return u.state.line(1)[level_pot * 7:level_pot * 7 + 9].strip()
        if AX.disp_number(level_text()) is None:
            self._step_until_change(level_pot, 1, level_text)    # the level shows once its V-Pot has moved
        if AX.disp_number(level_text()) is None:
            raise LogicError(f"the send level is not shown (LCD {u.state.line(0)!r} / {u.state.line(1)!r})")
        got = self._converge(level_pot, db, level_text, unit_hint="dB")
        return got

    def _step_until_change(self, vpot: int, direction: int, read: Callable[[], str], tries: int = 4) -> str:
        """One detent, re-sent (a few times) until Logic shows something else: single V-Pot messages are
        sometimes dropped, and the preselected name blinks."""
        u = self._need_mcu()
        before = read()
        for _ in range(tries):
            t0 = time.time()
            self._tick(vpot, direction)
            u.wait_lcd(t0, 0.35)
            u.settle(0.08, 0.5)
            cur = read()
            if cur and cur != before:
                return cur
        return read()

    def _converge(self, vpot: int, target: float, read: Callable[[], str], unit_hint: str = "", max_rounds: int = 60) -> str:
        """Turn a V-Pot until what `read()` shows is as close to `target` as Logic's step allows. The step per
        detent is measured as it goes (bursts while far, single detents near); stops at the closest display."""
        u = self._need_mcu()
        inf = (float("inf"), float("-inf"))

        def current():
            self._stable_lcd(0.25, 1.5)
            t = read()
            return AX.disp_number(t), t
        cur, text = current()
        if cur is None:
            raise LogicError(f"cannot read a number from {text!r}")
        best = (abs(cur - target), text, cur)
        per_tick: float | None = None
        stalls = 0
        for _ in range(max_rounds):
            err = target - cur
            if err == 0:
                break
            if cur in inf or per_tick is None:
                n = (1 if err > 0 else -1) * (8 if cur in inf else 1)
            else:
                n = int(round(err / per_tick))
                if n == 0:
                    break                                   # closer than one detent
                n = max(-48, min(48, n))
            self._tick(vpot, n)
            u.wait_lcd(time.time() - 0.05, 0.4)
            new, text = current()
            if new is None:
                break
            if new == cur:
                stalls += 1
                if stalls >= 3:
                    break                                   # end stop, or detents not taken
                per_tick = None
                continue
            stalls = 0
            if new not in inf and cur not in inf and abs(n) <= 8:
                per_tick = (new - cur) / n
            elif new not in inf and cur not in inf and per_tick is None:
                per_tick = (new - cur) / n
            if abs(new - target) < best[0]:
                best = (abs(new - target), text, new)
            elif per_tick is not None and abs(new - target) >= abs(err) and abs(n) == 1:
                break                                       # a single detent overshoots: the best is as close as it gets
            elif abs(new - target) >= abs(err) and abs(n) > 1:
                per_tick = None                             # the step size changed along the way (log scales): re-measure
            cur = new
        if best[2] != cur and per_tick:
            back = int(round((best[2] - cur) / per_tick))
            if back:
                self._tick(vpot, back)
                u.wait_lcd(time.time() - 0.05, 0.4)
        self._stable_lcd(0.25, 1.5)
        return read()

    # ---- plug-in parameters by displayed value, in the Plug-in Edit view
    def set_plugin_params(self, track_index: int, slot: int, params: dict, view: str = "tracks") -> ParamReport:
        """Set parameters of the plug-in in insert `slot` (1..) of a strip: {name: value} where value is a number
        in the units Logic shows (dB, ms, Hz, %, ratio) or an option name / on/off. Names are Logic's full
        parameter names or the LCD abbreviations."""
        self._need_mcu()
        rep = ParamReport()
        self.mcu_select(self._strip_index(track_index) if isinstance(track_index, str) else track_index)
        self.mcu_view(M.PLUGIN)
        row0, row1 = self._lcd()
        if not re.search(r"Ins[1-7]Pl Ins[2-8]Pl", row0 + row1):
            raise LogicError(f"the Mackie Control is not in the Plug-in Channel view (LCD: {row0!r} / {row1!r})")
        self._press(M.VPOT_PUSH + (slot - 1), settle=0.8)       # open the plug-in's edit view (and its window)
        row0, row1 = self._lcd()
        if re.search(r"Ins[1-7]Pl Ins[2-8]Pl", row0 + row1):
            raise LogicError(f"insert slot {slot} did not open an edit view (LCD: {row0!r} / {row1!r})")
        self._value_mode()
        plugin = self._edit_view_plugin()
        for name, val in params.items():
            try:
                try:
                    col = self._find_param(name, plugin)
                except LogicError:
                    self._press(M.NAME_VALUE, 0.3)            # redraw the names: a long name may have hidden one
                    self._press(M.NAME_VALUE, 0.3)
                    time.sleep(1.0)
                    col = self._find_param(name, plugin)
                rep.set[name] = self._set_param_column(col, val)
                time.sleep(1.5)                             # the long parameter name Logic shows after a move fades
            except LogicError as e:
                rep.errors.append(f"{name}: {e}")
        self.close_plugin_windows()
        return rep

    def set_instrument_params(self, track_index: int, params: dict, instrument: str = "") -> ParamReport:
        """Set parameters of a track's software instrument by displayed value, in the Instrument Edit view."""
        self._need_mcu()
        rep = ParamReport()
        self.mcu_select(track_index)
        for _ in range(3):
            self._press(M.INSTRUMENT, settle=0.5)
            self._stable_lcd(0.4, 2.0)
            row0, row1 = self._lcd()
            names_view = any(abbrev_matches(c, k.replace(" ", "")) for c in self._need_mcu().state.cells(0) if c for k in self.tracks()[:8])
            if not names_view and not row0.startswith("Volume Pan"):
                break
        self._value_mode()
        for name, val in params.items():
            try:
                try:
                    col = self._find_param(name, instrument)
                except LogicError:
                    self._press(M.NAME_VALUE, 0.3)
                    self._press(M.NAME_VALUE, 0.3)
                    time.sleep(1.0)
                    col = self._find_param(name, instrument)
                rep.set[name] = self._set_param_column(col, val)
                time.sleep(1.5)
            except LogicError as e:
                rep.errors.append(f"{name}: {e}")
        self.close_plugin_windows()
        return rep

    def _edit_view_plugin(self) -> str:
        """Plug-in name from the edit view's Name mode header ('... Ins.2 "Compressor (s/s)" Page 1/3')."""
        row0, _ = self._lcd()
        m = re.search(r'Ins\.\d+ "([^"]+)"', row0)
        if m:
            return m.group(1).split(" (")[0]
        self._press(M.NAME_VALUE)
        row0, _ = self._lcd()
        m = re.search(r'Ins\.\d+ "([^"]+)"', row0)
        self._press(M.NAME_VALUE)
        return m.group(1).split(" (")[0] if m else ""

    def _in_name_mode(self) -> bool:
        row0, _ = self._lcd()
        return bool(re.match(r'^(Track|Aux|Output|Stereo|Master|Bus)\b', row0)) and '"' in row0

    def _value_mode(self) -> None:
        """Value mode: parameter names in the upper row, values in the lower."""
        if self._in_name_mode():
            self._press(M.NAME_VALUE)

    def _name_mode(self) -> None:
        """Name mode: the header ('Track 3 "Bass" Ins.2 "Compressor" Page 1/3') above, the eight parameter names
        below — the only row where all eight names are readable (in Value mode the page label hides the last two)."""
        if not self._in_name_mode():
            self._press(M.NAME_VALUE)

    def _stable_lcd(self, quiet: float = 0.9, timeout: float = 3.0) -> None:
        """Wait until the LCD has stopped changing: Logic shows a parameter's long name for a moment after a
        V-Pot moves, and a preselection blinks."""
        u = self._need_mcu()
        t_end = time.time() + timeout
        while time.time() < t_end:
            if time.time() - u.state.lcd_changed >= quiet:
                return
            time.sleep(0.05)

    def _names(self) -> list[str]:
        """The eight parameter-name cells (Name mode's lower row), read twice a second apart so a long name Logic
        shows for a moment after a V-Pot move ('Threshold' spilling into the next cell) is not mistaken for them."""
        u = self._need_mcu()
        self._name_mode()
        t_end = time.time() + 5.0
        prev = None
        while time.time() < t_end:
            self._stable_lcd(0.6, 2.0)
            cells = u.state.cells(1)
            if cells == prev:
                return cells
            prev = cells
            time.sleep(0.8)
        return u.state.cells(1)

    def _values(self) -> list[str]:
        st = self._need_mcu().state
        self._value_mode()
        return [c.strip() for c in st.columns(1)]

    def _find_param(self, name: str, plugin: str) -> int:
        """Page through the edit view until a column's name stands for `name`; returns the column (0-7)."""
        table = LCD_NAMES.get(plugin, {})
        wanted = [table[k] for k in table if k.lower() == name.lower()] + [name]
        self._name_mode()
        for _ in range(12):                                   # back to the first page
            self._stable_lcd(0.5, 2.0)
            header = self._lcd()[0]
            m = re.search(r"Page (\d+)/(\d+)", header)
            if m is None or m.group(1) == "1":
                break
            self._press(M.CURSOR_LEFT, 0.3)
        seen_pages = set()
        for _ in range(12):
            names = self._names()
            key = tuple(names)
            for want in wanted:
                for i, n in enumerate(names):
                    if n and (n.lower() == want.lower()):
                        return i
            for want in wanted:
                for i, n in enumerate(names):
                    if n and abbrev_matches(n, want):
                        return i
            if key in seen_pages:
                break
            seen_pages.add(key)
            self._press(M.CURSOR_RIGHT, 0.15)
        raise LogicError(f"no parameter {name!r} in {plugin or 'this plug-in'} (LCD names seen: {sorted({n for p in seen_pages for n in p if n})})")

    def _set_param_column(self, col: int, val) -> str:
        u = self._need_mcu()

        def read():
            return self._values()[col]
        if isinstance(val, bool) or (isinstance(val, str) and AX.disp_number(val) is None):
            want = ("On" if val else "Off") if isinstance(val, bool) else str(val).strip()
            cur = read()
            seen = []
            def stable_read():
                time.sleep(0.6)                              # the long option name Logic flashes would be misread
                self._stable_lcd(0.4, 1.5)
                return read()
            cur = stable_read()

            def hit(c: str) -> bool:
                cl, wl = c.lower(), want.lower()
                return bool(c) and (cl == wl or (len(want) >= 3 and cl.startswith(wl[:len(c)])) or abbrev_matches(c, want)
                                    or (len(c) >= 4 and cl.replace(" ", "") in wl.replace(" ", "")))
            if hit(cur):
                return cur
            first = cur
            for _ in range(80):
                seen.append(cur)
                nxt = self._step_until_change(col, 1, stable_read)
                if nxt == cur:
                    # two-state parameters (On/Off) do not step: pressing the V-Pot toggles them
                    self._press(M.VPOT_PUSH + col, settle=0.4)
                    nxt = stable_read()
                    if nxt == cur:
                        break                                # end stop
                cur = nxt
                if hit(cur):
                    return cur
                if cur == first and len(seen) > 2:
                    break                                    # back where we started: the option is not in this list
            raise LogicError(f"no option {want!r} (options seen: {seen})")
        target = AX.disp_number(val) if isinstance(val, str) else float(val)
        shown = self._converge(col, float(target), read)
        for cut, full in ((" d", " dB"), (" m", " ms"), (" H", " Hz"), (" k", " kHz")):
            if shown.endswith(cut):
                return shown[: -len(cut)] + full                       # the 7-character cell cuts the unit short
        return shown

    # ------------------------------------------------------------------ bounce
    def bounce(self, out_path: str | Path, start_bar: int, end_bar: int, bit_depth: str = "24", sample_rate: str | None = None,
               tail: bool = False) -> Path:
        """File > Bounce > Project or Section… offline to a 24-bit WAV at `out_path` (its folder must be
        visible in a file panel, i.e. not hidden). `end_bar` is the last bar (inclusive)."""
        out_path = Path(out_path).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if out_path.exists():
            out_path.unlink()
        self.stop()
        self.focus()
        if not self.app.menu("File", "Bounce", "Project or Section…"):
            raise LogicError("File > Bounce is not available")
        dlg = AX.wait_for(lambda: next((d for d in self.app.dialogs() if AX.title(d).startswith("Bounce")), None), 8.0)
        if dlg is None:
            raise LogicError("the Bounce dialog did not open")
        try:
            rows = AX.find_all(dlg, lambda e: AX.role(e) == "AXCheckBox" and AX.attr(e, "AXIdentifier") == "enable", 5)
            for cb in rows:
                AX.set_checkbox(cb, AX.desc(cb) == "Uncompressed")
            pops = AX.find_all(dlg, lambda e: AX.role(e) == "AXPopUpButton", 4)
            for p in pops:
                v = str(AX.attr(p, "AXValue") or "")
                try:
                    if v.endswith("-bit") or v.endswith("bit float"):
                        AX.set_choice(p, f"{bit_depth}-bit")
                    elif v in ("WAVE", "AIFF", "CAF"):
                        AX.set_choice(p, "WAVE")
                    elif v in ("Offline", "Realtime"):
                        AX.set_choice(p, "Offline")
                    elif sample_rate and v.endswith("kHz"):
                        AX.set_choice(p, sample_rate)
                except AX.AXError as e:
                    self.say(f"bounce option {v!r}: {e}")
            for t, on in (("Add to Project", False), ("Add to Music", False), ("Include Audio Tail", tail), ("Include Tempo Information", False)):
                cb = AX.find(dlg, lambda e, t=t: AX.role(e) == "AXCheckBox" and AX.title(e) == t, 4)
                if cb is not None:
                    AX.set_checkbox(cb, on)
            groups = [g for g in AX.children(dlg) if AX.role(g) == "AXGroup" and AX.desc(g).startswith("\t")]
            if len(groups) >= 2:
                self._set_position_group(groups[0], start_bar)
                self._set_position_group(groups[1], end_bar + 1)
            AX.press(AX.find(dlg, lambda e: AX.role(e) == "AXButton" and AX.title(e) == "OK", 2))
        except Exception:
            AX.press(AX.find(dlg, lambda e: AX.role(e) == "AXButton" and AX.title(e) == "Cancel", 2))
            raise
        panel = AX.wait_for(lambda: next((d for d in self.app.dialogs() if AX.attr(d, "AXIdentifier") == "save-panel"), None), 8.0)
        if panel is None:
            raise LogicError("the bounce file panel did not open")
        self._panel_navigate(panel, out_path.parent)
        AX.set_value(AX.find(panel, lambda e: AX.attr(e, "AXIdentifier") == "saveAsNameTextField", 3), out_path.stem)
        AX.press(AX.find(panel, lambda e: AX.attr(e, "AXIdentifier") == "OKButton", 3))
        time.sleep(0.5)
        self._answer_alert(["Replace"], "already exists", timeout=1.5)
        candidates = [out_path, out_path.with_suffix(".wav"), out_path.parent / f"{out_path.stem}.wav"]

        def busy():
            # a bounce still running shows a progress window or its file panel; plug-in windows do not count
            return any(AX.attr(d, "AXIdentifier") in ("save-panel", "open-panel") or AX.desc(d) == "alert"
                       or AX.title(d).startswith("Bounce") for d in self.app.dialogs())

        def done():
            for c in candidates:
                if c.exists():
                    s1 = c.stat().st_size
                    time.sleep(0.6)
                    if c.stat().st_size == s1 and s1 > 1000 and not busy():
                        return c
            return None
        got = AX.wait_for(done, 300.0, 0.5)
        if got is None:
            raise LogicError(f"the bounce did not produce {out_path} (pending: {self.pending_alert()})")
        if got != out_path:
            got.rename(out_path)
        return out_path

    @staticmethod
    def _set_position_group(group, bar: int) -> None:
        """A bar.beat.div.tick display: step its bar segment to `bar` (AXIncrement = +1 bar) and the rest to 1."""
        segs = [c for c in AX.children(group) if AX.role(c) == "AXSlider"]
        if not segs:
            return
        for _ in range(400):
            cur = AX.disp_number(AX.shown(segs[0]))
            if cur is None or int(cur) == bar:
                break
            AX.do(segs[0], "AXIncrement" if cur < bar else "AXDecrement")
        for s in segs[1:]:
            for _ in range(20):
                cur = AX.disp_number(AX.shown(s))
                if cur is None or int(cur) <= 1:
                    break
                AX.do(s, "AXDecrement")

    # ------------------------------------------------------------------ automation, written in real time
    # Logic's fader law as the Mackie Control sees it: (14-bit position, dB) pairs read back from Logic 11.2
    FADER_CURVE = [(-8192, -90.0), (-3002, -20.9), (-2008, -16.3), (-1014, -12.0), (-14, -9.0), (1971, -5.5), (2497, -4.4),
                   (3414, -2.1), (4251, 0.0), (4977, 1.8), (8191, 6.0)]

    @classmethod
    def fader_for_db(cls, db: float) -> int:
        if db <= -90:
            return -8192
        pts = cls.FADER_CURVE
        for (p0, d0), (p1, d1) in zip(pts, pts[1:]):
            if d0 <= db <= d1:
                return int(round(p0 + (p1 - p0) * (db - d0) / (d1 - d0)))
        return 8191

    def set_automation_mode(self, track_index: int, mode: str) -> None:
        """'read' | 'latch' | 'touch' | 'write' | 'off' for a track, through the surface."""
        u = self._need_mcu()
        self.mcu_select(track_index)
        note = {"read": M.READ_OFF, "latch": M.LATCH, "touch": M.TOUCH, "write": M.WRITE, "off": M.READ_OFF}[mode]
        self._press(note)
        if mode == "off":
            self._press(note)
        u.settle(0.1, 0.5)

    def write_fader_automation(self, track_index: int, start_beat: float, length: float, points: list, bpm: float, say=None) -> int:
        """Play bars `start_beat`..`start_beat+length` once with the track in Latch and move its fader along
        `points` [(beat in clip, gain 0..1)] — Logic records that as volume automation. Returns 1 when written."""
        import math
        say = say or (lambda *_: None)
        u = self._need_mcu()
        pts = sorted((float(b), float(v)) for b, v in points)
        if len(pts) < 2:
            return 0

        def gain_at(t: float) -> float:
            if t <= pts[0][0]:
                return pts[0][1]
            for (t0, v0), (t1, v1) in zip(pts, pts[1:]):
                if t0 <= t <= t1:
                    return v0 if t1 == t0 else v0 + (v1 - v0) * (t - t0) / (t1 - t0)
            return pts[-1][1]

        def db(g: float) -> float:
            return -90.0 if g <= 0 else 20 * math.log10(g)
        bar0 = int(start_beat // 4) + 1
        self.stop()
        self.set_playhead(max(1, bar0 - 1))
        self.set_automation_mode(track_index, "latch")
        ch = track_index % 8
        say(f"writing volume automation on track {track_index + 1} from bar {bar0} ({length / 4:g} bars, real time)")
        u.hold(M.FADER_TOUCH + ch)
        u.send(self._mido().Message("pitchwheel", channel=ch, pitch=self.fader_for_db(db(gain_at(0.0)))))
        self.play()
        t_end = time.time() + (length + 8) * 60.0 / bpm + 10
        last = None
        try:
            while time.time() < t_end:
                pos = self.position_beats()
                if pos is None:
                    time.sleep(0.02)
                    continue
                rel = pos - start_beat
                if rel > length + 0.5:
                    break
                g = gain_at(max(0.0, rel))
                val = self.fader_for_db(db(g))
                if val != last:
                    u.send(self._mido().Message("pitchwheel", channel=ch, pitch=val))
                    last = val
                time.sleep(0.03)
        finally:
            u.release(M.FADER_TOUCH + ch)
            self.stop()
            self.set_automation_mode(track_index, "read")
        return 1

    def write_param_automation(self, track_index: int, slot: int, param: str, start_beat: float, length: float, points: list,
                               bpm: float, to_value, say=None, plugin: str = "") -> int:
        """Play bars `start_beat`..+`length` once with the track in Latch and turn the V-Pot of `param` (an insert's
        parameter in the Plug-in Edit view) so its displayed value follows `points` [(beat in clip, 0..1)] mapped by
        `to_value(v) -> displayed units`. Logic records the moves as that parameter's automation."""
        say = say or (lambda *_: None)
        self._need_mcu()
        pts = sorted((float(b), float(v)) for b, v in points)
        if len(pts) < 2:
            return 0

        def frac_at(t: float) -> float:
            if t <= pts[0][0]:
                return pts[0][1]
            for (t0, v0), (t1, v1) in zip(pts, pts[1:]):
                if t0 <= t <= t1:
                    return v0 if t1 == t0 else v0 + (v1 - v0) * (t - t0) / (t1 - t0)
            return pts[-1][1]
        self.stop()
        bar0 = int(start_beat // 4) + 1
        self.set_playhead(max(1, bar0 - 1))
        self.mcu_select(track_index)
        self.mcu_view(M.PLUGIN)
        self._press(M.VPOT_PUSH + (slot - 1), settle=0.8)
        self._value_mode()
        col = self._find_param(param, plugin or self._edit_view_plugin())

        def read():
            return self._values()[col]
        # park the parameter on its starting value before the pass
        self._converge(col, float(to_value(frac_at(0.0))), read)
        self._press(M.LATCH, 0.2)
        say(f"writing {param} automation on track {track_index + 1} from bar {bar0} ({length / 4:g} bars, real time)")
        self.play()
        t_end = time.time() + (length + 8) * 60.0 / bpm + 10
        per_tick: float | None = None
        last_val = AX.disp_number(read())
        try:
            while time.time() < t_end:
                pos = self.position_beats()
                if pos is None:
                    time.sleep(0.02)
                    continue
                rel = pos - start_beat
                if rel > length + 0.5:
                    break
                target = float(to_value(frac_at(max(0.0, rel + 0.15))))     # aim a little ahead: the detents take time
                cur = AX.disp_number(read())
                if cur is None or cur in (float("inf"), float("-inf")):
                    time.sleep(0.05)
                    continue
                err = target - cur
                if per_tick is None or per_tick == 0:
                    n = 1 if err > 0 else -1 if err < 0 else 0
                else:
                    n = max(-12, min(12, int(round(err / per_tick))))
                if n:
                    self._tick(col, n, spacing=0.006)
                    time.sleep(0.08)
                    new = AX.disp_number(read())
                    if new is not None and last_val is not None and new != cur and abs(n) <= 12:
                        per_tick = (new - cur) / n
                    last_val = new
                else:
                    time.sleep(0.05)
        finally:
            self.stop()
            self._press(M.READ_OFF, 0.2)
            self.leave_global_view()
        return 1

    @staticmethod
    def _mido():
        import mido
        return mido
