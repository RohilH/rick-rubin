"""Serum 2's parameters the way a producer thinks of them — the map a patch is edited with.

A Serum patch is a tree of modules (Oscillator0..4, VoiceFilter0/1, Env0..3, LFO0..9, ModSlot0..63, FXRack0..2,
Macro0..7, Global0, RoutingSlot0..6, VoicePanel0, ...), each holding `plainParams` named kParam…. The hosted
plug-in exposes ~2600 automation parameters by name (`SerumHost.params()`), but not the FX units, the mod matrix's
routing or LFO shapes; the tree has all of them. So patches are edited in the tree (`serum_patch.Patch`) and this
map says, for each setting: where it lives, its unit, its range, its init value, which plug-in parameter (if any)
is the same knob, and what it does in one line.

Everything here was read off Serum itself, not guessed:
  * where each exposed plug-in parameter lives in the tree — set it on the hosted plug-in and read the state
    back (`check_paths()` redoes this; the tests run it when Serum is installed);
  * units — tree values are mostly what Serum displays (pan ±50, cents, %, seconds). The exceptions have
    converters checked against Serum's display: levels are linear gain, envelope sustain is gain², filter cutoff
    is 0..1 on a log scale from 8 Hz to 22.05 kHz, the filter's output level and the master/direct/bus volumes
    carry fixed offsets;
  * menus (filter types, warp modes, unison stacks, sub shapes, LFO sync rates, ...): Serum's displayed names
    and the codes the tree stores, in `data/serum_tables.json`, written by `build_tables()` from the plug-in;
  * FX units, their parameters and the ranges factory presets use, and the mod matrix's destination ids, from
    the factory presets (also `build_tables()`).

Keys look like `osc_a.detune`, `filter_1.cutoff_hz`, `env_2.attack_ms`, `lfo_1.rate`, `macro_3.value`,
`global.glide_ms`; FX are `fx.<unit>.<param>` (`fx.distortion.drive`, `fx.reverb#2.wet`, `fx_bus1.delay.wet`).
`groups()` and `view(group)` are what `rick-rubin serum params --group filter` prints.
"""
from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

TABLES_PATH = Path(__file__).resolve().parent / "data" / "serum_tables.json"
FILTER_HZ_LO, FILTER_HZ_HI = 8.0, 22050.0


# ============================================================================ the data file
@lru_cache(maxsize=1)
def tables() -> dict:
    """Menus, LFO rate tables, FX parameters and mod destination ids (see `build_tables`)."""
    if not TABLES_PATH.exists():
        raise FileNotFoundError(f"{TABLES_PATH} is missing — rebuild it with `python -m rick_rubin.serum_params --rebuild` (needs Serum 2)")
    return json.loads(TABLES_PATH.read_text())


# ============================================================================ converters
# Each converter turns a value in the unit the key names (dB, ms, Hz, %, a menu name) into what the tree stores,
# and back. Menus: the tree stores a code ('MgL24', 'kSaw'); `None` in a table means "Serum's init value" (the key
# is left out of the tree, which is how Serum itself stores an untouched knob).
def _num(v) -> float:
    if isinstance(v, bool):
        return 1.0 if v else 0.0
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().lower().replace("ms", "").replace("hz", "").replace("db", "").replace("%", "").strip()
    if s in ("on", "true", "yes"):
        return 1.0
    if s in ("off", "false", "no"):
        return 0.0
    if s in ("-inf", "-∞"):
        return float("-inf")
    return float(s)


def _db_to_gain(db: float, power: float = 20.0, offset: float = 0.0) -> float:
    return 0.0 if db == float("-inf") else 10 ** ((db - offset) / power)


def _gain_to_db(x: float, power: float = 20.0, offset: float = 0.0) -> float:
    return float("-inf") if x <= 0 else power * math.log10(x) + offset


def _menu_norm(s: str) -> str:
    return re.sub(r"[^a-z0-9+\-/#]", "", str(s).lower())


@dataclass(frozen=True)
class Conv:
    """How a key's value maps to the tree. kind: num | bool | ms | gain | gain2 | pct2 | hz | menu | rate | code | text."""
    kind: str = "num"
    power: float = 20.0          # gain/gain2: dB = power*log10(x) + offset
    offset: float = 0.0
    table: str = ""              # menu/rate: the table name in serum_tables.json; code: the factory codes list

    def to_tree(self, v: Any) -> Any:
        k = self.kind
        if k == "text":
            return str(v)
        if k == "bool":
            return 1.0 if _num(v) >= 0.5 else 0.0
        if k == "ms":
            return _num(v) / 1000.0
        if k in ("gain", "gain2"):
            return _db_to_gain(_num(v), self.power, self.offset)
        if k == "pct2":
            return math.sqrt(max(0.0, _num(v)) / 100.0)
        if k == "hz":
            hz = min(FILTER_HZ_HI, max(FILTER_HZ_LO, _num(v)))
            return math.log(hz / FILTER_HZ_LO) / math.log(FILTER_HZ_HI / FILTER_HZ_LO)
        if k in ("menu", "rate"):
            rows = tables()["menus"][self.table]["values"]
            want = _menu_norm(v)
            for shown, code in rows:
                if _menu_norm(shown) == want or (isinstance(code, str) and _menu_norm(code) in (want, "k" + want)):
                    return code
            if k == "rate" and not isinstance(v, str) or (k == "rate" and re.fullmatch(r"-?[\d.]+", str(v).strip())):
                return _num(v)                       # a number: Serum's own 0..100 rate knob (free-running when sync is off)
            raise ValueError(f"{v!r} is not one of: {', '.join(s for s, _ in rows)}")
        if k == "code":
            codes = tables()["fx_codes"].get(self.table, [])
            want = _menu_norm(v)
            for c in codes:
                if _menu_norm(c) in (want, "k" + want):
                    return c
            if isinstance(v, str) and not re.fullmatch(r"-?[\d.]+", v.strip()):
                return v if v.startswith("k") or not codes or not codes[0].startswith("k") else "k" + v
            return _num(v)
        return _num(v)

    def from_tree(self, x: Any) -> Any:
        k = self.kind
        if k == "text" or x is None:
            return x
        if k in ("menu", "rate"):
            for shown, code in tables()["menus"][self.table]["values"]:
                if code == x or (isinstance(code, float) and isinstance(x, (int, float)) and abs(code - x) < 1e-6 * max(1.0, abs(code))):
                    return shown
            return x
        if isinstance(x, str):
            return x
        if k == "bool":
            return "on" if x >= 0.5 else "off"
        if k == "ms":
            return x * 1000.0
        if k in ("gain", "gain2"):
            return _gain_to_db(x, self.power, self.offset)
        if k == "pct2":
            return 100.0 * x * x
        if k == "hz":
            return FILTER_HZ_LO * (FILTER_HZ_HI / FILTER_HZ_LO) ** float(x)
        return x


NUM, BOOL, MS, TEXT = Conv(), Conv("bool"), Conv("ms"), Conv("text")
GAIN = Conv("gain")                      # dB = 20 log10(x): oscillator levels
SUSTAIN_DB = Conv("gain2", 40.0)         # dB = 40 log10(x): ENV 1 sustain, ENV 2-4 start/end
FILTER_OUT = Conv("gain2", 40.0, 12.0)   # dB = 40 log10(x) + 12: filter output level
MASTER = Conv("gain", 20.0, 3.0)         # dB = 20 log10(x) + 3: the master volume knob
BUS = Conv("gain", 20.0, 6.0)            # dB = 20 log10(x) + 6: direct out and FX bus volumes
PCT2 = Conv("pct2")                      # % = 100 x²: ENV 2-4 sustain
HZ = Conv("hz")


def menu(name: str) -> Conv:
    return Conv("menu", table=name)


# ============================================================================ the map
@dataclass(frozen=True)
class Param:
    key: str                  # e.g. "filter_1.cutoff_hz"
    group: str                # osc | noise | sub | filter | routing | env | lfo | mod | macro | global | random | arp
    module: str               # tree path, e.g. "VoiceFilter0" or "Oscillator0/WTOsc0"
    kparam: str               # e.g. "kParamFreq"; "" for non-plainParams fields (wavetable path, macro name)
    conv: Conv = NUM
    unit: str = ""
    lo: float | None = None
    hi: float | None = None
    init: Any = None          # Serum's init patch value in this key's unit (None: not known / module-specific)
    doc: str = ""
    raw: str | None = None    # the hosted plug-in's parameter name for the same knob
    field: str = ""           # for kparam "": the module field it edits ("relativePathToWT", "name")

    def show(self, v: Any) -> str:
        return fmt(v)


def fmt(v: Any) -> str:
    """A value as a short string: 425, 0.18, -inf, on, 'MG Low 24'."""
    if v is None:
        return "—"
    if isinstance(v, float):
        if v == float("-inf"):
            return "-inf"
        return f"{v:.0f}" if abs(v) >= 100 else f"{v:.3g}"
    return str(v)


_P: dict[str, Param] = {}


def _add(key, group, module, kparam, conv=NUM, unit="", lo=None, hi=None, init=None, doc="", raw=None, field=""):
    if key in _P:
        raise ValueError(f"duplicate key {key}")
    _P[key] = Param(key, group, module, kparam, conv, unit, lo, hi, init, doc, raw, field)


OSCS = (("a", 0), ("b", 1), ("c", 2))
ROUTE_SLOTS = {"osc_a": (0, "a"), "osc_b": (1, "b"), "osc_c": (2, "c"), "noise": (3, "noise"), "sub": (4, "sub_osc"),
               "filter_1": (5, "filter_1"), "filter_2": (6, "filter_2")}


def _build() -> None:
    for L, i in OSCS:
        o, w, k = f"Oscillator{i}", f"Oscillator{i}/WTOsc{i}", f"osc_{L}"
        r = f"{L}_"
        _add(f"{k}.on", "osc", o, "kParamEnable", BOOL, "", init="on" if i == 0 else "off", raw=r + "enable", doc="oscillator on/off")
        _add(f"{k}.level_db", "osc", o, "kParamVolume", GAIN, "dB", -120, 0, -5.0, "oscillator level (Serum shows % and dB; 75% = -5 dB)", r + "level")
        _add(f"{k}.pan", "osc", o, "kParamPan", NUM, "", -50, 50, 0, "pan, -50 left .. +50 right", r + "pan")
        _add(f"{k}.octave", "osc", o, "kParamOctave", NUM, "oct", -4, 4, 0, "octave shift", r + "octave_oct")
        _add(f"{k}.semi", "osc", o, "kParamPitch", NUM, "st", -12, 12, 0, "semitone shift", r + "semi_semitones")
        _add(f"{k}.fine_cents", "osc", o, "kParamFine", NUM, "cents", -100, 100, 0, "fine tune", r + "fine_cents")
        _add(f"{k}.coarse", "osc", o, "kParamCoarsePit", NUM, "st", -64, 64, 0, "continuous coarse pitch (the knob a mod slot sweeps for pitch drops)", r + "coarse_pitch")
        _add(f"{k}.unison", "osc", o, "kParamUnison", NUM, "voices", 1, 16, 1, "unison voices", r + "unison")
        _add(f"{k}.detune", "osc", o, "kParamDetune", NUM, "", 0, 1, 0.25, "unison detune (0..1; 0.1-0.2 is a gentle supersaw spread, 0.5+ is a smear)", r + "uni_detune")
        _add(f"{k}.blend", "osc", o, "kParamDetuneWid", NUM, "%", 0, 100, 75, "unison blend: level of the outer voices against the centre one", r + "uni_blend")
        _add(f"{k}.width", "osc", o, "kParamUnisonStereo", NUM, "%", -100, 100, 100, "unison stereo width", r + "uni_width")
        _add(f"{k}.stack", "osc", o, "kParamUnisonStack", menu("uni_stack"), "", init="off", doc="unison voices stacked in octaves/fifths", raw=r + "uni_stack")
        _add(f"{k}.detune_mode", "osc", o, "kParamDetuneMode", Conv("code", table="detune_mode"), "", doc="how unison voices spread (factory codes: kDetuneRandom kDetuneSuper kDetuneExp kDetuneInv); unset = Serum's linear spread")
        _add(f"{k}.span", "osc", o, "kParamUnisonSpan", NUM, "", -100, 100, 0, "unison span", r + "uni_span")
        _add(f"{k}.rand_start", "osc", o, "kParamRandomStart", NUM, "%", 0, 100, 0, "random start offset per unison voice", r + "uni_rand_start")
        _add(f"{k}.uni_warp", "osc", o, "kParamUnisonWarp", NUM, "", -100, 100, 0, "spread of warp amount across unison voices", r + "uni_warp")
        _add(f"{k}.uni_warp_2", "osc", o, "kParamUnisonWarp2", NUM, "", -100, 100, 0, "spread of warp 2 amount across unison voices", r + "uni_warp_2")
        _add(f"{k}.engine", "osc", o, "kParamType", Conv("code", table="osc_type"), "", init="wavetable",
             doc="oscillator engine (unset = wavetable; factory codes kOsc_Sample kOsc_MultiSample kOsc_Granular kOsc_Spectral)")
        _add(f"{k}.pitch_track", "osc", o, "kParamPitchTrack", BOOL, "", init="on", doc="follow the played key", raw=r + "pitch_track")
        _add(f"{k}.ratio", "osc", o, "kParamPitchRatio", NUM, "", 0.25, 64, 1, "pitch ratio (harmonic/ratio pitch modes)", r + "ratio")
        _add(f"{k}.hz_offset", "osc", o, "kParamHzOffset", NUM, "Hz", -1000, 1000, 0, "linear frequency offset (inharmonic beating)", r + "hz_offset_hz")
        _add(f"{k}.wavetable", "osc", w, "", TEXT, "", init="S2 Tables/Default Shapes.wav",
             doc="wavetable file, relative to Serum's Tables folder (`serum tables` lists them), e.g. 'Analog/MB Saw.wav'", field="relativePathToWT")
        _add(f"{k}.wt_pos", "osc", w, "kParamTablePos", NUM, "", 1, 256, 1, "position in the wavetable: 1 = first frame, 256 = last, whatever the table's frame count", r + "wt_pos")
        _add(f"{k}.uni_wt_pos", "osc", w, "kParamUnisonWTPos", NUM, "", -100, 100, 0, "spread of table position across unison voices", r + "uni_wt_pos")
        for n, sfx in (("", ""), ("_2", "2")):
            _add(f"{k}.warp{n}_mode", "osc", w, f"kParamWarpMenu{sfx}", menu("warp_mode"), "", init="Off", doc=f"warp {n[1:] or '1'} type (Sync, Bend, PWM, FM (B), PD, Asym, filters ...)", raw=f"{r}warp{n}_mode")
            _add(f"{k}.warp{n}", "osc", w, f"kParamWarp{sfx}", NUM, "", 0, 1, 0, f"warp {n[1:] or '1'} amount (0..1)", f"{r}warp{n}")
            _add(f"{k}.warp{n}_var", "osc", w, f"kParamWarpVar{sfx}", NUM, "", 0, 1, 0, f"warp {n[1:] or '1'} variant knob", f"{r}warp{n}_var")
        _add(f"{k}.phase", "osc", w, "kParamInitialPhase", NUM, "deg", 0, 360, 180, "start phase", r + "phase")
        _add(f"{k}.rand_phase", "osc", w, "kParamRandomPhase", NUM, "%", 0, 100, 100, "random start phase (0 = every note starts the same: punchier, more consistent bass)", r + "rand_phase")
        # sample / granular engine playback (used when engine is not wavetable)
        for kk, kp, unit, lo, hi, init, raw, doc in (
                ("start", "kParamStart", "%", 0, 100, 0, "start", "sample start"), ("end", "kParamEnd", "%", 0, 100, 100, "end", "sample end"),
                ("reverse", "kParamReverse", "", None, None, "Forward", "reverse", "sample direction"),
                ("scan_rate", "kParamScanRate", "%", -200, 200, 100, "scan_rate", "sample/granular scan speed"),
                ("scan_sync", "kParamScanBPMRate", "", None, None, "bar", "scan_bpm_rate", "scan rate in bars when tempo-locked"),
                ("scan_key_track", "kParamScanKeyTrack", "", None, None, "off", "scan_key_track", "scan rate follows the key"),
                ("position", "kParamPosition", "%", 0, 100, 0, "position", "granular/spectral position"),
                ("loop_start", "kParamLoopStart", "%", 0, 100, 0, "loop_start", "loop start"), ("loop_end", "kParamLoopEnd", "%", 0, 100, 100, "loop_end", "loop end"),
                ("loop_xfade", "kParamLoopCrossfade", "%", 0, 100, 0, "loop_x_fade", "loop crossfade"),
                ("loop_mode", "kParamLoopMode", "", None, None, "One-shot", "loop_mode", "sample loop mode"),
                ("loop_link", "kParamLoopStartLink", "", None, None, "off", "relative_loop", "loop follows the start point"),
                ("slice", "kParamSlicingSingleSlice", "", 1, 100, 1, "single_slice", "slice to play"),
                ("slice_to_end", "kParamSlicingPlayToEnd", "", None, None, "To Next Marker", "slice_play_mode", "slice plays to the next marker or to the end")):
            conv = (menu("loop_mode") if kk == "loop_mode" else menu("reverse") if kk == "reverse" else menu("scan_bpm_rate") if kk == "scan_sync"
                    else menu("slice_play_mode") if kk == "slice_to_end" else BOOL if kk in ("scan_key_track", "loop_link") else NUM)
            _add(f"{k}.sample_{kk}", "osc-sample", o, kp, conv, unit, lo, hi, init, doc, r + raw)

    o = "Oscillator3"
    _add("noise.on", "noise", o, "kParamEnable", BOOL, init="off", doc="noise oscillator on/off", raw="noise_enable")
    _add("noise.level_db", "noise", o, "kParamVolume", GAIN, "dB", -120, 0, -24.1, "noise level", "noise_level")
    _add("noise.pan", "noise", o, "kParamPan", NUM, "", -50, 50, 0, "pan", "noise_pan")
    _add("noise.pitch_track", "noise", o, "kParamPitchTrack", BOOL, init="off", doc="noise pitch follows the key", raw="noise_pitch_track")
    _add("noise.pitch", "noise", "Oscillator3/NoiseOsc3", "kParamColor", Conv("num"), "", 0, 1, 0.5, "noise pitch / colour knob (0..1; Serum shows %)", "noise_pitch")
    _add("noise.fine", "noise", "Oscillator3/NoiseOsc3", "kParamFine", NUM, "", -1, 1, 0, "noise fine pitch", "noise_fine")
    _add("noise.phase", "noise", "Oscillator3/NoiseOsc3", "kParamInitialPhase", NUM, "%", 0, 100, 0, "start point in the noise sample", "noise_phase")
    _add("noise.rand_phase", "noise", "Oscillator3/NoiseOsc3", "kParamRandomPhase", NUM, "%", 0, 100, 0, "random start point", "noise_rand_phase")
    _add("noise.type", "noise", "Oscillator3/NoiseOsc3", "kParamNoiseType", Conv("code", table="noise_type"), doc="noise type (factory: White Pink Brown Geiger); unset = Serum's init noise")
    _add("noise.one_shot", "noise", "Oscillator3/NoiseOsc3", "kParamOneShot", BOOL, init="off", doc="play the noise sample once instead of looping")

    o = "Oscillator4"
    _add("sub.on", "sub", o, "kParamEnable", BOOL, init="off", doc="sub oscillator on/off", raw="sub_enable")
    _add("sub.level_db", "sub", o, "kParamVolume", GAIN, "dB", -120, 0, -5.0, "sub level", "sub_level")
    _add("sub.pan", "sub", o, "kParamPan", NUM, "", -50, 50, 0, "pan (keep 0 for a bass)", "sub_pan")
    _add("sub.octave", "sub", o, "kParamOctave", NUM, "oct", -4, 4, 0, "octave", "sub_octave_oct")
    _add("sub.coarse", "sub", o, "kParamCoarsePit", NUM, "st", -64, 64, 0, "continuous coarse pitch", "sub_coarse_pitch")
    _add("sub.pitch_track", "sub", o, "kParamPitchTrack", BOOL, init="on", doc="follow the key", raw="sub_pitch_track")
    _add("sub.shape", "sub", "Oscillator4/SubOsc4", "kParamShape", menu("sub_shape"), init="Sine", doc="Sine RoundRect Triangle Saw Square Pulse", raw="sub_shape")
    _add("sub.phase", "sub", "Oscillator4/SubOsc4", "kParamInitialPhase", NUM, "deg", 0, 360, 0, "start phase", "sub_phase")
    _add("sub.cont_phase", "sub", "Oscillator4/SubOsc4", "kParamContiguousPhase", BOOL, init="off", doc="free-running phase (no reset per note)", raw="sub_cont_phase")

    for n in (1, 2):
        f, k = f"VoiceFilter{n - 1}", f"filter_{n}"
        _add(f"{k}.on", "filter", f, "kParamEnable", BOOL, init="off", doc="filter on/off", raw=f"{k}_on")
        _add(f"{k}.type", "filter", f, "kParamType", menu("filter_type"), init="MG Low 12", doc="filter type (`serum params --group filter --menus` lists the 108)", raw=f"{k}_type")
        _add(f"{k}.cutoff_hz", "filter", f, "kParamFreq", HZ, "Hz", FILTER_HZ_LO, FILTER_HZ_HI, 425.0, "cutoff (log knob: 0.5 = 425 Hz)", f"{k}_freq_hz")
        _add(f"{k}.res", "filter", f, "kParamReso", NUM, "%", 0, 100, 10, "resonance", f"{k}_res")
        _add(f"{k}.drive", "filter", f, "kParamDrive", NUM, "%", 0, 100, 0, "drive into the filter", f"{k}_drive")
        _add(f"{k}.var", "filter", f, "kParamVar", NUM, "%", 0, 100, 0, "the filter type's third knob (fat, spread, morph ... depends on type)", f"{k}_var")
        _add(f"{k}.mix", "filter", f, "kParamWet", NUM, "%", 0, 100, 100, "dry/wet", f"{k}_wet")
        _add(f"{k}.stereo", "filter", f, "kParamStereo", NUM, "%", 0, 100, 50, "stereo offset of the cutoff between L and R (50 = none)", f"{k}_stereo")
        _add(f"{k}.level_db", "filter", f, "kParamLevelOut", FILTER_OUT, "dB", -120, 12, 0.0, "output level", f"{k}_level")
        _add(f"{k}.key_track", "filter", f, "kParamKeyTrack", BOOL, init="off", doc="cutoff follows the key")
        _add(f"{k}.x", "filter", f, "kParamX", NUM, "", 0, 1, 0, "PZ (pole/zero) filter X", f"{k}_x")
        _add(f"{k}.y", "filter", f, "kParamY", NUM, "", 0, 1, 0, "PZ (pole/zero) filter Y", f"{k}_y")

    for k, (slot, raw) in ROUTE_SLOTS.items():
        rs = f"RoutingSlot{slot}"
        if not k.startswith("filter"):
            _add(f"{k}.filter_mix", "routing", rs, "kParamFilterBalance", NUM, "", -100, 100, -100,
                 "which filter this source feeds: -100 = filter 1 only, 0 = both, +100 = filter 2 only (only when the filter is on)", f"{raw}_filter_balance")
            _add(f"{k}.route", "routing", rs, "kParamRoutingDest", Conv("code", table="routing_dest"),
                 doc="where this source goes (factory codes kRoutingDestFilter kRoutingDestDirect kRoutingDestMaster kRoutingDestNone)")
        _add(f"{k}.bus1_pct", "routing", rs, "kParamFXBus1Level", NUM, "%", 0, 100, 0, "send to FX bus 1", f"{raw}_bus1")
        _add(f"{k}.bus2_pct", "routing", rs, "kParamFXBus2Level", NUM, "%", 0, 100, 0, "send to FX bus 2", f"{raw}_bus2")

    for n in (1, 2, 3, 4):
        e, k = f"Env{n - 1}", f"env_{n}"
        what = "the amp envelope" if n == 1 else "a mod envelope (route it in the mod matrix)"
        for kk, kp, init, raw in (("attack_ms", "kParamAttack", 1.0 if n == 1 else 0.5, "attack"), ("hold_ms", "kParamHold", 0.0, "hold"),
                                  ("decay_ms", "kParamDecay", 1000.0, "decay"), ("release_ms", "kParamRelease", 15.0, "release")):
            _add(f"{k}.{kk}", "env", e, kp, MS, "ms", 0, 32000, init, f"{kk[:-3]} time of {what}", f"{k}_{raw}")
        if n == 1:
            _add(f"{k}.sustain_db", "env", e, "kParamSustain", SUSTAIN_DB, "dB", -120, 0, 0.0, "sustain level of the amp envelope", f"{k}_sustain")
        else:
            _add(f"{k}.sustain_pct", "env", e, "kParamSustain", PCT2, "%", 0, 100, 100.0, "sustain level", f"{k}_sustain")
            _add(f"{k}.start_db", "env", e, "kParamStart", SUSTAIN_DB, "dB", -120, 0, float("-inf"), "level the envelope starts from", f"{k}_start")
            _add(f"{k}.end_db", "env", e, "kParamEnd", SUSTAIN_DB, "dB", -120, 0, float("-inf"), "level the release ends on", f"{k}_end")
        for kk, kp, init, raw in (("attack_curve", "kParamCurve1", 50, "atk_curve"), ("decay_curve", "kParamCurve2", 67, "dec_curve"), ("release_curve", "kParamCurve3", 67, "rel_curve")):
            _add(f"{k}.{kk}", "env", e, kp, NUM, "", 0, 100, init, f"{kk.split('_')[0]} curve (50 = linear)", f"{k}_{raw}")
        _add(f"{k}.sync", "env", e, "kParamBeatSync", BOOL, init="off", doc="envelope times in beats instead of seconds")

    for n in range(1, 11):
        lf, k = f"LFO{n - 1}", f"lfo_{n}"
        _add(f"{k}.rate", "lfo", lf, "kParamRate", Conv("rate", table="lfo_rate"), "", init="1/4",
             doc="rate: a sync division (32 bar .. 1/256, fast) while sync is on, else Serum's 0..100 rate knob", raw=f"{k}_rate")
        _add(f"{k}.sync", "lfo", lf, "kParamBeatSync", BOOL, init="on", doc="rate locked to the tempo")
        _add(f"{k}.dotted", "lfo", lf, "kParamDotted", BOOL, init="off", doc="dotted sync rate")
        _add(f"{k}.triplet", "lfo", lf, "kParamTriplets", BOOL, init="off", doc="triplet sync rate")
        _add(f"{k}.mode", "lfo", lf, "kParamMode", Conv("code", table="lfo_mode"), doc="trigger mode (factory: Free = runs freely, Envelope = plays once per note); unset = restarts every note")
        _add(f"{k}.type", "lfo", lf, "kParamType", Conv("code", table="lfo_type"), doc="unset = the drawn shape; factory alternatives: RandomSH Rossler Lorenz Path")
        _add(f"{k}.smooth", "lfo", lf, "kParamSmooth", NUM, "", 0, 100, 0, "smoothing", f"{k}_smooth")
        _add(f"{k}.rise", "lfo", lf, "kParamRise", Conv("rate", table="lfo_rise"), "", init="Off", doc="fade-in time", raw=f"{k}_rise")
        _add(f"{k}.delay", "lfo", lf, "kParamDelay", Conv("rate", table="lfo_rise"), "", init="Off", doc="delay before it starts", raw=f"{k}_delay")
        _add(f"{k}.phase", "lfo", lf, "kParamPhase", NUM, "deg", 0, 360, 0, "start phase", f"{k}_phase")
        _add(f"{k}.shape", "lfo", lf, "", TEXT, "", init="(Serum's init shape)",
             doc="the drawn shape: a file from Serum's 'LFO Shapes' folder ('Basic/Sine', 'Basic/Saw Down', 'Sidechain/SC1' ...) or points 'x:y,x:y,...' (0..1)", field="curveData")

    for n in range(1, 65):
        s = f"ModSlot{n - 1}"
        _add(f"mod_{n}.amount", "mod", s, "kParamAmount", NUM, "%", -100, 100, 0, "depth, in % of the destination's range", f"mod_{n}_amount")
        _add(f"mod_{n}.out", "mod", s, "kParamOut", NUM, "%", 0, 100, 100, "output scale of the slot", f"mod_{n}_out")

    for n in range(1, 9):
        _add(f"macro_{n}.value", "macro", f"Macro{n - 1}", "kParamValue", NUM, "%", 0, 100, 0, "macro knob", f"macro_{n}")
        _add(f"macro_{n}.name", "macro", f"Macro{n - 1}", "", TEXT, "", init="", doc="the label under the knob", field="name")

    g = "Global0"
    for kk, kp, conv, unit, lo, hi, init, raw, doc in (
            ("volume_db", "kParamMasterVolume", MASTER, "dB", -120, 3, -9.0, "main_vol", "master volume (Serum's init is -9 dB)"),
            ("direct_db", "kParamDirectVol", BUS, "dB", -120, 12, 0.0, "direct_vol", "direct-out volume"),
            ("bus1_db", "kParamFXBus1Vol", BUS, "dB", -120, 12, 0.0, "bus_1_vol", "FX bus 1 return volume"),
            ("bus2_db", "kParamFXBus2Vol", BUS, "dB", -120, 12, 0.0, "bus_2_vol", "FX bus 2 return volume"),
            ("mono", "kParamMonoToggle", BOOL, "", None, None, "off", "mono_toggle", "mono (one voice; with legato for slides)"),
            ("legato", "kParamLegato", BOOL, "", None, None, "off", "legato", "legato: overlapping notes do not retrigger the envelopes"),
            ("glide_ms", "kParamPortamentoTime", MS, "ms", 0, 8000, 0.0, "porta_time", "portamento time"),
            ("glide_curve", "kParamPortamentoCurve", NUM, "", -100, 100, 0, "porta_curve", "portamento curve"),
            ("glide_always", "kParamPortaAlways", BOOL, "", None, None, "off", "porta_always", "glide on every note, not only overlapping ones"),
            ("glide_scaled", "kParamPortaScaled", BOOL, "", None, None, "off", "porta_scaled", "glide time scales with the interval"),
            ("voices", "kParamPolyCount", NUM, "", 1, 32, None, None, "maximum voices when poly"),
            ("transpose", "kParamTranspose", NUM, "st", -24, 24, 0, "transpose_semitones", "transpose the whole patch"),
            ("bend_up", "kParamBendRangeUp", NUM, "st", -24, 24, 2, "bend_up_semitones", "pitch bend range up"),
            ("bend_down", "kParamBendRangeDn", NUM, "st", -24, 24, -2, "bend_down_semitones", "pitch bend range down"),
            ("mod_wheel", "kParamModWheel", NUM, "", 0, 100, 0, "mod_wheel", "mod wheel position stored with the patch"),
            ("tuning", "kParamMasterTuning", NUM, "", 0, 1, 0.5, "main_tuning", "master tune (0.5 = A440)"),
            ("amp", "kParamVoiceAmp", NUM, "", 0, 1, 0.5, "amp", "per-voice amplitude"),
            ("swing", "kParamSwing", NUM, "%", 0, 100, 0, "swing", "swing of Serum's own clip/arp player"),
            ("swing_div", "kParamSwingDiv", menu("swing_div"), "", None, None, "1/16", "swing_div", "swing grid"),
            ("bypass", "kParamBypass", BOOL, "", None, None, "off", "bypass", "bypass the whole synth"),
            ("oversampling", "kParamOversampling", NUM, "", 0, 2, None, None, "oversampling setting (factory 0..2)"),
            ("program", "kParamProgram", NUM, "", 0, 127, 0, "bank", "program slot (host bank switching; leave alone)")):
        _add(f"global.{kk}", "global", g, kp, conv, unit, lo, hi, init, doc, raw)

    v = "VoicePanel0"
    for kk, kp, init, raw, doc in (("detune", "kParamGlobalRandomOscDetune", 0, "osc_detune_rnd_cents", "random detune per voice (0..100; Serum shows 0..20 cents)"),
                                   ("pan", "kParamGlobalRandomOscPan", 0, "osc_pan_rand", "random pan per voice"),
                                   ("env_time", "kParamGlobalRandomEnvTime", 0, "env_rand", "random envelope times per voice"),
                                   ("cutoff", "kParamGlobalRandomFilterCutoff", 0, "cutoff_rand", "random cutoff per voice")):
        _add(f"random.{kk}", "random", v, kp, NUM, "%", 0, 100, init, doc, raw)

    for kk, mod, kp, raw, conv, init, doc in (
            ("arp.on", "Arp0", "kParamEnabled", "arp_enable", BOOL, "off", "Serum's arpeggiator (rick-rubin writes the notes itself: keep it off unless the patch is an arp by design)"),
            ("arp.rate", "Arp0", "kParamRate", "arp_rate", NUM, 0, "arp rate"), ("arp.shift", "Arp0", "kParamTransposeShift", "arp_shift", NUM, 0, "arp shift"),
            ("arp.range", "Arp0", "kParamTransposeRange", "arp_range", NUM, 0, "arp range"), ("arp.offset", "Arp0", "kParamOffset", "arp_offset", NUM, 0, "arp offset"),
            ("arp.repeats", "Arp0", "kParamRepeats", "arp_repeats", NUM, 0, "arp repeats"), ("arp.gate", "Arp0", "kParamGate", "arp_gate", NUM, 0, "arp gate"),
            ("arp.chance", "Arp0", "kParamChance", "arp_chance", NUM, 0, "arp chance"), ("arp.retrig_rate", "Arp0", "kParamRetrigRate", "arp_retrig_rate", NUM, 0, "arp retrigger rate"),
            ("arp.velo_decay", "Arp0", "kParamVeloDecay", "arp_velo_decay", NUM, 0, "arp velocity decay"), ("arp.velo_target", "Arp0", "kParamVeloTarget", "arp_velo_target", NUM, 0, "arp velocity target"),
            ("arp.transpose", "Arp0", "kParamTranspose", "arp_transpose", NUM, 0, "arp transpose"), ("arp.wrap_transpose", "Arp0", "kParamWrapTranspose", "arp_wrap_transpose", NUM, 0, "arp wrap transpose"),
            ("arp.wrap_range", "Arp0", "kParamWrapRange", "arp_wrap_range", NUM, 0, "arp wrap range"), ("arp.wrap_phantom_note", "Arp0", "kParamWrapPhantomNote", "arp_wrap_phantom_note", NUM, 0, "arp phantom note"),
            ("clip.on", "ClipPlayer0", "kParamEnabled", "clip_player_enable", BOOL, "off", "Serum's MIDI clip player (keep off: the song's notes drive the synth)"),
            ("clip.transpose", "ClipPlayer0", "kParamTranspose", "clip_player_transpose", NUM, 0, "clip transpose"),
            ("clip.rate", "ClipPlayer0", "kParamRate", "clip_player_rate", NUM, 0, "clip rate"), ("clip.offset", "ClipPlayer0", "kParamRegionOffset", "clip_player_offset", NUM, 0, "clip offset"),
            ("scale.key", "PitchQuantizer0", "kParamKey", "key", NUM, 0, "pitch quantizer key (0 = off, 1 = C ... 12 = B)"),
            ("scale.scale", "PitchQuantizer0", "kParamScale", "scale", NUM, None, "pitch quantizer scale number (leave off: the song's notes are already in key)")):
        _add(kk, "arp", mod, kp, conv, "", None, None, init, doc, raw)


_build()

GROUP_DOCS = {
    "osc": "oscillators A, B, C: level, pitch, unison, wavetable and position, warp",
    "osc-sample": "sample/granular/spectral playback of oscillators A-C (start, loop, scan)",
    "noise": "the noise oscillator", "sub": "the sub oscillator", "filter": "filters 1 and 2",
    "routing": "which filter / FX bus each source feeds", "env": "ENV 1 (amp) and ENV 2-4 (mod envelopes)",
    "lfo": "LFO 1-10", "mod": "mod matrix slots 1-64 (routing: --mod SOURCE:DEST:AMOUNT)", "macro": "macros 1-8",
    "global": "voices, glide, master volume, bend, transpose", "random": "per-voice randomness",
    "arp": "Serum's own arp / clip player / pitch quantizer (normally off here)", "fx": "the FX rack units (fx.<unit>.<param>)",
}

# hosted plug-in parameters with no place in the map, and why
IGNORED = [
    (r"cc\d+_chan_\d+", "MIDI CC proxies the VST3 host layer adds for each channel; not patch settings"),
    (r"aftertouch_chan_\d+|pitch_bend_chan_\d+|pitch_bend", "performance controls (aftertouch, pitch bend) the host layer adds; not stored in the patch"),
    (r"[abc]_param(4[4-9]|5[0-5])", "unused oscillator slots; setting them changes nothing in the patch"),
    (r"fx_(main|bus_[12])_param_\d+", "FX-rack automation proxies; not connected to any unit in a patch state (edit the units with fx.<unit>.<param>)"),
]


def all_params() -> dict[str, Param]:
    return dict(_P)


def ignored_reason(raw: str) -> str | None:
    for pat, why in IGNORED:
        if re.fullmatch(pat, raw):
            return why
    return None


def lookup(key: str) -> Param:
    """The map entry for a key, with a helpful error listing near matches."""
    k = key.strip()
    if k in _P:
        return _P[k]
    by_raw = [p for p in _P.values() if p.raw == k]
    if by_raw:
        return by_raw[0]
    head = k.split(".")[0]
    near = [x for x in _P if x.startswith(head + ".")] or [x for x in _P if k.split(".")[-1] in x][:20]
    raise KeyError(f"no Serum setting {key!r}" + (f"; {head} has: {', '.join(near[:40])}" if near else "; see `rick-rubin serum params --group <group>`"))


def groups() -> dict[str, list[Param]]:
    out: dict[str, list[Param]] = {}
    for p in _P.values():
        out.setdefault(p.group, []).append(p)
    return out


# ============================================================================ FX units
def fx_units() -> dict[str, dict]:
    """{"distortion": {"key": "FXDistortion", "type": 0, "params": {snake_name: {"kparam", "lo", "hi", "codes", "doc"}}}, ...}"""
    return tables()["fx"]


FX_DOCS = {
    "distortion": {"drive": "drive amount, %", "wet": "dry/wet %", "mode": "distortion type (TapeSat, Tube, SoftClip, Diode1, Overdrive, Downsample ...)",
                   "prepost": "where the unit's filter sits (factory values 1, 2)", "freq": "filter frequency of the unit, 0..1", "lphp": "filter morph LP..HP, %",
                   "bw": "filter bandwidth", "level_out": "output gain (0..1)"},
    "reverb": {"wet": "dry/wet %", "size": "room size %", "type": "reverb model (factory: kHall kVintage kAbyss kSpace; unset = Serum's init model)", "pre_delay": "pre-delay, seconds",
               "feedback": "decay %", "width": "stereo width %", "freq": "low cut %", "freq_b": "high cut / damping %"},
    "delay": {"wet": "dry/wet %", "feedback": "feedback %", "time_l": "left time (beats when synced)", "time_r": "right time", "freq": "filter centre, Hz",
              "bw": "filter bandwidth (octaves)", "mode": "delay mode (factory values 1, 2)", "beat_sync": "0 = free time (factory presets store 0 to unsync)"},
    "chorus": {"wet": "dry/wet %", "rate": "LFO rate, Hz", "depth": "depth, ms", "delay": "delay 1, ms", "delay2": "delay 2, ms", "feedback": "feedback %", "filt": "low cut, Hz"},
    "compressor": {"thresh": "threshold (0..1 of full scale)", "ratio": "ratio (1 .. 1e6 = limiter)", "attack": "attack, ms", "release": "release, ms",
                   "makeup": "make-up gain (linear)", "multiband": "1 = multiband (OTT-style)", "wet": "dry/wet %"},
    "eq": {"freq1": "low band frequency, Hz", "gain1": "low band gain, dB", "reso1": "low band Q %", "type1": "band shape (factory values 1, 2)",
           "freq2": "high band frequency, Hz", "gain2": "high band gain, dB", "reso2": "high band Q %", "type2": "band shape (factory values 1, 2)"},
    "filter": {"type": "filter type code (same codes as filter_1.type: MgL12, H24, ...)", "freq": "cutoff 0..1 (log 8 Hz .. 22 kHz like filter_1)", "reso": "resonance %",
               "drive": "drive %", "wet": "dry/wet %", "var": "the type's third knob"},
    "hyper": {"wet": "hyper dry/wet %", "rate": "rate %", "detune": "detune %", "unison": "voices 0..7", "dim_e_size": "dimension size %", "dim_e_wet": "dimension dry/wet %"},
    "utility": {"width": "stereo width % (100 = unchanged)", "hpf": "high-pass, Hz", "lpf": "low-pass, Hz", "lf_mono": "1 = mono below lf_xover", "lf_xover": "mono-bass crossover, Hz",
                "balance": "L/R balance", "level_out": "output gain (0..1)"},
}


def _snake(kparam: str) -> str:
    s = kparam.removeprefix("kParam")
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", s)
    return s.lower().replace("l_p_h_p", "lphp").replace("b_w", "bw")


# ============================================================================ mod matrix
MOD_SOURCES = {"mod_wheel": 1, "env_1": 2, "env_2": 3, "env_3": 4, "env_4": 5,
               **{f"lfo_{i}": 5 + i for i in range(1, 11)},
               "velocity": 16, "note": 17, "random_1": 21, "random_2": 22, "alternate_1": 23, "alternate_2": 24,
               **{f"macro_{i}": 24 + i for i in range(1, 9)}}
# measured on the hosted plug-in (source -> OSC A level, several notes/velocities): see docs. Others are given as "#n".
MOD_SOURCE_NAMES = {v: k for k, v in MOD_SOURCES.items()}


def mod_source(s: str | int) -> int:
    if isinstance(s, int):
        return s
    t = str(s).strip().lower().replace(" ", "_")
    if t.startswith("#") and t[1:].isdigit():
        return int(t[1:])
    if t in MOD_SOURCES:
        return MOD_SOURCES[t]
    raise KeyError(f"unknown mod source {s!r}; use one of {', '.join(MOD_SOURCES)} or '#n' (Serum's source number)")


def mod_source_name(n: int | list) -> str:
    if isinstance(n, list):
        n = n[0] if n else 0
    return MOD_SOURCE_NAMES.get(int(n), f"#{n}")


def mod_param_id(type_string: str, kparam: str) -> int | None:
    """Serum's parameter index of `kparam` inside a module type (from the factory presets' mod slots)."""
    return tables()["mod_param_ids"].get(f"{type_string}.{kparam}")


# ============================================================================ views
def view(group: str, values: dict[str, Any] | None = None, menus: bool = False) -> str:
    """One screen per group: key, unit, range, init, value (when a patch is given), what it does."""
    gs = groups()
    if group == "fx":
        return fx_view()
    if group not in gs:
        raise KeyError(f"no group {group!r}; groups: {', '.join(list(gs) + ['fx'])}")
    rows = gs[group]
    if group in ("mod",) and values is None:
        rows = [p for p in rows if p.key.startswith("mod_1.")]
    collapse = group in ("lfo", "env") and values is None
    if collapse:
        first = {"lfo": "lfo_1.", "env": None}[group]
        rows = [p for p in rows if (first and p.key.startswith(first)) or (not first and p.key.split(".")[0] in ("env_1", "env_2"))]
    L = [f"## {group} — {GROUP_DOCS.get(group, '')}", "| key | unit | range | init | " + ("value | " if values is not None else "") + "what it does |",
         "|---|---|---|---|" + ("---|" if values is not None else "") + "---|"]
    for p in rows:
        if values is not None and group in ("mod", "lfo", "osc-sample", "arp") and p.key not in values:
            continue
        rng = f"{p.show(p.lo)}..{p.show(p.hi)}" if p.lo is not None else ("menu" if p.conv.kind in ("menu", "rate") else "on/off" if p.conv.kind == "bool" else "")
        val = (p.show(values[p.key]) if p.key in values else "init") if values is not None else None
        L.append(f"| {p.key} | {p.unit} | {rng} | {p.show(p.init)} | " + (f"{val} | " if val is not None else "") + f"{p.doc} |")
    if collapse:
        L.append(f"(the same keys exist for {'lfo_1 .. lfo_10' if group == 'lfo' else 'env_3 and env_4 (like env_2)'})")
    if group == "mod":
        L += ["", "Routing: `--mod SOURCE:DEST:AMOUNT` adds a slot (amount -100..100 % of the destination's range), `--unmod DEST` or "
              "`--unmod N` removes. Sources: " + ", ".join(MOD_SOURCES) + ", or '#n'. DEST is any key above with a tree parameter, e.g. "
              "filter_1.cutoff_hz, osc_a.wt_pos, osc_a.fine_cents, env_1.decay_ms, fx.reverb.wet."]
    if menus:
        for p in rows:
            if p.conv.kind in ("menu", "rate"):
                vals = [s for s, _ in tables()["menus"][p.conv.table]["values"]]
                L.append(f"- {p.key}: " + ", ".join(dict.fromkeys(vals)))
    return "\n".join(L) + "\n"


def fx_view() -> str:
    L = ["## fx — FX rack units: fx.<unit>.<param> (main rack), fx_bus1.<unit>.<param>, fx_bus2.<unit>.<param>; "
         "a second unit of a kind is <unit>#2. Add with --fx-add UNIT[:BUS], remove with --fx-remove UNIT.",
         "Values are Serum's own (what the knob shows: %, Hz, ms, s, dB) unless noted; ranges are those used by the factory presets; "
         "an unset parameter is at Serum's init value.", ""]
    for name, u in fx_units().items():
        docs = FX_DOCS.get(name, {})
        parts = []
        for pn, d in u["params"].items():
            rng = f" {d['lo']:.3g}..{d['hi']:.3g}" if d.get("lo") is not None else (" " + "/".join(c.lstrip("k") for c in d.get("codes", [])[:8]) if d.get("codes") else "")
            parts.append(f"{pn}{rng}" + (f" ({docs[pn]})" if pn in docs else ""))
        L.append(f"- **{name}** ({u['key']}): " + "; ".join(parts))
    return "\n".join(L) + "\n"


# ============================================================================ building the data file from Serum itself
MENU_PARAMS = {"filter_type": "filter_1_type", "warp_mode": "a_warp_mode", "uni_stack": "a_uni_stack", "sub_shape": "sub_shape",
               "loop_mode": "a_loop_mode", "lfo_rate": "lfo_1_rate", "lfo_rise": "lfo_1_rise", "swing_div": "swing_div",
               "scan_bpm_rate": "a_scan_bpm_rate", "reverse": "a_reverse", "slice_play_mode": "a_slice_play_mode"}
FX_NAMES = {"FXDistortion": "distortion", "FXFlanger": "flanger", "FXPhaser": "phaser", "FXChorus": "chorus", "FXDelay": "delay",
            "FXComp": "compressor", "FXReverb": "reverb", "FXEQ": "eq", "FXFilter": "filter", "FXHyperD": "hyper", "FXBode": "frequency_shifter",
            "FXConv": "convolve", "FXUtils": "utility", "FXSplit": "split", "FXSplit3": "split3", "FXSplitMS": "split_ms"}


def _state_tree(host) -> dict:
    from .serum import _unpack, split_state
    host.plugin([], duration=0.005, sample_rate=44100, reset=False)          # parameter changes land in the state after a block
    return _unpack(split_state(bytes(host.plugin.raw_state))[0])[1]


def tree_get(tree: dict, module: str, kparam: str):
    d: Any = tree
    for part in module.split("/"):
        d = d.get(part, {}) if isinstance(d, dict) else {}
    pp = d.get("plainParams") if isinstance(d, dict) else None
    return pp.get(kparam) if isinstance(pp, dict) else None


def build_tables(host=None, presets_root: str | Path | None = None, progress=None) -> dict:
    """Rebuild data/serum_tables.json: every menu read off the hosted plug-in (each option set in turn, the code
    read back from the state), and the FX units, their parameters, ranges and codes, the mod matrix's
    destination parameter ids, from the factory presets."""
    import collections

    from . import serum
    host = host or serum.SerumHost.get()
    P = host.plugin
    say = progress or (lambda *_: None)
    menus = {}
    for name, raw in MENU_PARAMS.items():
        path = next(p for p in _P.values() if p.raw == raw)
        P.raw_state = host.init_state
        n = len(P.parameters[raw].valid_values)
        rows = []
        for i in range(n):
            P.raw_state = host.init_state
            prm = P.parameters[raw]
            prm.raw_value = i / (n - 1) if n > 1 else 0.0
            rows.append([str(prm.string_value).strip(), tree_get(_state_tree(host), path.module, path.kparam)])
        P.raw_state = host.init_state
        menus[name] = {"param": raw, "values": rows}
        say(f"menu {name}: {len(rows)} options")
    root = Path(presets_root) if presets_root else serum.preset_root()
    fx: dict[str, dict] = {}
    vals: dict = collections.defaultdict(lambda: collections.defaultdict(list))
    ids: dict = collections.defaultdict(collections.Counter)
    codes: dict = collections.defaultdict(set)
    for f in sorted(root.rglob("*.SerumPreset")):
        try:
            _, t = serum.read_preset(f)
        except Exception:  # noqa: BLE001
            continue
        for r in range(3):
            for unit in (t.get(f"FXRack{r}") or {}).get("FX") or []:
                for k, v in unit.items():
                    if k in FX_NAMES and isinstance(v, dict):
                        fx.setdefault(FX_NAMES[k], {"key": k, "type": unit.get("type"), "params": {}})
                        for kp, x in (v.get("plainParams") if isinstance(v.get("plainParams"), dict) else {}).items():
                            vals[k][kp].append(x)
        for k, v in t.items():
            if k.startswith("ModSlot") and isinstance(v, dict) and v.get("destModuleTypeString"):
                ids[f"{v['destModuleTypeString']}.{v['destModuleParamName']}"][v.get("destModuleParamID")] += 1
            if k.startswith("Oscillator") and isinstance(v, dict):
                pp = v.get("plainParams") if isinstance(v.get("plainParams"), dict) else {}
                for kp, tab in (("kParamType", "osc_type"), ("kParamDetuneMode", "detune_mode")):
                    if isinstance(pp.get(kp), str):
                        codes[tab].add(pp[kp])
                no = v.get("NoiseOsc3")
                if isinstance(no, dict) and isinstance(no.get("plainParams"), dict) and isinstance(no["plainParams"].get("kParamNoiseType"), str):
                    codes["noise_type"].add(no["plainParams"]["kParamNoiseType"])
            if k.startswith("LFO") and isinstance(v, dict) and isinstance(v.get("plainParams"), dict):
                for kp, tab in (("kParamMode", "lfo_mode"), ("kParamType", "lfo_type")):
                    if isinstance(v["plainParams"].get(kp), str):
                        codes[tab].add(v["plainParams"][kp])
            if k.startswith("RoutingSlot") and isinstance(v, dict) and isinstance(v.get("plainParams"), dict):
                if isinstance(v["plainParams"].get("kParamRoutingDest"), str):
                    codes["routing_dest"].add(v["plainParams"]["kParamRoutingDest"])
    for name, u in fx.items():
        for kp, xs in sorted(vals[u["key"]].items()):
            nums = [x for x in xs if isinstance(x, (int, float)) and not isinstance(x, bool)]
            strs = sorted({x for x in xs if isinstance(x, str)})
            d: dict[str, Any] = {"kparam": kp}
            if nums:
                d.update(lo=float(min(nums)), hi=float(max(nums)))
            if strs:
                d["codes"] = strs
                codes[f"fx.{name}.{_snake(kp)}"] = set(strs)
            u["params"][_snake(kp)] = d
    out = {"source": f"Serum 2 {_unpack_version(host)}; factory presets in {root}",
           "plugin_params": list(P.parameters),
           "menus": menus, "fx": dict(sorted(fx.items(), key=lambda kv: kv[1]["type"])),
           "fx_codes": {k: sorted(v) for k, v in codes.items()},
           "mod_param_ids": {k: c.most_common(1)[0][0] for k, c in sorted(ids.items())}}
    TABLES_PATH.parent.mkdir(parents=True, exist_ok=True)
    TABLES_PATH.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    tables.cache_clear()
    return out


def _unpack_version(host) -> str:
    from .serum import _unpack, split_state
    return str(_unpack(split_state(host.init_state)[0])[0].get("productVersion", "?"))


def check_paths(host=None, keys: list[str] | None = None) -> list[str]:
    """Problems with the map, checked against the hosted plug-in: for each key with a plug-in name, set that
    parameter and confirm the tree changes where the map says (and nowhere else in plainParams)."""
    from . import serum
    host = host or serum.SerumHost.get()
    P = host.plugin
    bad = []
    names = set(P.parameters)
    for p in _P.values():
        if keys and p.key not in keys:
            continue
        if not p.raw or not p.kparam:
            continue
        if p.raw not in names:
            bad.append(f"{p.key}: the plug-in has no parameter {p.raw!r}")
            continue
        P.raw_state = host.init_state
        base = tree_get(_state_tree(host), p.module, p.kparam)
        hit = False
        for x in (0.13, 0.87):
            P.raw_state = host.init_state
            P.parameters[p.raw].raw_value = x
            if tree_get(_state_tree(host), p.module, p.kparam) != base:
                hit = True
                break
        if not hit:
            bad.append(f"{p.key}: setting {p.raw} does not change {p.module}.{p.kparam}")
    P.raw_state = host.init_state
    return bad


if __name__ == "__main__":  # pragma: no cover
    import sys
    if "--rebuild" in sys.argv:
        t = build_tables(progress=lambda m: print("·", m, file=sys.stderr))
        print(f"wrote {TABLES_PATH}: {len(t['menus'])} menus, {len(t['fx'])} FX units, {len(t['mod_param_ids'])} mod destinations")
    if "--check" in sys.argv:
        problems = check_paths()
        print("\n".join(problems) or "every mapped plug-in parameter lands where the map says")
