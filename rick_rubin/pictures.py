"""Pictures of what a producer would look at on a plug-in — drawn for an agent to read.

* `imager_png`   — a stereo imager: vectorscope, correlation over time, width by band.
* `spectrum_png` — a spectrum analyzer: one or several sounds overlaid on a log-frequency axis.
* `serum_png`    — the important parts of a Serum 2 patch: oscillator shapes, envelopes, filter,
                   macros, FX chain, and what a played note actually looks and sounds like.

Tables stay the primary reading view (they are exact); these are for the moments a shape says
more than numbers: is the low end a vertical line, where do two sounds fight, what does this
patch's envelope do.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np

from .samples import read_audio

BAND_EDGES = [20, 60, 120, 250, 500, 1000, 2000, 4000, 8000, 16000]
REGIONS = [("sub", 20, 60), ("bass", 60, 200), ("low-mid", 200, 800), ("mid", 800, 4000), ("high", 4000, 12000), ("air", 12000, 20000)]


def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def _smooth_spectrum(m: np.ndarray, sr: int, points: int = 240) -> tuple[np.ndarray, np.ndarray]:
    """Average spectrum in dB on a log-frequency grid (about 1/6-octave smoothing)."""
    n = 8192
    if len(m) < n:
        m = np.pad(m, (0, n - len(m)))
    hop = n // 2
    win = np.hanning(n)
    acc = np.zeros(n // 2 + 1)
    k = 0
    for i in range(0, len(m) - n + 1, hop):
        acc += np.abs(np.fft.rfft(m[i:i + n] * win)) ** 2
        k += 1
    acc /= max(1, k)
    f = np.fft.rfftfreq(n, 1 / sr)
    grid = np.geomspace(20, min(20000, sr / 2 * 0.98), points)
    out = np.empty(points)
    for j, fc in enumerate(grid):
        lo, hi = fc / 2 ** (1 / 12), fc * 2 ** (1 / 12)
        sel = (f >= lo) & (f < hi)
        out[j] = acc[sel].mean() if sel.any() else acc[np.argmin(np.abs(f - fc))]
    return grid, 10 * np.log10(out + 1e-14)


def _freq_axis(ax):
    ax.set_xscale("log")
    ax.set_xlim(20, 20000)
    ax.set_xticks([20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000])
    ax.set_xticklabels(["20", "50", "100", "200", "500", "1k", "2k", "5k", "10k", "20k"], fontsize=7)
    for _, lo, _ in REGIONS[1:]:
        ax.axvline(lo, color="0.75", lw=0.5, zorder=0)


# ============================================================================ imager
def imager_png(wav: str | Path, out: str | Path, title: str | None = None, t0: float = 0.0, t1: float | None = None) -> Path:
    """Vectorscope + correlation over time + width per band for `wav` (or the span t0..t1 seconds of it)."""
    from scipy.signal import butter, sosfilt
    plt = _plt()
    sr, x = read_audio(wav)
    x = x[int(t0 * sr): int(t1 * sr) if t1 else None]
    if x.shape[1] == 1:
        x = np.repeat(x, 2, axis=1)
    L, R = x[:, 0].astype(np.float64), x[:, 1].astype(np.float64)
    mid, side = (L + R) / 2, (L - R) / 2
    peak = max(np.abs(mid).max(), np.abs(side).max(), 1e-9)
    fig = plt.figure(figsize=(13, 4.6))
    gs = fig.add_gridspec(2, 3, width_ratios=[1, 1.5, 1.3], height_ratios=[1, 1], hspace=0.45, wspace=0.28,
                          left=0.05, right=0.98, top=0.88, bottom=0.12)

    ax = fig.add_subplot(gs[:, 0])                                   # vectorscope: up = mono, sideways = width
    ax.hist2d(side / peak, mid / peak, bins=160, range=[[-1, 1], [-1, 1]], cmap="magma", norm="log", cmin=1)
    ax.plot([-1, 1], [-1, 1], color="0.6", lw=0.5)
    ax.plot([-1, 1], [1, -1], color="0.6", lw=0.5)
    ax.axvline(0, color="0.4", lw=0.5)
    ax.set_facecolor("black")
    ax.set_xlabel("side (L−R): width", fontsize=8)
    ax.set_ylabel("mid (L+R): mono", fontsize=8)
    ax.set_title("vectorscope — a vertical line is mono;\na round cloud is wide; wider than tall is out of phase", fontsize=8)
    ax.set_xticks([-1, 0, 1]); ax.set_xticklabels(["L", "", "R"])
    ax.set_yticks([])

    ax = fig.add_subplot(gs[0, 1])                                   # correlation over time
    win = int(0.25 * sr)
    n = max(1, len(L) // win)
    corr, tt = [], []
    for i in range(n):
        a, b = L[i * win:(i + 1) * win], R[i * win:(i + 1) * win]
        d = np.sqrt((a * a).sum() * (b * b).sum())
        corr.append((a * b).sum() / d if d > 1e-9 else 1.0)
        tt.append(t0 + (i + 0.5) * win / sr)
    ax.axhspan(-1, 0, color="#d33", alpha=0.12)
    ax.plot(tt, corr, color="C0", lw=1)
    ax.set_ylim(-1, 1.05)
    ax.set_xlim(tt[0], tt[-1] if len(tt) > 1 else tt[0] + 1)
    ax.set_title("correlation over time (+1 mono · 0 very wide · below 0 cancels in mono)", fontsize=8)
    ax.set_xlabel("seconds", fontsize=7)
    ax.tick_params(labelsize=7)

    ax = fig.add_subplot(gs[1, 1])                                   # side level over time
    k = int(0.05 * sr)
    m_env = np.sqrt(np.mean(mid[: len(mid) // k * k].reshape(-1, k) ** 2, axis=1) + 1e-12)
    s_env = np.sqrt(np.mean(side[: len(side) // k * k].reshape(-1, k) ** 2, axis=1) + 1e-12)
    te = t0 + (np.arange(len(m_env)) + 0.5) * k / sr
    ax.plot(te, 20 * np.log10(m_env), color="0.3", lw=0.8, label="mid")
    ax.plot(te, 20 * np.log10(s_env), color="C1", lw=0.8, label="side")
    ax.set_ylim(-70, 0)
    ax.set_xlim(te[0], te[-1])
    ax.legend(fontsize=7, loc="lower right", ncol=2)
    ax.set_title("mid and side level (dB)", fontsize=8)
    ax.set_xlabel("seconds", fontsize=7)
    ax.tick_params(labelsize=7)

    ax = fig.add_subplot(gs[:, 2])                                   # width per band
    labels, vals, cors = [], [], []
    for lo, hi in zip(BAND_EDGES[:-1], BAND_EDGES[1:]):
        sos = butter(4, [lo, min(hi, sr / 2 * 0.99)], btype="band", fs=sr, output="sos")
        l, r = sosfilt(sos, L), sosfilt(sos, R)
        em, es = (((l + r) / 2) ** 2).sum(), (((l - r) / 2) ** 2).sum()
        d = np.sqrt((l * l).sum() * (r * r).sum())
        labels.append(f"{lo if lo < 1000 else str(lo // 1000) + 'k'}–{hi if hi < 1000 else str(hi // 1000) + 'k'}")
        vals.append(100 * es / (em + es) if em + es > 1e-12 else 0.0)
        cors.append((l * r).sum() / d if d > 1e-9 else 1.0)
    y = np.arange(len(labels))
    colors = ["#d33" if (lo < 120 and v > 10) or c < 0 else "C1" for (lo, v, c) in zip(BAND_EDGES[:-1], vals, cors)]
    ax.barh(y, vals, color=colors)
    for yi, v, c in zip(y, vals, cors):
        ax.text(min(v + 1.5, 44), yi, f"{v:.0f}%  corr {c:+.2f}", va="center", fontsize=7)
    ax.set_yticks(y); ax.set_yticklabels([s + " Hz" for s in labels], fontsize=7)
    ax.set_xlim(0, 55)
    ax.axvline(50, color="0.5", lw=0.5, ls=":")
    ax.set_title("width by band: side % (0 = mono, 50 = L and R unrelated)\nred = wide low end or out of phase", fontsize=8)
    ax.tick_params(labelsize=7)
    fig.suptitle(title or f"stereo image — {Path(wav).name}", fontsize=11)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=110)
    plt.close(fig)
    return out


# ============================================================================ spectrum analyzer
def spectrum_png(sounds: list[tuple[str, str | Path]], out: str | Path, title: str | None = None,
                 spans: dict[str, tuple[float, float]] | None = None) -> Path:
    """Average spectra of one or more files overlaid (label, path). `spans` limits a label to (t0, t1) seconds.
    Read it like an analyzer on an EQ: where two curves sit on top of each other they compete; a hump
    is a resonance; a curve that stays high below 100 Hz owns the low end."""
    plt = _plt()
    fig, ax = plt.subplots(figsize=(13, 4.4))
    fig.subplots_adjust(left=0.06, right=0.98, top=0.9, bottom=0.12)
    top = -200.0
    for i, (label, path) in enumerate(sounds):
        sr, x = read_audio(path)
        if spans and label in spans:
            a, b = spans[label]
            x = x[int(a * sr): int(b * sr)]
        f, db = _smooth_spectrum(x.mean(axis=1).astype(np.float64), sr)
        top = max(top, db.max())
        ax.plot(f, db, lw=1.3, color=f"C{i}", label=label)
        if len(sounds) == 1:
            ax.fill_between(f, db, -200, color=f"C{i}", alpha=0.15)
        pk = int(np.argmax(db))
        ax.annotate(f"{f[pk]:.0f} Hz", (f[pk], db[pk]), textcoords="offset points", xytext=(4, 4), fontsize=7, color=f"C{i}")
    _freq_axis(ax)
    ax.set_ylim(top - 72, top + 6)
    for name, lo, hi in REGIONS:
        ax.text(np.sqrt(lo * hi), top + 3, name, ha="center", fontsize=7, color="0.45")
    ax.set_ylabel("dB (relative)", fontsize=8)
    ax.set_xlabel("Hz", fontsize=8)
    ax.grid(axis="y", color="0.85", lw=0.5)
    ax.legend(fontsize=8, loc="lower left", ncol=min(4, len(sounds)))
    ax.tick_params(labelsize=7)
    fig.suptitle(title or "spectrum", fontsize=11)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=110)
    plt.close(fig)
    return out


# ============================================================================ serum patch panel
def _secs(text: str) -> float | None:
    m = re.match(r"\s*(-?[\d.]+)\s*(ms|s)?", str(text))
    if not m:
        return None
    v = float(m.group(1))
    return v / 1000.0 if m.group(2) == "ms" else v


def _num(text: str) -> float | None:
    m = re.match(r"\s*(-?[\d.]+)", str(text))
    return float(m.group(1)) if m else None


def serum_png(preset: str | Path, out: str | Path, note: str | int = "C2", params: dict | None = None) -> Path:
    """One picture of a Serum 2 patch: the wavetable frame each oscillator plays, the three main
    envelopes, the macros and what they move, the FX chain, and a note rendered through the plug-in
    (waveform, spectrum, level over time)."""
    from . import serum
    from .theory import name as pname, note as parse_note
    plt = _plt()
    path = serum.find(str(preset))
    meta, tree = serum.read_preset(path)
    host = serum.SerumHost.get()
    name = host.load(path)
    host.set(params)
    val = {n: v for n, v, _ in host.params()}
    pitch = parse_note(note) if isinstance(note, str) else int(note)
    sr = 44100
    audio = host.render([(pitch, 0.0, 1.0, 100)], 2.5, sr)
    mono = audio.mean(axis=1).astype(np.float64)

    fig = plt.figure(figsize=(14, 8))
    gs = fig.add_gridspec(3, 4, hspace=0.5, wspace=0.3, left=0.04, right=0.985, top=0.9, bottom=0.06)

    # --- oscillators: the wavetable frame in use
    tables_root = serum.preset_root().parent / "Tables"
    for col, (letter, idx) in enumerate((("a", 0), ("b", 1), ("c", 2))):
        ax = fig.add_subplot(gs[0, col])
        on = val.get(f"{letter}_enable", "Off").strip().lower() in ("on", "1")
        osc = tree.get(f"Oscillator{idx}", {})
        wt = osc.get(f"WTOsc{idx}", {}) if isinstance(osc, dict) else {}
        rel = wt.get("relativePathToWT") if isinstance(wt, dict) else None
        drawn = False
        if rel and (tables_root / rel).exists():
            try:
                _, w = read_audio(tables_root / rel)
                w = w[:, 0]
                frames = max(1, len(w) // 2048)
                pos = _num(val.get(f"{letter}_wt_pos", "1")) or 1
                fi = int(max(0, min(frames - 1, round(pos) - 1)))
                ax.plot(w[fi * 2048:(fi + 1) * 2048], color="#3fbf5f" if on else "0.65", lw=1.4)
                ax.set_title(f"OSC {letter.upper()} {'ON' if on else 'off'} — {Path(rel).stem}, frame {fi + 1}/{frames}", fontsize=8,
                             color="k" if on else "0.5")
                drawn = True
            except Exception:  # noqa: BLE001
                pass
        if not drawn:
            ax.text(0.5, 0.5, "no wavetable\n(sample / granular / spectral)" if on else "off", ha="center", va="center", fontsize=8, color="0.5")
            ax.set_title(f"OSC {letter.upper()} {'ON' if on else 'off'}", fontsize=8, color="k" if on else "0.5")
        info = "  ".join(f"{k} {val[f'{letter}_{p}']}" for k, p in (("oct", "octave_oct"), ("semi", "semi_semitones"), ("fine", "fine_cents"),
                                                                   ("unison", "unison"), ("level", "level"), ("pan", "pan")) if f"{letter}_{p}" in val)
        ax.set_xlabel(info, fontsize=7)
        ax.set_xticks([]); ax.set_yticks([]); ax.set_ylim(-1.1, 1.1)

    # --- filter + sub/noise summary as text
    ax = fig.add_subplot(gs[0, 3])
    ax.axis("off")
    lines = []
    for k in (1, 2):
        if f"filter_{k}_on" in val:
            on = val[f"filter_{k}_on"].strip().lower() in ("on", "1")
            lines.append(f"FILTER {k} {'ON ' if on else 'off'} {val.get(f'filter_{k}_type', '')}")
            lines.append(f"   cutoff {val.get(f'filter_{k}_freq_hz', '?')} Hz  res {val.get(f'filter_{k}_res', '?')}  drive {val.get(f'filter_{k}_drive', '?')}")
    for label, key in (("SUB", "sub_enable"), ("NOISE", "noise_enable")):
        if key in val:
            lines.append(f"{label} {val[key]}" + (f"  level {val[label.lower() + '_level']}" if label.lower() + "_level" in val else ""))
    lines += [f"voices: {'mono' if val.get('mono_toggle', '').strip().lower() in ('on', '1') else 'poly'}  porta {val.get('porta_time', '?')}",
              f"main vol {val.get('main_vol', '?')}"]
    fx = [k[2:] for i, rack in sorted((kk, v) for kk, v in tree.items() if kk.startswith("FXRack") and isinstance(v, dict))
          for unit in (rack.get("FX") or []) for k in unit if k.startswith("FX")]
    lines.append("FX: " + (" → ".join(fx) if fx else "none"))
    ax.text(0, 1, "\n".join(ln[:46] for ln in lines), va="top", fontsize=7.5, family="monospace")
    ax.set_title("filters, voices, FX chain", fontsize=8)

    # --- envelopes
    for col, k in enumerate((1, 2, 3)):
        ax = fig.add_subplot(gs[1, col])
        a, h, d, r = (_secs(val.get(f"env_{k}_{p}", "")) for p in ("attack", "hold", "decay", "release"))
        s = _num(val.get(f"env_{k}_sustain", ""))
        if None not in (a, d, r) and s is not None:
            h = h or 0.0
            s_lin = 10 ** (s / 20) if s <= 0 and "dB" in val.get(f"env_{k}_sustain", "") else (s / 100 if s > 1 else s)
            hold_s = max(0.15, 0.25 * (a + h + d + r))
            ts = [0, a, a + h, a + h + d, a + h + d + hold_s, a + h + d + hold_s + r]
            ys = [0, 1, 1, s_lin, s_lin, 0]
            ax.plot(ts, ys, color="#2aa7d6", lw=1.6)
            ax.fill_between(ts, ys, color="#2aa7d6", alpha=0.25)
            ax.axvspan(ts[3], ts[4], color="0.9", zorder=0)
            ax.set_xlabel(f"A {val[f'env_{k}_attack']}  H {val.get(f'env_{k}_hold', '-')}  D {val[f'env_{k}_decay']}  "
                          f"S {val[f'env_{k}_sustain']}  R {val[f'env_{k}_release']}", fontsize=7)
        else:
            ax.text(0.5, 0.5, "n/a", ha="center", va="center", color="0.5")
        ax.set_title(f"ENV {k}" + (" (amp)" if k == 1 else ""), fontsize=8)
        ax.set_yticks([]); ax.tick_params(labelsize=6)

    # --- macros
    ax = fig.add_subplot(gs[1, 3])
    names, targets = {}, {}
    for kk, v in tree.items():
        if kk.startswith("Macro") and kk[5:].isdigit() and isinstance(v, dict):
            names[int(kk[5:])] = v.get("name", "")
        if kk.startswith("ModSlot") and isinstance(v, dict) and v.get("destModuleTypeString"):
            src = (v.get("source") or [None])[0]
            if isinstance(src, int) and serum.FIRST_MACRO_SOURCE <= src < serum.FIRST_MACRO_SOURCE + 8:
                targets.setdefault(src - serum.FIRST_MACRO_SOURCE, []).append(
                    f"{v['destModuleTypeString'].replace('Voice', '')}.{str(v.get('destModuleParamName', '')).replace('kParam', '')}")
    mv = [(_num(val.get(f"macro_{i + 1}", "0")) or 0.0) for i in range(8)]
    ax.barh(range(8), mv, color="#888")
    for i in range(8):
        label = names.get(i, "") + (" → " + ", ".join(targets[i][:3]) + ("…" if len(targets.get(i, [])) > 3 else "") if i in targets else "")
        text = f"{i + 1} {label}"
        ax.text(2, i, text if len(text) <= 52 else text[:51] + "…", va="center", fontsize=6.5)
    ax.set_xlim(0, 100); ax.set_ylim(7.6, -0.6); ax.set_yticks([])
    ax.set_title("macros: value and what each one moves", fontsize=8)
    ax.tick_params(labelsize=6)

    # --- the note it plays
    ax = fig.add_subplot(gs[2, 0])
    k = 220
    env = np.sqrt(np.mean(mono[: len(mono) // k * k].reshape(-1, k) ** 2, axis=1) + 1e-12)
    ax.plot(np.arange(len(env)) * k / sr, 20 * np.log10(env), color="0.2", lw=1)
    ax.axvspan(0, 1.0, color="0.92", zorder=0)
    ax.set_ylim(-70, 0)
    ax.set_title(f"level of a 1 s {pname(pitch)} (grey = key held)", fontsize=8)
    ax.set_xlabel("seconds", fontsize=7); ax.tick_params(labelsize=6)

    ax = fig.add_subplot(gs[2, 1])
    seg = mono[int(0.3 * sr): int(0.3 * sr) + int(sr * 4 / max(20.0, 440 * 2 ** ((pitch - 69) / 12)))]
    ax.plot(seg, color="#3fbf5f", lw=1)
    ax.set_title("output waveform (about 4 cycles, 0.3 s in)", fontsize=8)
    ax.set_xticks([]); ax.set_yticks([])

    ax = fig.add_subplot(gs[2, 2:])
    f, db = _smooth_spectrum(mono[: int(1.0 * sr)], sr)
    ax.plot(f, db, color="C3", lw=1.3)
    ax.fill_between(f, db, -200, color="C3", alpha=0.15)
    _freq_axis(ax)
    ax.set_ylim(db.max() - 72, db.max() + 6)
    f0 = 440 * 2 ** ((pitch - 69) / 12)
    ax.axvline(f0, color="0.3", lw=0.6, ls=":")
    ax.text(f0, db.max() + 2, f" played {pname(pitch)} = {f0:.0f} Hz", fontsize=7)
    ax.set_title("spectrum of that note — where the patch's energy sits", fontsize=8)
    ax.tick_params(labelsize=6)

    tags = ", ".join(t for t in meta.get("tags", []) if t != "Preview")
    fig.suptitle(f"Serum 2 — {name}" + (f"  [{tags}]" if tags else "") + (f"  with {params}" if params else ""), fontsize=12)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=105)
    plt.close(fig)
    return out


# ============================================================================ sample comparer
def audition_png(paths: list[str | Path], out: str | Path, title: str | None = None) -> Path:
    """Candidate samples side by side: every waveform on the same time and level scale (so length,
    punch and decay compare at a glance), their spectra overlaid, and the key numbers next to each."""
    from .samples import describe_sample
    plt = _plt()
    items = []
    for p in paths:
        sr, x = read_audio(p)
        items.append((Path(p), sr, x.mean(axis=1).astype(np.float64), describe_sample(p)))
    longest = max(len(m) / sr for _, sr, m, _ in items)
    span = longest if longest <= 2.5 else min(longest, 16.0)
    n = len(items)
    fig = plt.figure(figsize=(14, 1.0 + 0.95 * n + 3.6))
    gs = fig.add_gridspec(n + 1, 2, width_ratios=[2.2, 1.5], height_ratios=[0.95] * n + [3.6], hspace=0.35, wspace=0.03,
                          left=0.13, right=0.985, top=1 - 0.6 / (1.0 + 0.95 * n + 3.6), bottom=0.07)
    for i, (path, sr, m, d) in enumerate(items):
        ax = fig.add_subplot(gs[i, 0])
        k = max(1, int(sr * span / 1600))
        seg = m[: int(span * sr)]
        seg = seg[: len(seg) // k * k].reshape(-1, k)
        tt = np.arange(len(seg)) * k / sr
        ax.fill_between(tt, seg.min(axis=1), seg.max(axis=1), color=f"C{i}", lw=0)
        ax.set_xlim(0, span); ax.set_ylim(-1.05, 1.05); ax.set_yticks([])
        ax.set_ylabel(path.stem[:22], rotation=0, ha="right", va="center", fontsize=8, color=f"C{i}")
        if i < n - 1:
            ax.set_xticklabels([])
        else:
            ax.set_xlabel("seconds (same scale for all)", fontsize=7)
        ax.tick_params(labelsize=6)
        b = d["bands"]
        loud = f"{d['lufs']:.1f} LUFS" if d["lufs"] == d["lufs"] and d["lufs"] != float("-inf") else f"{d['rms_db']:.1f} dB rms"
        pitch = f"{d['pitch']} ({d['pitch_hz']:.0f} Hz, {d['cents']:+.0f}c)" if d["pitch"] else "unpitched"
        decay = f"{d['decay_ms']:.0f} ms" if d["decay_ms"] == d["decay_ms"] else "sustains"
        tx = fig.add_subplot(gs[i, 1])
        tx.axis("off")
        tx.text(0.03, 0.5, f"{d['seconds']:.2f} s   peak {d['peak_db']:.1f} dB   {loud}   crest {d['crest_db']:.0f} dB\n"
                           f"attack {d['attack_ms']:.0f} ms   decay {decay}   centroid {d['centroid_hz']:.0f} Hz   {pitch}\n"
                           f"sub {b['sub']:.0f}%  bass {b['bass']:.0f}%  low-mid {b['lowmid']:.0f}%  mid {b['mid']:.0f}%  high {b['high']:.0f}%   "
                           f"side {d['side_pct']:.1f}%",
                va="center", fontsize=7.5, family="monospace")
    ax = fig.add_subplot(gs[n, :])
    top = -200.0
    for i, (path, sr, m, d) in enumerate(items):
        f, db = _smooth_spectrum(m, sr)
        top = max(top, db.max())
        ax.plot(f, db, lw=1.4, color=f"C{i}", label=path.stem[:28])
    _freq_axis(ax)
    ax.set_ylim(top - 72, top + 6)
    for name, lo, hi in REGIONS:
        ax.text(np.sqrt(lo * hi), top + 3, name, ha="center", fontsize=7, color="0.45")
    ax.grid(axis="y", color="0.88", lw=0.5)
    ax.legend(fontsize=7.5, loc="lower left", ncol=min(4, n))
    ax.set_xlabel("Hz — spectra overlaid", fontsize=8)
    ax.tick_params(labelsize=7)
    fig.suptitle(title or "sample comparison", fontsize=11)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=105)
    plt.close(fig)
    return out
