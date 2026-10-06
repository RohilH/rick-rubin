"""Self-evaluation: symbolic lint (hard rules) + audio measurements of the preview.

`lint(song)` checks the score against house production rules — no audio needed.
`measure(wav, song)` measures the rendered preview per section (loudness,
spectral balance, crest factor) and checks the energy curve actually happens.
`report(...)` produces eval.md, the agent's self-eval reading view.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from .model import BEATS_PER_BAR, STEP, Song
from .theory import Key, name as pname

MELODIC = {"bass", "sub", "chords", "stab", "pad", "lead", "arp", "pluck", "keys", "organ", "vocal"}
NON_BASS_MELODIC = MELODIC - {"bass", "sub"}


@dataclass
class Issue:
    severity: str        # error | warn | info
    rule: str
    where: str
    message: str

    def __str__(self) -> str:
        icon = {"error": "✗", "warn": "!", "info": "·"}[self.severity]
        return f"{icon} [{self.rule}] {self.where}: {self.message}"


# ============================================================================ symbolic lint
def lint(song: Song) -> list[Issue]:
    I: list[Issue] = []
    add = lambda sev, rule, where, msg: I.append(Issue(sev, rule, where, msg))  # noqa: E731

    for e in song.validate():
        add("error", "S0-structure", "song", e)
    if any(i.severity == "error" for i in I):
        return I

    key = song.key_obj
    # H1 tempo
    if not 118 <= song.bpm <= 130:
        add("warn", "H1-tempo", "song", f"{song.bpm:g} BPM is outside the usual house range 118-130")
    if not 50 <= song.swing <= 66:
        add("warn", "H1-tempo", "song", f"swing {song.swing:g}% outside 50-66%")

    # H2 phrasing
    for s in song.sections:
        if s.bars % 4:
            add("error", "H2-phrasing", s.name, f"{s.bars} bars is not a multiple of 4 — DJs will lose the phrase")
        elif s.bars % 8:
            add("warn", "H2-phrasing", s.name, f"{s.bars} bars is not a multiple of 8")
        if s.bars > 32 and not s.fills and not s.automation and all(p.start == 0 and p.end is None for p in s.parts.values()):
            add("warn", "H2-phrasing", s.name, f"{s.bars} static bars — change something every 8/16 bars (fill, part entry, automation)")

    tracks = {t.name: t for t in song.tracks}
    starts = song.section_starts()

    def playing_roles(bar0: int, bar1: int) -> set[str]:
        roles = set()
        for sec, sb in zip(song.sections, starts):
            for tn, p in sec.parts.items():
                a = sb + p.start
                b = sb + (sec.bars if p.end is None else p.end)
                if a < bar1 and b > bar0:
                    roles.add(tracks[tn].role)
        return roles

    # H3 DJ-friendly intro/outro
    if song.sections:
        first, last = song.sections[0], song.sections[-1]
        if first.kind != "intro" or first.bars < 16:
            add("warn", "H3-dj-friendly", first.name, "intro shorter than 16 bars — fine for a radio edit, not for a club mix")
        mel = playing_roles(0, 8) & MELODIC
        if mel:
            add("warn", "H3-dj-friendly", first.name, f"melodic/bass parts in the first 8 bars ({', '.join(sorted(mel))}) clash in DJ mixes")
        if "kick" not in playing_roles(0, 8):
            add("info", "H3-dj-friendly", first.name, "no kick in the first 8 bars — DJs beat-match on the kick")
        if last.kind != "outro" or last.bars < 16:
            add("warn", "H3-dj-friendly", last.name, "outro shorter than 16 bars")
        tb = song.total_bars
        mel = playing_roles(tb - 8, tb) & MELODIC
        if mel:
            add("warn", "H3-dj-friendly", last.name, f"melodic parts in the last 8 bars ({', '.join(sorted(mel))})")

    clips, _ = song.flatten()

    # H4 key / H5 bass range+mono / H10 low-end mud / H13 density
    out_key: dict[str, set] = defaultdict(set)
    for c in clips:
        role = tracks[c.track].role
        if role not in MELODIC:
            continue
        for n in c.notes:
            if not key.contains(n.pitch):
                out_key[c.track].add(pname(n.pitch))
        if role in ("bass", "sub"):
            lo, hi = min(n.pitch for n in c.notes), max(n.pitch for n in c.notes)
            if lo < 24 or hi > 55:
                add("warn", "H5-bass", c.section, f"{c.track} spans {pname(lo)}-{pname(hi)}; keep house bass ~C0-G2 (24-55)")
            ns = sorted(c.notes, key=lambda n: n.start)
            overl = sum(1 for a, b in zip(ns, ns[1:]) if a.start + a.dur > b.start + 1e-6)
            if overl:
                add("warn", "H5-bass", c.section, f"{c.track} has {overl} overlapping notes — bass should be monophonic")
        elif role in NON_BASS_MELODIC:
            low = [n for n in c.notes if n.pitch < 48]
            if low:
                add("warn", "H10-low-end", c.section, f"{c.track} has {len(low)} notes below C2 — mud against the bass; voice higher or high-pass")
            by_t = defaultdict(int)
            for n in c.notes:
                by_t[round(n.start, 3)] += 1
            if by_t and max(by_t.values()) > 6:
                add("warn", "H13-density", c.section, f"{c.track} stacks {max(by_t.values())} notes at once")
    for tn, ps in out_key.items():
        add("warn", "H4-key", tn, f"notes outside {song.key}: {', '.join(sorted(ps))}")

    # H6 kick vs bass collisions
    kick_on = {round(c.start + n.start, 3) for c in clips if tracks[c.track].role == "kick" for n in c.notes}
    for t in song.tracks:
        if t.role not in ("bass", "sub"):
            continue
        ons = [round(c.start + n.start, 3) for c in clips if c.track == t.name for n in c.notes]
        if ons:
            frac = sum(o in kick_on for o in ons) / len(ons)
            if frac > 0.25 and not t.sidechain:
                add("warn", "H6-kick-bass", t.name, f"{frac:.0%} of bass notes land on kicks and the bass is not sidechained")
            elif frac > 0.5:
                add("info", "H6-kick-bass", t.name, f"{frac:.0%} of bass notes land on kicks (sidechained — OK if intentional)")

    # H7 grid
    for p in song.patterns.values():
        off = [n for n in p.notes if abs(n.start / (STEP / 2) - round(n.start / (STEP / 2))) > 1e-3]
        if off:
            add("info", "H7-grid", p.name, f"{len(off)} notes off the 1/32 grid (fine if deliberate swing/humanize)")
        if any(n.dur < 1 / 16 for n in p.notes):
            add("warn", "H7-grid", p.name, "notes shorter than 1/64 note may not trigger reliably")

    # H8 energy & drops
    kinds = [s.kind for s in song.sections]
    energies = [s.energy for s in song.sections]
    for i, s in enumerate(song.sections):
        if s.kind == "drop":
            if i == 0 or kinds[i - 1] not in ("build", "breakdown", "bridge"):
                add("warn", "H8-energy", s.name, "drop is not preceded by a build/breakdown — no tension to release")
            if s.energy < max(energies) - 2:
                add("info", "H8-energy", s.name, "drop energy well below the track peak")
            if "kick" not in playing_roles(starts[i], starts[i] + 1):
                add("error", "H8-energy", s.name, "no kick on the first bar of the drop")
        if s.kind == "build" and s.bars > 16:
            add("warn", "H8-energy", s.name, "build longer than 16 bars loses tension")
        if s.kind == "breakdown" and "kick" in playing_roles(starts[i], starts[i] + s.bars):
            add("info", "H8-energy", s.name, "kick plays during the breakdown")
    if "drop" not in kinds:
        add("warn", "H8-energy", "song", "no section of kind 'drop'")

    # H11 robotic drums
    for p in song.patterns.values():
        trk = tracks.get(p.track or "")
        if trk and trk.role in ("hat", "perc", "shaker") and len(p.notes) >= 8 and len({n.vel for n in p.notes}) == 1:
            add("info", "H11-groove", p.name, "every hit has the same velocity — add accents/ghosts")

    # H14 samples: Simpler range, loop lengths, loop keys
    for t in song.tracks:
        if t.sample and not t.is_drum and t.sample_root is not None:
            far = sorted({n.pitch for c in clips if c.track == t.name for n in c.notes if abs(n.pitch - t.sample_root) > 24})
            if far:
                add("warn", "H14-samples", t.name, f"notes {pname(far[0])}-{pname(far[-1])} are more than 2 octaves from the sample's "
                    f"root {pname(round(t.sample_root))} — a repitched one-shot sounds thin or smeared that far out")
    for sec in song.sections:
        for tn, part in sec.parts.items():
            pat = song.patterns[part.pattern]
            if pat.is_audio:
                span = (sec.bars if part.end is None else part.end) - part.start
                if span % pat.bars:
                    add("info", "H14-samples", sec.name, f"{tn} plays {span} bars of the {pat.bars}-bar loop {pat.name!r} — the last pass is cut short")
    for p in song.patterns.values():
        if p.is_audio and p.key:
            try:
                pk = Key.parse(p.key)
            except ValueError:
                add("warn", "H4-key", p.name, f"audio loop has an unreadable key {p.key!r}")
                continue
            if {(pk.root + i) % 12 for i in pk.intervals} != {(key.root + i) % 12 for i in key.intervals}:
                add("warn", "H4-key", p.name, f"audio loop is in {pk}, the song is in {song.key} (not the same key or its relative)")

    # H12 unused
    used = {p.pattern for s in song.sections for p in s.parts.values()} | {f.pattern for s in song.sections for f in s.fills.values()}
    for pn in song.patterns:
        if pn not in used:
            add("info", "H12-unused", pn, "pattern not used in any section")
    for t in song.tracks:
        if not any(t.name in s.parts or t.name in s.fills for s in song.sections):
            add("info", "H12-unused", t.name, "track never plays")
    return I


# ============================================================================ audio measurement
def _kweight(x: np.ndarray, sr: int) -> np.ndarray:
    from scipy.signal import lfilter
    # BS.1770 pre-filter (high shelf) + RLB high-pass, designed for any sample rate
    G, Q, fc = 3.999843853973347, 0.7071752369554196, 1681.974450955533
    A = 10 ** (G / 40); w0 = 2 * np.pi * fc / sr; al = np.sin(w0) / (2 * Q); cw = np.cos(w0); sA = np.sqrt(A)
    b = [A * ((A + 1) + (A - 1) * cw + 2 * sA * al), -2 * A * ((A - 1) + (A + 1) * cw), A * ((A + 1) + (A - 1) * cw - 2 * sA * al)]
    a = [(A + 1) - (A - 1) * cw + 2 * sA * al, 2 * ((A - 1) - (A + 1) * cw), (A + 1) - (A - 1) * cw - 2 * sA * al]
    y = lfilter(b, a, x, axis=0)
    Q, fc = 0.5003270373238773, 38.13547087602444
    w0 = 2 * np.pi * fc / sr; al = np.sin(w0) / (2 * Q); cw = np.cos(w0)
    b = [(1 + cw) / 2, -(1 + cw), (1 + cw) / 2]
    a = [1 + al, -2 * cw, 1 - al]
    return lfilter(b, a, y, axis=0)


def loudness_lufs(x: np.ndarray, sr: int) -> float:
    """Integrated loudness (ITU-R BS.1770-4 gating). x: (n,) or (n, ch)."""
    if x.ndim == 1:
        x = x[:, None]
    y = _kweight(x, sr)
    blk, hop = int(0.4 * sr), int(0.1 * sr)
    if len(y) < blk:
        return float("-inf")
    idx = np.arange(0, len(y) - blk + 1, hop)
    cs = np.cumsum(np.concatenate([np.zeros((1, y.shape[1])), y ** 2]), axis=0)
    ms = (cs[idx + blk] - cs[idx]) / blk
    lk = -0.691 + 10 * np.log10(np.maximum(ms.sum(axis=1), 1e-12))
    g = lk > -70
    if not g.any():
        return float("-inf")
    rel = -0.691 + 10 * np.log10(ms[g].sum(axis=1).mean()) - 10
    g2 = g & (lk > rel)
    return float(-0.691 + 10 * np.log10(ms[g2].sum(axis=1).mean()))


BANDS = [("sub", 20, 60), ("bass", 60, 200), ("lowmid", 200, 800), ("mid", 800, 4000), ("high", 4000, 12000), ("air", 12000, 20000)]


@dataclass
class SectionStats:
    name: str
    kind: str
    energy: int
    lufs: float
    peak_db: float
    crest_db: float
    bands: dict[str, float]          # % of energy per band
    centroid_hz: float


@dataclass
class Measurement:
    integrated_lufs: float
    peak_db: float
    clipped_samples: int
    sections: list[SectionStats] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)


def measure(wav_path: str | Path, song: Song) -> Measurement:
    from scipy.io import wavfile
    sr, data = wavfile.read(wav_path)
    x = data.astype(np.float32) / (32768.0 if data.dtype == np.int16 else 1.0)
    if x.ndim == 1:
        x = x[:, None]
    mono = x.mean(axis=1)
    spbar = 60.0 / song.bpm * BEATS_PER_BAR
    m = Measurement(loudness_lufs(x, sr), float(20 * np.log10(np.abs(x).max() + 1e-12)), int((np.abs(x) >= 0.999).sum()))
    for sec, sb in zip(song.sections, song.section_starts()):
        a, b = int(sb * spbar * sr), int((sb + sec.bars) * spbar * sr)
        seg, segm = x[a:b], mono[a:b]
        if len(segm) < sr:
            continue
        rms = np.sqrt(np.mean(segm ** 2)) + 1e-12
        pk = np.abs(segm).max() + 1e-12
        spec = np.abs(np.fft.rfft(segm * np.hanning(len(segm)))) ** 2
        freqs = np.fft.rfftfreq(len(segm), 1 / sr)
        tot = spec[(freqs >= 20) & (freqs < 20000)].sum() + 1e-12
        bands = {nm: float(100 * spec[(freqs >= lo) & (freqs < hi)].sum() / tot) for nm, lo, hi in BANDS}
        cen = float((freqs * spec).sum() / (spec.sum() + 1e-12))
        m.sections.append(SectionStats(sec.name, sec.kind, sec.energy, loudness_lufs(seg, sr),
                                       float(20 * np.log10(pk)), float(20 * np.log10(pk / rms)), bands, cen))
    _audio_checks(m)
    return m


def _audio_checks(m: Measurement) -> None:
    add = lambda sev, rule, where, msg: m.issues.append(Issue(sev, rule, where, msg))  # noqa: E731
    if m.clipped_samples > 0:
        add("warn", "A1-clipping", "master", f"{m.clipped_samples} clipped samples")
    secs = m.sections
    if not secs:
        return
    drops = [s for s in secs if s.kind == "drop"]
    if drops:
        d = min(s.lufs for s in drops)
        for s in secs:
            if s.kind == "breakdown" and s.lufs > d - 3:
                add("warn", "A2-contrast", s.name, f"{s.lufs:.1f} LUFS vs quietest drop {d:.1f} — breakdown should sit ≥3 LU below the drop")
            if s.kind in ("intro", "outro", "groove", "bridge") and s.lufs > d + 0.5:
                add("warn", "A2-contrast", s.name, f"{s.lufs:.1f} LUFS is louder than the drop ({d:.1f})")
    # does measured loudness follow the intended energy curve?
    # DJ intros/outros are drum-loud by design, so judge the curve on the body of the track
    body = [s for s in secs if s.kind not in ("intro", "outro")]
    if len(body) >= 3:
        e = np.array([s.energy for s in body], float)
        l = np.array([s.lufs for s in body], float)
        if np.std(e) > 0 and np.std(l) > 0:
            r = float(np.corrcoef(e, l)[0, 1])
            if r < 0.5:
                add("warn", "A3-energy-curve", "song", f"measured loudness tracks the intended energy curve poorly (r={r:.2f})")
            else:
                add("info", "A3-energy-curve", "song", f"loudness follows intended energy (r={r:.2f})")
    for s in drops:
        low = s.bands["sub"] + s.bands["bass"]
        if low < 25:
            add("warn", "A4-low-end", s.name, f"only {low:.0f}% energy below 200 Hz in a drop — weak kick/bass")
        elif low > 90:
            add("warn", "A4-low-end", s.name, f"{low:.0f}% energy below 200 Hz — low end may swamp the mix")
        if s.bands["high"] + s.bands["air"] < 1.0:
            add("warn", "A5-top-end", s.name, "almost no energy above 4 kHz — dull drop (hats/air)")
        if s.crest_db < 6:
            add("warn", "A6-dynamics", s.name, f"crest factor {s.crest_db:.1f} dB — over-compressed/flat")


# ============================================================================ report
def report(song: Song, lint_issues: list[Issue], meas: Measurement | None = None) -> str:
    L = [f"# Self-eval — {song.title}", ""]
    errs = [i for i in lint_issues if i.severity == "error"] + ([i for i in meas.issues if i.severity == "error"] if meas else [])
    warns = [i for i in lint_issues if i.severity == "warn"] + ([i for i in meas.issues if i.severity == "warn"] if meas else [])
    verdict = "FAIL" if errs else ("PASS with warnings" if warns else "PASS")
    L.append(f"**Verdict: {verdict}** — {len(errs)} errors, {len(warns)} warnings")
    L.append("")
    L.append("## Score lint")
    L.extend(str(i) for i in lint_issues) if lint_issues else L.append("clean")
    if meas:
        L.append("")
        L.append(f"## Preview audio — {meas.integrated_lufs:.1f} LUFS integrated, peak {meas.peak_db:.1f} dBFS")
        L.append("(preview synth levels are relative; compare sections with each other, not with commercial masters)")
        L.append("")
        L.append("| section | kind | energy | LUFS | crest dB | sub% | bass% | lowmid% | mid% | high% | air% | centroid |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for s in meas.sections:
            b = s.bands
            L.append(f"| {s.name} | {s.kind} | {s.energy} | {s.lufs:.1f} | {s.crest_db:.1f} | {b['sub']:.0f} | {b['bass']:.0f} | "
                     f"{b['lowmid']:.0f} | {b['mid']:.0f} | {b['high']:.1f} | {b['air']:.1f} | {s.centroid_hz:.0f} Hz |")
        L.append("")
        L.append("## Audio checks")
        L.extend(str(i) for i in meas.issues) if meas.issues else L.append("clean")
    return "\n".join(L) + "\n"
