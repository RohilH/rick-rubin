"""A minimal in-memory imitation of the Live Object Model, enough to exercise the
bridge handlers and push_song end-to-end over a real socket."""
from __future__ import annotations

import json
import math
import socket
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "rick_rubin" / "live" / "remote_script" / "RickRubin"))
from handlers import Handlers  # noqa: E402


SONG_TEMPO = [120.0]


class Param:
    def __init__(self, name, lo, hi, value, fmt, items=None):
        self.name, self.min, self.max, self.value, self._fmt = name, lo, hi, value, fmt
        self.is_quantized, self.value_items = items is not None, items or []
        if items:
            self._fmt = lambda v: items[int(round(v))]

    def str_for_value(self, v):
        return self._fmt(v)


def _vol_fmt(v):
    # Live-like curve: 0.85 -> 0 dB, 0 -> -inf, 1 -> +6 dB
    if v <= 1e-6:
        return "-inf dB"
    db = 40 * math.log10(v / 0.85) if v < 0.85 else (v - 0.85) / 0.15 * 6
    return "%.1f dB" % db


def _hz_fmt(v):
    hz = 20.0 * 1000.0 ** v
    return "%.2f kHz" % (hz / 1000.0) if hz >= 1000 else "%.0f Hz" % hz


def _send_fmt(v):
    return "-inf dB" if v <= 1e-6 else "%.1f dB" % (-60 * (1 - v) ** 1.5)


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
    def __init__(self, start, length, path=None):
        self.start_time, self.length, self.name, self.notes, self.envs = start, length, "", [], {}
        self.is_midi_clip = path is None
        self.file_path, self.warping = path, True

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


class ClipSlot:
    def __init__(self, track):
        self._track, self.clip = track, None

    @property
    def has_clip(self):
        return self.clip is not None

    def create_clip(self, length):
        assert not self._track.is_audio
        self.clip = Clip(0.0, length)

    def create_audio_clip(self, path):
        assert self._track.is_audio
        self.clip = Clip(0.0, _wav_beats(path), path)

    def delete_clip(self):
        self.clip = None


def _wav_beats(path):
    import wave
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate() * SONG_TEMPO[0] / 60.0


class Mixer:
    def __init__(self):
        self.volume = Param("Track Volume", 0.0, 1.0, 0.85, _vol_fmt)
        self.panning = Param("Track Panning", -1.0, 1.0, 0.0, lambda v: "%dC" % (v * 50))
        self.sends = [Param("A-Reverb", 0.0, 1.0, 0.0, _send_fmt), Param("B-Delay", 0.0, 1.0, 0.0, _send_fmt)]


class Simpler(Device):
    def __init__(self):
        Device.__init__(self, "Simpler", "OriginalSimpler", [
            Param("Transpose", -48.0, 48.0, 0.0, lambda v: "%d st" % round(v)),
            Param("Detune", -50.0, 50.0, 0.0, lambda v: "%d ct" % round(v)),
            Param("Volume", -36.0, 36.0, -12.0, lambda v: "%.1f dB" % v),
            Param("Vol < Vel", 0.0, 100.0, 35.0, lambda v: "%.0f %%" % v),
        ])
        self.sample_path, self.playback_mode, self.voices = None, 0, 1

    def replace_sample(self, path):
        self.sample_path = path


class Track:
    def __init__(self, name, audio=False):
        self.name, self.mute, self.color_index = name, False, 0
        self.devices, self.arrangement_clips = [], []
        self.mixer_device = Mixer()
        self.has_midi_input = not audio
        self.is_audio = audio
        self.clip_slots = [ClipSlot(self) for _ in range(2)]

    def duplicate_clip_to_arrangement(self, clip, start):
        # like Live: the copy is a new arrangement clip; session envelopes become automation at that position
        c = Clip(start, clip.length, clip.file_path)
        c.name, c.notes, c.envs, c.warping = clip.name, list(clip.notes), dict(clip.envs), clip.warping
        c.is_midi_clip = clip.is_midi_clip
        self.arrangement_clips.append(c)

    def create_audio_clip(self, path, start):
        assert self.is_audio, "create_audio_clip on a MIDI track"
        c = Clip(start, _wav_beats(path), path)
        self.arrangement_clips.append(c)
        return c

    def create_midi_clip(self, start, length):
        assert not self.is_audio
        c = Clip(start, length)
        self.arrangement_clips.append(c)
        return c

    def delete_clip(self, c):
        self.arrangement_clips.remove(c)

    def delete_device(self, i):
        del self.devices[i]

    def insert_device(self, name, index=None):
        if name == "Simpler":
            d = Simpler()
            self.devices.insert(0 if index is None else index, d)
            return
        if name == "Auto Filter":
            # like Live 12's Auto Filter: raw 0..1, shown as 20 Hz .. 20 kHz
            d = Device(name, "AutoFilter2", [Param("Frequency", 0.0, 1.0, 1.0, _hz_fmt)])
        elif name == "Compressor":
            ms = lambda lo, hi: (lambda v: (lambda x: "%.2f s" % (x / 1000) if x >= 1000 else "%.2f ms" % x)(lo * (hi / lo) ** v))  # noqa: E731
            d = Device(name, "Compressor2", [
                Param("Threshold", 0.0, 1.0, 1.0, lambda v: "-inf dB" if v <= 0 else "%.1f dB" % (-60 + 66 * v)),
                Param("Ratio", 0.0, 1.0, 0.0, lambda v: "inf : 1" if v >= 1 else "%.2f : 1" % (1 / (1 - v))),
                Param("Attack", 0.0, 1.0, 0.0, ms(0.01, 1000.0)),
                Param("Release", 0.0, 1.0, 0.0, ms(1.0, 3000.0)),
                Param("Knee", 0.0, 18.0, 6.0, lambda v: "%.1f dB" % v),
                Param("Dry/Wet", 0.0, 1.0, 1.0, lambda v: "%.0f %%" % (100 * v)),
                Param("Makeup", 0.0, 1.0, 0.0, None, ["Off", "On"]),
                Param("Model", 0.0, 2.0, 1.0, None, ["Peak", "RMS", "Expand"]),
                Param("LookAhead", 0.0, 2.0, 0.0, None, ["0 ms", "1 ms", "10 ms"]),
                Param("S/C EQ Freq", 0.0, 1.0, 0.0, _hz_fmt),
                Param("S/C On", 0.0, 1.0, 0.0, None, ["Off", "On"]),
            ])
            d.available_input_routing_channels = [{"display_name": c} for c in ("Pre FX", "Post FX", "Post Mixer")]
            d.input_routing_channel = None
            d.available_input_routing_types = [{"display_name": t} for t in ("No Input", "1-Kick", "Kick")]
        elif name == "Chord":
            ps = []
            for i in range(1, 7):
                ps += [Param("Shift%d" % i, -36.0, 36.0, 0.0, lambda v: "%+d st" % round(v) if round(v) else "0 st"),
                       Param("Velocity%d" % i, 1.0, 200.0, 100.0, lambda v: "%.0f %%" % v)]
            d = Device(name, "MidiChord", ps + [Param("Strum", -400.0, 400.0, 0.0, lambda v: "%.2f ms" % v)])
        elif name == "Pitch":
            d = Device(name, "MidiPitcher", [Param("Pitch", -128.0, 128.0, 0.0, lambda v: "%+d st" % round(v) if round(v) else "0 st")])
        elif name in ("Reverb", "Delay", "Channel EQ", "Utility", "Arpeggiator", "Limiter", "Saturator"):
            d = Device(name, name.replace(" ", ""), [Param("Dry/Wet", 0.0, 1.0, 0.5, lambda v: "%.0f %%" % (100 * v)),
                                                     Param("Decay Time", 0.0, 1.0, 0.3, lambda v: "%.0f ms" % (200 * 300 ** v))])
        else:
            raise RuntimeError("unknown device " + name)
        if index is None:
            self.devices.append(d)
        else:
            self.devices.insert(index, d)


class Cue:
    def __init__(self, t):
        self.time, self.name = t, ""


class View:
    selected_track = None


class Song:
    def __init__(self):
        self.tracks = [Track("1-MIDI")]
        self.return_tracks = [Track("A-Reverb", audio=True), Track("B-Delay", audio=True)]
        self.return_tracks[0].insert_device("Reverb")
        self.return_tracks[1].insert_device("Delay")
        self.master_track = Track("Main", audio=True)
        self.tempo = 120.0
        self.signature_numerator, self.signature_denominator = 4, 4
        self.cue_points, self.current_song_time, self.is_playing = [], 0.0, False
        self.view = View()
        self.song_length = 0

    def create_midi_track(self, i):
        t = Track("MIDI")
        if i < 0:
            self.tracks.append(t)
        else:
            self.tracks.insert(i, t)

    def create_audio_track(self, i):
        t = Track("Audio", audio=True)
        if i < 0:
            self.tracks.append(t)
        else:
            self.tracks.insert(i, t)

    @property
    def tempo(self):
        return SONG_TEMPO[0]

    @tempo.setter
    def tempo(self, v):
        SONG_TEMPO[0] = v

    def delete_track(self, i):
        del self.tracks[i]

    def create_scene(self, i):
        for t in self.tracks:
            t.clip_slots.append(ClipSlot(t))

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
        self.user_library = Item("User Library", [], False)
        self.plugins = Item("Plug-Ins", [Item("Xfer Records", [Item("Serum 2")], False)], False)

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
        while True:                                      # one client after another, like the remote script
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
