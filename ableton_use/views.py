"""On-demand visual drill-down (cf. video-use's timeline_view).

`timeline_view(song, bars=(65, 80), wav=...)` draws, for a bar range:
  * section ruler,
  * a piano-roll lane per track (drums as hit ticks, melodic as note bars),
  * the preview waveform with the kick-sidechain pump visible,
  * a log-frequency spectrogram.
Use it at decision points (a transition, a drop, a muddy bar) — not as a scan tool.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from .model import BEATS_PER_BAR, Song


def timeline_view(song: Song, out_path: str | Path, bars: tuple[int, int] | None = None,
                  wav: str | Path | None = None, tracks: list[str] | None = None) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    b0, b1 = bars or (1, song.total_bars)          # 1-based inclusive
    t0, t1 = (b0 - 1) * BEATS_PER_BAR, b1 * BEATS_PER_BAR
    clips, markers = song.flatten()
    trks = [t for t in song.tracks if not tracks or t.name in tracks]
    trks = [t for t in trks if any(c.track == t.name and c.start < t1 and c.start + c.length > t0 for c in clips)]

    n_audio = 2 if wav else 0
    heights = [0.35] + [0.55 if t.is_drum else 1.0 for t in trks] + [1.4] * n_audio
    fig, axes = plt.subplots(len(heights), 1, figsize=(14, 0.8 + 0.75 * sum(heights)), sharex=True,
                             gridspec_kw={"height_ratios": heights, "hspace": 0.08, "top": 0.965, "bottom": 0.05})
    axes = np.atleast_1d(axes)
    spb = 60.0 / song.bpm

    # section ruler
    ax = axes[0]
    for sec, sb in zip(song.sections, song.section_starts()):
        s, e = sb * BEATS_PER_BAR, (sb + sec.bars) * BEATS_PER_BAR
        if e <= t0 or s >= t1:
            continue
        ax.axvspan(max(s, t0), min(e, t1), color=f"C{sb % 10}", alpha=0.25)
        ax.text(max(s, t0) + 0.3, 0.5, f"{sec.name} (E{sec.energy})", va="center", fontsize=9, weight="bold")
    ax.set_yticks([])
    ax.set_ylim(0, 1)

    for ax, t in zip(axes[1:], trks):
        mine = [c for c in clips if c.track == t.name]
        ps = []
        for c in mine:
            for n in c.notes:
                st = c.start + n.start
                if t0 <= st < t1:
                    ps.append(n.pitch)
                    if t.is_drum:
                        ax.vlines(st, 0, n.vel / 127, color="k", lw=1.2)
                    else:
                        ax.add_patch(plt.Rectangle((st, n.pitch - 0.4), n.dur, 0.8, color=plt.cm.viridis(n.vel / 127)))
            for prm, pts in c.envelopes.items():
                xs = [c.start + p[0] for p in pts]
                ys = [p[1] for p in pts]
                if t.is_drum:
                    ax.plot(xs, ys, color="r", lw=1, alpha=0.7)
                elif ps:
                    lo, hi = min(ps) - 1, max(ps) + 1
                    ax.plot(xs, [lo + y * (hi - lo) for y in ys], color="r", lw=1, alpha=0.7, label=prm)
        if t.is_drum:
            ax.set_ylim(0, 1.05)
            ax.set_yticks([])
        elif ps:
            ax.set_ylim(min(ps) - 2, max(ps) + 2)
        ax.set_ylabel(t.name, rotation=0, ha="right", va="center", fontsize=9)
        ax.tick_params(labelsize=7)

    if wav:
        from scipy.io import wavfile
        sr, data = wavfile.read(wav)
        x = data.astype(np.float32) / 32768.0
        x = x.mean(axis=1) if x.ndim > 1 else x
        a, b = int(t0 * spb * sr), min(len(x), int(t1 * spb * sr))
        seg = x[a:b]
        beats = t0 + np.arange(len(seg)) / sr / spb
        axw, axs = axes[-2], axes[-1]
        step = max(1, len(seg) // 6000)
        env_hi = np.array([seg[i:i + step].max() for i in range(0, len(seg), step)])
        env_lo = np.array([seg[i:i + step].min() for i in range(0, len(seg), step)])
        axw.fill_between(beats[::step][: len(env_hi)], env_lo, env_hi, color="0.3", lw=0)
        axw.set_ylabel("preview", rotation=0, ha="right", va="center", fontsize=9)
        axw.set_ylim(-1, 1)
        nfft = 2048
        hop = nfft // 2
        frames = np.lib.stride_tricks.sliding_window_view(seg, nfft)[::hop] * np.hanning(nfft) if len(seg) > nfft else None
        if frames is not None:
            S = 20 * np.log10(np.abs(np.fft.rfft(frames, axis=1)).T + 1e-9)
            f = np.fft.rfftfreq(nfft, 1 / sr)
            tt = t0 + (np.arange(S.shape[1]) * hop + nfft / 2) / sr / spb
            axs.pcolormesh(tt, f[1:], S[1:], shading="auto", cmap="magma", vmin=S.max() - 80, vmax=S.max())
            axs.set_yscale("log")
            axs.set_ylim(30, 16000)
            axs.set_ylabel("Hz", rotation=0, ha="right", va="center", fontsize=9)

    for ax in axes:
        for bar in range(b0, b1 + 2):
            x = (bar - 1) * BEATS_PER_BAR
            ax.axvline(x, color="0.6" if (bar - 1) % 8 else "0.2", lw=0.4 if (bar - 1) % 8 else 0.9, zorder=0)
    axes[-1].set_xlim(t0, t1)
    ticks = list(range(b0, b1 + 1, max(1, (b1 - b0 + 1) // 16)))
    axes[-1].set_xticks([(b - 1) * BEATS_PER_BAR for b in ticks])
    axes[-1].set_xticklabels([str(b) for b in ticks])
    axes[-1].set_xlabel("bar")
    fig.suptitle(f"{song.title} — bars {b0}-{b1}", fontsize=11, y=0.995)
    fig.savefig(out_path, dpi=90, bbox_inches="tight")
    plt.close(fig)
    return out_path
