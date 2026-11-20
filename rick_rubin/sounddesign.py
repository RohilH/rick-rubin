"""What a synth sound does over one note, in numbers — the facts a sound-design brief talks about.

`describe_sound` measures one played note (a Serum render, or any wav of a single sound):

  envelope   attack, decay, sustain (dB under the peak), release after the note-off
  tone       spectral centroid early / late in the held part (a filter opening or closing), spectral tilt
             (dB per octave, 100 Hz - 10 kHz), harmonic-to-noise ratio, how many harmonics stand within 30 dB of
             the strongest, odd-vs-even harmonic balance (saturation and square-ish waves lift the odd ones)
  balance    share of energy per band (sub, bass, low-mid, mid, high, air) and stereo side share per band
  movement   how much brightness and level move while the note is held, and the rate of that movement
             (from the autocorrelation of the centroid/level curves: an LFO on the filter shows up here)
  pitch      the note it plays (with octave and cents), how steady it is, and any pitch drop at the start

It adds words to the shared vocabulary (`samples.character_words`): opens / closes, moving, noisy, pure / rich,
odd-heavy / even-heavy, plucky, pitch-drop, drifting. `describe_table` prints several sounds side by side; the
first row is the reference the others are compared to.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np

FRAME_S = 0.005
OCT_EDGES = [100, 200, 400, 800, 1600, 3200, 6400, 12800]


def _level_curve(m: np.ndarray, sr: int, hold_s: float = 0.01) -> np.ndarray:
    """Peak-hold level in dB every 5 ms: the largest |sample| within `hold_s` around each point. With `hold_s` longer
    than a period of the note, the curve follows the envelope rather than the waveform."""
    from scipy.ndimage import maximum_filter1d
    k = max(1, sr // 1000)
    env = np.abs(m[: len(m) // k * k]).reshape(-1, k).max(axis=1)            # 1 ms
    env = maximum_filter1d(env, size=max(1, int(round(hold_s * 1000))), mode="nearest")
    step = int(FRAME_S * 1000)
    return 20 * np.log10(env[::step] + 1e-9)


def _stft(m: np.ndarray, sr: int, n: int = 2048, hop: int = 512):
    if len(m) < n:
        m = np.pad(m, (0, n - len(m)))
    frames = 1 + (len(m) - n) // hop
    idx = np.arange(n)[None, :] + hop * np.arange(frames)[:, None]
    spec = np.abs(np.fft.rfft(m[idx] * np.hanning(n), axis=1)) ** 2
    return np.fft.rfftfreq(n, 1 / sr), spec, hop / sr


def _rate(curve: np.ndarray, dt: float) -> float | None:
    """Dominant periodic rate (Hz) of a curve, from its autocorrelation; None when nothing repeats."""
    c = curve - curve.mean()
    if len(c) < 8 or np.std(c) < 1e-9:
        return None
    ac = np.correlate(c, c, "full")[len(c) - 1:]
    ac /= ac[0] + 1e-12
    lo = max(2, int(round(1 / 12.0 / dt)))           # nothing faster than 12 Hz (faster is the note itself, or a growl)
    hi = int(len(ac) * 0.65)                          # at least ~1.5 periods inside the held part
    if hi <= lo + 2:
        return None
    seg = ac[lo:hi]
    peaks = [i for i in range(1, len(seg) - 1) if seg[i] >= seg[i - 1] and seg[i] >= seg[i + 1] and seg[i] > 0.3]
    if not peaks:
        return None
    return 1.0 / ((peaks[0] + lo) * dt)


def describe_sound(sr: int, x: np.ndarray, name: str = "", held_s: float | None = None, bpm: float | None = None) -> dict:
    """Measurements of one note. `held_s`: how long the key was held (for sustain/release); `bpm` puts the
    movement rate in note values too."""
    from .analysis import WIDTH_BANDS, stereo_stats
    from .pitch import hz, track_pitch
    from .samples import describe_audio
    from .theory import name as pitch_name
    if x.ndim == 1:
        x = x[:, None]
    if x.shape[1] == 1:
        x = np.repeat(x, 2, axis=1)
    base = describe_audio(sr, x, name)
    m = x.mean(axis=1).astype(np.float64)
    times, midi = track_pitch(x, sr, fmin=25.0, fmax=2000.0)
    f0_all = hz(float(np.nanmedian(midi))) if np.isfinite(midi).sum() >= 5 else None
    lv = _level_curve(m, sr, max(0.01, 1.5 / f0_all) if f0_all else 0.01)
    top = float(lv.max())
    t = lambda i: i * FRAME_S
    on = np.flatnonzero(lv > top - 40)
    onset = int(on[0]) if len(on) else 0
    peak_i = int(np.flatnonzero(lv >= top - 1.0)[0])                  # first time it is (nearly) at full level
    rise = np.flatnonzero(lv >= top + 20 * np.log10(0.1))
    a10 = int(rise[0]) if len(rise) else onset
    held_end = int(round(held_s / FRAME_S)) if held_s else None
    if held_end is None or held_end >= len(lv):
        loud = np.flatnonzero(lv > top - 60)
        held_end = int(loud[-1]) if len(loud) else len(lv) - 1
    held_end = max(held_end, peak_i + 2)
    attack_ms = float(t(peak_i - a10) * 1000)                         # 10 % -> full level
    # sustain: the level over the last third of the held part, relative to full level (floored at -90 dB)
    s0 = peak_i + max(1, (held_end - peak_i) * 2 // 3)
    sustain = max(top - 90.0, float(np.median(lv[s0:held_end]))) if held_end > s0 else top
    sus_rel = sustain - top
    # decay: from full level until it first comes within 1 dB of the sustain level (or 40 dB down, for a pluck)
    target = max(sustain, top - 40.0) + 1.0
    hit = np.flatnonzero(lv[peak_i:held_end] <= target)
    decay_ms = float(t(int(hit[0])) * 1000) if len(hit) and sus_rel < -1.0 else 0.0
    # release: from the note-off until 40 dB under the level at note-off
    release_ms = None
    if held_s and held_end < len(lv) - 2:
        ref = lv[held_end]
        rel = np.flatnonzero(lv[held_end:] < ref - 40)
        release_ms = float(t(int(rel[0])) * 1000) if len(rel) else float(t(len(lv) - held_end) * 1000)
    # tone over the held part (from 20 ms after the onset to the note-off)
    f, spec, dt = _stft(m, sr)
    fr = lambda i: min(spec.shape[0] - 1, max(0, int(round(t(i) / dt))))
    a0, a1 = fr(onset + 4), fr(held_end)
    if a1 <= a0 + 2:
        a1 = min(spec.shape[0], a0 + 3)
    body = spec[a0:a1]
    band = (f >= 20) & (f < 20000)
    bright = (body[:, band] * f[band]).sum(axis=1) / (body[:, band].sum(axis=1) + 1e-12)
    k = max(1, len(bright) // 6)
    early, late = float(np.median(bright[:k])), float(np.median(bright[-k:]))
    avg = body.mean(axis=0)
    oct_db = []
    for lo, hi in zip(OCT_EDGES[:-1], OCT_EDGES[1:]):
        sel = (f >= lo) & (f < hi)
        oct_db.append(10 * np.log10(avg[sel].sum() + 1e-14))
    tilt = float(np.polyfit(np.log2(np.sqrt(np.array(OCT_EDGES[:-1]) * np.array(OCT_EDGES[1:]))), oct_db, 1)[0])
    # movement while held, once the decay has settled
    settle = peak_i + int(decay_ms / 1000 / FRAME_S)
    if held_end - settle < 0.5 * (held_end - peak_i):                 # a "decay" that eats half the note is movement, not a decay
        settle = peak_i
    held_c = bright[max(0, fr(settle) - a0):]
    lv_held = lv[settle:held_end]
    move_pct = float(100 * np.std(held_c) / (np.mean(held_c) + 1e-9)) if len(held_c) > 4 else 0.0
    wobble_db = float(np.std(lv_held)) if len(lv_held) > 4 else 0.0
    rate = _rate(np.log(held_c + 1), dt) if move_pct > 3 else None
    if rate is None and wobble_db > 1.0:
        rate = _rate(lv_held, FRAME_S)
    # pitch and harmonics, over the held part
    sel = (times >= t(onset) + 0.02) & (times <= t(held_end)) & ~np.isnan(midi)
    pitch = pitch_txt = None
    stab = drop = None
    hnr = n_harm = odd_even = None
    if sel.sum() >= 5:
        p = midi[sel]
        pitch = float(np.median(p))
        stab = float(np.std((p - pitch) * 100))
        first = midi[(times >= t(onset)) & (times <= t(onset) + 0.04) & ~np.isnan(midi)]
        drop = float((np.median(first) - pitch) * 100) if len(first) else 0.0
        pitch_txt = f"{pitch_name(int(round(pitch)))} {(pitch - round(pitch)) * 100:+.0f}c"
        f0 = hz(pitch)
        seg = m[int(t(max(settle, onset + 4)) * sr): int(t(held_end) * sr)]
        if len(seg) >= int(0.1 * sr):
            n = 1 << int(np.ceil(np.log2(len(seg))))
            S = np.abs(np.fft.rfft(seg * np.hanning(len(seg)), n)) ** 2
            F = np.fft.rfftfreq(n, 1 / sr)
            harm = np.zeros_like(S, dtype=bool)
            amps = []
            for h in range(1, 41):
                fc = h * f0
                if fc > min(16000, sr / 2 - 100):
                    break
                w = (F > fc * (1 - 0.015) - 3) & (F < fc * (1 + 0.015) + 3)       # 1.5 %: room for unison detune
                harm |= w
                amps.append(S[w].sum())
            tot = S[(F >= 20) & (F < 16000)].sum() + 1e-14
            hs = S[harm].sum()
            hnr = float(10 * np.log10(hs / max(tot - hs, 1e-14)))
            if len(amps) >= 3:
                a = np.array(amps) + 1e-14
                n_harm = int((10 * np.log10(a / a.max()) > -30).sum())
                odd, even = a[2::2].sum(), a[1::2].sum()                    # harmonics 3, 5, 7 ... and 2, 4, 6 ...
                odd_even = float(10 * np.log10(odd / even))
    st = stereo_stats(x, sr)
    d = {
        "name": name, "seconds": len(x) / sr, "peak_db": base["peak_db"], "lufs": base["lufs"],
        "attack_ms": attack_ms, "decay_ms": decay_ms, "sustain_db": float(sus_rel), "release_ms": release_ms,
        "centroid_early_hz": early, "centroid_late_hz": late, "tilt_db_oct": tilt, "hnr_db": hnr, "harmonics": n_harm, "odd_even_db": odd_even,
        "bands": base["bands"], "side": {nm: float(st.bands[nm][0]) for nm, _, _ in WIDTH_BANDS}, "side_pct": float(st.side_pct),
        "movement_pct": move_pct, "wobble_db": wobble_db, "rate_hz": rate, "pitch": pitch, "pitch_txt": pitch_txt,
        "pitch_wobble_cents": stab, "pitch_drop_cents": drop,
    }
    if rate and bpm:
        beats = (bpm / 60.0) / rate
        d["rate_beats"] = beats
    # the shared words, from this table's own numbers: attack as measured here; "decay" in the shared vocabulary is
    # the time to fall 20 dB while held (NaN = sustained)
    fall = np.flatnonzero(lv[peak_i:held_end] < top - 20)
    d["character"] = sound_words(d, dict(base, attack_ms=attack_ms, decay_ms=float(t(int(fall[0])) * 1000) if len(fall) else float("nan")))
    return d


def sound_words(d: dict, base: dict | None = None) -> list[str]:
    """The shared character words plus sound-design ones:
    opens / closes   centroid at the end of the held part > 1.4x / < 0.7x the start (a filter envelope or sweep)
    moving           brightness moves > 8 % or level > 1.5 dB while held, at a steady rate (an LFO)
    noisy · pure · rich   harmonic-to-noise < 6 dB · fewer than 4 harmonics within 30 dB · 15 or more
    odd-heavy / even-heavy  odd harmonics 6 dB above / below the even ones (square-ish or saturated / saw-like is ~0)
    plucky           falls more than 20 dB within 400 ms while held
    pitch-drop       starts > 100 cents above the note it settles on · drifting: pitch wobbles > 8 cents"""
    from .samples import character_words
    w = list(character_words(base)) if base else []
    if d["centroid_late_hz"] > 1.4 * d["centroid_early_hz"]:
        w.append("opens")
    elif d["centroid_late_hz"] < 0.7 * d["centroid_early_hz"]:
        w.append("closes")
    if (d["movement_pct"] > 8 or d["wobble_db"] > 1.5) and d.get("rate_hz"):
        w.append("moving")
    if d["hnr_db"] is not None:
        if d["hnr_db"] < 6:
            w.append("noisy")
        if d["harmonics"] is not None and d["harmonics"] < 4:
            w.append("pure")
        elif d["harmonics"] is not None and d["harmonics"] >= 15:
            w.append("rich")
        if d["odd_even_db"] is not None and d["odd_even_db"] > 6:
            w.append("odd-heavy")
        elif d["odd_even_db"] is not None and d["odd_even_db"] < -6:
            w.append("even-heavy")
    if d["sustain_db"] < -20 and d["decay_ms"] < 400:
        w.append("plucky")
    if d["pitch_drop_cents"] is not None and d["pitch_drop_cents"] > 100:
        w.append("pitch-drop")
    if d["pitch_wobble_cents"] is not None and d["pitch_wobble_cents"] > 8:
        w.append("drifting")
    return list(dict.fromkeys(w))


def _f(v, fmt="{:.0f}", none="—") -> str:
    return none if v is None or (isinstance(v, float) and not math.isfinite(v)) else fmt.format(v)


def _rate_txt(d: dict) -> str:
    if not d.get("rate_hz"):
        return "—"
    s = f"{d['rate_hz']:.2f} Hz"
    if d.get("rate_beats"):
        b = d["rate_beats"]
        s += f" ({b:.2f} beats)" if b < 4 else f" ({b / 4:.2f} bars)"
    return s


HEAD = ("| sound | attack | decay | sustain | release | bright early→late | tilt dB/oct | harm/noise | harmonics (odd-even) | "
        "sub/bass/lowmid/mid/high/air % | side low/lowmid/mid/high % | movement | pitch | words |")


def row(d: dict) -> str:
    b, s = d["bands"], d["side"]
    return (f"| {d['name']} | {_f(d['attack_ms'])} ms | {_f(d['decay_ms'])} ms | {_f(d['sustain_db'], '{:+.1f}')} dB | {_f(d['release_ms'])} ms | "
            f"{_f(d['centroid_early_hz'])}→{_f(d['centroid_late_hz'])} Hz | {_f(d['tilt_db_oct'], '{:+.1f}')} | {_f(d['hnr_db'], '{:.1f}')} dB | "
            f"{_f(d['harmonics'])} ({_f(d['odd_even_db'], '{:+.1f}')} dB) | "
            f"{b['sub']:.0f}/{b['bass']:.0f}/{b['lowmid']:.0f}/{b['mid']:.0f}/{b['high']:.0f}/{b['air']:.1f} | "
            f"{s['low']:.1f}/{s['lowmid']:.1f}/{s['mid']:.1f}/{s['high']:.1f} | "
            f"{_f(d['movement_pct'], '{:.0f}')}% {_f(d['wobble_db'], '{:.1f}')} dB {_rate_txt(d)} | "
            f"{d['pitch_txt'] or '—'}{_wobble(d)} | {' '.join(d['character'])} |")


def _wobble(d: dict) -> str:
    return "" if d["pitch_wobble_cents"] is None else f" ±{d['pitch_wobble_cents']:.0f}c"


def describe_table(rows: list[dict]) -> str:
    """Sounds side by side; with more than one, a second table says how each differs from the first."""
    L = [HEAD, "|" + "---|" * (HEAD.count("|") - 1)]
    L += [row(d) for d in rows]
    if len(rows) > 1:
        ref = rows[0]
        L += ["", f"changes against {ref['name']}:"]
        for d in rows[1:]:
            L.append(f"- {d['name']}: " + delta_text(ref, d))
    return "\n".join(L)


def delta_text(a: dict, b: dict) -> str:
    """'brighter +38% early / +12% late, sustain +3.1 dB, odd-even +4.2 dB, side(high) +6%; words +rich -warm'"""
    out = []

    def pct(x, y):
        return 100.0 * (y - x) / x if x else 0.0
    for k, label in (("centroid_early_hz", "bright early"), ("centroid_late_hz", "bright late")):
        v = pct(a[k], b[k])
        if abs(v) >= 5:
            out.append(f"{label} {v:+.0f}%")
    for k, label, unit, th in (("attack_ms", "attack", " ms", 2), ("decay_ms", "decay", " ms", 15), ("sustain_db", "sustain", " dB", 0.8),
                               ("release_ms", "release", " ms", 15), ("tilt_db_oct", "tilt", " dB/oct", 0.4), ("hnr_db", "harm/noise", " dB", 1.0),
                               ("odd_even_db", "odd-even", " dB", 1.0), ("movement_pct", "movement", " %", 2), ("lufs", "loudness", " LU", 0.5)):
        x, y = a.get(k), b.get(k)
        if x is None or y is None or not (math.isfinite(x) and math.isfinite(y)):
            continue
        if abs(y - x) >= th:
            out.append(f"{label} {y - x:+.1f}{unit}" if unit.strip() in ("dB", "dB/oct", "LU") else f"{label} {y - x:+.0f}{unit}")
    if (a.get("harmonics") or 0) != (b.get("harmonics") or 0):
        out.append(f"harmonics {a.get('harmonics')}→{b.get('harmonics')}")
    for nm in ("sub", "bass", "lowmid", "mid", "high", "air"):
        dv = b["bands"][nm] - a["bands"][nm]
        if abs(dv) >= 3:
            out.append(f"{nm} {dv:+.0f}pt")
    for nm in ("low", "high"):
        dv = b["side"][nm] - a["side"][nm]
        if abs(dv) >= 3:
            out.append(f"side({nm}) {dv:+.0f}pt")
    wa, wb = set(a["character"]), set(b["character"])
    if wa != wb:
        out.append("words " + " ".join([f"+{w}" for w in sorted(wb - wa)] + [f"-{w}" for w in sorted(wa - wb)]))
    return ", ".join(out) or "no measurable change"


def describe_file(path: str | Path, held_s: float | None = None, bpm: float | None = None) -> dict:
    from .samples import read_audio
    sr, x = read_audio(path)
    return describe_sound(sr, x, Path(path).name, held_s, bpm)
