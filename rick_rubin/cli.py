"""rick-rubin command line. Every command takes a project folder."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .project import Project


def _bars(s: str) -> tuple[int, int]:
    a, _, b = s.partition("-")
    return int(a), int(b or a)


def _main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="rick-rubin", description="Agentic house-music production rendered to Ableton Live.")
    ap.add_argument("--set", action="append", default=[], metavar="NAME=VALUE", dest="options",
                    help="run this command with an `option()` choice of song.py switched (repeatable), e.g. --set bass=reese")
    ap.add_argument("--daw", choices=["live", "logic"], default=os.environ.get("RICK_RUBIN_DAW", "live"),
                    help="which DAW push/capture/status talk to: Ableton Live (default) or Logic Pro (also: RICK_RUBIN_DAW=logic)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="start a project: an empty song.py to write the song in")
    s.add_argument("dir")
    s.add_argument("--title", required=True)
    s.add_argument("--bpm", type=float, required=True)
    s.add_argument("--key", required=True, help='e.g. "F minor", "D dorian"')

    s = sub.add_parser("check", help="lint and type-check song.py, build it, and run the music lint — everything that can be wrong before listening")
    s.add_argument("dir")
    s.add_argument("--audio", action="store_true", help="also render the preview and run the audio checks")

    s = sub.add_parser("build", help="run song.py and refresh song.json + score.md (other commands do this automatically)")
    s.add_argument("dir")

    def zoom(sp):
        sp.add_argument("--bars", type=_bars, help="zoom in on a bar range, e.g. 33-48")
        sp.add_argument("--tracks", nargs="*", help="zoom in on these tracks only")

    s = sub.add_parser("score", help="print the packed score (and refresh score.md); --bars/--tracks print a zoomed score")
    s.add_argument("dir")
    zoom(s)

    s = sub.add_parser("capture", help="record the pushed arrangement from Live's own output (real time) and measure it")
    s.add_argument("dir")
    zoom(s)
    s.add_argument("--port", type=int, default=9889)

    for name, hlp in (("midi", "export song.mid + per-track .mid"),
                      ("undo", "revert the last edit batch"),
                      ("info", "one-line JSON summary")):
        sub.add_parser(name, help=hlp).add_argument("dir")

    s = sub.add_parser("edit", help="apply JSON edit ops from a file or '-' (stdin)")
    s.add_argument("dir")
    s.add_argument("ops")

    s = sub.add_parser("preview", help="render preview.wav")
    s.add_argument("dir")
    s.add_argument("--stems", action="store_true")

    s = sub.add_parser("eval", help="lint + render + measure -> eval.md")
    s.add_argument("dir")
    s.add_argument("--no-audio", action="store_true")
    s.add_argument("--live", action="store_true", help="measure live.wav (from `capture`) instead of rendering the preview")
    zoom(s)

    s = sub.add_parser("view", help="timeline PNG for a bar range, e.g. --bars 65-80")
    s.add_argument("dir")
    s.add_argument("--bars", type=_bars)
    s.add_argument("--tracks", nargs="*")

    s = sub.add_parser("push", help="render into Ableton Live via the bridge")
    s.add_argument("dir")
    s.add_argument("--replace", action="store_true", help="delete same-named tracks first")
    s.add_argument("--clean", action="store_true", help="also remove the set's untouched empty tracks (Live Intro/Lite have a 16/8-track limit)")
    s.add_argument("--update", action="store_true", help="redo only what changed since the last push from this project: a changed part rebuilds "
                   "its track, a changed device parameter / fader / send is set in place (full replace if the set no longer matches)")
    s.add_argument("--no-instruments", action="store_true")
    s.add_argument("--automation", action="store_true", help="Logic: also write the sections' volume automation (played in real time)")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=9889)

    s = sub.add_parser("watch", help="hot reload: every save of song.py is rebuilt and only what changed is redone in Live, while it plays")
    s.add_argument("dir")
    s.add_argument("--bars", type=_bars, help="loop this bar range in Live, e.g. 81-88")
    s.add_argument("--play", action="store_true", help="start Live's playback")
    s.add_argument("--port", type=int, default=9889)

    s = sub.add_parser("sample", help="import a one-shot or loop into <dir>/samples/ (loops are conformed to the song tempo)")
    s.add_argument("dir")
    s.add_argument("src")
    s.add_argument("--name", required=True)
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--loop", action="store_true", help="tempo-match and cut to whole bars; plays on an audio track")
    g.add_argument("--oneshot", action="store_true", help="copy as-is; plays in a Simpler")
    s.add_argument("--src-bpm", type=float, help="tempo of the source loop")
    s.add_argument("--bars", type=int, help="loop length in bars (default: nearest whole bar)")
    s.add_argument("--align", default="start", choices=["start", "end"], help="'end' keeps the tail (risers)")
    s.add_argument("--end-at", type=float, help="seconds into the loop to cut at first; with --align end, puts that moment (a riser's peak) on the next downbeat")
    s.add_argument("--melodic", action="store_true", help="measure the one-shot's pitch (sample_root)")

    s = sub.add_parser("width", help="stereo image report: correlation, side %%, mono loss, per band and per section")
    s.add_argument("dir")
    s.add_argument("wav", nargs="?", help="file to analyse (default: live.wav if captured, else preview.wav); a sample path gets a whole-file report")
    s.add_argument("--bars", type=_bars, help="zoom in on a bar range of the mix")
    s.add_argument("--png", action="store_true", help="also draw the imager picture (vectorscope, correlation over time, width by band)")

    s = sub.add_parser("spectrum", help="spectrum analyzer picture: overlay the spectra of files, or of soloed tracks of the song")
    s.add_argument("dir")
    s.add_argument("files", nargs="*", help="audio files to overlay (project-relative or absolute)")
    s.add_argument("--tracks", nargs="*", help="instead of files: solo each of these tracks in the offline render and overlay them")
    s.add_argument("--bars", type=_bars, help="with --tracks or the mix: only this bar range")
    s.add_argument("--mix", action="store_true", help="include the full mix (live.wav if captured, else the preview)")

    s = sub.add_parser("ab", help="candidates side by side: build, render (or push to Live and record) each `option()` choice and compare the measurements")
    s.add_argument("dir")
    s.add_argument("variants", nargs="+", metavar="NAME=VALUE", help="one candidate each, e.g. hatvel=35 hatvel=60; several switches: bass=reese,hatvel=35; "
                   "a label can be put in front: bright:stab=sq,cutoff=90")
    zoom(s)
    s.add_argument("--live", action="store_true", help="push each candidate to Live and record it (real time) instead of the offline preview")
    s.add_argument("--no-base", action="store_true", help="leave out the song as it stands (it is the first column otherwise)")
    s.add_argument("--hits", action="store_true", help="also print the per-step hit levels of each candidate")
    s.add_argument("--reference", action="store_true", help="also put each candidate against the reference tracks (movement, texture changes, "
                   "loudness, width ...): arrangement candidates want this, over 16 bars or more")
    s.add_argument("--port", type=int, default=9889)

    s = sub.add_parser("compare", help="audio files side by side: loudness, crest, bands, width, transients (first file is the baseline)")
    s.add_argument("dir")
    s.add_argument("files", nargs="+")

    s = sub.add_parser("hits", help="level of every 16th step, bar by bar, next to the written velocities — do the accents and ghosts come out as written?")
    s.add_argument("dir")
    s.add_argument("wav", nargs="?", help="an audio file (default: render the preview, or --live to record from Live)")
    zoom(s)
    s.add_argument("--live", action="store_true", help="record the bars from Live (soloing --tracks)")
    s.add_argument("--grid", type=int, default=16)
    s.add_argument("--start-bar", type=int, help="the bar the wav file starts on (default 1; zoom/live_bars_081-... files start on bar 81)")

    s = sub.add_parser("devices", help="a Live device's parameters with their ranges and choices, read from Live (remembered afterwards)")
    s.add_argument("names", nargs="*", help="device names, e.g. Compressor Saturator \"Channel EQ\"; none: list the ones already read")
    s.add_argument("--refresh", action="store_true")
    s.add_argument("--port", type=int, default=9889)

    s = sub.add_parser("reference", help="measure a mix against released tracks: loudness, punch, balance, width, pump, movement")
    s.add_argument("action", choices=["add", "list", "compare"])
    s.add_argument("paths", nargs="*", help="add: audio files of released tracks in the genre · compare: a project folder, "
                                            "optionally followed by a wav (default: its live.wav, else preview.wav)")

    s = sub.add_parser("transcribe", help="syllables of a vocal sample with bar.beat.sixteenth positions and ms offsets (cached; shown in score.md)")
    s.add_argument("dir")
    s.add_argument("sample", help="project-relative path, e.g. samples/vocal.wav")
    s.add_argument("--text", help="the lyric, if you know it — more reliable than recognising it")
    s.add_argument("--bpm", type=float, help="tempo to map onto (default: the song's — right for conformed loops)")
    s.add_argument("--model", default="small.en", help="Whisper model for the words: small.en, medium.en, large-v3 ...")
    s.add_argument("--language")

    s = sub.add_parser("samples", help="this project's samples (raw downloads and imports) with their measured character; search and sort them")
    s.add_argument("dir")
    s.add_argument("words", nargs="*", help="words that must match the file name or character (snappy dark subby wide ...)")
    s.add_argument("--not", dest="exclude", nargs="+", default=[], metavar="WORD", help="leave out anything matching these words")
    s.add_argument("--sort", help="attack decay bright dark sub bass wide loud length")
    s.add_argument("--like", help="rank by closeness in sound to this sample (project-relative path)")

    s = sub.add_parser("audition", help="compare candidate samples side by side by measurement (length, punch, spectrum, pitch+octave, width)")
    s.add_argument("dir")
    s.add_argument("files", nargs="+", help="sample files (project-relative or absolute); pass every candidate for one role together")
    s.add_argument("--png", metavar="NAME", help="also draw the comparison (waveforms on one scale + overlaid spectra) to views/audition_NAME.png")

    s = sub.add_parser("browse", help="list what Live's browser offers: instruments, presets, effects, plug-ins (needs the bridge)")
    s.add_argument("path", nargs="?", default="", help='e.g. "sounds", "sounds/Bass", "instruments/Drift", "drums", "audio_effects", "plugins", "user_library"')
    s.add_argument("--search", help="only names containing this text")
    s.add_argument("--port", type=int, default=9889)

    s = sub.add_parser("notes", help="the notes inside a single-voice sample: pitch with octave, cents, position, length (cached; shown in score.md)")
    s.add_argument("dir")
    s.add_argument("sample", help="project-relative path, e.g. samples/vocal.wav")
    s.add_argument("--bpm", type=float, help="tempo to map onto (default: the song's)")
    s.add_argument("--fmin", type=float, default=65.0, help="lowest pitch to look for in Hz (lower it for bass: 30)")
    s.add_argument("--fmax", type=float, default=1000.0)

    s = sub.add_parser("retime", help="audio-quantize a vocal loop: slide each word (or syllable) so its vowel lands on the grid")
    s.add_argument("dir")
    s.add_argument("sample", help="a transcribed loop, e.g. samples/vocal.wav")
    s.add_argument("--name", required=True, help="name of the new loop (samples/<name>.wav)")
    s.add_argument("--by", default="word", choices=["word", "syllable"])
    s.add_argument("--grid", type=int, default=16, choices=[4, 8, 16, 32], help="note value to land on (default 16ths)")
    s.add_argument("--strength", type=float, default=1.0, help="0..1: how far towards the grid to move")
    s.add_argument("--move", action="append", default=[], metavar="N=POS",
                   help="place piece N yourself, e.g. --move 3=2.3.1 (bar.beat.sixteenth); repeatable")

    s = sub.add_parser("split", help="separate a recording into stems (vocals, drums, bass, guitar, piano, other) with Logic Pro's Stem Splitter")
    s.add_argument("dir")
    s.add_argument("source", help="the recording (wav, aiff, mp3, m4a), project-relative or absolute, e.g. refs/track.wav")
    s.add_argument("--stems", default="all", help="comma-separated: vocals,drums,bass,guitar,piano,other (default all)")
    s.add_argument("--out", help="folder for <stem>.wav (default: stems/<source name>/ in the project)")
    s.add_argument("--from", dest="start_s", type=float, help="split only from this second of the recording")
    s.add_argument("--to", dest="end_s", type=float, help="... up to this second")
    s.add_argument("--submix", action="store_true", help="also write the stems not asked for, summed (Logic's Submix), as submix.wav")
    s.add_argument("--close", action="store_true", help="close the Logic project afterwards (it is saved either way)")

    s = sub.add_parser("serum", help="read Serum 2 presets: `serum list` to find one, `serum show NAME` for its patch sheet")
    s.add_argument("action", choices=["list", "search", "index", "show", "params", "render", "view"])
    s.add_argument("words", nargs="*", help="show/params/render/view: the preset's name (or words from it, or a path); "
                                            "search/list: words that must all match")
    s.add_argument("--sort", help="search: attack decay bright dark sub bass wide loud length")
    s.add_argument("--like", nargs="+", help="search: rank by closeness in sound to this preset (its name, or words from it)")
    s.add_argument("--not", dest="exclude", nargs="+", default=[], metavar="WORD", help="search: leave out anything matching these words")
    s.add_argument("--limit", type=int, default=25)
    s.add_argument("--note", action="append", default=[], help="render: note(s) to play, e.g. --note C1 --note G1 (default C2); Ableton naming")
    s.add_argument("--secs", type=float, default=1.0, help="render: how long each note is held")
    s.add_argument("--set", action="append", default=[], metavar="PARAM=VALUE", help="render/params: set a Serum parameter first, e.g. --set macro_1=80")
    s.add_argument("--out", help="render: the wav to write (e.g. <project>/samples/raw/reese_C1.wav); view: the png to write")
    s.add_argument("--search", help="list: words that must appear in the name, description, author or folder")
    s.add_argument("--tag", help="list: Wavetable | Poly | Mono | Multisample | Sample | Granular | Spectral | Arp | Clip")
    s.add_argument("--folder", help="list: e.g. Pads, Bass, Leads")
    s.add_argument("--root", help="preset folder (default: Serum 2's own)")

    s = sub.add_parser("remember", help="append a session entry to project.md")
    s.add_argument("dir")
    for k in ("strategy", "decisions", "reasoning", "outstanding"):
        s.add_argument(f"--{k}", default="")

    s = sub.add_parser("install-bridge", help="copy the RickRubin remote script into Live's User Library")
    s.add_argument("--dest", help="Remote Scripts folder (default: your User Library)")

    s = sub.add_parser("status", help="check the Live bridge connection")
    s.add_argument("--port", type=int, default=9889)

    a = ap.parse_args(argv)
    if a.options:
        from . import options
        os.environ[options.ENV] = json.dumps({**options.active(), **options.parse(a.options)})

    if a.cmd == "init":
        p = Project.init(a.dir, a.title, a.bpm, a.key)
        print(f"created {p.source_path}\nWrite the song there (SKILL.md, 'Writing a song'), then: rick-rubin score {a.dir}")
    elif a.cmd == "check":
        stages, errors = Project(a.dir).check(audio=a.audio)
        for name, ok, out in stages:
            print(f"{'ok  ' if ok else 'FAIL'}  {name}")
            if out and out != "ok":
                print("\n".join("      " + ln for ln in out.splitlines()))
        print(f"\n{'check failed' if errors else 'check passed'} — {errors} error(s)")
        return 1 if errors else 0
    elif a.cmd == "build":
        p = Project(a.dir)
        song = p.build()
        print(f"built {p.song_path.name}: {len(song.tracks)} tracks, {len(song.patterns)} patterns, {song.total_bars} bars")
    elif a.cmd == "score":
        print(Project(a.dir).score(a.bars, a.tracks))
    elif a.cmd == "info":
        print(json.dumps(Project(a.dir).summary()))
    elif a.cmd == "midi":
        for path in Project(a.dir).midi():
            print(path)
    elif a.cmd == "undo":
        print("restored", Project(a.dir).undo())
    elif a.cmd == "edit":
        raw = sys.stdin.read() if a.ops == "-" else Path(a.ops).read_text()
        for line in Project(a.dir).edit(json.loads(raw)):
            print(line)
    elif a.cmd == "preview":
        r = Project(a.dir).preview(stems=a.stems)
        print(f"{r.path} ({r.duration_s:.1f}s)" + (f", {len(r.stems)} stems" if r.stems else ""))
    elif a.cmd == "capture":
        from .analysis import measure, measurement_table, stereo_report
        p = Project(a.dir)
        r = p.capture(a.bars, a.tracks, port=a.port, progress=lambda m: print("·", m, file=sys.stderr), daw=a.daw)
        song = p.load()
        m = measure(r["path"], song, bars=a.bars, file_start_bar=r["bars"][0])
        what = ", ".join(x for x in (f"bars {r['bars'][0]}-{r['bars'][1]}", "solo " + " ".join(a.tracks) if a.tracks else "") if x)
        print(f"# {"Logic bounce" if a.daw == "logic" else "Live capture"} — {what}\n{r['path']}  ({r['seconds']:.1f} s, {m.integrated_lufs:.1f} LUFS, peak {m.peak_db:.1f} dBFS, "
              f"{m.clipped_samples} clipped samples)\n")
        print("\n".join(measurement_table(m)))
        print("\n".join(str(i) for i in m.issues))
        print()
        print(stereo_report(r["path"], song, a.bars, r["bars"][0]))
        print("view:", p.view(a.bars, a.tracks, wav=r["path"], wav_start_bar=r["bars"][0]))
    elif a.cmd == "eval" and (a.bars or a.tracks or a.live):
        from .analysis import measure, measurement_table
        p = Project(a.dir)
        if a.live:
            if a.tracks:
                ap.error("--live measures Live's full mix; use `capture --tracks ...` to record a solo")
            wav, m = p.live_path, measure(p.live_path, p.load(), bars=a.bars)
        else:
            wav, m = p.measure_zoom(a.bars, a.tracks)
        what = ", ".join(x for x in (f"bars {a.bars[0]}-{a.bars[1]}" if a.bars else "", "tracks " + " ".join(a.tracks) if a.tracks else "") if x) or "whole song"
        print(f"# Measured — {what} ({'Live capture' if a.live else 'offline preview'}: {wav.name})")
        print(f"{m.integrated_lufs:.1f} LUFS, peak {m.peak_db:.1f} dBFS\n")
        print("\n".join(measurement_table(m)))
        print("\n".join(str(i) for i in m.issues))
    elif a.cmd == "eval":
        r = Project(a.dir).evaluate(audio=not a.no_audio)
        print(r.text)
        return 1 if r.errors else 0
    elif a.cmd == "view":
        print(Project(a.dir).view(a.bars, a.tracks))
    elif a.cmd == "push":
        rep = Project(a.dir).push(a.host, a.port, a.replace, not a.no_instruments, clean=a.clean, update=a.update, daw=a.daw,
                                  automation=a.automation, progress=lambda m: print("·", m, file=sys.stderr))
        print(rep.text())
    elif a.cmd == "watch":
        try:
            Project(a.dir).watch(a.bars, a.play, port=a.port, say=lambda m: print(m, flush=True), daw=a.daw)
        except KeyboardInterrupt:
            print("stopped watching")
    elif a.cmd == "sample":
        if a.loop and not a.src_bpm:
            ap.error("--loop needs --src-bpm (the tempo the loop was recorded at)")
        r = Project(a.dir).add_sample(a.src, a.name, loop=a.loop, src_bpm=a.src_bpm, bars=a.bars, align=a.align, melodic=a.melodic, end_at=a.end_at)
        print(r.describe())
        from .samples import FEATURE_HEAD, analyse_project_samples, feature_row
        rows = analyse_project_samples(Project(a.dir).root)          # measured character, recorded in the manifest
        if r.rel in rows:
            print(FEATURE_HEAD + "\n" + feature_row(rows[r.rel], r.rel))
        var = "".join(ch if ch.isalnum() else "_" for ch in a.name)
        if r.kind == "loop":
            print("in song.py:")
            print(f'  {var}_trk = song.add_track("{a.name.title()}", "perc", audio=True)')
            print(f'  {var} = song.pattern("{a.name}", {var}_trk, audio="{r.rel}", bars={r.bars})')
        else:
            root = f", sample_root={r.root:.2f}" if r.root is not None else ""
            print(f'in song.py:  song.add_track("{a.name.title()}", "<role>", sample="{r.rel}"{root})')
    elif a.cmd == "width":
        from .analysis import stereo_report
        p = Project(a.dir)
        if a.wav:
            wav = Path(a.wav) if Path(a.wav).exists() else p.root / a.wav
            full_mix = wav.resolve() in (p.live_path.resolve(), p.preview_path.resolve())
        else:
            wav, full_mix = (p.live_path if p.live_path.exists() else p.preview_path), True
            if wav == p.preview_path:
                print("(no Live capture yet — this is the offline sketch, whose stems are mono; width only reflects panning)\n")
        text = stereo_report(wav, p.load() if full_mix else None, a.bars if full_mix else None)
        if full_mix and not a.bars:
            (p.root / "width.md").write_text(text)
        print(text)
        if a.png:
            from .pictures import imager_png
            t0 = t1 = None
            if full_mix and a.bars:
                spbar = 240.0 / p.load().bpm
                t0, t1 = (a.bars[0] - 1) * spbar, a.bars[1] * spbar
            tag = f"_bars_{a.bars[0]:03d}-{a.bars[1]:03d}" if (full_mix and a.bars) else ""
            print("picture:", imager_png(wav, p.root / "views" / f"imager_{wav.stem}{tag}.png", t0=t0 or 0.0, t1=t1))
    elif a.cmd == "spectrum":
        from .pictures import spectrum_png
        p = Project(a.dir)
        song = p.load()
        spbar = 240.0 / song.bpm
        span = ((a.bars[0] - 1) * spbar, a.bars[1] * spbar) if a.bars else None
        sounds, spans = [], {}
        for f in a.files:
            path = Path(f) if Path(f).exists() else p.root / f
            sounds.append((path.stem, path))
        from .render.preview import render_preview
        mix_peak = None
        if a.tracks:                                  # solos keep their level relative to the full offline mix
            mix_peak = 10 ** (render_preview(song, p.preview_path).peak_dbfs_premaster / 20)
        for t in a.tracks or []:
            wav = p.zoom_path("preview", None, [t])
            render_preview(song, wav, tracks=[t], master_peak=mix_peak)
            sounds.append((t, wav))
            if span:
                spans[t] = span
        if a.mix or not sounds:
            mix = p.live_path if p.live_path.exists() else p.preview_path
            sounds.append((f"mix ({mix.stem})", mix))
            if span:
                spans[f"mix ({mix.stem})"] = span
        name = "spectrum_" + "+".join(lbl.split(" ")[0] for lbl, _ in sounds)[:80] + (f"_bars_{a.bars[0]:03d}-{a.bars[1]:03d}" if a.bars else "")
        title = "spectrum — " + ", ".join(lbl for lbl, _ in sounds) + (f" — bars {a.bars[0]}-{a.bars[1]}" if a.bars else "")
        print(spectrum_png(sounds, p.root / "views" / f"{name}.png", title, spans))
    elif a.cmd == "ab":
        import re

        from . import options
        from .analysis import compare_table, hit_levels, hits_text
        from .samples import read_audio
        p = Project(a.dir)
        variants: list[tuple[str, dict[str, str]]] = [] if a.no_base else [("base", {})]
        for v in a.variants:
            label, colon, rest = v.partition(":")
            if not colon:
                label, rest = re.sub(r"[^A-Za-z0-9.+-]+", "-", v).strip("-"), v
            variants.append((label, options.parse([rest])))
        files = p.ab(variants, a.bars, a.tracks, a.live, port=a.port, progress=lambda m: print("·", m, file=sys.stderr), daw=a.daw)
        song = p.load()
        what = ", ".join(x for x in (f"bars {a.bars[0]}-{a.bars[1]}" if a.bars else "whole song", "solo " + " ".join(a.tracks) if a.tracks else "") if x)
        print(f"# A/B — {what} ({('bounced from Logic' if a.daw == 'logic' else 'recorded from Live') if a.live else 'offline preview'})")
        for label, vals in variants:
            print(f"- {label}: " + (", ".join(f"{k}={v}" for k, v in vals.items()) or "the song as it stands"))
        print()
        print(compare_table([(lbl, f) for lbl, f in files]))
        if a.reference:
            from . import reference as ref
            shelf = ref.load_shelf()
            if not shelf:
                print("\n(no references on the shelf: `rick-rubin reference add <released tracks>`)")
            else:
                print("\nagainst the reference tracks ('!' = outside their range" + ("" if a.live else "; offline preview: only the arrangement lines "
                      "— movement, repeats, texture changes — mean anything, the sound lines need --live") + ")")
                print(ref.compare_many([ref.profile(f, lbl, bpm=song.bpm) for lbl, f in files], shelf))
        if a.hits:
            for label, f in files:
                sr, x = read_audio(f)
                print(f"\n{label}")
                print(hits_text(hit_levels(x, sr, song.bpm), a.bars[0] if a.bars else 1))
        print("\nfiles: " + "  ".join(str(f.relative_to(p.root)) for _, f in files))
        print("keep a winner by making it the default of its option() in song.py" + ("; Live holds the song as it stands again" if a.live else ""))
    elif a.cmd == "compare":
        from .analysis import compare_table
        p = Project(a.dir)
        files = [Path(f) if Path(f).exists() else p.root / f for f in a.files]
        missing = [str(f) for f in files if not f.exists()]
        if missing:
            ap.error("not found: " + ", ".join(missing))
        print(compare_table([(f.stem, f) for f in files]))
    elif a.cmd == "hits":
        print(Project(a.dir).hits(a.bars, a.tracks, a.wav, a.live, a.grid, a.start_bar, progress=lambda m: print("·", m, file=sys.stderr)))
    elif a.cmd == "devices":
        from .live import LiveBridge
        from .live.client import describe_device, device_text, devices_cache, live_lock
        cache = json.loads(devices_cache().read_text()) if devices_cache().exists() else {}
        if not a.names:
            for d in cache.values():
                print(f"{d['device']}: " + ", ".join(q["name"] for q in d["parameters"]))
            print(f"{len(cache)} devices read so far — `rick-rubin devices <name>` reads one from Live (what Live has: `rick-rubin browse audio_effects`)")
            return 0
        for n in a.names:
            hit = next((d for k, d in cache.items() if k.lower() == n.lower()), None)
            if hit is None or a.refresh:
                with live_lock("devices", port=a.port), LiveBridge(port=a.port) as b:
                    hit = describe_device(b, n)
            print(device_text(hit) + "\n")
    elif a.cmd == "reference":
        from . import reference as ref
        if a.action == "add":
            if not a.paths:
                ap.error("reference add needs audio files")
            added = ref.add_references(a.paths, progress=lambda m: print("·", m, file=sys.stderr))
            print(ref.SUMMARY_HEAD + "\n" + "\n".join(ref.summary_row(x) for x in added))
            print(f"{len(ref.load_shelf())} references on the shelf ({ref.shelf_path()}); only measurements are stored, not audio")
        elif a.action == "list":
            shelf = ref.load_shelf()
            print(ref.SUMMARY_HEAD + "\n" + "\n".join(ref.summary_row(x) for x in shelf))
            print(f"{len(shelf)} references")
        else:
            shelf = ref.load_shelf()
            if not shelf:
                ap.error("no references yet: `rick-rubin reference add <released tracks in the genre>`")
            if not a.paths:
                ap.error("reference compare needs a project folder")
            proj = Project(a.paths[0])
            wav = Path(a.paths[1]) if len(a.paths) > 1 else (proj.live_path if proj.live_path.exists() else proj.preview_path)
            if not wav.exists():
                wav = proj.root / a.paths[1]
            if wav == proj.preview_path:
                print("(no Live capture: comparing the offline preview — its loudness, punch and width are not Live's)\n")
            song = proj.load()
            text = ref.compare(ref.profile(wav, f"{song.title} ({wav.name})", bpm=song.bpm), shelf)
            if wav.resolve() == proj.live_path.resolve():       # reference.md is the reading of the full Live capture only
                (proj.root / "reference.md").write_text(text)
            print(text)
    elif a.cmd == "transcribe":
        from .transcribe import table, transcribe
        p = Project(a.dir)
        bpm = a.bpm or p.tempo()
        words = transcribe((p.root / a.sample), bpm, a.model, a.language, a.text)
        print(f"{a.sample} at {bpm:g} BPM — {len(words)} words, {sum(len(w.syllables) for w in words)} syllables")
        print("(position and offset are of the vowel — what is heard as on or off the beat; 'cut at' is where the sound starts)")
        print(table(words))
    elif a.cmd == "samples":
        from .samples import FEATURE_HEAD, analyse_project_samples, feature_row, search_rows, similar
        p = Project(a.dir)
        rows = analyse_project_samples(p.root)
        hits = search_rows(rows, list(a.words) + ["-" + w for w in a.exclude], a.sort)
        if a.like:
            if a.like not in rows:
                ap.error(f"{a.like} is not one of this project's samples")
            hits = [(k, d) for k, d, _ in similar({k: d for k, d in dict(hits).items() if k != a.like}, rows[a.like], 20)]
        print(FEATURE_HEAD)
        for name, d in hits:
            print(feature_row(d, name))
        print(f"{len(hits)} of {len(rows)} samples (analysis cached in samples/manifest.json)")
    elif a.cmd == "audition":
        from .samples import audition_table
        p = Project(a.dir)
        files = [Path(f) if Path(f).exists() else p.root / f for f in a.files]
        missing = [str(f) for f in files if not f.exists()]
        if missing:
            ap.error("not found: " + ", ".join(missing))
        print(audition_table(files))
        if a.png:
            from .pictures import audition_png
            print("picture:", audition_png(files, p.root / "views" / f"audition_{a.png}.png", f"sample comparison — {a.png}"))
    elif a.cmd == "browse":
        from .live import LiveBridge
        with LiveBridge(port=a.port) as b:
            parts = [x for x in a.path.split("/") if x]
            if not parts:
                print("categories: sounds, instruments, drums, audio_effects, midi_effects, plugins, user_library, packs, samples, clips")
                return 0
            path = "app.browser." + parts[0]
            for want in parts[1:]:
                kids = b.call("lom", path=path + ".children")
                hit = [i for i, k in enumerate(kids) if k.lower() == want.lower()] or [i for i, k in enumerate(kids) if want.lower() in k.lower()]
                if not hit:
                    ap.error(f"no {want!r} in {path.split('.', 2)[2]}; have: {', '.join(kids[:60])}")
                path += f".children[{hit[0]}]"
            kids = b.call("lom", path=path + ".children")
            shown = [k for k in kids if not a.search or a.search.lower() in k.lower()]
            for k in shown:
                print(k)
            print(f"{len(shown)} of {len(kids)} items in {a.path} — load one by name with instrument=\"<name without extension>\" "
                  "(folders can be browsed further: browse \"" + a.path + "/<folder>\")")
    elif a.cmd == "notes":
        from .pitch import sample_notes, table
        from .transcribe import load_words
        p = Project(a.dir)
        song = p._run_source() if p.source_path.exists() else p.load()
        notes = sample_notes(p.root / a.sample, a.bpm or song.bpm, song.key_obj, fmin=a.fmin, fmax=a.fmax)
        print(f"{a.sample} at {a.bpm or song.bpm:g} BPM, song key {song.key} ('!' = outside it)")
        print(table(notes, load_words(p.root / a.sample)))
    elif a.cmd == "retime":
        from .transcribe import load_words, retime_loop
        p = Project(a.dir)
        src = p.root / a.sample
        words = load_words(src)
        if words is None:
            ap.error(f"{a.sample} has no transcription yet: run `rick-rubin transcribe {a.dir} {a.sample}` first")
        moves = {int(k): v for k, v in (m.split("=", 1) for m in a.move)}
        dst = p.root / "samples" / f"{a.name}.wav"
        rows = retime_loop(src, dst, p.tempo(), words, a.by, a.grid, a.strength, moves)
        print(f"samples/{a.name}.wav — {len(rows)} pieces moved by {a.by}, onto 1/{a.grid} notes")
        print(" n  piece        from        to          shift")
        for r in rows:
            print(f"{r['n']:2d}  {r['text']:<12} {r['from_pos']:<11} {r['to_pos']:<11} {r['shift_ms']:+6.0f} ms")
        print(f'in song.py:  audio="samples/{a.name}.wav"')
    elif a.cmd == "serum":
        from . import serum
        a.name = " ".join(a.words) or None            # one preset name for show/params/render/view
        if a.action == "show":
            if not a.name:
                ap.error("serum show needs a preset name")
            print(serum.sheet(serum.find(a.name, a.root)))
        elif a.action == "index":
            idx = serum.build_index(a.root, progress=lambda m: print("·", m, file=sys.stderr))
            bad = [d["name"] for d in idx.values() if "error" in d]
            print(f"indexed {len(idx)} presets -> {serum.index_path()}" + (f"; {len(bad)} could not be rendered: {', '.join(bad[:8])}" if bad else ""))
        elif a.action == "search":
            from .samples import FEATURE_HEAD, feature_row
            words = list(a.words) + (a.search.split() if a.search else []) + ["-" + w for w in a.exclude]
            a.like = " ".join(a.like) if a.like else None
            hits = serum.search(words, a.folder, a.tag, a.sort, a.like, a.limit)
            print("each preset measured on the key that makes it sound around C2 (so registers are comparable); 'oct' is the patch's own "
                  "octave offset: -2 means playing C2 sounds as C0 — write its notes two octaves higher than you want to hear")
            print(FEATURE_HEAD)
            for _, d in hits:
                label = f"{d['folder']}/{d['name']}" + (f" [{d['voices']}; oct {d.get('patch_octave', 0):+d}; fx {' '.join(d['fx']) or '-'}]")
                print(feature_row(d, label))
            print(f"{len(hits)} shown" + (f" (closest to {a.like!r} first)" if a.like else "") + " — words can be character (snappy dark subby wide sustained ...), "
                  "folder, tag, mono/poly, engine (wavetable sample granular spectral sub noise), fx (reverb delay distortion ...) or macro names")
        elif a.action == "view":
            from .pictures import serum_png
            if not a.name or not a.out:
                ap.error("serum view needs a preset name and --out FILE.png")
            vals = {k: (float(v) if v.replace(".", "", 1).replace("-", "", 1).isdigit() else v) for k, _, v in (kv.partition("=") for kv in a.set)}
            print(serum_png(a.name, a.out, (a.note or ["C2"])[0], vals or None))
        elif a.action in ("params", "render"):
            if not a.name:
                ap.error(f"serum {a.action} needs a preset name")
            vals = {}
            for kv in a.set:
                k, _, v = kv.partition("=")
                vals[k] = float(v) if v.replace(".", "", 1).replace("-", "", 1).isdigit() else v
            host = serum.SerumHost.get()
            name = host.load(a.name, a.root)
            host.set(vals)
            if a.action == "params":
                rows = host.params(a.search)
                for n, v, (lo, hi) in rows:
                    rng = f"range {lo:g}..{hi:g}" if isinstance(lo, (int, float)) and isinstance(hi, (int, float)) else ""
                    print(f"{n:<34} {v:<22} {rng}")
                print(f"{len(rows)} parameters of {name!r}" + (f" matching {a.search!r}" if a.search else " — narrow with --search (macro, filter_1, env_1, a_, fx_ ...)"))
            else:
                from .samples import audition_table, write_wav24
                from .theory import note as parse_note
                if not a.out:
                    ap.error("serum render needs --out FILE.wav")
                pitches = [parse_note(n) for n in (a.note or ["C2"])]
                tail = 1.5
                notes = [(p_, i * (a.secs + tail), a.secs, 100) for i, p_ in enumerate(pitches)]
                audio = host.render(notes, len(pitches) * (a.secs + tail))
                Path(a.out).parent.mkdir(parents=True, exist_ok=True)
                write_wav24(a.out, 44100, audio)
                print(f"{name!r} playing {' '.join(a.note or ['C2'])} -> {a.out}")
                print(audition_table([a.out]))
        else:
            rows = serum.catalog(a.root, a.search or a.name, a.tag, a.folder)
            for r in rows:
                print(f"{r.folder + '/' if r.folder else ''}{r.name}  [{', '.join(r.tags)}]" + (f"  — {r.description}" if r.description else ""))
            print(f"{len(rows)} presets")
    elif a.cmd == "remember":
        Project(a.dir).remember(a.strategy, a.decisions, a.reasoning, a.outstanding)
        print("ok")
    elif a.cmd == "install-bridge":
        from .live import install_bridge
        t = install_bridge(a.dest)
        print(f"installed to {t}\nRestart Live, then Settings > Link, Tempo & MIDI > Control Surface: RickRubin")
    elif a.cmd == "split":
        from .logic.stems import parse_stems, split_stems
        try:
            parse_stems(a.stems)
        except ValueError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
        project_dir = Path(a.dir)
        recording = Path(a.source) if Path(a.source).is_absolute() else project_dir / a.source
        stems_dir = Path(a.out) if a.out else project_dir / "stems" / recording.stem
        r = split_stems(recording, stems_dir, a.stems, a.submix, a.start_s, a.end_s, a.close, progress=lambda m: print("·", m, file=sys.stderr))
        print(f"# Logic Stem Splitter — {a.source} ({r['seconds']:.1f} s at {r['sample_rate']} Hz, split in {r['split_s']:.0f} s)")
        for st, path in r["stems"].items():
            rms, peak = r["levels"][st]
            print(f"{st:7s} {path}  {rms:6.1f} dB RMS, peak {peak:5.1f} dBFS" + ("  — near silent: nothing of this in the recording" if st in r["silent"] else ""))
        print(f"Logic project: {r['project']} ({'closed' if a.close else 'open in Logic: a stack of stem tracks, the original muted'})")
    elif a.cmd == "status" and a.daw == "logic":
        from .logic import LogicBridge
        with LogicBridge(progress=lambda m: print("·", m, file=sys.stderr)) as b:
            print(json.dumps(b.ping()))
    elif a.cmd == "status":
        from .live import LiveBridge
        with LiveBridge(port=a.port) as b:
            print(json.dumps(b.call("ping")))
    return 0


def main(argv: list[str] | None = None) -> int:
    from .live.client import BridgeError
    try:
        return _main(argv)
    except BridgeError as e:                      # the DAW said no, or is not there: a message, not a stack trace
        daw = "Logic" if type(e).__name__ == "LogicError" else "Live"
        print(f"error ({daw}): {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
