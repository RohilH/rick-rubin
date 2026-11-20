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
    region: str = ""                     # the name of the track's (first) region

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

    # ---- what a session reads besides the strips
    def selected_tracks(self, w=None):
        return [self.fake.selected] if self.fake.selected is not None else []

    def mixer_window(self, project=None):
        return "mixer"

    def project_path(self, w=None):
        return self.fake.path


class FakeLogicBridge:
    PLUGINS = {"compressor", "channel eq", "autofilter", "limiter", "chromaverb", "tape delay", "stereo delay", "space designer", "adaptive limiter",
               "kickstart 2", "trackspacer 2.5"}
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
        self.selected: int | None = None
        self.selections: list[int] = []      # every select_track call, in order
        self.path: Path | None = None        # the saved .logicx package, when there is one
        self.alert: tuple[str, list[str]] | None = None
        self.said: list[str] = []
        self.imports: list[tuple[int, Path, int, int]] = []
        self.midi_imports: list[tuple[Path, int]] = []
        self.fader_stop: float | None = None  # a fader that will not go below this (a readback that differs)
        self.transposed: dict[str, int] = {"Bass": 12}   # Logic puts +12 on the region of a bass program

    def say(self, m):
        self.said.append(m)

    @property
    def main(self):
        return self.project

    def pending_alert(self):
        return self.alert

    def tempo(self):
        return 124.0

    def control_text(self, name):
        return {"Key Signature": "Amin", "Time Signature": "4/4"}.get(name)

    def close_plugin_windows(self):
        pass

    def rename_track(self, track_index, name):
        self._strips[track_index].name = name
        return name

    def add_instrument_track(self):
        n = len(self.tracks())
        self._strips.insert(n, FakeStrip(f"Inst {n + 1}"))
        return n

    def import_midi(self, path, bar=1):
        if not Path(path).exists():
            raise LogicError(f"{path} does not exist")
        self.midi_imports.append((Path(path), bar))
        n = len(self.tracks())
        self._strips.insert(n, FakeStrip(f"Inst {n + 1}", region=Path(path).stem))
        return [n]

    def region_transpose(self, track_index):
        return self.transposed.get(self._strip(track_index).name, 0)

    def set_transpose(self, track_index, semitones):
        self.transposed[self._strip(track_index).name] = semitones
        return semitones

    def load_setting(self, ref, path, plugin="instrument", nth=0):
        if not Path(path).exists():
            raise LogicError(f"{path} does not exist")
        self._strip(ref).params.setdefault(0, {})["setting"] = Path(path).stem
        return Path(path).stem

    def remove_plugin(self, ref, slot):
        s = self._strip(ref)
        if not 1 <= slot <= len(s.inserts):
            raise LogicError(f"no plug-in in insert {slot}")
        s.inserts.pop(slot - 1)
        return list(s.inserts)

    def clear_inserts(self, ref):
        self._strip(ref).inserts = []
        return True

    def read_plugin_params(self, track_index, slot, max_pages=40):
        s = self._strip(track_index)
        return s.inserts[slot - 1], dict(s.params.get(slot, {"Thrshld": "-20.0 dB", "Ratio": "2.0:1"}))

    def read_instrument_params(self, track_index, max_pages=40):
        return dict(self._strip(track_index).params.get(0, {"Cutoff": "50 %"}))

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
        names = self._smf_names(path)
        self._strips = [FakeStrip(f"Patch {i}", region=names[i] if i < len(names) else "") for i in range(n_tracks)]
        self.imports = []
        self.deleted: list[str] = []
        return title

    @staticmethod
    def _smf_names(path) -> list[str]:
        import struct
        data = Path(path).read_bytes()
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
        return names[1:]                                 # the first chunk is the conductor track

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
        # Logic names tracks after their regions: MIDI regions carry the MIDI track names, audio regions the file's
        for s in self._strips:
            if s.kind == "track" and s.region:
                s.name = s.region
        self.tracks_named = self.tracks()
        return self.tracks()

    def delete_track(self, index):
        t = [s for s in self._strips if s.kind == "track"][index]
        self.deleted.append(t.name)
        self._strips.remove(t)

    def add_audio_track(self):
        n = len(self.tracks())
        self._strips.insert(n, FakeStrip(f"Audio {n + 1}", instrument=None))
        return n

    def import_audio(self, track_index, path, bar, beat=1, keep_file_rate=False, **_k):
        if not Path(path).exists():
            raise LogicError(f"{path} does not exist")
        self.imports.append((track_index, Path(path), bar, beat))
        self._strips[track_index].region = self._strips[track_index].region or Path(path).stem
        return True

    def select_track(self, index):
        self.selected = index
        self.selections.append(index)

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
        if self.fader_stop is not None:
            db = max(db, self.fader_stop)
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
