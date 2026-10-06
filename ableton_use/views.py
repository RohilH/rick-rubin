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
                  wav: str | Path | None = None, tracks: list[str] | None = None,
                  wav_start_bar: int = 1) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    b0, b1 = bars or (1, song.total_bars)          # 1-based inclusive
    t0, t1 = (b0 - 1) * BEATS_PER_BAR, b1 * BEATS_PER_BAR
    clips, markers = song.flatten(sounding=True)
    trks = [t for t in song.tracks if not tracks or t.name in tracks]
    trks = [t for t in trks if any(c.track == t.name and c.start < t1 and c.start + c.length > t0 for c in clips)]

    from .pitch import load_notes
    n_audio = 2 if wav else 0
    spb = 60.0 / song.bpm
    # an audio track whose loops have been through `ableton-use notes` gets its own lane of sung notes under the waveform
    sung_lanes: dict[str, list[tuple[float, float, float, str]]] = {}        # track -> (start beat, length, pitch, name)
    for t in trks:
        if not t.audio:
            continue
        lane = []
        for c in clips:
            if c.track != t.name or not c.audio:
                continue
            notes = load_notes(song.resolve(c.audio)) or []
            for s0, ln, off in c.segments:
                for n in notes:
                    nb = n.start_s / spb
                    if off <= nb < off + ln and t0 <= c.start + s0 + nb - off < t1:
                        lane.append((c.start + s0 + nb - off, min(n.beats, off + ln - nb), n.midi, n.name))
        if lane:
            sung_lanes[t.name] = lane
    rows: list[tuple[str, object]] = []
    for t in trks:
        rows.append(("track", t))
        if t.name in sung_lanes:
            rows.append(("sung", t))
    heights = [0.35] + [(0.55 if t.is_drum else 1.0) if kind == "track" else 1.1 for kind, t in rows] + [1.4] * n_audio
    fig, axes = plt.subplots(len(heights), 1, figsize=(14, 0.8 + 0.75 * sum(heights)), sharex=True,
                             gridspec_kw={"height_ratios": heights, "hspace": 0.08, "top": 0.965, "bottom": 0.05})
    axes = np.atleast_1d(axes)

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

    for ax, (kind, t) in zip(axes[1:], rows):
        if kind == "sung":                                   # the notes the sample sings, as a piano roll of its own
            lane = sung_lanes[t.name]
            # range from the notes that carry the melody; stray blips are drawn at the edge rather than stretching the lane
            w = np.array([x[1] for x in lane])
            order = np.argsort([x[2] for x in lane])
            cum = np.cumsum(w[order]) / w.sum()
            pitches = np.array([x[2] for x in lane])[order]
            lo_p = float(np.floor(pitches[np.searchsorted(cum, 0.04)])) - 1.5
            hi_p = float(np.ceil(pitches[min(len(pitches) - 1, np.searchsorted(cum, 0.96))])) + 2.5
            for st, ln, midi, nm in lane:
                y = min(max(midi, lo_p + 0.5), hi_p - 1.5)
                ax.add_patch(plt.Rectangle((st, y - 0.4), ln, 0.8, color="C1" if y == midi else "0.6"))
                ax.text(st, y + 0.55, nm, fontsize=6.5, color="C1" if y == midi else "0.5", va="bottom")
            ax.set_ylim(lo_p, hi_p)
            ax.set_yticks([])
            ax.grid(False)
            ax.set_ylabel(f"{t.name}\nnotes", rotation=0, ha="right", va="center", fontsize=8)
            ax.tick_params(labelsize=6)
            continue
        mine = [c for c in clips if c.track == t.name]
        ps = []
        for c in mine:
            if c.audio:
                # audio clip: the file's own waveform, one box per pass of the loop
                from .samples import read_audio
                sr_a, xa = read_audio(song.resolve(c.audio))
                xa = np.abs(xa).max(axis=1)
                for s0, ln, off in c.segments:
                    a = c.start + s0
                    if a >= t1 or a + ln <= t0:
                        continue
                    seg = xa[int(off * spb * sr_a): int((off + ln) * spb * sr_a)]
                    k = max(1, len(seg) // 800)
                    env = np.array([seg[i:i + k].max() for i in range(0, len(seg), k)])
                    xs = a + np.arange(len(env)) * k / sr_a / spb
                    ax.fill_between(xs, 0.5 - env / 2, 0.5 + env / 2, color="C0", lw=0)
                    ax.add_patch(plt.Rectangle((a, 0.02), ln, 0.96, fill=False, ec="C0", lw=0.8))
                for prm, pts in c.envelopes.items():
                    ax.plot([c.start + q[0] for q in pts], [q[1] for q in pts], color="r", lw=1, alpha=0.7)
                ax.set_ylim(0, 1)
                ax.set_yticks([])
                continue
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
        from .samples import read_audio
        sr, x = read_audio(wav)
        x = x.mean(axis=1)
        w0 = (wav_start_bar - 1) * BEATS_PER_BAR          # beat at which the audio file starts
        a, b = max(0, int((t0 - w0) * spb * sr)), min(len(x), int((t1 - w0) * spb * sr))
        seg = x[a:b]
        beats = max(t0, w0) + np.arange(len(seg)) / sr / spb
        axw, axs = axes[-2], axes[-1]
        step = max(1, len(seg) // 6000)
        env_hi = np.array([seg[i:i + step].max() for i in range(0, len(seg), step)])
        env_lo = np.array([seg[i:i + step].min() for i in range(0, len(seg), step)])
        axw.fill_between(beats[::step][: len(env_hi)], env_lo, env_hi, color="0.3", lw=0)
        axw.set_ylabel(Path(wav).stem, rotation=0, ha="right", va="center", fontsize=9)
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

    # Grid: bar lines always; quarter-note lines at 16 bars or fewer; lighter eighth-note lines at 8 or fewer;
    # faint 16th lines at 4 or fewer.
    # Drawn over the content (thin, translucent) so they also show on the waveform and spectrogram.
    nbars = b1 - b0 + 1
    for ax in axes:
        for bar in range(b0, b1 + 2):
            x = (bar - 1) * BEATS_PER_BAR
            strong = (bar - 1) % 8 == 0
            ax.axvline(x, color="0.15" if strong or nbars <= 16 else "0.6", lw=0.9 if strong else (0.7 if nbars <= 16 else 0.4),
                       zorder=4 if nbars <= 16 else 0, alpha=0.8 if nbars <= 16 else 1.0)
            if bar > b1:
                continue
            if nbars <= 16:
                for beat in range(1, BEATS_PER_BAR):
                    ax.axvline(x + beat, color="0.35", lw=0.45, ls=(0, (4, 3)), zorder=4, alpha=0.55)
            if nbars <= 8:                                   # eighth notes: lighter than the quarters
                for beat in range(BEATS_PER_BAR):
                    ax.axvline(x + beat + 0.5, color="0.45", lw=0.35, ls=(0, (2, 3)), zorder=4, alpha=0.45)
            if nbars <= 4:                                   # sixteenths: lightest
                for beat in range(BEATS_PER_BAR):
                    for off in (0.25, 0.75):
                        ax.axvline(x + beat + off, color="0.55", lw=0.25, ls=(0, (1, 4)), zorder=4, alpha=0.4)
    axes[-1].set_xlim(t0, t1)
    ticks = list(range(b0, b1 + 1, max(1, nbars // 16)))
    axes[-1].set_xticks([(b - 1) * BEATS_PER_BAR for b in ticks])
    axes[-1].set_xticklabels([str(b) for b in ticks])
    if nbars <= 8:                                         # name the beats inside each bar: 41 .2 .3 .4 42 ...
        minor = [(b - 1) * BEATS_PER_BAR + k for b in range(b0, b1 + 1) for k in range(1, BEATS_PER_BAR)]
        axes[-1].set_xticks(minor, minor=True)
        axes[-1].set_xticklabels([f".{k + 1}" for _ in range(b0, b1 + 1) for k in range(1, BEATS_PER_BAR)], minor=True, fontsize=6, color="0.4")
    axes[-1].set_xlabel("bar" + (" .beat" if nbars <= 8 else ""))
    fig.suptitle(f"{song.title} — bars {b0}-{b1}", fontsize=11, y=0.995)
    fig.savefig(out_path, dpi=90, bbox_inches="tight")
    plt.close(fig)
    return out_path
