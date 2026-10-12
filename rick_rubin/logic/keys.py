"""Keystrokes delivered to Logic Pro's process only (CGEventPostToPid), so nothing is typed into whatever
app the person at the Mac is using. Used for the few places Logic offers no accessibility path: its own
pop-up menus (plug-in and send menus have a search field), file dialogs (⌘⇧G 'go to folder'), and text
entry in dialogs."""
from __future__ import annotations

import time

try:
    import Quartz
    HAVE_QUARTZ = True
except ImportError:  # pragma: no cover
    HAVE_QUARTZ = False

# US keyboard virtual key codes
KEYCODES = {
    "a": 0, "s": 1, "d": 2, "f": 3, "h": 4, "g": 5, "z": 6, "x": 7, "c": 8, "v": 9, "b": 11, "q": 12, "w": 13, "e": 14,
    "r": 15, "y": 16, "t": 17, "1": 18, "2": 19, "3": 20, "4": 21, "6": 22, "5": 23, "=": 24, "9": 25, "7": 26, "-": 27,
    "8": 28, "0": 29, "]": 30, "o": 31, "u": 32, "[": 33, "i": 34, "p": 35, "l": 37, "j": 38, "'": 39, "k": 40, ";": 41,
    "\\": 42, ",": 43, "/": 44, "n": 45, "m": 46, ".": 47, "`": 50, " ": 49,
    "return": 36, "tab": 48, "delete": 51, "escape": 53, "left": 123, "right": 124, "down": 125, "up": 126,
    "home": 115, "end": 119, "pageup": 116, "pagedown": 121, "forwarddelete": 117,
}
SHIFTED = {"!": "1", "@": "2", "#": "3", "$": "4", "%": "5", "^": "6", "&": "7", "*": "8", "(": "9", ")": "0", "_": "-", "+": "=",
           "{": "[", "}": "]", "|": "\\", ":": ";", '"': "'", "<": ",", ">": ".", "?": "/", "~": "`"}
MODS = {"cmd": 1 << 20, "shift": 1 << 17, "alt": 1 << 19, "option": 1 << 19, "ctrl": 1 << 18, "control": 1 << 18}


def _post(pid: int, code: int, down: bool, flags: int = 0) -> None:
    ev = Quartz.CGEventCreateKeyboardEvent(None, code, down)
    Quartz.CGEventSetFlags(ev, flags)
    Quartz.CGEventPostToPid(pid, ev)


def key(pid: int, name: str, *mods: str, delay: float = 0.02) -> None:
    """One key press, e.g. key(pid, "g", "cmd", "shift")."""
    code = KEYCODES[name.lower()] if len(name) > 1 or name.lower() in KEYCODES else None
    flags = 0
    if code is None:
        if name in SHIFTED:
            code, flags = KEYCODES[SHIFTED[name]], MODS["shift"]
        elif name.isupper():
            code, flags = KEYCODES[name.lower()], MODS["shift"]
        else:
            raise ValueError(f"no key code for {name!r}")
    for m in mods:
        flags |= MODS[m]
    _post(pid, code, True, flags)
    time.sleep(delay)
    _post(pid, code, False, flags)
    time.sleep(delay)


def type_text(pid: int, text: str, delay: float = 0.015) -> None:
    """Type `text` into Logic. Characters outside the US map go through the unicode path."""
    for ch in text:
        if ch == "\n":
            key(pid, "return", delay=delay)
            continue
        low = ch.lower()
        if ch in SHIFTED or (ch.isalpha() and ch.isupper()) or low in KEYCODES:
            key(pid, ch, delay=delay)
        else:
            ev = Quartz.CGEventCreateKeyboardEvent(None, 0, True)
            Quartz.CGEventKeyboardSetUnicodeString(ev, len(ch), ch)
            Quartz.CGEventPostToPid(pid, ev)
            ev2 = Quartz.CGEventCreateKeyboardEvent(None, 0, False)
            Quartz.CGEventKeyboardSetUnicodeString(ev2, len(ch), ch)
            Quartz.CGEventPostToPid(pid, ev2)
            time.sleep(delay)
