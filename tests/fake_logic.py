"""A stand-in for LogicBridge: remembers what a push asked Logic to do, so push_song can be tested without
Logic Pro (the real bridge drives the app through accessibility and a Mackie Control emulation)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from rick_rubin.logic.ax import StripInfo
from rick_rubin.logic.bridge import LogicError, ParamReport


@dataclass
class FakeStrip:
    name: str
    kind: str = "track"
    volume: float = 0.0
    pan: int = 0
    mute: bool = False
    solo: bool = False
    inserts: list[str] = field(default_factory=list)
    instrument: str | None = "ES2"
    sends: dict[int, float] = field(default_factory=dict)
    side_chains: dict[int, str] = field(default_factory=dict)
    params: dict[int, dict] = field(default_factory=dict)

    def info(self, i: int) -> StripInfo:
        return StripInfo(i, self.name, f"{self.volume:.1f} dB", str(self.pan), self.mute, self.solo, list(self.inserts), self.instrument,
                         [f"Bus {b}" for b in sorted(self.sends)], "Stereo Output", "Read", self.kind)


class _App:
    def __init__(self, fake):
        self.fake = fake

    def project_windows(self):
        return list(self.fake.projects)

    def project_title(self, w):
        return w

    def main_window(self, title=None):
        return title if title in self.fake.projects else None


class FakeLogicBridge:
    PLUGINS = {"compressor", "channel eq", "autofilter", "limiter", "chromaverb", "tape delay", "stereo delay", "space designer", "adaptive limiter"}
    INSTRUMENTS = {"retro synth", "alchemy", "es2", "quick sampler", "drum machine designer", "serum 2"}

    def __init__(self):
        self.projects: list[str] = []
        self.project: str | None = None
        self._strips: list[FakeStrip] = []
        self.tracks_named: list[str] = []
        self.opened: list[Path] = []
        self.saved: list[Path] = []
        self.closed: list[str] = []
        self.patches: list[tuple[int, str]] = []
        self.playhead = (1, 1)
        self.app = _App(self)
        self.n = 0

    # ---- lifecycle / projects
    def ping(self):
        return {"logic_version": "11.2 (fake)", "mcu": True, "project": self.project}

    def open_midi_project(self, path, expect_tracks=None, close_ours=True, ours=()):
        from rick_rubin.render.midi import read_midi_notes
        self.opened.append(Path(path))
        self.n += 1
        title = f"Untitled {self.n}"
        self.projects.append(title)
        self.project = title
        notes = read_midi_notes(path)
        n_tracks = max(t for t, *_ in notes) if notes else 0
        self._strips = [FakeStrip(f"Patch {i}") for i in range(n_tracks)]
        self._region_names = []
        return title

    def close_project(self, title=None, save=False):
        t = title or self.project
        self.closed.append(t)
        if t in self.projects:
            self.projects.remove(t)
        return True

    def save_project_as(self, folder, name):
        p = Path(folder) / f"{name}.logicx"
        self.saved.append(p)
        self.projects[self.projects.index(self.project)] = name
        self.project = name
        return p

    def tracks(self):
        return [s.name for s in self._strips if s.kind == "track"]

    def name_tracks_by_regions(self):
        # Logic names tracks after their regions, which carry the MIDI track names
        import struct
        data = self.opened[-1].read_bytes()
        names, pos = [], 14
        ntrk = struct.unpack(">H", data[10:12])[0]
        for _ in range(ntrk):
            ln = struct.unpack(">I", data[pos + 4:pos + 8])[0]
            chunk = data[pos + 8:pos + 8 + ln]
            i = chunk.find(b"\xff\x03")
            if i >= 0:
                n = chunk[i + 2]
                names.append(chunk[i + 3:i + 3 + n].decode())
            pos += 8 + ln
        for s, nm in zip(self._strips, names[1:]):
            s.name = nm
        self.tracks_named = list(names[1:])
        return self.tracks()

    def select_track(self, index):
        self.selected = index

    # ---- strips
    def _strip(self, ref) -> FakeStrip:
        if isinstance(ref, str):
            for s in self._strips:
                if s.name == ref:
                    return s
            raise LogicError(f"no strip {ref!r}")
        if ref >= len(self._strips):
            raise LogicError(f"no strip #{ref + 1}")
        return self._strips[ref]

    def strip(self, ref):
        return self._strip(ref)

    def strips(self):
        return [s.info(i) for i, s in enumerate(self._strips)]

    def strip_info(self, ref):
        s = self._strip(ref)
        return s.info(self._strips.index(s))

    def set_volume(self, ref, db):
        self._strip(ref).volume = round(db, 1)
        return f"{round(db, 1):.1f} dB"

    def set_pan(self, ref, pan):
        self._strip(ref).pan = round(pan * 64)
        return str(round(pan * 64))

    def set_mute(self, ref, on):
        self._strip(ref).mute = on
        return on

    def set_solo(self, ref, on):
        self._strip(ref).solo = on
        return on

    def insert_plugin(self, ref, name, view="tracks", index=None):
        if name.lower() not in self.PLUGINS:
            raise LogicError(f"no plug-in {name!r} in Logic's list")
        s = self._strip(ref)
        s.inserts.append(name)
        return name

    def load_instrument(self, ref, name, index=None):
        if name.lower() not in self.INSTRUMENTS:
            raise LogicError(f"no instrument {name!r}")
        self._strip(ref).instrument = name
        return name

    def load_patch(self, track_index, query):
        self.patches.append((track_index, query))
        s = self._strip(track_index)
        s.instrument = "Alchemy"
        return {"query": query, "loaded": True, "instrument": "Alchemy", "inserts": s.inserts}

    def set_plugin_params(self, track_index, slot, params, view="tracks"):
        s = self._strip(track_index)
        rep = ParamReport()
        for k, v in params.items():
            if k == "Nope":
                rep.errors.append("no parameter 'Nope'")
            else:
                rep.set[k] = f"{v}"
        s.params.setdefault(slot, {}).update(rep.set)
        return rep

    def set_instrument_params(self, track_index, params, instrument=""):
        rep = ParamReport()
        for k, v in params.items():
            rep.set[k] = f"{v}"
        self._strip(track_index).params.setdefault(0, {}).update(rep.set)
        return rep

    def set_side_chain(self, ref, plugin, source, nth=0):
        s = self._strip(ref)
        if source not in self.tracks():
            raise LogicError(f"no side chain source {source!r}")
        s.side_chains[nth] = source
        return f"{source} (Inst {self.tracks().index(source) + 1})"

    def set_send(self, track_index, bus, db, slot=1):
        s = self._strip(track_index)
        if db is None:
            s.sends.pop(bus, None)
            return "off"
        s.sends[bus] = db
        if not any(x.name == f"Aux {bus}" for x in self._strips):
            self._strips.append(FakeStrip(f"Aux {bus}", kind="aux", instrument=None))
        if not any(x.kind == "output" for x in self._strips):
            self._strips.append(FakeStrip("Stereo Out", kind="output", instrument=None))
        return f"{db:.1f} dB"

    def set_playhead(self, bar, beat=1):
        self.playhead = (bar, beat)
        return self.playhead

    def write_fader_automation(self, *a, **k):
        return 1

    def bounce(self, out_path, start_bar, end_bar, **k):
        from rick_rubin.samples import write_wav24
        import numpy as np
        out = Path(out_path)
        write_wav24(out, 44100, np.zeros((44100, 2), np.float32))
        return out
