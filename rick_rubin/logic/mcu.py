"""A Mackie Control emulated on a virtual MIDI port, as Logic Pro sees it.

Logic has no scripting API for its mixer, but it speaks the Mackie Control protocol to any MIDI
device that answers the handshake — and it finds such a device by itself the moment the port
appears (Logic Pro > Control Surfaces, no user setup). This module is the surface: it keeps the
state Logic mirrors to a real unit (the two-line LCD, the eight fader positions, the time display,
button LEDs, the assignment display) and sends what a hand on the unit would send (faders, V-Pot
turns, button presses). Everything else — which plug-in a column of the LCD stands for, what a value
reads — is interpreted in bridge.py.

Protocol notes (Mackie Control, as implemented by Logic Pro 11.2):
  buttons        note on (ch 1) velocity 127 = press, 0 = release; LEDs come back the same way
  faders         pitch bend on channels 1-9 (9 = master), 14 bit, -8192 = bottom
  V-Pot turn     CC 0x10+n, value: bits 0-3 steps, bit 6 set = counter-clockwise
  V-Pot ring     CC 0x30+n from Logic (LED ring state)
  time display   CC 0x40-0x49 from Logic, one 7-segment digit each (ASCII), 0x49 is the leftmost
  assignment     CC 0x4A-0x4B from Logic, 7-segment codes
  LCD            sysex F0 00 00 66 14 12 <offset 0-111> <ascii...> F7, 2 lines x 56 chars
  handshake      F0 00 00 66 14 00 F7 (query) -> 01 serial challenge; 02 -> 03 serial
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Callable

PORT_NAME = "rick-rubin MCU"
MCU_ID = [0x00, 0x00, 0x66, 0x14]
SERIAL = [ord(c) & 0x7F for c in "RICKRUB"]

# ---- button note numbers
REC = 0            # +channel 0-7
SOLO = 8
MUTE = 16
SELECT = 24
VPOT_PUSH = 32
TRACK, SEND, PAN, PLUGIN, EQ, INSTRUMENT = 40, 41, 42, 43, 44, 45
BANK_LEFT, BANK_RIGHT, CHANNEL_LEFT, CHANNEL_RIGHT = 46, 47, 48, 49
FLIP, GLOBAL_VIEW, NAME_VALUE, SMPTE_BEATS = 50, 51, 52, 53
F1 = 54            # F1-F8 = 54-61
VIEW_MIDI, VIEW_INPUTS, VIEW_AUDIO, VIEW_INSTRUMENTS, VIEW_AUX, VIEW_BUSSES, VIEW_OUTPUTS, VIEW_USER = range(62, 70)
SHIFT, OPTION, CONTROL, CMD_ALT = 70, 71, 72, 73
READ_OFF, WRITE, TRIM, TOUCH, LATCH, GROUP = 74, 75, 76, 77, 78, 79
SAVE, UNDO, CANCEL, ENTER = 80, 81, 82, 83
MARKER, NUDGE, CYCLE, DROP, REPLACE, CLICK, SOLO_BTN = 84, 85, 86, 87, 88, 89, 90
REWIND, FAST_FWD, STOP, PLAY, RECORD = 91, 92, 93, 94, 95
CURSOR_UP, CURSOR_DOWN, CURSOR_LEFT, CURSOR_RIGHT, ZOOM, SCRUB = 96, 97, 98, 99, 100, 101
FADER_TOUCH = 104  # +channel 0-8
LED_SMPTE, LED_BEATS, LED_RUDE_SOLO = 113, 114, 115

# how a 7-segment code on the assignment display reads (bit 0 = a ... bit 6 = g), enough for Logic's modes
_SEVEN_SEG = {
    0x3F: "0", 0x06: "1", 0x5B: "2", 0x4F: "3", 0x66: "4", 0x6D: "5", 0x7D: "6", 0x07: "7", 0x7F: "8", 0x6F: "9",
    0x77: "A", 0x7C: "b", 0x39: "C", 0x5E: "d", 0x79: "E", 0x71: "F", 0x3D: "G", 0x76: "H", 0x30: "I", 0x38: "L",
    0x54: "n", 0x5C: "o", 0x73: "P", 0x50: "r", 0x78: "t", 0x3E: "U", 0x00: " ",
}


@dataclass
class SurfaceState:
    lcd: list[str] = field(default_factory=lambda: [" "] * 112)
    faders: list[int] = field(default_factory=lambda: [-8192] * 9)        # pitch bend values, ch 0-8
    vpot_rings: list[int] = field(default_factory=lambda: [0] * 8)
    time_digits: list[str] = field(default_factory=lambda: [" "] * 10)    # index 0 = CC 0x40 (rightmost)
    assignment: list[int] = field(default_factory=lambda: [0, 0])          # CC 0x4A (right), 0x4B (left)
    leds: dict[int, bool] = field(default_factory=dict)
    last_change: float = 0.0
    lcd_changed: float = 0.0

    # ---- readings
    def line(self, n: int) -> str:
        return "".join(self.lcd[n * 56:(n + 1) * 56])

    def columns(self, n: int) -> list[str]:
        """The LCD line as the 8 channel-strip columns of 7 characters (the 7th is a separator)."""
        row = self.line(n)
        return [row[i * 7:i * 7 + 7].rstrip() for i in range(8)]

    def cells(self, n: int) -> list[str]:
        return [c[:6].strip() for c in self.columns(n)]

    def time_text(self) -> str:
        return "".join(reversed(self.time_digits))

    def position(self) -> tuple[int, int, int, int] | None:
        """Bars, beats, division, ticks in Beats mode: ' 10 2 2 88' -> (10, 2, 2, 88)."""
        t = self.time_text()
        try:
            return int(t[0:3]), int(t[3:5]), int(t[5:7]), int(t[7:10])
        except ValueError:
            return None

    def beats(self) -> float | None:
        """Playhead in beats from the song start (division = 16ths, ticks = 1/240 of a 16th in Logic)."""
        p = self.position()
        if p is None:
            return None
        bar, beat, div, tick = p
        return (bar - 1) * 4 + (beat - 1) + (div - 1) * 0.25 + tick / 240.0 * 0.25

    def mode(self) -> str:
        return "".join(_SEVEN_SEG.get(c & 0x7F, "?") for c in reversed(self.assignment)) + ("." if self.assignment[0] & 0x40 else "")


class MackieControl:
    """The emulated unit. `open()` creates the virtual port; Logic detects it within a second."""

    def __init__(self, name: str = PORT_NAME, log: Callable[[str], None] | None = None):
        self.name = name
        self.state = SurfaceState()
        self._log = log or (lambda *_: None)
        self._in = self._out = None
        self._lock = threading.Lock()
        self.handshakes = 0
        self.listeners: list[Callable[[object], None]] = []

    # ------------------------------------------------------------------ port
    def open(self) -> "MackieControl":
        import mido
        self._out = mido.open_output(self.name, virtual=True)
        self._in = mido.open_input(self.name, virtual=True, callback=self._on_message)
        return self

    def close(self) -> None:
        for p in (self._in, self._out):
            try:
                if p:
                    p.close()
            except Exception:  # noqa: BLE001
                pass
        self._in = self._out = None

    def send(self, msg) -> None:
        with self._lock:
            assert self._out is not None, "port not open"
            self._out.send(msg)

    # ------------------------------------------------------------------ what Logic sends
    def _on_message(self, msg) -> None:
        st = self.state
        now = time.time()
        try:
            if msg.type == "sysex":
                d = list(msg.data)
                if d[:4] == MCU_ID and len(d) > 4:
                    cmd = d[4]
                    if cmd == 0x00:                                   # device query
                        self._reply([0x01] + SERIAL + [0x01, 0x02, 0x03, 0x04])
                    elif cmd == 0x02:                                 # host connection reply
                        self._reply([0x03] + SERIAL)
                        self.handshakes += 1
                    elif cmd == 0x13:                                 # version request
                        self._reply([0x14] + [ord(c) for c in "V1.0"])
                    elif cmd == 0x12 and len(d) > 5:                  # LCD text
                        off = d[5]
                        for i, ch in enumerate(d[6:]):
                            if 0 <= off + i < 112:
                                st.lcd[off + i] = chr(ch) if 32 <= ch < 127 else " "
                        st.lcd_changed = now
                elif len(d) > 3 and d[0] == 0x7E and d[2] == 0x06 and d[3] == 0x01:     # universal identity request
                    self.send(self._mido().Message("sysex", data=[0x7E, 0x00, 0x06, 0x02] + MCU_ID + [0x00, 0x01, 0x00, 0x00, 0x00, 0x00]))
            elif msg.type == "pitchwheel" and 0 <= msg.channel <= 8:
                st.faders[msg.channel] = msg.pitch
            elif msg.type == "control_change":
                if 0x40 <= msg.control <= 0x49:
                    st.time_digits[msg.control - 0x40] = chr(msg.value) if msg.value >= 32 else " "
                elif msg.control in (0x4A, 0x4B):
                    st.assignment[msg.control - 0x4A] = msg.value
                elif 0x30 <= msg.control <= 0x37:
                    st.vpot_rings[msg.control - 0x30] = msg.value
            elif msg.type in ("note_on", "note_off"):
                st.leds[msg.note] = msg.type == "note_on" and msg.velocity > 0
            st.last_change = now
        except Exception as e:  # noqa: BLE001
            self._log(f"mcu: error on {msg}: {e}")
        for fn in list(self.listeners):
            try:
                fn(msg)
            except Exception:  # noqa: BLE001
                pass

    @staticmethod
    def _mido():
        import mido
        return mido

    def _reply(self, body: list[int]) -> None:
        self.send(self._mido().Message("sysex", data=MCU_ID + body))

    # ------------------------------------------------------------------ what a hand would do
    def press(self, note: int, hold: float = 0.03) -> None:
        mido = self._mido()
        self.send(mido.Message("note_on", channel=0, note=note, velocity=127))
        time.sleep(hold)
        self.send(mido.Message("note_on", channel=0, note=note, velocity=0))

    def hold(self, note: int) -> None:
        self.send(self._mido().Message("note_on", channel=0, note=note, velocity=127))

    def release(self, note: int) -> None:
        self.send(self._mido().Message("note_on", channel=0, note=note, velocity=0))

    def fader(self, channel: int, value: int, touch: bool = True) -> None:
        """Move fader `channel` (0-7, 8 = master) to a 14-bit position (-8192..8191), with a touch around it
        like a finger would make (Logic only writes automation for touched faders)."""
        mido = self._mido()
        value = max(-8192, min(8191, int(value)))
        if touch:
            self.hold(FADER_TOUCH + channel)
        self.send(mido.Message("pitchwheel", channel=channel, pitch=value))
        if touch:
            time.sleep(0.01)
            self.release(FADER_TOUCH + channel)

    def vpot(self, n: int, steps: int) -> None:
        """Turn V-Pot `n` (0-7) by `steps` detents (negative = counter-clockwise)."""
        mido = self._mido()
        direction = 0x40 if steps < 0 else 0x00
        left = abs(int(steps))
        while left > 0:
            k = min(left, 15)
            self.send(mido.Message("control_change", channel=0, control=0x10 + n, value=direction | k))
            left -= k
            if left:
                time.sleep(0.004)

    def wait_lcd(self, since: float, timeout: float = 0.6) -> bool:
        """Wait until Logic has rewritten the LCD after `since` (a time.time()), then a moment for it to settle."""
        t_end = time.time() + timeout
        while time.time() < t_end:
            if self.state.lcd_changed > since:
                time.sleep(0.08)
                return True
            time.sleep(0.01)
        return False

    def settle(self, quiet: float = 0.12, timeout: float = 1.0) -> None:
        """Wait until Logic has stopped sending for `quiet` seconds (it rewrites the LCD in several messages)."""
        t_end = time.time() + timeout
        while time.time() < t_end:
            if time.time() - self.state.last_change >= quiet:
                return
            time.sleep(0.01)
