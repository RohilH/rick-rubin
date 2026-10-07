"""The packed score — the agent's primary reading view (cf. video-use's takes_packed.md).

The LLM never listens to the song. It *reads* it: one compact markdown file with
the arrangement map, energy curve, and every pattern as step strings / note
events. ~5-10 KB for a full track. Audio and pictures come only on demand
(`preview` + `analysis` + `views`).
"""
from __future__ import annotations

from collections import defaultdict

from .model import BEATS_PER_BAR, STEP, Pattern, Song, fmt_pos, notes_to_steps
from .theory import chord_name, name as pname


def _mmss(sec: float) -> str:
    return f"{int(sec // 60)}:{int(sec % 60):02d}"


def pattern_text(p: Pattern, song: Song) -> list[str]:
    head = f"### {p.name}  ({p.bars} bar{'s' if p.bars > 1 else ''}"
    if p.track:
        head += f", {p.track}"
    head += ")" + (f" — {p.desc}" if p.desc else "")
    lines = [head]
    if p.is_audio:
        lines.append(f"  audio loop '{p.audio}'" + (f", key {p.key}" if p.key else "") + f" — repeats every {p.bars} bar{'s' if p.bars > 1 else ''}")
        from .transcribe import load_words, words_text
        words = load_words(song.resolve(p.audio))
        if words:
            lines.extend(words_text(words))
        from .pitch import load_notes, notes_text
        sung = load_notes(song.resolve(p.audio))
        if sung:
            lines.extend(notes_text(sung))
        return lines
    if not p.notes:
        lines.append("  (empty)")
        return lines
    if p.is_steppable():
        lines.append(f"  pitch {pname(p.notes[0].pitch)}  steps (16ths, | = bar): {notes_to_steps(p.notes, p.bars)}")
        return lines
    key = song.key_obj
    groups: dict[float, list] = defaultdict(list)
    for n in sorted(p.notes, key=lambda n: (n.start, n.pitch)):
        groups[round(n.start, 4)].append(n)
    chordy = sum(len(g) > 1 for g in groups.values()) > len(groups) / 2
    out_of_key = sorted({pname(n.pitch) for n in p.notes if not key.contains(n.pitch)})
    by_bar: dict[int, list[str]] = defaultdict(list)
    for t, g in groups.items():
        bar = int(t // BEATS_PER_BAR)
        dur = max(n.dur for n in g)
        vel = round(sum(n.vel for n in g) / len(g))
        if len(g) > 1:
            label = f"{chord_name([n.pitch for n in g])}[{' '.join(pname(n.pitch) for n in g)}]"
        else:
            label = pname(g[0].pitch)
        by_bar[bar].append(f"{fmt_pos(t).split('.', 1)[1]} {label} {dur:g}" + ("" if vel in (100,) else f" v{vel}"))
    if chordy:
        # chord summary line per bar
        summ = []
        for b in range(p.bars):
            names = []
            for t, g in groups.items():
                if int(t // BEATS_PER_BAR) == b and len(g) > 1:
                    nm = chord_name([n.pitch for n in g])
                    if not names or names[-1] != nm:
                        names.append(nm)
            summ.append(" ".join(names) or "-")
        lines.append("  chords/bar: " + " | ".join(summ))
    b = 0
    while b < p.bars:
        evs = by_bar.get(b, [])
        if evs:
            lines.append(f"  bar {b + 1}: " + "; ".join(evs))
            b += 1
            continue
        e = b
        while e + 1 < p.bars and not by_bar.get(e + 1):
            e += 1
        lines.append(f"  bar {b + 1}: —" if e == b else f"  bars {b + 1}-{e + 1}: —")
        b = e + 1
    if out_of_key:
        lines.append(f"  ! out of key ({song.key}): {', '.join(out_of_key)}")
    return lines


def arrangement_grid(song: Song, cell_bars: int = 4) -> list[str]:
    """One row per track, one char per `cell_bars` bars. '█' plays, '▒' fill only, '·' silent."""
    starts = song.section_starts()
    total = song.total_bars
    ncell = -(-total // cell_bars)
    width = max(len(t.name) for t in song.tracks) if song.tracks else 4
    cells: dict[str, list[str]] = {t.name: ["·"] * ncell for t in song.tracks}
    for sec, sb in zip(song.sections, starts):
        for tname, part in sec.parts.items():
            end = sec.bars if part.end is None else part.end
            for b in range(sb + part.start, sb + end):
                cells[tname][b // cell_bars] = "█"
        for tname, fill in sec.fills.items():
            fp = song.patterns[fill.pattern]
            every = fill.every or sec.bars
            for pe in range(every, sec.bars + 1, every):
                for b in range(sb + pe - fp.bars, sb + pe):
                    c = b // cell_bars
                    if cells[tname][c] == "·":
                        cells[tname][c] = "▒"
    # section ruler
    ruler = [" "] * ncell
    for sec, sb in zip(song.sections, starts):
        lab = sec.name[: max(1, sec.bars // cell_bars)]
        for i, ch in enumerate(lab):
            if sb // cell_bars + i < ncell:
                ruler[sb // cell_bars + i] = ch
    lines = [f"{'':{width}}  {''.join(ruler)}"]
    for t in song.tracks:
        lines.append(f"{t.name:{width}}  {''.join(cells[t.name])}")
    return lines


def _only(song: Song, sec) -> Song:
    import copy
    s = copy.copy(song)
    s.sections = [sec]
    return s


def pack(song: Song, include_patterns: bool = True, bars: tuple[int, int] | None = None,
         tracks: list[str] | None = None) -> str:
    """The packed score. `bars` (1-based, inclusive) and `tracks` zoom in: only the
    sections touching that range, only those tracks, and only the patterns they use there."""
    if bars or tracks:
        import copy
        full, song = song, copy.deepcopy(song)
        keep_t = [t for t in song.tracks if not tracks or t.name in tracks]
        names = {t.name for t in keep_t}
        secs = []
        for sec, sb in zip(song.sections, full.section_starts()):
            if bars and (sb + sec.bars < bars[0] or sb + 1 > bars[1]):
                continue
            sec.parts = {k: v for k, v in sec.parts.items() if k in names}
            sec.fills = {k: v for k, v in sec.fills.items() if k in names}
            sec.automation = {k: v for k, v in sec.automation.items() if k in names}
            secs.append((sb, sec))
        used = {p.pattern for _, sec in secs for p in list(sec.parts.values()) + list(sec.fills.values())}
        head = [f"# {song.title} — zoom: " + ", ".join(x for x in (f"bars {bars[0]}-{bars[1]}" if bars else "", "tracks " + " ".join(sorted(names)) if tracks else "") if x),
                f"{song.bpm:g} BPM · {song.key} · swing {song.swing:g}%", "", "## Tracks"]
        whole = pack(full, include_patterns=False).splitlines()
        head += [ln for ln in whole if ln.startswith("- ") and ln[2:].split(" (")[0] in names]
        head += ["", "## Sections (bar numbers are the song's)", "| section | kind | bars | energy | playing | fills | automation |", "|---|---|---|---|---|---|---|"]
        for sb, sec in secs:
            row = next(ln for ln in pack(_only(song, sec), include_patterns=False).splitlines() if ln.startswith("| 0 |"))
            cells = row.split(" | ")
            head.append(f"| {cells[1]} | {cells[2]} | {sb + 1}-{sb + sec.bars} ({sec.bars}) | " + " | ".join(cells[5:]))
        head += ["", "## Patterns"]
        for pn, p in song.patterns.items():
            if pn in used:
                head.extend(pattern_text(p, song))
                head.append("")
        return "\n".join(head).rstrip() + "\n"
    L: list[str] = []
    spb = 60.0 / song.bpm * BEATS_PER_BAR
    L.append(f"# {song.title}")
    L.append(f"{song.bpm:g} BPM · {song.key} · swing {song.swing:g}% · {song.total_bars} bars · {_mmss(song.duration_s)}"
             + (f" · {song.meta.get('subgenre')} / {song.meta.get('template')}" if song.meta.get("subgenre") else ""))
    if song.meta.get("options"):
        L.append("options (song.py `option()`; switch with `ableton-use ab` or `--set`): " + ", ".join(
            f"{k}={v['value']}" + ("" if v["value"] == v["default"] else f" (default {v['default']})") for k, v in song.meta["options"].items()))
    L.append("")
    L.append("## Tracks")
    for t in song.tracks:
        flags = [f for f, on in (("sidechain", t.sidechain), ("swing", t.swing), ("muted", t.mute)) if on]
        if t.audio:
            inst = "audio track"
        elif t.serum:
            inst = f"Serum 2 preset '{t.serum}' (rendered through the plug-in)" + (" " + ", ".join(f"{k}={v}" for k, v in t.serum_params.items()) if t.serum_params else "")
        elif t.sample:
            inst = f"Simpler '{t.sample}'" + (f" root {pname(round(t.sample_root))} ({t.sample_root:.2f})" if t.sample_root is not None else " one-shot")
        else:
            inst = f"inst '{t.instrument[0] if t.instrument else '?'}'"
        if t.groove:
            g = t.groove
            bits = [g["template"]] if g.get("template") else []
            bits += [f"swing {g['swing']:g}%"] if "swing" in g else []
            bits += ["timing ms " + " ".join(f"{v:+g}" if v else "·" for v in g["timing"])] if "timing" in g else []
            bits += ["accent " + " ".join(f"{v:+g}" if v else "·" for v in g["accent"])] if "accent" in g else []
            bits += [f"gate {g['gate']:g}"] if "gate" in g else []
            bits += [f"humanize ±{g['humanize'].get('ms', 0):g} ms ±{g['humanize'].get('vel', 0):g} vel"] if g.get("humanize") else []
            flags.append("groove " + ", ".join(bits))
        if t.delay_ms:
            flags.append(f"delay {t.delay_ms:+g} ms")
        if t.sends:
            flags.append("sends " + ", ".join(f"{k} {v:g} dB" for k, v in sorted(t.sends.items())))
        if t.instrument_params:
            flags.append("inst " + ", ".join(f"{k} {v}" for k, v in t.instrument_params.items()))
        for e in t.midi_effects:
            prm = ", ".join(f"{k} {v}" for k, v in (e.get("params") or {}).items())
            flags.append("midi fx " + e["device"] + (f": {prm}" if prm else ""))
        for e in t.effects:
            prm = ", ".join(f"{k} {v}" for k, v in (e.get("params") or {}).items())
            flags.append("fx " + e["device"] + (f" keyed from {e['sidechain']}" if e.get("sidechain") else "") + (f": {prm}" if prm else ""))
        L.append(f"- {t.name} ({t.role}) {t.volume_db:+.0f} dB, pan {t.pan:+.1f}, {inst}" + (f" [{', '.join(flags)}]" if flags else ""))
    for letter in sorted(song.returns):
        L.append(f"- return {letter}: " + " → ".join(e["device"] + (" (" + ", ".join(f"{k} {v}" for k, v in (e.get("params") or {}).items()) + ")" if e.get("params") else "") for e in song.returns[letter]))
    if song.master_effects:
        L.append("- master: " + " → ".join(e["device"] + (" (" + ", ".join(f"{k} {v}" for k, v in (e.get("params") or {}).items()) + ")" if e.get("params") else "") for e in song.master_effects))
    L.append("")
    L.append("## Sections")
    L.append("| # | section | kind | bars | time | energy | playing | fills | automation |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for i, (sec, sb) in enumerate(zip(song.sections, song.section_starts())):
        def part_s(tn, p):
            s = tn if p.pattern.lower() == tn.lower() else f"{tn}={p.pattern}"
            end = sec.bars if p.end is None else p.end
            if p.start or end != sec.bars:
                s += f"[{p.start + 1}-{end}]"
            if p.transpose:
                s += f"{p.transpose:+d}st"
            return s
        playing = ", ".join(part_s(tn, p) for tn, p in sec.parts.items()) or "—"
        fills = ", ".join(f"{tn}={f.pattern}" + (f"/{f.every}" if f.every else "") for tn, f in sec.fills.items()) or "—"
        auto = ", ".join(f"{tn}.{prm} {v[0] if not isinstance(v[0], list) else v[0][1]}→{v[-1] if not isinstance(v[-1], list) else v[-1][1]}"
                         for tn, d in sec.automation.items() for prm, v in d.items()) or "—"
        L.append(f"| {i} | **{sec.name}** | {sec.kind} | {sb + 1}-{sb + sec.bars} ({sec.bars}) | {_mmss(sb * spb)} | {sec.energy} | {playing} | {fills} | {auto} |")
    L.append("")
    L.append("## Energy curve (intended)")
    L.append("```")
    L.append(" ".join(f"{s.name}:{'▁▂▃▄▅▆▇██'[min(8, round(s.energy * 0.8))]}{s.energy}" for s in song.sections))
    L.append("```")
    L.append("")
    L.append("## Arrangement map (1 char = 4 bars; █ plays, ▒ fill only)")
    L.append("```")
    L.extend(arrangement_grid(song))
    L.append("```")
    if include_patterns:
        L.append("")
        L.append("## Patterns  (events: beat.sixteenth note length-in-beats [vVEL if not 100]; '—' = no new notes, held notes ring on)")
        for p in song.patterns.values():
            L.extend(pattern_text(p, song))
            L.append("")
    return "\n".join(L).rstrip() + "\n"
