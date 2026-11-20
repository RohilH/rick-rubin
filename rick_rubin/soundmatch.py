"""How far a synth sound is from a target recording, and moving a few patch settings to close the gap.

`distance(target, candidate)` compares two recordings of the same notes after levelling them (loudness is a
fader, not a sound): the average spectrum (1/6-octave, dB), the level envelope over time, brightness early and
late in the note, stereo side share overall and in the low end, and the odd/even harmonic balance. It returns
one number and its parts, so the agent can see *what* still differs.

`fit(patch, target, keys)` is coordinate descent over a small set of patch keys the agent chose (from the patch
sheet: the handful that matter). Each step is one offline render of the target's notes, about a second. It
never touches keys it was not given, and it does not invent a sound: it moves the agent's knobs.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np

SR = 44100
WEIGHTS = {"spectrum": 1 / 3.0, "envelope": 1 / 6.0, "brightness": 1.5, "width": 0.1, "harmonics": 1 / 6.0}


def _level(x: np.ndarray) -> np.ndarray:
    m = x.mean(axis=1) if x.ndim > 1 else x
    r = float(np.sqrt(np.mean(m.astype(np.float64) ** 2))) + 1e-12
    return x / r * 0.1


def _spectrum(x: np.ndarray, sr: int) -> np.ndarray:
    from .pictures import _smooth_spectrum
    m = (x.mean(axis=1) if x.ndim > 1 else x).astype(np.float64)
    grid, db = _smooth_spectrum(m, sr, 120)
    sel = (grid >= 40) & (grid <= 16000)
    d = db[sel]
    return d - d.mean()


def features(sr: int, x: np.ndarray, held_s: float | None = None) -> dict:
    from .sounddesign import _level_curve, describe_sound
    x = _level(x)
    d = describe_sound(sr, x, "", held_s)
    f0 = None
    if d.get("pitch") is not None:
        from .pitch import hz
        f0 = hz(d["pitch"])
    lv = _level_curve(x.mean(axis=1), sr, max(0.01, 1.5 / f0) if f0 else 0.01)
    lv = np.maximum(lv - lv.max(), -50.0)
    return {"describe": d, "spectrum": _spectrum(x, sr), "level": lv}


def distance(a: dict, b: dict) -> tuple[float, dict]:
    """(total, parts) between two `features` (target first)."""
    da, db = a["describe"], b["describe"]
    n = min(len(a["level"]), len(b["level"]))
    parts = {
        "spectrum": float(np.mean(np.abs(a["spectrum"] - b["spectrum"]))),
        "envelope": float(np.mean(np.abs(a["level"][:n] - b["level"][:n]))),
        "brightness": abs(math.log2(max(db["centroid_early_hz"], 1) / max(da["centroid_early_hz"], 1))) +
                      abs(math.log2(max(db["centroid_late_hz"], 1) / max(da["centroid_late_hz"], 1))),
        "width": abs(db["side_pct"] - da["side_pct"]) + abs(db["side"]["low"] - da["side"]["low"]),
        "harmonics": abs((db["odd_even_db"] or 0.0) - (da["odd_even_db"] or 0.0)) if da["odd_even_db"] is not None and db["odd_even_db"] is not None else 0.0,
    }
    return float(sum(WEIGHTS[k] * v for k, v in parts.items())), parts


def parts_text(parts: dict) -> str:
    return (f"spectrum {parts['spectrum']:.1f} dB, envelope {parts['envelope']:.1f} dB, brightness {parts['brightness']:.2f} oct, "
            f"width {parts['width']:.1f} pt, odd-even {parts['harmonics']:.1f} dB")


# ---------------------------------------------------------------------------- fitting
@dataclass
class FitStep:
    n: int
    key: str
    value: Any
    dist: float
    kept: bool


@dataclass
class FitResult:
    patch: Any
    start: float
    best: float
    parts_start: dict
    parts_best: dict
    values: dict
    steps: list[FitStep] = field(default_factory=list)
    transpose: int = 0
    renders: int = 0


def onsets(sr: int, x: np.ndarray, rise_db: float = 9.0, min_gap_s: float = 0.05) -> list[float]:
    """Note starts: where the level jumps by `rise_db` within 40 ms (a repeated note retriggers even at one pitch)."""
    from .sounddesign import FRAME_S, _level_curve
    lv = _level_curve(x.mean(axis=1) if x.ndim > 1 else x, sr, 0.01)
    top = lv.max()
    out: list[int] = []
    first = np.flatnonzero(lv > top - 40)
    if len(first):
        out.append(int(first[0]))                                  # the first sound, even when the file starts on it
    for i in range(1, len(lv)):
        lo_i = max(0, i - 8)
        j = lo_i + int(np.argmin(lv[lo_i:i]))
        if lv[i] - lv[j] >= rise_db and lv[i] > top - 40:
            k = j + int(np.argmax(lv[j:i + 1] > lv[j] + 3.0))       # where the rise starts, not the bottom of the dip
            if (k - out[-1]) * FRAME_S >= min_gap_s:
                out.append(k)
    return [i * FRAME_S for i in out]


def target_notes(path, bpm: float | None = None) -> list[tuple[int, float, float, int]]:
    """The notes a single-voice recording plays, as render notes (pitch, start s, length s, velocity 100): starts and
    ends from the level (onsets split repeated notes), pitches from the pitch tracker inside each note."""
    from .pitch import track_pitch
    from .samples import read_audio
    from .sounddesign import FRAME_S, _level_curve
    sr, x = read_audio(path)
    starts = onsets(sr, x)
    times, midi = track_pitch(x, sr, fmin=25.0, fmax=2000.0)
    lv = _level_curve(x.mean(axis=1), sr, 0.01)
    out = []
    for k, a in enumerate(starts):
        b = starts[k + 1] if k + 1 < len(starts) else len(x) / sr
        sel = (times >= a + 0.02) & (times < b) & ~np.isnan(midi)
        if sel.sum() < 3:
            continue
        seg = lv[int(a / FRAME_S): int(b / FRAME_S)]
        loud = np.flatnonzero(seg > seg.max() - 12) if len(seg) else []
        end = a + (loud[-1] + 1) * FRAME_S if len(loud) else b
        out.append((int(round(float(np.median(midi[sel])))), round(a, 4), round(float(max(0.03, min(b, end) - a)), 4), 100))
    _ = bpm
    return out


def _render(patch, notes, seconds: float, bpm: float | None, transpose: int = 0) -> np.ndarray:
    from . import serum
    _, a = serum.render_preset(patch, [(p + transpose, s, d, v) for p, s, d, v in notes], seconds, bpm=bpm)
    return a


def _key_range(patch, key: str) -> tuple[float, float, bool]:
    """(lo, hi, log scale?) for a key the fit may move."""
    from . import serum_params as sp
    from .serum_patch import _fx_key
    fx = _fx_key(key)
    if fx:
        d = sp.fx_units()[fx[1]]["params"].get(fx[3]) or {}
        lo, hi = d.get("lo"), d.get("hi")
        if lo is None or hi is None or lo == hi:
            raise ValueError(f"{key}: no numeric range known (factory presets never vary it)")
        return float(lo), float(hi), lo > 0 and hi / max(lo, 1e-9) > 50
    p = sp.lookup(key)
    if p.lo is None or p.conv.kind in ("menu", "rate", "bool", "text", "code"):
        raise ValueError(f"{key} is not a number the fit can move (it is a {p.conv.kind}); set it yourself")
    lo, hi = float(p.lo), float(p.hi)
    if p.unit == "ms":
        lo = max(lo, 0.5)
    if p.unit == "dB" and lo < -60:
        lo = -60.0
    return lo, hi, p.unit in ("Hz", "ms") and lo > 0


def fit(patch, target_path, keys: list[str], iters: int = 30, notes=None, bpm: float | None = None, progress=None) -> FitResult:
    """Move `keys` of `patch` (a serum_patch.Patch) so its render of the target's notes measures closer to the target."""
    from .samples import read_audio
    say = progress or (lambda *_: None)
    sr, tx = read_audio(target_path)
    seconds = len(tx) / sr
    notes = notes or target_notes(target_path, bpm)
    if not notes:
        raise ValueError("no notes found in the target; give --note/--secs to play one yourself")
    held = notes[-1][1] + notes[-1][2] if len(notes) == 1 else None
    tf = features(sr, tx, held)
    base = patch.copy()
    # play in the register the target sounds in (patches carry their own octave settings)
    probe = _render(base, notes, seconds, bpm)
    pf = features(SR, probe, held)
    transpose = 0
    tp, cp = tf["describe"].get("pitch"), pf["describe"].get("pitch")
    if tp is not None and cp is not None:
        transpose = int(12 * round((tp - cp) / 12))
    renders = 1

    def score(p) -> tuple[float, dict]:
        nonlocal renders
        renders += 1
        return distance(tf, features(SR, _render(p, notes, seconds, bpm, transpose), held))
    cur = base
    best, parts = score(cur)
    start, parts0 = best, parts
    ranges = {k: _key_range(cur, k) for k in keys}
    vals = {}
    for k in keys:
        v = cur.get(k)
        lo, hi, _ = ranges[k]
        vals[k] = float(v) if isinstance(v, (int, float)) and math.isfinite(v) else (lo + hi) / 2
    step = {k: (1.0 if ranges[k][2] else 0.25 * (ranges[k][1] - ranges[k][0])) for k in keys}   # log keys: an octave
    steps: list[FitStep] = []
    n = 0
    i = 0
    while renders < iters + 2 and any(step[k] > (0.02 if ranges[k][2] else 0.004 * (ranges[k][1] - ranges[k][0])) for k in keys):
        k = keys[i % len(keys)]
        i += 1
        lo, hi, logk = ranges[k]
        improved = False
        for sign in (+1, -1):
            if renders >= iters + 2:
                break
            v = vals[k] * (2 ** (sign * step[k])) if logk else vals[k] + sign * step[k]
            v = min(hi, max(lo, v))
            if abs(v - vals[k]) < 1e-9:
                continue
            cand = cur.copy()
            cand.set(k, v)
            d, pr = score(cand)
            n += 1
            steps.append(FitStep(n, k, v, d, d < best))
            say(f"{n:3d} {k}={v:.4g} -> {d:.3f}" + (" kept" if d < best else ""))
            if d < best:
                best, parts, cur, vals[k] = d, pr, cand, v
                improved = True
                break
        if not improved:
            step[k] /= 2
    return FitResult(cur, start, best, parts0, parts, vals, steps, transpose, renders)
