"""A Serum 2 patch as data: read it, change it by producer-facing keys, save it as a real `.SerumPreset`.

    p = Patch.open("BS Gunman Reese")             # a preset by name/words/path; Patch.open(None) is Serum's init patch
    p.apply({"osc_a.detune": 0.18, "filter_1.cutoff_hz": 800, "env_2.attack_ms": 40})
    p.add_fx("distortion", params={"drive": 35, "mode": "TapeSat"})
    p.add_mod("lfo_1", "filter_1.cutoff_hz", 25)
    p.save("songs/x/serum/presets/night-bass-round.SerumPreset", name="night-bass-round")

The keys, units and ranges are `serum_params`' (`rick-rubin serum params --group filter`). Edits go into the same
tree Serum stores in its preset files, so the result opens in Serum's own UI and renders through the hosted
plug-in exactly as saved (`SerumHost.load_patch`). Nothing here chooses a sound: the agent writes the settings.
"""
from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Any

from . import serum_params as sp

SHAPES_DIR = "LFO Shapes"


def _module(tree: dict, path: str, create: bool = True) -> dict | None:
    d: Any = tree
    for part in path.split("/"):
        if not isinstance(d, dict):
            return None
        if part not in d:
            if not create:
                return None
            d[part] = {"plainParams": {}}
        d = d[part]
    return d if isinstance(d, dict) else None


def _plain(mod: dict) -> dict:
    pp = mod.get("plainParams")
    if not isinstance(pp, dict):                 # Serum writes the string "default" for an untouched module
        pp = {}
        mod["plainParams"] = pp
    return pp


def _num_id(name: str) -> tuple[str, int]:
    m = re.fullmatch(r"([A-Za-z]+?)(\d+)", name)
    if not m:
        raise ValueError(f"cannot address module {name!r} in the mod matrix")
    return m.group(1), int(m.group(2))


def _fx_key(key: str) -> tuple[int, str, int, str] | None:
    """'fx.reverb#2.wet' -> (rack 0, 'reverb', 2nd, 'wet'); 'fx_bus1.delay.wet' -> (rack 1, 'delay', 1st, 'wet')."""
    m = re.fullmatch(r"fx(?:_bus([12]))?\.([a-z0-9_]+)(?:#(\d+))?\.([a-z0-9_]+)", key.strip())
    if not m:
        return None
    return (int(m.group(1) or 0), m.group(2), int(m.group(3) or 1), m.group(4))


def shape_points(text: str) -> dict:
    """'0:0,0.5:1,1:0' (x 0..1, y 0..1 with 1 = top) -> Serum's curveData (its y axis runs top = 0)."""
    pts = []
    for part in re.split(r"[,\s]+", text.strip()):
        if part:
            x, _, y = part.partition(":")
            pts.append((float(x), float(y)))
    if len(pts) < 2 or any(not (0 <= x <= 1 and 0 <= y <= 1) for x, y in pts):
        raise ValueError("an LFO shape needs at least two x:y points with x and y in 0..1")
    pts.sort(key=lambda p: p[0])
    xs = [x for x, _ in pts] + [1.0]
    ys = [1.0 - y for _, y in pts] + [1.0 - pts[0][1]]
    return {"curveVals": [0.5] * len(xs), "numPoints": len(pts), "xVals": xs, "yVals": ys}


def find_shape(name: str) -> Path:
    from .serum import preset_root
    root = preset_root().parent / SHAPES_DIR
    want = name.lower().removesuffix(".xfershape")
    hits = [p for p in root.rglob("*.XferShape") if str(p.relative_to(root)).lower().removesuffix(".xfershape") == want
            or p.stem.lower() == want.split("/")[-1]]
    if not hits:
        raise FileNotFoundError(f"no LFO shape {name!r} under {root} (e.g. Basic/Sine, Basic/Saw Down, Basic/Triangle, Sidechain/SC1)")
    return hits[0]


class Patch:
    """A preset's header and parameter tree, edited in place."""

    def __init__(self, meta: dict, tree: dict, source: str | None = None):
        self.meta = meta
        self.tree = tree
        self.source = source
        self.log: list[str] = []

    # ------------------------------------------------------------------ open
    @classmethod
    def open(cls, preset: str | Path | None, root: str | Path | None = None) -> Patch:
        from . import serum
        if preset is None or str(preset).strip().lower() in ("init", "- init -"):
            return cls.init()
        path = serum.find(str(preset), root)
        meta, tree = serum.read_preset(path)
        return cls(meta, tree, str(path))

    @classmethod
    def init(cls) -> Patch:
        """Serum's init patch, as a preset tree (read from a fresh hosted instance)."""
        from . import serum
        host = serum.SerumHost.get()
        comp, cont = serum.split_state(host.init_state)
        (cm, ct), (_, kt) = serum._unpack(comp), serum._unpack(cont)
        tree = {k: v for k, v in kt.items() if k not in ("component",)}
        tree.update({k: v for k, v in ct.items() if k != "component"})
        tree.update({"fileType": "SerumPreset", "presetName": "Init", "presetAuthor": "", "presetDescription": ""})
        meta = {"fileType": "SerumPreset", "presetAuthor": "", "presetDescription": "", "presetName": "Init", "product": cm.get("product", "Serum2"),
                "productVersion": cm.get("productVersion"), "tags": [], "url": cm.get("url", ""), "vendor": cm.get("vendor", "Xfer Records"),
                "version": cm.get("version")}
        return cls(meta, copy.deepcopy(tree), None)

    def copy(self) -> Patch:
        p = Patch(copy.deepcopy(self.meta), copy.deepcopy(self.tree), self.source)
        p.log = list(self.log)
        return p

    @property
    def name(self) -> str:
        return self.meta.get("presetName") or (Path(self.source).stem if self.source else "Init")

    # ------------------------------------------------------------------ plain settings
    def get(self, key: str) -> Any:
        fx = _fx_key(key)
        if fx:
            unit = self._fx_unit(fx[0], fx[1], fx[2])
            if unit is None:
                return None
            kp, conv = self._fx_param(fx[1], fx[3])
            v = _plain(unit[1]).get(kp)
            return conv.from_tree(v) if v is not None else None
        p = sp.lookup(key)
        mod = _module(self.tree, p.module, create=False)
        if mod is None:
            return p.init
        if p.field == "curveData":
            return mod.get("curveDisplayName") or ("custom" if mod.get("curveData") else p.init)
        if p.field:
            return mod.get(p.field, p.init)
        pp = mod.get("plainParams")
        v = pp.get(p.kparam) if isinstance(pp, dict) else None
        return p.conv.from_tree(v) if v is not None else p.init

    def set(self, key: str, value: Any) -> None:
        if key in ("mod", "mods"):
            for m in value if isinstance(value, list) else [value]:
                self.add_mod(**m) if isinstance(m, dict) else self.add_mod(*parse_mod(m))
            return
        fx = _fx_key(key)
        if fx:
            unit = self._fx_unit(fx[0], fx[1], fx[2])
            if unit is None:
                raise KeyError(f"{key}: the patch has no {fx[1]}" + (f" #{fx[2]}" if fx[2] > 1 else "") + f" in {'the main FX rack' if not fx[0] else f'FX bus {fx[0]}'} — "
                               f"add it first (--fx-add {fx[1]}{':bus' + str(fx[0]) if fx[0] else ''}); it has: {', '.join(u for u, *_ in self.fx()) or 'no FX'}")
            kp, conv = self._fx_param(fx[1], fx[3])
            _plain(unit[1])[kp] = conv.to_tree(value)
            self.log.append(f"{key}={value}")
            return
        p = sp.lookup(key)
        mod = _module(self.tree, p.module)
        if mod is None:
            raise KeyError(f"{key}: the patch tree has no {p.module}")
        if p.field == "relativePathToWT":
            from .serum import preset_root
            rel = str(value).strip()
            if not (preset_root().parent / "Tables" / rel).exists():
                hits = [q for q in (preset_root().parent / "Tables").rglob("*.wav") if q.stem.lower() == Path(rel).stem.lower()]
                if not hits:
                    raise FileNotFoundError(f"no wavetable {rel!r} under Serum's Tables folder (`rick-rubin serum tables`)")
                rel = str(hits[0].relative_to(preset_root().parent / "Tables"))
            mod["relativePathToWT"] = rel
            for k in ("numFrames", "numChannels", "sampleRate", "flex"):     # Serum re-reads them from the file
                mod.pop(k, None)
            mod.pop("embeddedWT", None)
        elif p.field == "curveData":
            if re.match(r"^\s*[\d.]+\s*:", str(value)):
                mod["curveData"] = shape_points(str(value))
                mod["curveDisplayName"] = "Custom"
            else:
                from . import serum
                path = find_shape(str(value))
                _, t = serum.read_preset(path)
                mod["curveData"] = copy.deepcopy(t["LFO"])
                mod["curveDisplayName"] = path.stem
        elif p.field:
            mod[p.field] = str(value)
        else:
            tv = p.conv.to_tree(value)
            pp = _plain(mod)
            if tv is None:
                pp.pop(p.kparam, None)                      # the menu's init option: leave the knob untouched
            else:
                if p.lo is not None and isinstance(tv, float) and p.conv.kind == "num" and not (p.lo - 1e-9 <= tv <= p.hi + 1e-9):
                    raise ValueError(f"{key}={value}: out of range {p.lo:g}..{p.hi:g} {p.unit}")
                pp[p.kparam] = tv
        self.log.append(f"{key}={value}")

    def apply(self, settings: dict | None) -> Patch:
        for k, v in (settings or {}).items():
            self.set(k, v)
        return self

    def read(self) -> dict[str, Any]:
        """Every mapped setting the patch stores (others are at Serum's init value), in the map's units."""
        out: dict[str, Any] = {}
        for p in sp.all_params().values():
            mod = _module(self.tree, p.module, create=False)
            if mod is None:
                continue
            if p.field == "relativePathToWT":
                if mod.get(p.field) and mod[p.field] != p.init:
                    out[p.key] = mod[p.field]
            elif p.field == "curveData":
                if mod.get("curveData"):
                    out[p.key] = mod.get("curveDisplayName") or "custom"
            elif p.field:
                if mod.get(p.field):
                    out[p.key] = mod[p.field]
            else:
                pp = mod.get("plainParams")
                if isinstance(pp, dict) and p.kparam in pp:
                    out[p.key] = p.conv.from_tree(pp[p.kparam])
        return out

    # ------------------------------------------------------------------ FX rack
    def fx(self) -> list[tuple[str, int, int, dict]]:
        """[(label like 'fx.reverb' / 'fx_bus1.delay#2', rack, position, {param: value})] in rack order."""
        out = []
        units = sp.fx_units()
        by_key = {u["key"]: name for name, u in units.items()}
        for r in range(3):
            rack = self.tree.get(f"FXRack{r}") or {}
            seen: dict[str, int] = {}
            for pos, unit in enumerate(rack.get("FX") or []):
                k = next((x for x in unit if x.startswith("FX") and isinstance(unit[x], dict)), None)
                if k is None:
                    continue
                name = by_key.get(k, k.lower())
                seen[name] = seen.get(name, 0) + 1
                label = ("fx" if r == 0 else f"fx_bus{r}") + f".{name}" + (f"#{seen[name]}" if seen[name] > 1 else "")
                pp = unit[k].get("plainParams") if isinstance(unit[k].get("plainParams"), dict) else {}
                params = {}
                for kp, v in pp.items():
                    pn = sp._snake(kp)
                    _, conv = self._fx_param(name, pn, strict=False)
                    params[pn] = conv.from_tree(v)
                out.append((label, r, pos, params))
        return out

    def _fx_unit(self, rack: int, name: str, nth: int) -> tuple[int, dict] | None:
        units = sp.fx_units()
        if name not in units:
            raise KeyError(f"no FX unit {name!r}; Serum's units: {', '.join(units)}")
        key = units[name]["key"]
        n = 0
        for pos, unit in enumerate((self.tree.get(f"FXRack{rack}") or {}).get("FX") or []):
            if isinstance(unit.get(key), dict):
                n += 1
                if n == nth:
                    return pos, unit[key]
        return None

    def _fx_param(self, name: str, param: str, strict: bool = True) -> tuple[str, sp.Conv]:
        u = sp.fx_units()[name]
        d = u["params"].get(param)
        if d is None:
            if strict:
                raise KeyError(f"{name} has no parameter {param!r}; it has: {', '.join(u['params'])}")
            kp = "kParam" + "".join(w.capitalize() for w in param.split("_"))
            return kp, sp.NUM
        return d["kparam"], (sp.Conv("code", table=f"fx.{name}.{param}") if d.get("codes") else sp.NUM)

    def add_fx(self, name: str, rack: int = 0, position: int | None = None, params: dict | None = None) -> str:
        units = sp.fx_units()
        if name not in units:
            raise KeyError(f"no FX unit {name!r}; Serum's units: {', '.join(units)}")
        u = units[name]
        r = self.tree.setdefault(f"FXRack{rack}", {"FX": [], "displayName": "", "plainParams": "default"})
        chain = r.setdefault("FX", [])
        unit = {u["key"]: {"plainParams": {}}, "type": u["type"]}
        chain.insert(len(chain) if position is None else position, unit)
        nth = sum(1 for x in chain[: chain.index(unit) + 1] if isinstance(x.get(u["key"]), dict))
        label = ("fx" if rack == 0 else f"fx_bus{rack}") + f".{name}" + (f"#{nth}" if nth > 1 else "")
        self.log.append(f"+{label}")
        for k, v in (params or {}).items():
            self.set(f"{label}.{k}", v)
        return label

    def remove_fx(self, label: str) -> None:
        m = re.fullmatch(r"fx(?:_bus([12]))?\.([a-z0-9_]+)(?:#(\d+))?", label.strip())
        if not m:
            raise ValueError(f"{label!r}: name a unit like fx.reverb, fx.delay#2 or fx_bus1.chorus")
        rack, name, nth = int(m.group(1) or 0), m.group(2), int(m.group(3) or 1)
        hit = self._fx_unit(rack, name, nth)
        if hit is None:
            raise KeyError(f"the patch has no {label}")
        del self.tree[f"FXRack{rack}"]["FX"][hit[0]]
        self.log.append(f"-{label}")

    # ------------------------------------------------------------------ mod matrix
    def mods(self) -> list[dict]:
        out = []
        for i in range(64):
            s = self.tree.get(f"ModSlot{i}") or {}
            if not s.get("destModuleTypeString"):
                continue
            pp = s.get("plainParams") if isinstance(s.get("plainParams"), dict) else {}
            src = s.get("source") or [0, 0]
            out.append({"slot": i + 1, "source": sp.mod_source_name(src[0]), "aux": sp.mod_source_name(src[1]) if len(src) > 1 and src[1] else None,
                        "dest": self._dest_label(s), "amount": pp.get("kParamAmount", 0.0), "bipolar": bool(pp.get("kParamBipolar", 0))})
        return out

    def _dest_label(self, s: dict) -> str:
        t, i, kp = s.get("destModuleTypeString", "?"), s.get("destModuleID", 0), s.get("destModuleParamName", "?")
        for p in sp.all_params().values():
            last = p.module.split("/")[-1]
            if p.kparam == kp and last == f"{t}{i}":
                return p.key
        if t.startswith("FX"):
            name = next((n for n, u in sp.fx_units().items() if u["key"] == t), t.lower())
            rack, pos = divmod(int(i), 100)
            return f"{'fx' if not rack else f'fx_bus{rack}'}.{name}[{pos}].{sp._snake(kp)}"
        return f"{t}{i}.{kp}"

    def _dest(self, dest: str) -> tuple[str, int, str]:
        fx = _fx_key(dest)
        if fx:
            unit = self._fx_unit(fx[0], fx[1], fx[2])
            if unit is None:
                raise KeyError(f"{dest}: the patch has no such FX unit (add it first)")
            kp, _ = self._fx_param(fx[1], fx[3])
            return sp.fx_units()[fx[1]]["key"], fx[0] * 100 + unit[0], kp
        p = sp.lookup(dest)
        if not p.kparam:
            raise KeyError(f"{dest} cannot be modulated")
        t, i = _num_id(p.module.split("/")[-1])
        return t, i, p.kparam

    def add_mod(self, source: str | int, dest: str, amount: float, bipolar: bool = False, aux: str | int | None = None,
                slot: int | None = None) -> int:
        """Route `source` to `dest` by `amount` (-100..100, % of the destination's range). Returns the slot (1-64)."""
        t, i, kp = self._dest(dest)
        pid = sp.mod_param_id(t, kp)
        if pid is None:
            raise KeyError(f"{dest}: Serum's parameter id for {t}.{kp} is not known (no factory preset modulates it)")
        if not -100 <= float(amount) <= 100:
            raise ValueError("mod amount is -100..100 (% of the destination's range)")
        if slot is None:
            slot = next((n + 1 for n in range(64) if not (self.tree.get(f"ModSlot{n}") or {}).get("destModuleTypeString")), None)
            if slot is None:
                raise RuntimeError("all 64 mod slots are in use")
        pp: dict[str, Any] = {"kParamAmount": float(amount)}
        if bipolar:
            pp["kParamBipolar"] = 1.0
        self.tree[f"ModSlot{slot - 1}"] = {"destModuleID": i, "destModuleParamID": pid, "destModuleParamName": kp, "destModuleTypeString": t,
                                           "plainParams": pp, "source": [sp.mod_source(source), sp.mod_source(aux) if aux else 0]}
        self.log.append(f"mod {slot}: {source} -> {dest} {float(amount):+g}")
        return slot

    def remove_mod(self, what: str | int) -> int:
        """Clear slot N, or every slot that targets the key `what`. Returns how many were cleared."""
        n = 0
        for m in self.mods():
            if (str(what).isdigit() and m["slot"] == int(what)) or m["dest"] == str(what):
                self.tree[f"ModSlot{m['slot'] - 1}"] = {"plainParams": {}}
                n += 1
        if not n:
            raise KeyError(f"no mod slot matches {what!r}")
        self.log.append(f"unmod {what}")
        return n

    # ------------------------------------------------------------------ saving
    def save(self, path: str | Path, name: str | None = None, author: str | None = None, description: str | None = None,
             tags: list[str] | None = None) -> Path:
        """Write a real .SerumPreset (same container Serum writes; header hash = MD5 of the compressed block)."""
        from .serum import _pack
        path = Path(path)
        if path.suffix.lower() != ".serumpreset":
            path = path.with_suffix(".SerumPreset")
        meta = dict(self.meta)
        meta["fileType"] = "SerumPreset"
        for k, v in (("presetName", name or path.stem), ("presetAuthor", author), ("presetDescription", description)):
            if v is not None:
                meta[k] = v
                self.tree[k] = v
        if tags is not None:
            meta["tags"] = list(tags)
            self.tree["tags"] = list(tags)
        meta.pop("hash", None)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(_pack(meta, self.tree))
        self.meta = meta
        self.source = str(path)
        return path

    def summary(self) -> str:
        """The patch as key=value lines by group, plus mod routings and the FX chain."""
        vals = self.read()
        by: dict[str, list[str]] = {}
        allp = sp.all_params()
        for k, v in vals.items():
            p = allp[k]
            if p.group == "mod" or _same(v, p.init):              # slots are listed as routings below; init values say nothing
                continue
            by.setdefault(p.group, []).append(f"{k}={p.show(v)}")
        L = [f"# {self.name}" + (f"  ({self.source})" if self.source else "  (Serum init)")]
        for g in sp.GROUP_DOCS:
            if g in by:
                L.append(f"- {g}: " + "  ".join(by[g]))
        fx = self.fx()
        if fx:
            L.append("- fx: " + " → ".join(lab + (" (" + ", ".join(f"{k} {sp.fmt(v)}" for k, v in prm.items()) + ")" if prm else "") for lab, _, _, prm in fx))
        ms = self.mods()
        if ms:
            L.append("- mod: " + "; ".join(f"{m['source']} → {m['dest']} {m['amount']:+.0f}" + (" bipolar" if m["bipolar"] else "") +
                                          (f" (× {m['aux']})" if m["aux"] else "") for m in ms))
        return "\n".join(L) + "\n"


def _same(v: Any, init: Any) -> bool:
    if isinstance(v, (int, float)) and isinstance(init, (int, float)):
        return abs(float(v) - float(init)) <= 0.006 * max(1.0, abs(float(init))) or (v == init)
    return v is not None and init is not None and str(v).lower() == str(init).lower()


def parse_mod(text: str) -> tuple[str, str, float]:
    """'lfo_1:filter_1.cutoff_hz:25' -> ('lfo_1', 'filter_1.cutoff_hz', 25.0)"""
    parts = text.split(":")
    if len(parts) != 3:
        raise ValueError(f"{text!r}: write a routing as SOURCE:DEST:AMOUNT, e.g. lfo_1:filter_1.cutoff_hz:25")
    return parts[0].strip(), parts[1].strip(), float(parts[2])


def parse_assignments(items: list[str]) -> dict[str, Any]:
    """['osc_a.detune=0.18', 'filter_1.type=MG Low 24'] -> dict; numbers become floats."""
    out: dict[str, Any] = {}
    for it in items:
        for kv in re.split(r"\s+(?=[\w.#]+=)", it.strip()):        # 'a=1 b=MG Low 24' is two settings
            k, eq, v = kv.partition("=")
            if not eq:
                raise ValueError(f"{kv!r}: write settings as key=value, e.g. filter_1.cutoff_hz=800")
            v = v.strip()
            out[k.strip()] = float(v) if re.fullmatch(r"-?\d+(\.\d*)?|-?\.\d+", v) else v
    return out


def is_patch_key(k: str) -> bool:
    """A serum_params key (dotted, or 'mod') rather than one of the hosted plug-in's own parameter names."""
    return "." in k or k in ("mod", "mods", "fx_add", "fx_remove", "unmod")


# ============================================================================ hearing a patch by measurement
def render_note(patch: Patch, note: str | int = "C2", secs: float = 1.0, bpm: float | None = None, tail: float = 1.5,
                velocity: int = 100):
    """One held note through the hosted Serum (the same notes for every variant). Returns (sr, audio, held seconds)."""
    from . import serum
    from .theory import note as parse_note
    pitch = parse_note(note) if isinstance(note, str) else int(note)
    _, audio = serum.render_preset(patch, [(pitch, 0.0, secs, velocity)], secs + tail, bpm=bpm)
    return 44100, audio, secs


def audition(base: Patch, variants: list[tuple[str, dict]], note: str | int = "C2", secs: float = 1.0, bpm: float | None = None,
             out_dir: str | Path | None = None) -> list[dict]:
    """Render the base patch and each variant (base + its settings) on the same note and describe each.
    `variants`: [(label, {key: value, "mod": [...], "fx_add": [...], "fx_remove": [...], "unmod": [...]})]."""
    from .samples import write_wav24
    from .sounddesign import describe_sound
    rows = []
    for label, settings in [("base", {})] + list(variants):
        p = base.copy()
        apply_edits(p, settings)
        sr, audio, held = render_note(p, note, secs, bpm)
        if out_dir:
            Path(out_dir).mkdir(parents=True, exist_ok=True)
            write_wav24(Path(out_dir) / f"{re.sub(r'[^A-Za-z0-9._=-]+', '_', label)[:80]}.wav", sr, audio)
        rows.append(describe_sound(sr, audio, label, held, bpm))
    return rows


def apply_edits(p: Patch, settings: dict) -> Patch:
    """Settings plus the structural edits: fx_add ['distortion', 'reverb:bus1'], fx_remove ['fx.chorus'],
    unmod ['filter_1.cutoff_hz' or slot numbers], mod ['lfo_1:filter_1.cutoff_hz:25' or dicts]."""
    s = dict(settings)
    for u in s.pop("fx_remove", []) or []:
        p.remove_fx(u)
    for u in s.pop("fx_add", []) or []:
        name, _, bus = str(u).partition(":")
        p.add_fx(name.strip(), rack=int(bus.replace("bus", "") or 0) if bus else 0)
    for u in s.pop("unmod", []) or []:
        p.remove_mod(u)
    mods = s.pop("mod", None) or []
    plain = {k: v for k, v in s.items() if not _fx_key(k)}
    fx = {k: v for k, v in s.items() if _fx_key(k)}
    p.apply(plain)
    p.apply(fx)
    for m in mods if isinstance(mods, list) else [mods]:
        p.add_mod(**m) if isinstance(m, dict) else p.add_mod(*parse_mod(m))
    return p
