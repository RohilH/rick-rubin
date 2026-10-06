"""Read Serum 2 presets as text — the agent's view of a patch.

Live exposes nothing of a plug-in's inside to scripts, and an LLM should not
have to squint at a screenshot of 200 knobs. But a `.SerumPreset` file is
readable: an `XferJson` header (name, author, description, tags) followed by a
zstd-compressed CBOR tree that stores every module's *non-default* parameters by
name. `sheet()` turns that into a one-screen patch sheet — the parts of Serum's
UI that matter: oscillators and their wavetables, filters, envelopes, LFOs, FX
rack, macros and the mod matrix. `catalog()` lists the installed presets so an
agent can pick one by folder, tag or words in its name/description.

Needs the optional dependency: `pip install "ableton-use[serum]"`.
"""
from __future__ import annotations

import json
import platform
import struct
from dataclasses import dataclass, field
from pathlib import Path

MAGIC = b"XferJson\x00"
ZSTD = b"\x28\xb5\x2f\xfd"
OSC_NAMES = {0: "OSC A", 1: "OSC B", 2: "OSC C", 3: "NOISE", 4: "SUB"}
ENGINES = {"WTOsc": "wavetable", "SampleOsc": "sample", "MultiSampleOsc": "multisample", "GranularOsc": "granular",
           "SpectralOsc": "spectral", "SubOsc": "sub", "NoiseOsc": "noise"}
FIRST_MACRO_SOURCE = 25      # mod sources 25..32 are Macro 1..8 (seen in factory presets; other source ids are not decoded)


def preset_root() -> Path:
    if platform.system() == "Windows":
        return Path.home() / "Documents" / "Xfer" / "Serum 2 Presets" / "Presets"
    return Path("/Library/Audio/Presets/Xfer Records/Serum 2 Presets/Presets")


@dataclass
class PresetInfo:
    name: str
    path: Path
    folder: str
    author: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)


def read_meta(path: str | Path) -> dict:
    """Header only (fast): presetName, presetAuthor, presetDescription, tags."""
    with open(path, "rb") as f:
        head = f.read(17)
        if head[:9] != MAGIC:
            raise ValueError(f"{path}: not a Serum 2 preset")
        return json.loads(f.read(struct.unpack("<Q", head[9:17])[0]))


def read_preset(path: str | Path) -> tuple[dict, dict]:
    """(header, full parameter tree)."""
    try:
        import cbor2
        import zstandard
    except ImportError as e:  # pragma: no cover
        raise RuntimeError('reading Serum presets needs: pip install "ableton-use[serum]"') from e
    b = Path(path).read_bytes()
    if b[:9] != MAGIC:
        raise ValueError(f"{path}: not a Serum 2 preset")
    n = struct.unpack("<Q", b[9:17])[0]
    meta = json.loads(b[17:17 + n])
    rest = b[17 + n:]
    i = rest.find(ZSTD)
    if i < 0:
        raise ValueError(f"{path}: no compressed payload")
    return meta, cbor2.loads(zstandard.ZstdDecompressor().decompress(rest[i:], max_output_size=200_000_000))


def catalog(root: str | Path | None = None, search: str | None = None, tag: str | None = None,
            folder: str | None = None) -> list[PresetInfo]:
    """Installed presets, filtered by words (all must appear in name/description/author/folder), tag and folder."""
    root = Path(root) if root else preset_root()
    words = (search or "").lower().split()
    out = []
    for p in sorted(root.rglob("*.SerumPreset")):
        try:
            m = read_meta(p)
        except (ValueError, OSError, json.JSONDecodeError):
            continue
        rel = p.relative_to(root)
        info = PresetInfo(m.get("presetName") or p.stem, p, str(rel.parent) if rel.parent != Path(".") else "",
                          m.get("presetAuthor", ""), m.get("presetDescription", ""),
                          [t for t in m.get("tags", []) if t != "Preview"])
        hay = " ".join([info.name, info.description, info.author, info.folder]).lower()
        if any(w not in hay for w in words):
            continue
        if tag and tag.lower() not in [t.lower() for t in info.tags]:
            continue
        if folder and folder.lower() not in info.folder.lower():
            continue
        out.append(info)
    return out


def find(name: str, root: str | Path | None = None) -> Path:
    """A preset by path, exact name, or unique words."""
    p = Path(name).expanduser()
    if p.exists():
        return p
    hits = catalog(root, search=name)
    exact = [h for h in hits if h.name.lower() == name.lower()]
    if len(exact) == 1 or (exact and not hits):
        return exact[0].path
    if len(hits) == 1:
        return hits[0].path
    if not hits:
        raise FileNotFoundError(f"no Serum preset matches {name!r}")
    raise ValueError(f"{len(hits)} presets match {name!r}: " + ", ".join(h.name for h in hits[:12]) + (" ..." if len(hits) > 12 else ""))


# ---------------------------------------------------------------------------- patch sheet
def _v(x) -> str:
    if isinstance(x, bool):
        return "on" if x else "off"
    if isinstance(x, float):
        return f"{x:.0f}" if abs(x) >= 100 else f"{x:.3g}"
    s = str(x)
    return s[1:] if len(s) > 1 and s[0] == "k" and s[1].isupper() else s


def _params(d, skip: tuple[str, ...] = ()) -> str:
    pp = d.get("plainParams") if isinstance(d, dict) else None
    if not isinstance(pp, dict):
        return ""
    return ", ".join(f"{k[6:] if k.startswith('kParam') else k} {_v(v)}" for k, v in pp.items()
                     if not k.startswith("kUIParam") and k not in skip)


def _numbered(tree: dict, prefix: str) -> list[tuple[int, dict]]:
    out = []
    for k, v in tree.items():
        if k.startswith(prefix) and k[len(prefix):].isdigit() and isinstance(v, dict):
            out.append((int(k[len(prefix):]), v))
    return sorted(out)


def sheet(path: str | Path) -> str:
    """One-screen text view of a patch. Only what differs from Serum's init patch is
    listed (that is how the file stores it), so a short sheet is a simple patch."""
    meta, t = read_preset(path)
    L = [f"# {meta.get('presetName') or Path(path).stem} — Serum 2 preset",
         " · ".join(x for x in (f"by {meta['presetAuthor']}" if meta.get("presetAuthor") else "",
                                "tags: " + ", ".join(g for g in meta.get("tags", []) if g != "Preview"),
                                f"\"{meta['presetDescription']}\"" if meta.get("presetDescription") else "") if x),
         "(values are Serum's own units; anything not listed is at its init value)", ""]

    L.append("## Oscillators")
    for i, o in _numbered(t, "Oscillator"):
        pp = o.get("plainParams") if isinstance(o.get("plainParams"), dict) else {}
        on = bool(pp.get("kParamEnable", 1.0 if i == 0 else 0.0))       # init patch: only OSC A is on
        bits = []
        for k, v in o.items():
            eng = next((nm for pre, nm in ENGINES.items() if k.startswith(pre)), None)
            if eng is None or not isinstance(v, dict):
                continue
            src = v.get("relativePathToWT") or v.get("relativePathToSample") or v.get("relativePath") or ""
            own = _params(v)
            if src or own:
                bits.append(eng + (f" '{Path(str(src)).stem}'" if src else "") + (f" ({own})" if own else ""))
        own = _params(o, skip=("kParamEnable",))
        if on or own or bits:
            L.append(f"- {OSC_NAMES.get(i, f'OSC {i}')} {'ON ' if on else 'off'} " + "; ".join(x for x in (", ".join(bits), own) if x))

    filt = [(i, f) for i, f in _numbered(t, "VoiceFilter") if _params(f)]
    if filt:
        L += ["", "## Filters"] + [f"- FILTER {i + 1}: {_params(f)}" for i, f in filt]
    routes = [(i, r) for i, r in _numbered(t, "RoutingSlot") if _params(r)]
    if routes:
        L.append("- routing: " + "; ".join(f"{OSC_NAMES.get(i, i)} → {_params(r)}" for i, r in routes))

    mods = []
    for pre, label in (("Env", "ENV"), ("LFO", "LFO")):
        for i, m in _numbered(t, pre):
            own = _params(m, skip=("kParamCurve1", "kParamCurve2", "kParamCurve3", "kParamDefaultMode"))
            shape = m.get("curveData") or m.get("pathData")
            if own or shape:
                mods.append(f"- {label} {i + 1}: {own}" + (" [custom shape]" if shape else ""))
    if mods:
        L += ["", "## Envelopes and LFOs (ENV 1 is the amp envelope)"] + mods

    fx = []
    for i, rack in _numbered(t, "FXRack"):
        for unit in rack.get("FX") or []:
            for k, v in unit.items():
                if k.startswith("FX") and isinstance(v, dict):
                    fx.append(f"- {k[2:]}" + (f" (rack {i + 1})" if i else "") + (f": {_params(v)}" if _params(v) else ""))
    if fx:
        L += ["", "## FX (in order; 'Wet 0' units are switched in by a macro if one targets them)"] + fx

    macros = {i: m for i, m in _numbered(t, "Macro")}
    targets: dict[int, list[str]] = {}
    matrix = []
    for i, s in _numbered(t, "ModSlot"):
        src = (s.get("source") or [None])[0]
        if src is None or not s.get("destModuleTypeString"):
            continue                                   # unused slot
        dest = f"{s.get('destModuleTypeString', '?')}{s.get('destModuleID', '')}.{str(s.get('destModuleParamName', '?')).replace('kParam', '')}"
        amt = (s.get("plainParams") or {}).get("kParamAmount") if isinstance(s.get("plainParams"), dict) else None
        line = f"{dest} {amt:+.0f}" if isinstance(amt, (int, float)) else dest
        if isinstance(src, int) and FIRST_MACRO_SOURCE <= src < FIRST_MACRO_SOURCE + 8:
            targets.setdefault(src - FIRST_MACRO_SOURCE, []).append(line)
        else:
            matrix.append(f"- source #{src} → {line}")
    if macros or targets:
        L += ["", "## Macros (what the eight knobs do)"]
        for i in sorted(set(macros) | set(targets)):
            m = macros.get(i, {})
            val = (m.get("plainParams") or {}).get("kParamValue") if isinstance(m.get("plainParams"), dict) else None
            L.append(f"- Macro {i + 1} '{m.get('name', '')}'" + (f" at {val:.0f}%" if isinstance(val, (int, float)) else "")
                     + (" → " + "; ".join(targets[i]) if i in targets else ""))
    if matrix:
        L += ["", "## Other modulation (source ids are Serum's internal numbers)"] + matrix

    glob = "; ".join(x for x in (_params(g) for _, g in _numbered(t, "Global")) if x)
    if glob:
        L += ["", "## Global", "- " + glob]
    return "\n".join(L) + "\n"


# ============================================================================ playing Serum without its window
# Serum's plug-in state uses the same container as its preset files (an XferJson header whose
# "hash" is the MD5 of the zstd block, then a zstd-compressed CBOR tree), split in two: a
# "processor" tree with every module's parameters and a "controller" tree with UI state and the
# preset's name. So a .SerumPreset can be turned into a plug-in state directly. Hosting the VST3
# in-process (pedalboard) then gives a Serum that loads any preset, takes any of its ~2600
# parameters by name, and renders MIDI to audio offline — no Live, no clicking.
VST3_PATH = Path("/Library/Audio/Plug-Ins/VST3/Serum2.vst3")
_JUCE64 = ".ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+"


def _juce_decode(s: str) -> bytes:
    n, _, data = s.partition(".")
    bits = 0
    for i, ch in enumerate(data):
        bits |= _JUCE64.index(ch) << (6 * i)
    return (bits & ((1 << (8 * int(n))) - 1)).to_bytes(int(n), "little")


def _juce_encode(data: bytes) -> str:
    bits = int.from_bytes(data, "little")
    return f"{len(data)}." + "".join(_JUCE64[(bits >> (6 * i)) & 63] for i in range((len(data) * 8 + 5) // 6))


def _unpack(blob: bytes) -> tuple[dict, dict]:
    import cbor2
    import zstandard
    n = struct.unpack("<Q", blob[9:17])[0]
    return json.loads(blob[17:17 + n]), cbor2.loads(zstandard.ZstdDecompressor().decompress(blob[17 + n + 8:], max_output_size=200_000_000))


def _pack(meta: dict, tree: dict) -> bytes:
    import hashlib
    import cbor2
    import zstandard
    raw = cbor2.dumps(tree)
    z = zstandard.ZstdCompressor(level=3).compress(raw)
    j = json.dumps(dict(meta, hash=hashlib.md5(z).hexdigest()), separators=(",", ":")).encode()
    return MAGIC + struct.pack("<Q", len(j)) + j + struct.pack("<II", len(raw), 2) + z


def split_state(raw_state: bytes) -> tuple[bytes, bytes]:
    """(processor blob, controller blob) from a hosted Serum's raw VST3 state."""
    import re
    xml = raw_state[8:].split(b"\x00")[0].decode()
    return (_juce_decode(re.search(r"<IComponent>(.*?)</IComponent>", xml).group(1)),
            _juce_decode(re.search(r"<IEditController>(.*?)</IEditController>", xml).group(1)))


def join_state(comp: bytes, cont: bytes) -> bytes:
    xml = ('<?xml version="1.0" encoding="UTF-8"?> <VST3PluginState><IComponent>' + _juce_encode(comp) +
           "</IComponent><IEditController>" + _juce_encode(cont) + "</IEditController></VST3PluginState>").encode()
    return b"VC2!" + struct.pack("<I", len(xml) + 1) + xml + b"\x00"


def preset_state(preset: str | Path, init_state: bytes) -> bytes:
    """The plug-in state that makes Serum sound like `preset`, built on a fresh instance's own state."""
    comp0, cont0 = split_state(init_state)
    (cm, ct), (km, kt) = _unpack(comp0), _unpack(cont0)
    pm, pt = read_preset(preset)
    comp_tree = {k: v for k, v in pt.items() if k in ct or k not in kt}
    for k in ("fileType", "presetAuthor", "presetDescription", "presetName"):
        comp_tree.pop(k, None)
    comp_tree["component"] = "processor"
    cont_tree = dict(kt)
    cont_tree.update({k: v for k, v in pt.items() if k in kt})
    cont_tree["component"] = "controller"
    ver = {"version": pm.get("version", cm.get("version")), "productVersion": pm.get("productVersion", cm.get("productVersion"))}
    names = {"presetName": pm.get("presetName", Path(preset).stem), "presetAuthor": pm.get("presetAuthor", ""),
             "presetDescription": pm.get("presetDescription", "")}
    return join_state(_pack(dict(cm, **ver), comp_tree), _pack(dict(km, **ver, **names), cont_tree))


class SerumHost:
    """One in-process Serum 2. Loading the plug-in takes a few seconds, so reuse the instance (`SerumHost.get()`)."""
    _shared: "SerumHost | None" = None

    def __init__(self, vst3: str | Path = VST3_PATH):
        try:
            import pedalboard
        except ImportError as e:  # pragma: no cover
            raise RuntimeError('playing Serum needs: pip install "ableton-use[serum]"') from e
        if not Path(vst3).exists():
            raise FileNotFoundError(f"Serum 2 VST3 not found at {vst3}")
        self.plugin = pedalboard.load_plugin(str(vst3), plugin_name="Serum 2")
        self.init_state = bytes(self.plugin.raw_state)
        self.loaded: str | None = None

    @classmethod
    def get(cls) -> "SerumHost":
        if cls._shared is None:
            cls._shared = cls()
        return cls._shared

    def load(self, preset: str | Path | None, root: str | Path | None = None) -> str:
        """Load a preset by name, words or path (None = the init patch). Returns the preset's name."""
        if preset is None:
            self.plugin.raw_state = self.init_state
            self.loaded = None
            return "- Init -"
        path = find(str(preset), root)
        self.plugin.raw_state = preset_state(path, self.init_state)
        self.loaded = str(path)
        return read_meta(path).get("presetName") or path.stem

    def params(self, search: str | None = None) -> list[tuple[str, str, tuple]]:
        """(name, current value as shown, (min, max)) for parameters whose name contains `search`."""
        out = []
        for name, prm in self.plugin.parameters.items():
            if search and search.lower() not in name.lower():
                continue
            out.append((name, str(prm.string_value).strip(), (prm.min_value, prm.max_value)))
        return out

    def set(self, values: dict | None) -> None:
        """Set parameters by name, e.g. {"macro_1": 60, "filter_1_freq_hz": 800, "env_1_release": 0.3}."""
        for k, v in (values or {}).items():
            if k not in self.plugin.parameters:
                near = [n for n in self.plugin.parameters if k.split("_")[0] in n][:12]
                raise KeyError(f"Serum has no parameter {k!r}" + (f"; similar: {', '.join(near)}" if near else ""))
            setattr(self.plugin, k, v)

    def render(self, notes: list[tuple[int, float, float, int]], seconds: float, sr: int = 44100):
        """Audio (n, 2) for notes [(midi pitch, start_s, length_s, velocity)]. Pitches are Ableton's numbers (C3 = 60)."""
        import numpy as np
        from mido import Message
        ev = []
        for pitch, start, dur, vel in notes:
            ev.append((max(0.0, start), 1, Message("note_on", note=int(pitch), velocity=int(max(1, min(127, vel))))))
            ev.append((max(0.0, start + dur), 0, Message("note_off", note=int(pitch))))
        msgs = []
        for t, _, m in sorted(ev, key=lambda e: (e[0], e[1])):          # at equal times, note-offs first
            msgs.append(m.copy(time=t))
        audio = self.plugin(msgs, duration=float(seconds), sample_rate=sr, reset=True)
        return np.ascontiguousarray(audio.T, dtype=np.float32)


def render_preset(preset: str | Path | None, notes: list[tuple[int, float, float, int]], seconds: float,
                  params: dict | None = None, sr: int = 44100, root: str | Path | None = None):
    """Load a preset, set parameters, render the notes. Returns (preset name, audio (n, 2))."""
    host = SerumHost.get()
    name = host.load(preset, root)
    host.set(params)
    return name, host.render(notes, seconds, sr)


def write_vstpreset(preset: str | Path, dst: str | Path, params: dict | None = None) -> Path:
    """A standard VST3 preset file carrying this Serum preset — for hosts that load .vstpreset files."""
    host = SerumHost.get()
    host.load(preset)
    host.set(params)
    comp, cont = split_state(bytes(host.plugin.raw_state))
    head = 48
    lst = b"List" + struct.pack("<i", 2) + b"Comp" + struct.pack("<qq", head, len(comp)) + b"Cont" + struct.pack("<qq", head + len(comp), len(cont))
    Path(dst).write_bytes(b"VST3" + struct.pack("<i", 1) + b"56534558667350736572756D20320000" + struct.pack("<q", head + len(comp) + len(cont)) + comp + cont + lst)
    return Path(dst)


def track_stem(song, track, clips) -> Path:
    """The whole song's worth of one Serum track, rendered through the plug-in: every note of the
    track's clips, the preset named in `track.serum`, parameters from `track.serum_params`. The file
    is exactly the song's length and cached in <project>/serum/ by content, so unchanged tracks
    are not rendered twice."""
    import hashlib
    import numpy as np
    from .samples import write_wav24
    spb = 60.0 / song.bpm
    notes = sorted((n.pitch, round((c.start + n.start) * spb, 6), round(n.dur * spb, 6), n.vel)
                   for c in clips if c.track == track.name for n in c.notes)
    path = find(track.serum)
    sig = hashlib.sha1(json.dumps([str(path), path.stat().st_mtime, track.serum_params, notes, song.bpm, song.total_bars],
                                  sort_keys=True, default=str).encode()).hexdigest()[:10]
    base = Path(song.base_dir) if song.base_dir is not None else Path(".")
    out = base / "serum" / f"{track.name}.{sig}.wav"
    if out.exists():
        return out
    sr = 44100
    total = song.total_bars * 4 * spb
    _, audio = render_preset(path, notes, total, track.serum_params, sr)
    audio = audio[: int(round(total * sr))]
    f = int(0.005 * sr)
    audio[-f:] *= np.linspace(1, 0, f, dtype=np.float32)[:, None]
    out.parent.mkdir(parents=True, exist_ok=True)
    for old in out.parent.glob(f"{track.name}.*.wav"):               # one current stem per track
        old.unlink()
    write_wav24(out, sr, audio)
    return out


# ============================================================================ searchable index of presets
INDEX_NOTE = 48          # C2: every preset is played on the same key, so octave differences between patches show up
INDEX_VERSION = 2


def index_path() -> Path:
    """Where the preset index lives: inside this repo's (git-ignored) .cache folder."""
    return Path(__file__).resolve().parent.parent / ".cache" / "serum-index.json"


def _patch_facts(tree: dict) -> dict:
    """Searchable facts read straight from the patch: voices, oscillator engines, FX, macro names."""
    engines, fx, macros = set(), [], []
    for i, o in _numbered(tree, "Oscillator"):
        pp = o.get("plainParams") if isinstance(o.get("plainParams"), dict) else {}
        if not pp.get("kParamEnable", 1.0 if i == 0 else 0.0):
            continue
        if i == 4:
            engines.add("sub")
        elif i == 3:
            engines.add("noise")
        else:
            used = [nm for pre, nm in ENGINES.items() for k, v in o.items() if k.startswith(pre) and isinstance(v, dict)
                    and (v.get("plainParams") != "default" or v.get("relativePathToWT") or v.get("relativePathToSample"))]
            engines.update(used or ["wavetable"])
    for _, rack in _numbered(tree, "FXRack"):
        for unit in rack.get("FX") or []:
            fx += [k[2:].lower() for k, v in unit.items() if k.startswith("FX") and isinstance(v, dict)]
    for _, m in _numbered(tree, "Macro"):
        if m.get("name"):
            macros.append(str(m["name"]).lower())
    glob = next((g.get("plainParams") for _, g in _numbered(tree, "Global") if isinstance(g.get("plainParams"), dict)), {}) or {}
    return {"voices": "mono" if glob.get("kParamMonoToggle") else "poly", "engines": sorted(engines), "fx": fx, "macros": macros}


def _index_worker(conn) -> None:
    """Child process: plays presets it is sent and returns their measurements. Lives in its own process so a
    preset whose render never returns can be killed without losing the whole build."""
    from .samples import describe_audio, jsonable
    host = SerumHost()
    conn.send(("ready", None))
    while True:
        path = conn.recv()
        if path is None:
            return
        try:
            _, tree = read_preset(path)
            host.load(path)
            audio = host.render([(INDEX_NOTE, 0.0, 1.0, 100)], 2.5)
            d = jsonable(describe_audio(44100, audio, Path(path).stem))
            d.update(_patch_facts(tree))
            conn.send(("ok", d))
        except Exception as e:  # noqa: BLE001
            conn.send(("error", f"{type(e).__name__}: {e}"))


def build_index(root: str | Path | None = None, progress=None, limit: int | None = None, timeout_s: float = 30.0) -> dict:
    """Play every installed preset once (a 1 s C2) through the hosted plug-in and record what it sounds
    like — attack, decay, brightness, low-end share, width, the pitch that actually comes out — next to
    its folder, tags, description and patch facts. Later runs only render presets that are new or changed;
    the file is saved as it goes; a preset that does not render within `timeout_s` is skipped and noted."""
    import multiprocessing as mp
    from .theory import name as pitch_name
    path = index_path()
    old = {}
    if path.exists():
        data = json.loads(path.read_text())
        if data.get("version") == INDEX_VERSION:
            old = data.get("presets", {})
    out: dict[str, dict] = {}
    todo = catalog(root)[:limit]

    def save(presets: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps({"version": INDEX_VERSION, "note": INDEX_NOTE, "presets": presets}) + "\n")
        tmp.replace(path)

    ctx = mp.get_context("spawn")
    worker = None
    conn = None

    def start():
        nonlocal worker, conn
        conn, child = ctx.Pipe()
        worker = ctx.Process(target=_index_worker, args=(child,), daemon=True)
        worker.start()
        if not conn.poll(120) or conn.recv()[0] != "ready":
            raise RuntimeError("the Serum host did not start")

    def stop():
        nonlocal worker
        if worker is not None and worker.is_alive():
            worker.kill()
            worker.join(5)
        worker = None

    try:
        for n, info in enumerate(todo):
            key = str(info.path)
            mt = round(info.path.stat().st_mtime, 3)
            if key in old and old[key].get("mtime") == mt:
                out[key] = old[key]
                continue
            base = {"name": info.name, "folder": info.folder, "tags": info.tags, "author": info.author,
                    "description": info.description, "mtime": mt, "played": pitch_name(INDEX_NOTE)}
            if worker is None:
                start()
            conn.send(key)
            if conn.poll(timeout_s):
                status, d = conn.recv()
                out[key] = {**d, **base, "silent": d["peak_db"] < -70} if status == "ok" else {**base, "error": d}
            else:                                          # stuck: kill it, note it, carry on with a fresh host
                stop()
                out[key] = {**base, "error": f"did not render within {timeout_s:g} s"}
            if progress and (n % 25 == 0 or n == len(todo) - 1):
                progress(f"{n + 1}/{len(todo)} {info.name}")
            if n % 40 == 39:
                save({**old, **out})
    finally:
        if worker is not None and worker.is_alive():
            try:
                conn.send(None)
                worker.join(3)
            except Exception:  # noqa: BLE001
                pass
            stop()
    save(out)
    return out


def load_index() -> dict[str, dict] | None:
    path = index_path()
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    return data.get("presets") if data.get("version") == INDEX_VERSION else None


def search(words: list[str] | None = None, folder: str | None = None, tag: str | None = None, sort: str | None = None,
           like: str | None = None, limit: int = 25) -> list[tuple[str, dict]]:
    """Presets from the index matching all `words` — which may come from the name, description, author, folder,
    tags, measured character (snappy, dark, subby, wide, sustained ...), voices (mono/poly), oscillator engines,
    FX names or macro names; '-word' excludes. `like` ranks by closeness in sound to that preset."""
    from .samples import search_rows, similar
    idx = load_index()
    if idx is None:
        raise FileNotFoundError("no Serum index yet — run `ableton-use serum index` once (a few minutes)")
    rows = {k: d for k, d in idx.items() if "error" not in d and not d.get("silent")}
    if folder:
        rows = {k: d for k, d in rows.items() if folder.lower() in d["folder"].lower()}
    if tag:
        rows = {k: d for k, d in rows.items() if tag.lower() in [t.lower() for t in d["tags"]]}
    extra = {k: " ".join([d["name"], d["folder"], d.get("author", ""), d.get("description", ""), " ".join(d["tags"]), d["voices"],
                          " ".join(d["engines"]), " ".join(d["fx"]), " ".join(d["macros"])]) for k, d in rows.items()}
    hits = dict(search_rows(rows, words, sort, extra))
    if like:
        target_path = str(find(like))
        target = idx.get(target_path)
        if target is None or "error" in target:
            raise KeyError(f"{like!r} is not in the index (yet) — run `ableton-use serum index`, or it did not render")
        return [(k, d) for k, d, _ in similar({k: d for k, d in hits.items() if k != target_path}, target, limit)]
    return list(hits.items())[:limit]
