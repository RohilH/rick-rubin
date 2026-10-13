"""Logic Pro through the macOS accessibility API (what VoiceOver sees).

Logic exposes its Mixer, plug-in windows, menu bar, dialogs and the control bar as accessibility
elements, and these can be read and pressed from another process *without* taking the keyboard
focus or the mouse away from whoever is using the Mac. What the accessibility tree does not offer
(Logic's own pop-up menus, text entry) is done with keystrokes posted to Logic's process only
(keys.py), which the person at the Mac never sees either. Nothing here moves the mouse.

Quirks learned on Logic Pro 11.2 (macOS 15):
  - sliders (faders, pan, plug-in parameters) ignore the value given to AXSetValue and move one
    fine step in its direction; AXIncrement / AXDecrement move ten fine steps (one bar for position
    fields). Their displayed value is in AXValueDescription ("-6.0 dB", "200 Hz"), which set_slider() reads.
    Exception: the control bar's playhead 'bar' and 'beat' sliders take absolute values.
  - Logic's own pop-up menus (insert slots, sends, outputs) open on AXPress (the call reports failure)
    as windows the accessibility tree does not show; the plug-in menus have a search field that takes
    posted keystrokes, and Return / arrows work in them. Standard pop-ups (plug-in header, dialogs)
    expose an AXMenu child once pressed.
  - menu bar items work; so do dialog buttons, check boxes, text fields and NSSavePanel sidebars.
  - a track's name field cannot be set; tracks are named through the Tracks area's Functions menu.
"""
from __future__ import annotations

import math
import re
import time
from dataclasses import dataclass
from typing import Any
from collections.abc import Callable

try:
    from ApplicationServices import (AXUIElementCopyActionNames, AXUIElementCopyAttributeNames, AXUIElementCopyAttributeValue,
                                     AXUIElementCreateApplication, AXUIElementPerformAction, AXUIElementSetAttributeValue)
    from AppKit import NSWorkspace
    HAVE_AX = True
except ImportError:  # pragma: no cover - not on macOS
    HAVE_AX = False

APP_NAME = "Logic Pro"
BUNDLE_ID = "com.apple.logic10"


class AXError(RuntimeError):
    pass


def logic_pid() -> int | None:
    if not HAVE_AX:
        return None
    for a in NSWorkspace.sharedWorkspace().runningApplications():
        if a.bundleIdentifier() == BUNDLE_ID or a.localizedName() == APP_NAME:
            return a.processIdentifier()
    return None


def attr(el, name: str):
    if el is None:
        return None
    err, val = AXUIElementCopyAttributeValue(el, name, None)
    return val if err == 0 else None


def attrs(el) -> list[str]:
    err, names = AXUIElementCopyAttributeNames(el, None)
    return list(names) if err == 0 else []


def actions(el) -> list[str]:
    err, names = AXUIElementCopyActionNames(el, None)
    return [str(x) for x in names] if err == 0 else []


def press(el) -> bool:
    return el is not None and AXUIElementPerformAction(el, "AXPress") == 0


def do(el, action: str) -> bool:
    return el is not None and AXUIElementPerformAction(el, action) == 0


def set_value(el, value) -> bool:
    return el is not None and AXUIElementSetAttributeValue(el, "AXValue", value) == 0


def set_attr(el, name: str, value) -> bool:
    return el is not None and AXUIElementSetAttributeValue(el, name, value) == 0


def children(el) -> list:
    return list(attr(el, "AXChildren") or []) if el is not None else []


def role(el) -> str:
    return str(attr(el, "AXRole") or "")


def desc(el) -> str:
    return str(attr(el, "AXDescription") or "")


def title(el) -> str:
    return str(attr(el, "AXTitle") or "")


def value(el):
    return attr(el, "AXValue")


def shown(el) -> str:
    """A slider's displayed value ('-6.0 dB') or a field's text."""
    v = attr(el, "AXValueDescription")
    if v is None:
        v = attr(el, "AXValue")
    return "" if v is None else str(v)


def is_on(el) -> bool:
    return str(attr(el, "AXValue")).lower() in ("1", "true", "on")


def find(el, pred: Callable[[Any], bool], maxdepth: int = 14):
    """Depth-first search below `el` (inclusive)."""
    stack = [(el, 0)]
    while stack:
        e, d = stack.pop()
        try:
            if pred(e):
                return e
        except Exception:  # noqa: BLE001
            pass
        if d < maxdepth:
            stack.extend((c, d + 1) for c in reversed(children(e)))
    return None


def find_all(el, pred: Callable[[Any], bool], maxdepth: int = 14) -> list:
    out = []
    stack = [(el, 0)]
    while stack:
        e, d = stack.pop()
        try:
            if pred(e):
                out.append(e)
        except Exception:  # noqa: BLE001
            pass
        if d < maxdepth:
            stack.extend((c, d + 1) for c in reversed(children(e)))
    return out


def by_desc(el, text: str, role_: str | None = None, maxdepth: int = 14):
    return find(el, lambda e: desc(e) == text and (role_ is None or role(e) == role_), maxdepth)


def dump(el, maxdepth: int = 6) -> str:
    out = []

    def walk(e, d):
        if d > maxdepth:
            return
        parts = [role(e)]
        for k in ("AXSubrole", "AXTitle", "AXDescription", "AXIdentifier"):
            v = attr(e, k)
            if v:
                parts.append(f"{k[2:].lower()}={str(v)!r}")
        v = attr(e, "AXValue")
        if v is not None and not hasattr(v, "count"):
            parts.append(f"value={str(v)[:40]!r}")
        vd = attr(e, "AXValueDescription")
        if vd:
            parts.append(f"shown={str(vd)!r}")
        out.append("  " * d + " ".join(parts))
        for c in children(e):
            walk(c, d + 1)
    walk(el, 0)
    return "\n".join(out)


def wait_for(fn: Callable[[], Any], timeout: float = 5.0, interval: float = 0.1):
    """Poll `fn` until it returns something truthy (returned) or `timeout` passes (None)."""
    t_end = time.time() + timeout
    while True:
        try:
            v = fn()
        except Exception:  # noqa: BLE001
            v = None
        if v:
            return v
        if time.time() > t_end:
            return None
        time.sleep(interval)


# ============================================================================ the app
class LogicApp:
    def __init__(self):
        if not HAVE_AX:
            raise AXError("the Logic bridge needs pyobjc (macOS): pip install \"rick-rubin[logic]\"")
        pid = logic_pid()
        if pid is None:
            raise AXError("Logic Pro is not running")
        self.pid = pid
        self.el = AXUIElementCreateApplication(pid)

    # ---- windows
    def windows(self) -> list:
        return list(attr(self.el, "AXWindows") or [])

    def window(self, pred: Callable[[Any], bool]):
        for w in self.windows():
            if pred(w):
                return w
        return None

    @staticmethod
    def _is_main(w) -> bool:
        """A project's main window has a Control Bar; the separate Mixer window does not."""
        return attr(w, "AXSubrole") == "AXStandardWindow" and any(role(c) == "AXGroup" and desc(c) == "Control Bar" for c in children(w))

    def project_windows(self) -> list:
        """Main windows of open projects: title '<project> - <focused pane>' (one per project)."""
        return [w for w in self.windows() if self._is_main(w) and " - " in title(w)]

    def main_window(self, project: str | None = None):
        """The project window, of `project` if given (title prefix), else the frontmost one."""
        wins = self.project_windows()
        if project is not None:
            for w in wins:
                if title(w).startswith(project + " - ") or title(w).rsplit(" - ", 1)[0] == project:
                    return w
            return None
        return wins[0] if wins else self.window(self._is_main)

    def mixer_window(self, project: str | None = None):
        for w in self.windows():
            t = title(w)
            if attr(w, "AXSubrole") == "AXStandardWindow" and not self._is_main(w) and t.rsplit(" - ", 1)[-1].startswith("Mixer"):
                if project is None or t.startswith(project + " - "):
                    return w
        return None

    def project_title(self, w=None) -> str | None:
        w = w or self.main_window()
        if w is None:
            return None
        return title(w).rsplit(" - ", 1)[0]

    @staticmethod
    def project_path(w):
        """The .logicx package a project window shows (its AXDocument URL), or None while it is unsaved."""
        from pathlib import Path
        from urllib.parse import unquote, urlparse
        url = attr(w, "AXDocument")
        return Path(unquote(urlparse(str(url)).path)) if url else None

    def dialogs(self) -> list:
        """Dialogs and alerts: every window that is not a standard document window."""
        return [w for w in self.windows() if attr(w, "AXSubrole") != "AXStandardWindow"]

    def alerts(self) -> list:
        out = []
        for w in self.windows():
            if attr(w, "AXSubrole") != "AXStandardWindow" and desc(w) == "alert":
                out.append(w)
            out += [c for c in children(w) if role(c) == "AXSheet"]
        return out

    def plugin_windows(self) -> list:
        return [w for w in self.windows() if attr(w, "AXSubrole") == "AXDialog" and desc(w) != "alert"
                and find(w, lambda e: desc(e) == "bypass", 2) is not None and find(w, lambda e: desc(e) == "view", 2) is not None]

    def make_key(self, w) -> None:
        """Make `w` Logic's main/key window (menus act on it); Logic itself stays in the background."""
        set_attr(w, "AXMain", True)
        set_attr(w, "AXFocused", True)
        do(w, "AXRaise")
        time.sleep(0.15)

    @staticmethod
    def alert_text(al) -> str:
        return " ".join(str(attr(t, "AXValue") or "") for t in find_all(al, lambda e: role(e) == "AXStaticText", 3))

    @staticmethod
    def alert_buttons(al) -> list[str]:
        return [title(b) for b in find_all(al, lambda e: role(e) == "AXButton" and title(e), 3)]

    def answer(self, al, button: str) -> bool:
        b = find(al, lambda e: role(e) == "AXButton" and title(e).replace("’", "'") == button.replace("’", "'"), 3)
        return press(b)

    # ---- menu bar
    def menu_item(self, *path: str):
        """A menu bar item by titles, e.g. ("File", "Bounce", "Project or Section…"). Trailing ellipsis optional;
        'Select All' may also be given as its action name 'selectAll:'."""
        el = attr(self.el, "AXMenuBar")
        if el is None:
            raise AXError("Logic has no menu bar (not running?)")
        for part in path:
            want = part.rstrip("…").rstrip(".")
            nxt = find(el, lambda e, want=want, part=part: role(e) in ("AXMenuBarItem", "AXMenuItem") and (
                title(e).rstrip("…").rstrip(".") == want or str(attr(e, "AXIdentifier") or "") == part), 3 if not part.endswith(":") else 6)
            if nxt is None:
                raise AXError(f"no menu item {' > '.join(path)!r} (stopped at {part!r})")
            el = nxt
        return el

    def menu(self, *path: str) -> bool:
        return press(self.menu_item(*path))

    def menu_enabled(self, *path: str) -> bool:
        return bool(attr(self.menu_item(*path), "AXEnabled"))

    def undo_title(self) -> str:
        try:
            return title(self.menu_item("Edit", "undo:"))
        except AXError:
            return ""

    # ---- control bar (transport, tempo, playhead) of a project window
    def control(self, text: str, w=None):
        w = w or self.main_window()
        return by_desc(w, text) if w is not None else None

    def tempo(self, w=None) -> float | None:
        el = self.control("Tempo", w)
        v = attr(el, "AXValue") if el is not None else None
        return float(v) if v is not None else None

    def playhead(self, w=None) -> tuple[int, int] | None:
        g = self.control("Playhead Position", w)
        if g is None:
            return None
        bar = beat = None
        for c in children(g):
            if desc(c) == "bar":
                bar = attr(c, "AXValue")
            elif desc(c) == "beat":
                beat = attr(c, "AXValue")
        return (int(bar), int(beat)) if bar is not None and beat is not None else None

    def set_playhead(self, bar: int, beat: int = 1, w=None) -> tuple[int, int] | None:
        g = self.control("Playhead Position", w)
        if g is None:
            raise AXError("no playhead display in the control bar")
        for c in children(g):
            if desc(c) == "bar":
                set_value(c, float(bar))
            elif desc(c) == "beat":
                set_value(c, float(beat))
        time.sleep(0.1)
        return self.playhead(w)

    def is_playing(self, w=None) -> bool | None:
        el = self.control("Play", w)
        return None if el is None else is_on(el)

    def toggle(self, text: str, on: bool, w=None) -> bool:
        el = self.control(text, w)
        if el is None:
            return False
        if is_on(el) != on:
            return press(el)
        return True

    def tracks(self, w=None) -> list[str]:
        """Track names as the Tracks area shows them ('Track 3 “Bass”' -> 'Bass')."""
        w = w or self.main_window()
        hdr = find(w, lambda e: desc(e) == "Tracks header", 10) if w is not None else None
        out = []
        for k in children(hdr) if hdr is not None else []:
            m = re.match(r'Track \d+ “(.*)”$', desc(k))
            out.append(m.group(1) if m else desc(k))
        return out

    def track_headers(self, w=None) -> list:
        w = w or self.main_window()
        hdr = find(w, lambda e: desc(e) == "Tracks header", 10) if w is not None else None
        return children(hdr) if hdr is not None else []

    def select_track(self, index: int, w=None) -> bool:
        heads = self.track_headers(w)
        if index >= len(heads):
            raise AXError(f"no track {index + 1} (the project has {len(heads)})")
        foc = next((k for k in children(heads[index]) if desc(k) == "Has Focus"), None)
        return press(foc)

    def tracks_functions_menu(self, w=None):
        w = w or self.main_window()
        return find(w, lambda e: role(e) == "AXMenuButton" and desc(e) == "Functions", 8)


# ============================================================================ numbers as Logic shows them
_NUM = re.compile(r"[-+]?\d+(?:[.,]\d+)?")


def disp_number(text: str) -> float | None:
    """'-6.0 dB' -> -6.0, '3.56 kHz' -> 3560, '120 ms' -> 120, '1.2 s' -> 1200, '51.0ms' -> 51, 'inf' -> inf,
    '4.0:1' -> 4.0, '2.1:1' -> 2.1, '-oo dB' -> -inf, 'Off' -> None, '60 %' -> 60, '7040.0' -> 7040."""
    t = str(text).strip().lower().replace(",", ".")
    if not t:
        return None
    if t.startswith(("-inf", "-oo", "-∞")):
        return -math.inf
    if t.startswith(("inf", "+inf", "oo", "∞")):
        return math.inf
    m = _NUM.search(t)
    if not m:
        return None
    v = float(m.group())
    rest = t[m.end():].strip()
    if rest.startswith("khz"):
        return v * 1000.0
    if rest == "s" or rest.startswith("s ") or rest.startswith("sec"):
        return v * 1000.0
    if rest.startswith("min"):
        return v * 60000.0
    return v


def slider_value(el) -> tuple[float | None, str]:
    s = shown(el)
    return disp_number(s), s


def set_slider(el, target: float, tolerance: float = 0.0, max_moves: int = 3000) -> str:
    """Move an accessibility slider until its *displayed* value is `target` (in the units it shows: dB, Hz, ms,
    %...). Logic's sliders only step (fine via AXSetValue, coarse via AXIncrement), so this walks: coarse steps
    while far, fine steps near, and stops on the closest display. Returns the display text."""
    raw_min, raw_max = attr(el, "AXMinValue"), attr(el, "AXMaxValue")
    if attr(el, "AXValue") is None or raw_min is None or raw_max is None:
        raise AXError("not a slider")
    acts = actions(el)
    coarse_ok = "AXIncrement" in acts and "AXDecrement" in acts

    def move(up: bool, coarse: bool) -> bool:
        before = attr(el, "AXValue")
        if coarse and coarse_ok:
            do(el, "AXIncrement" if up else "AXDecrement")
        else:
            set_value(el, raw_max if up else raw_min)
        return attr(el, "AXValue") != before

    v, s = slider_value(el)
    if v is None:
        raise AXError(f"slider shows {s!r}, not a number")
    if math.isinf(target):
        for _ in range(max_moves):
            if not move(target > 0, True):
                break
        return shown(el)
    best = (abs(v - target), attr(el, "AXValue"), s)
    coarse = coarse_ok
    moves = 0
    while moves < max_moves:
        moves += 1
        up = v < target
        moved = move(up, coarse)
        nv, ns = slider_value(el)
        if nv is None:
            break
        err = abs(nv - target)
        if err < best[0]:
            best = (err, attr(el, "AXValue"), ns)
        if not moved:
            if coarse:
                coarse = False                         # at an end stop for coarse steps: try fine
                continue
            break
        crossed = (nv >= target) if up else (nv <= target)
        if crossed:
            if coarse:
                coarse = False
            elif err <= tolerance or err >= abs(v - target):
                break
        v = nv
    cur = attr(el, "AXValue")
    if cur is not None and best[1] is not None and cur != best[1]:
        for _ in range(80):
            cur = attr(el, "AXValue")
            if cur == best[1]:
                break
            set_value(el, raw_max if cur < best[1] else raw_min)
    return shown(el)


def popup_menu(el, timeout: float = 1.0, actions_: tuple[str, ...] = ("AXShowMenu", "AXPress")):
    """Open a standard pop-up button and return its AXMenu child. Logic's plug-in header pop-ups must be opened
    with AXPress: an item chosen from a menu opened by AXShowMenu crashed Logic 11.2 every time."""
    menu = None
    for action in actions_:
        do(el, action)
        menu = wait_for(lambda: next((k for k in children(el) if role(k) == "AXMenu"), None), timeout, 0.05)
        if menu is not None:
            break
    if menu is None:
        raise AXError("pop-up menu did not open")
    return menu


def menu_titles(menu) -> list[str]:
    return [title(i) for i in children(menu) if role(i) == "AXMenuItem"]


def choose_in_menu(menu, option: str, allow_sub: bool = True) -> str:
    """Press the item called `option` (exact, else substring, case-insensitive) in `menu`, searching one
    level of submenus too (the submenu is opened by pressing its parent first)."""
    want = option.strip().lower()
    items = [i for i in children(menu) if role(i) == "AXMenuItem"]
    hit = next((i for i in items if title(i).lower() == want), None) or next((i for i in items if want and want in title(i).lower()), None)
    if hit is not None and not children(hit):
        press(hit)
        time.sleep(0.1)
        return title(hit)
    if allow_sub:
        for i in items:
            subs = [c for c in children(i) if role(c) == "AXMenu"]
            if not subs:
                continue
            kids = [k for k in children(subs[0]) if role(k) == "AXMenuItem"]
            sub_hit = next((k for k in kids if title(k).lower() == want), None) or next((k for k in kids if want in title(k).lower()), None)
            if sub_hit is not None:
                press(i)
                time.sleep(0.15)
                press(sub_hit)
                time.sleep(0.1)
                return title(sub_hit)
    do(menu, "AXCancel")
    raise AXError(f"no option {option!r} among {menu_titles(menu)}")


def set_choice(el, option: str) -> str:
    """Pick `option` in a standard pop-up button and return what it now shows."""
    menu = popup_menu(el)
    picked = choose_in_menu(menu, option)
    time.sleep(0.1)
    return str(attr(el, "AXValue") or picked)


def set_checkbox(el, on: bool) -> bool:
    if is_on(el) != bool(on):
        press(el)
        time.sleep(0.05)
    return is_on(el)


# ============================================================================ the Mixer
@dataclass
class StripInfo:
    index: int
    name: str
    volume: str
    pan: str
    mute: bool
    solo: bool
    inserts: list[str]                 # top to bottom, as Logic shows them
    instrument: str | None
    sends: list[str]
    output: str
    automation: str
    kind: str = ""                     # 'track' | 'aux' | 'output' | 'master'


class Mixer:
    """Logic's Mixer window in 'Tracks' view: one channel strip per track in track order, then the aux
    strips, then Stereo Out and Master. Everything on a strip is an accessibility element."""

    def __init__(self, app: LogicApp, project: str | None = None):
        self.app = app
        self.project = project

    def window(self):
        """The window holding our project's Mixer: the separate Mixer window, or the main window when the Mixer
        is shown as a pane in it (its title then ends in '- Mixer')."""
        w = self.app.mixer_window(self.project)
        if w is None:
            main = self.app.main_window(self.project)
            if main is None:
                raise AXError("no project window to open a Mixer for")
            def pane(win):
                # the Mixer shown as a pane of the main window (the Inspector's channel strips are a 'Mixer' area too, but empty)
                area = find(win, lambda e: role(e) == "AXLayoutArea" and desc(e) == "Mixer" and len(children(e)) > 1, 7) if win is not None else None
                return win if area is not None else None
            if pane(main) is not None:
                return main
            self.app.make_key(main)
            if not self.app.menu("Window", "Open Mixer"):
                raise AXError("could not open the Mixer window")
            w = wait_for(lambda: self.app.mixer_window(self.project) or pane(self.app.main_window(self.project)), 6.0)
            if w is None:
                raise AXError("the Mixer window did not appear")
        return w

    def ensure_tracks_view(self, w=None) -> None:
        """The Mixer's 'Tracks' view: every track's strip in order, then the aux, output and master strips.
        (A Mackie Control Global View switches the Mixer to 'All' filtered to one strip type.)"""
        w = w or self.window()
        rb = find(w, lambda e: role(e) == "AXRadioButton" and desc(e) == "Tracks", 6)
        if rb is not None and not is_on(rb):
            press(rb)
            time.sleep(0.4)

    def strips(self) -> list:
        w = self.window()
        self.ensure_tracks_view(w)

        def read():
            area = find(w, lambda e: role(e) == "AXLayoutArea" and desc(e) == "Mixer" and len(children(e)) > 0, 7)
            return [c for c in children(area)] if area is not None else []
        return wait_for(read, 4.0, 0.2) or []

    @staticmethod
    def control(strip, text: str):
        return next((k for k in children(strip) if desc(k) == text), None)

    def info(self, strip, index: int = -1) -> StripInfo:
        """Read a strip. Its children run from the bottom of the strip upwards: name, mute, solo, fader, level,
        peak, pan, automation, group, output, then the send slots ('send button' when empty, else a group named
        after the bus followed by a 'send knob'), the insert slots ('audio plug-in' when empty, 'insert bar' +
        group when filled), the instrument group (software instruments only), 'MIDI plug-in', EQ, meter, setting."""
        kids = children(strip)
        name_el = next((k for k in kids if desc(k) == "name"), None)
        vol = next((k for k in kids if desc(k) == "volume fader"), None)
        pan = next((k for k in kids if desc(k) == "pan"), None)
        mute = next((k for k in kids if desc(k) == "mute"), None)
        solo = next((k for k in kids if desc(k) == "solo"), None)
        auto = next((k for k in kids if role(k) == "AXGroup" and "automation" in desc(k)), None)
        out = next((k for k in kids if role(k) == "AXButton" and ("Output" in desc(k) or desc(k).startswith("Bus ") or desc(k) == "No Output")), None)
        i_midi = next((i for i, k in enumerate(kids) if desc(k) == "MIDI plug-in"), None)
        sends: list[str] = []
        inserts: list[str] = []
        instrument = None
        limit = i_midi if i_midi is not None else len(kids)
        for i, k in enumerate(kids[:limit]):
            if role(k) != "AXGroup" or k is auto or desc(k) in ("audio plug-in", "insert bar", "send button", "MIDI plug-in", ""):
                continue
            nxt = kids[i + 1] if i + 1 < len(kids) else None
            if nxt is not None and desc(nxt) == "send knob":
                sends.append(desc(k))
            elif i_midi is not None and i == i_midi - 1:
                instrument = desc(k)
            else:
                inserts.append(desc(k))
        inserts.reverse()                                  # top to bottom
        nm = str(attr(name_el, "AXValue") or desc(strip)) if name_el is not None else desc(strip)
        kind = "track"
        if nm == "Master":
            kind = "master"
        elif nm.startswith("Stereo Out") or (out is not None and desc(out) == "No Output"):
            kind = "output"
        elif nm.startswith("Aux "):
            kind = "aux"
        return StripInfo(index, nm, shown(vol) if vol is not None else "", shown(pan) if pan is not None else "",
                         is_on(mute) if mute is not None else False, is_on(solo) if solo is not None else False,
                         inserts, instrument, sends, desc(out) if out is not None else "",
                         desc(auto) if auto is not None else "", kind)

    def all_info(self) -> list[StripInfo]:
        return [self.info(s, i) for i, s in enumerate(self.strips())]

    def strip(self, name: str):
        for s in self.strips():
            nm = self.control(s, "name")
            if (nm is not None and str(attr(nm, "AXValue")) == name) or desc(s) == name:
                return s
        return None

    def set_volume(self, strip, db: float) -> str:
        return set_slider(self.control(strip, "volume fader"), db, tolerance=0.05)

    def set_pan(self, strip, pan: float) -> str:
        """pan -1..1 -> Logic's -64..63 (shown as a plain number, '0' centre)."""
        el = self.control(strip, "pan")
        target = max(-64, min(63, round(max(-1.0, min(1.0, pan)) * 64)))
        s = set_slider(el, float(target), tolerance=0.5)
        return s or str(attr(el, "AXValue"))

    def set_mute(self, strip, on: bool) -> bool:
        el = self.control(strip, "mute")
        if is_on(el) != on:
            press(el)
            time.sleep(0.05)
        return is_on(el)

    def set_solo(self, strip, on: bool) -> bool:
        el = self.control(strip, "solo")
        if is_on(el) != on:
            press(el)
            time.sleep(0.05)
        return is_on(el)

    def insert_groups(self, strip) -> list:
        """The filled insert groups, top to bottom (Logic's order), plus a flag for the instrument group."""
        kids = children(strip)
        auto = next((k for k in kids if role(k) == "AXGroup" and "automation" in desc(k)), None)
        i_midi = next((i for i, k in enumerate(kids) if desc(k) == "MIDI plug-in"), len(kids))
        first_insert = next((i for i, k in enumerate(kids) if desc(k) in ("audio plug-in", "insert bar")), 0)
        groups = [k for i, k in enumerate(kids) if role(k) == "AXGroup" and k is not auto and first_insert <= i < i_midi]
        return list(reversed(groups))

    def instrument_group(self, strip):
        kids = children(strip)
        i_midi = next((i for i, k in enumerate(kids) if desc(k) == "MIDI plug-in"), None)
        if i_midi is None:
            return None
        g = kids[i_midi - 1] if i_midi > 0 else None
        return g if g is not None and role(g) == "AXGroup" else None

    def empty_insert_slot(self, strip):
        return self.control(strip, "audio plug-in")

    def open_plugin(self, strip, name: str, nth: int = 0):
        """Press 'open' on the nth insert called `name` (case-insensitive prefix match; 'instrument' = the
        instrument slot) and return the plug-in window."""
        if name == "instrument":
            hits = [self.instrument_group(strip)]
        else:
            want = name.lower()
            groups = self.insert_groups(strip)
            hits = [g for g in groups if desc(g).lower() == want] or [g for g in groups if desc(g).lower().startswith(want[:6])]
        if len(hits) <= nth or hits[0] is None:
            raise AXError(f"no insert {name!r} #{nth + 1} on this strip (have {[desc(g) for g in self.insert_groups(strip)]})")
        before = {id(w) for w in self.app.plugin_windows()}
        titles_before = [title(w) for w in self.app.plugin_windows()]
        btn = next((k for k in children(hits[nth]) if desc(k) == "open"), None)
        if not press(btn):
            raise AXError(f"could not press 'open' on {name!r}")
        t_end = time.time() + 4.0
        while time.time() < t_end:
            wins = self.app.plugin_windows()
            new = [w for w in wins if id(w) not in before]
            if new:
                return new[-1]
            if wins and [title(w) for w in wins] != titles_before:
                return wins[-1]
            time.sleep(0.1)
        wins = self.app.plugin_windows()
        if wins:
            return wins[-1]                                  # Link mode: the one window shows the pressed plug-in
        raise AXError(f"{name!r} did not open a window")

    def set_bypass(self, strip, name: str, bypass: bool, nth: int = 0) -> bool:
        hits = [g for g in self.insert_groups(strip) if desc(g).lower() == name.lower()]
        if len(hits) <= nth:
            raise AXError(f"no insert {name!r} on this strip")
        return set_checkbox(next((k for k in children(hits[nth]) if desc(k) == "bypass"), None), bypass)


# ============================================================================ plug-in windows
class PluginWindow:
    """An open Logic plug-in window. The header has close / view / bypass / side chain and preset pop-ups;
    whatever parameters the plug-in's own view exposes appear as named sliders, check boxes and pop-ups."""

    def __init__(self, el):
        self.el = el

    def title(self) -> str:
        return title(self.el)

    def close(self) -> None:
        b = find(self.el, lambda e: desc(e) == "close" and role(e) == "AXButton", 2)
        if b is not None:
            press(b)

    def controls(self) -> list:
        head = {"link", "view", "bypass", "compare", "close", "toolbar", "previous", "next", "Undo", "Redo"}
        return [e for e in find_all(self.el, lambda e: role(e) in ("AXSlider", "AXCheckBox", "AXPopUpButton") and (desc(e) or title(e)), 8)
                if desc(e) not in head and attr(e, "AXParent") is not self.el or role(e) != "AXPopUpButton"]

    def params(self) -> list[tuple[str, str, str]]:
        """[(name, kind, shown)] for every parameter control the window exposes."""
        kinds = {"AXSlider": "slider", "AXCheckBox": "switch", "AXPopUpButton": "choice"}
        return [(desc(e), kinds[role(e)], shown(e)) for e in self.controls()]

    def param(self, name: str):
        want = name.lower()
        els = self.controls()
        return next((e for e in els if desc(e).lower() == want), None) or next((e for e in els if want in desc(e).lower()), None)

    def set(self, name: str, val) -> str:
        el = self.param(name)
        if el is None:
            raise AXError(f"no parameter {name!r} in the window (have: {', '.join(p[0] for p in self.params()) or 'none'})")
        r = role(el)
        if r == "AXSlider":
            if isinstance(val, str):
                num = disp_number(val)
                if num is None:
                    raise AXError(f"{name}: cannot read {val!r}")
                val = num
            return set_slider(el, float(val))
        if r == "AXCheckBox":
            if isinstance(val, str):
                val = val.strip().lower() in ("on", "true", "1", "yes")
            return "On" if set_checkbox(el, bool(val)) else "Off"
        return set_choice(el, str(val))

    def get(self, name: str) -> str:
        el = self.param(name)
        if el is None:
            raise AXError(f"no parameter {name!r}")
        return shown(el)

    def header_popups(self) -> list:
        return [c for c in children(self.el) if role(c) == "AXPopUpButton"]

    def side_chain_popup(self):
        """The side chain selector: the header pop-up whose menu offers 'Internal'/'None' and track lists."""
        pops = self.header_popups()
        for p in pops:
            if str(attr(p, "AXValue") or "") in ("Internal", "None") or "(Inst" in str(attr(p, "AXValue") or "") or "(Audio" in str(attr(p, "AXValue") or ""):
                return p
        return pops[0] if pops else None

    def side_chain_options(self) -> dict[str, list[str]]:
        p = self.side_chain_popup()
        if p is None:
            return {}
        menu = popup_menu(p, actions_=("AXPress",))
        out: dict[str, list[str]] = {"": []}
        for i in children(menu):
            if role(i) != "AXMenuItem":
                continue
            subs = [c for c in children(i) if role(c) == "AXMenu"]
            if subs:
                out[title(i)] = [title(k) for k in children(subs[0]) if role(k) == "AXMenuItem"]
            elif title(i):
                out[""].append(title(i))
        do(menu, "AXCancel")
        return out

    def set_side_chain(self, source: str) -> str:
        """Choose the side chain input: a channel strip name ('Kick', shown as 'Kick (Inst 1)'), 'None'/'Internal',
        or 'Inst 3' / 'Audio 2' / 'Bus 1'. Returns what the pop-up shows afterwards."""
        p = self.side_chain_popup()
        if p is None:
            raise AXError("this plug-in has no side chain selector")
        menu = popup_menu(p, actions_=("AXPress",))
        want = source.strip().lower()
        items = [i for i in children(menu) if role(i) == "AXMenuItem"]
        for i in items:                                      # top level: None / Internal
            if title(i).lower() == want and not children(i):
                press(i)
                time.sleep(0.15)
                return str(attr(self.side_chain_popup(), "AXValue") or title(i))
        best = None
        for i in items:
            subs = [c for c in children(i) if role(c) == "AXMenu"]
            if not subs:
                continue
            for k in children(subs[0]):
                t = title(k)
                low = t.lower()
                name_part = low.rsplit(" (", 1)[0]
                paren = low[low.rfind("(") + 1:-1] if "(" in low else ""
                score = 3 if name_part == want else 2 if paren == want else 1 if want and want in low else 0
                if score and (best is None or score > best[0]):
                    best = (score, i, k)
        if best is None:
            do(menu, "AXCancel")
            raise AXError(f"no side chain source {source!r}; offered: " + "; ".join(
                f"{title(i)}: {[title(k) for k in children(children(i)[0])]}" for i in items if children(i)))
        _, parent, item = best
        chosen = title(item)
        press(parent)
        time.sleep(0.15)
        press(item)
        time.sleep(0.6)
        now = str(attr(self.side_chain_popup(), "AXValue") or "")
        # Logic shows the short form ('Inst 1') a moment later; report the item that was chosen if the pop-up lags
        return now if now and now not in ("Internal", "None") else chosen
