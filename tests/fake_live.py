"""A minimal in-memory imitation of the Live Object Model, enough to exercise the
bridge handlers and push_song end-to-end over a real socket."""
from __future__ import annotations

import json
import math
import socket
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ableton_use" / "live" / "remote_script" / "AbletonUse"))
from handlers import Handlers  # noqa: E402


class Param:
    def __init__(self, name, lo, hi, value, fmt):
        self.name, self.min, self.max, self.value, self._fmt = name, lo, hi, value, fmt

    def str_for_value(self, v):
        return self._fmt(v)


def _vol_fmt(v):
    # Live-like curve: 0.85 -> 0 dB, 0 -> -inf, 1 -> +6 dB
    if v <= 1e-6:
        return "-inf dB"
    db = 40 * math.log10(v / 0.85) if v < 0.85 else (v - 0.85) / 0.15 * 6
    return "%.1f dB" % db


class Device:
    def __init__(self, name, class_name, params):
        self.name, self.class_name, self.parameters = name, class_name, params
        self.available_input_routing_types = []
        self.input_routing_type = None


class Envelope:
    def __init__(self):
        self.steps = []

    def insert_step(self, t, d, v):
        self.steps.append((t, d, v))


class Clip:
    def __init__(self, start, length):
        self.start_time, self.length, self.name, self.notes, self.envs = start, length, "", [], {}
        self.is_midi_clip = True

    def add_new_notes(self, specs):
        self.notes.extend(specs)

    def set_notes(self, notes):
        self.notes.extend(notes)

    def get_notes_extended(self, *a):
        return self.notes

    def automation_envelope(self, p):
        return self.envs.get(id(p))

    def create_automation_envelope(self, p):
        self.envs[id(p)] = Envelope()
        return self.envs[id(p)]


class Mixer:
    def __init__(self):
        self.volume = Param("Track Volume", 0.0, 1.0, 0.85, _vol_fmt)
        self.panning = Param("Track Panning", -1.0, 1.0, 0.0, lambda v: "%dC" % (v * 50))


class Track:
    def __init__(self, name):
        self.name, self.mute, self.color_index = name, False, 0
        self.devices, self.arrangement_clips = [], []
        self.mixer_device = Mixer()
        self.has_midi_input = True

    def create_midi_clip(self, start, length):
        c = Clip(start, length)
        self.arrangement_clips.append(c)
        return c

    def delete_clip(self, c):
        self.arrangement_clips.remove(c)

    def insert_device(self, name):
        if name == "Auto Filter":
            d = Device(name, "AutoFilter", [Param("Frequency", 20.0, 18500.0, 18500.0, lambda v: "%.0f Hz" % v)])
        elif name == "Compressor":
            d = Device(name, "Compressor2", [
                Param("Threshold", 0.0, 1.0, 1.0, lambda v: "%.1f dB" % (-60 + 60 * v)),
                Param("Ratio", 0.0, 1.0, 0.0, lambda v: "%.2f : 1" % (1 + 99 * v ** 3)),
                Param("Release", 0.0, 1.0, 0.0, lambda v: "%.1f ms" % (1 + 2999 * v ** 2)),
                Param("Attack", 0.0, 1.0, 0.0, lambda v: "%.2f ms" % (0.01 + 999 * v ** 3)),
                Param("S/C On", 0.0, 1.0, 0.0, lambda v: "on" if v > 0.5 else "off"),
            ])
            d.available_input_routing_types = [{"display_name": t} for t in ("No Input", "1-Kick", "Kick")]
        else:
            raise RuntimeError("unknown device " + name)
        self.devices.append(d)


class Cue:
    def __init__(self, t):
        self.time, self.name = t, ""


class View:
    selected_track = None


class Song:
    def __init__(self):
        self.tracks = [Track("1-MIDI")]
        self.tempo, self.signature_numerator, self.signature_denominator = 120.0, 4, 4
        self.cue_points, self.current_song_time, self.is_playing = [], 0.0, False
        self.view = View()
        self.song_length = 0

    def create_midi_track(self, i):
        t = Track("MIDI")
        if i < 0:
            self.tracks.append(t)
        else:
            self.tracks.insert(i, t)

    def delete_track(self, i):
        del self.tracks[i]

    def set_or_delete_cue(self):
        for c in self.cue_points:
            if c.time == self.current_song_time:
                self.cue_points.remove(c)
                return
        self.cue_points.append(Cue(self.current_song_time))

    def start_playing(self):
        self.is_playing = True

    def stop_playing(self):
        self.is_playing = False


class Item:
    def __init__(self, name, children=(), loadable=True):
        self.name, self.children, self.is_loadable = name, list(children), loadable
        self.is_folder = bool(children)


class Browser:
    def __init__(self, song):
        self._song = song
        self.drums = Item("Drums", [Item("Drum Rack", loadable=True), Item("Kits", [Item("909 Core Kit.adg")], False)], False)
        self.instruments = Item("Instruments", [Item("Operator"), Item("Wavetable"), Item("Drift")], False)
        self.sounds = Item("Sounds", [], False)
        self.audio_effects = Item("Audio Effects", [Item("Auto Filter"), Item("Compressor")], False)

    def load_item(self, item):
        t = self._song.view.selected_track
        t.devices.append(Device(item.name.replace(".adg", ""), "InstrumentGroupDevice", []))


class App:
    def __init__(self, song):
        self.browser = Browser(song)

    def get_major_version(self):
        return 12

    def get_minor_version(self):
        return 3

    def get_bugfix_version(self):
        return 0


class FakeLiveServer:
    """Runs Handlers behind a real TCP socket, like the remote script does."""

    def __init__(self):
        self.song = Song()
        self.app = App(self.song)
        self.handlers = Handlers(lambda: self.song, lambda: self.app, None)
        self.sock = socket.socket()
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(1)
        self.port = self.sock.getsockname()[1]
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        conn, _ = self.sock.accept()
        buf = b""
        while True:
            chunk = conn.recv(65536)
            if not chunk:
                break
            buf += chunk
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                req = json.loads(line)
                resp = self.handlers.dispatch(req)
                resp["id"] = req.get("id")
                conn.sendall((json.dumps(resp) + "\n").encode())
