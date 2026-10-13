---
name: rick-rubin
description: Write house / EDM tracks as Python code — every note, rhythm, groove and section written by you — then read, measure and render them into Ableton Live or Logic Pro (samples, instruments, effects, sidechain, automation) and check the result on audio recorded back from the DAW. No templates or generators. Ask, confirm the plan, write, self-eval, push, capture, persist.
---

# rick-rubin

## Principle

1. **You never listen. You read.** The track lives in `song.json`; `score.md` is its packed reading view (arrangement map, energy curve, every pattern as step strings / note events — ~6 KB for a 5-minute track). `eval.md` adds *measured* loudness, crest factor and spectral balance per section from an offline preview render. `view` draws piano roll + waveform + spectrogram for a bar range — **on demand, at decision points only**, never as a scan.
2. **Rhythm and arrangement are primary; sound design follows.** House lives or dies on the groove and on 8/16/32-bar phrasing. Get those right in the score, then let Live's instruments do the timbre.
3. **Ask → confirm → execute → self-eval → push → persist.** Never build until the user has approved a plain-English plan.
4. **`song.py` is the source of truth; Ableton is a render target.** Changes go into `song.py`, then get re-pushed (`--replace`). Never "fix" things inside Live and expect them to come back.
5. **You write the music. All of it.** There are no templates, generators or presets in this library and none may be added (see `CLAUDE.md`). Every note, rhythm, voicing, groove number and section in `song.py` is yours. The "House craft" notes below describe what the genre does; they are not parts to copy.
6. **Explore; do not one-shot.** The first sample, preset, bassline or hook that works is a draft. Shortlist, compare by measurement and in context, iterate, and record what lost and why (`PREFERENCES.md`, and "Exploring" below).
7. **Verify before you present.** If `eval` fails, you are not done.

## Hard rules (production correctness — non-negotiable)

1. **Phrasing:** section lengths are multiples of 8 bars (a 4-bar pickup at most). Something changes every 8 bars, something big every 16.
2. **DJ-friendly edges:** intro and outro ≥ 16 bars, drums-led; no bass/chords/hook in the first or last 8 bars (unless the user explicitly asks for a radio edit).
3. **One tempo, 118–130 BPM.** No tempo changes inside a track.
4. **In key.** Melodic notes stay in `song.key`; a chromatic note must be deliberate and mentioned in your reasoning.
5. **Low end:** bass is monophonic, roughly C0–G2 (MIDI 24–55), sidechained to the kick, and mostly avoids kick hits. Nothing but kick and bass below C2 (MIDI 48).
6. **Drops earn their impact:** every drop follows a build or breakdown and starts with the kick on bar 1. A beat of silence (`kick_gap`, the roll's silent last beat) before the drop is the classic move.
7. **Pitch convention is Ableton's:** C3 = MIDI 60, C1 = 36 (kick), Drum Rack pads start at C1.
8. **Edit `song.py`, then re-read `score.md`.** Never hand-edit `song.json` or flattened MIDI; they are build outputs.
9. **Self-eval before showing or pushing:** `rick-rubin eval <dir>` must have 0 errors. Cap at 3 eval passes — then report what's left instead of looping.
10. **Push only after eval passes, and only with the bridge connected** (`rick-rubin status`). Re-pushes use `--replace`.
11. **Strategy confirmation before execution.**
12. **All outputs in the project folder.** Never write inside the rick-rubin repo.
13. **Measure sample pitch; never trust filenames.** Sample packs disagree on octave naming (a "C2" bass is often MIDI 36 = Ableton's C1) and are rarely dead in tune. Import melodic one-shots with `--melodic` and use the `sample_root` it prints.

## Setup

First-time install lives in `install.md`. On cold start just verify: `rick-rubin --help` runs (package installed), and — before any push — `rick-rubin status` reaches Live. You drive everything through the `rick-rubin` CLI (or `from rick_rubin import Project` in a Python snippet) with your own shell and file tools; there is no separate agent runtime. Run `view` and Read the PNG it prints to look at it.

## Directory layout

```
<project>/
├── song.py        ← source of truth: the song, written by you in Python
├── song.json      ← built from song.py; what the other tools read
├── score.md       ← packed score — your primary reading view
├── eval.md        ← latest self-eval
├── project.md     ← memory; append one section per session
├── preview.wav    ← offline sketch render (numpy synth)
├── live.wav       ← the arrangement recorded from Live's own output (`capture`); zoom/ holds partial takes
├── midi/          ← song.mid + per-track .mid (manual fallback)
├── views/         ← on-demand timeline PNGs
├── samples/       ← imported one-shots and conformed loops (`sample`); raw downloads in samples/raw/
└── history/       ← snapshot before every edit batch (`undo`)
```

## Commands

```
rick-rubin init <dir> --title "..." --bpm 126 --key "A minor"   # a song project from project-template/: CLAUDE.md, empty song.py, project.md, manifest
rick-rubin audition <dir> samples/raw/kick_*.wav [--png name]   # candidates side by side: punch, decay, spectrum, pitch+octave, width, character
rick-rubin samples <dir> [words] [--sort bright] [--like samples/x.wav]   # the project's sample library, searchable by measured character
rick-rubin serum search [words] [--folder Bass] [--sort sub] [--like "<preset>"]   # Serum presets by how they sound (run `serum index` once)
rick-rubin browse "sounds/Bass" [--search sub]     # what Live offers: instruments, presets, effects, plug-ins
rick-rubin check <dir> [--audio]             # ruff + mypy on song.py, build, music lint — run after every edit
rick-rubin build <dir>                       # run song.py -> song.json + score.md (every other command does this when song.py changed)
rick-rubin score <dir> [--bars 33-48] [--tracks Bass Kick]   # print/refresh score.md; with a zoom, print just that slice
rick-rubin transcribe <dir> samples/vocal.wav [--text "lyric"]   # syllables -> bar.beat.16th + ms off the grid
rick-rubin retime <dir> samples/vocal.wav --name vocal_q          # audio-quantize a loose vocal loop, word by word
rick-rubin notes <dir> samples/vocal.wav                          # the notes inside a sample: pitch+octave, cents, position
rick-rubin width <dir> [file]                # stereo image: correlation, side %, mono loss, per band and section
rick-rubin split <dir> refs/track.wav [--stems vocals,bass] [--from 60 --to 90]   # a recording's stems with Logic Pro's Stem Splitter -> stems/track/<stem>.wav
rick-rubin sample <dir> <file> --name N --oneshot [--melodic]                       # Simpler one-shot; --melodic measures its pitch
rick-rubin sample <dir> <file> --name N --loop --src-bpm B [--bars N] [--align end] [--end-at S] # audio loop, conformed to the song tempo
rick-rubin eval <dir>                        # lint + preview render + measurements -> eval.md (exit 1 on errors)
rick-rubin eval <dir> --bars 33-48 --tracks Bass Kick   # zoom: measure a bar range and/or a solo of some tracks
rick-rubin capture <dir> [--bars 33-48] [--tracks Bass Kick]   # record Live's real output (real time), measure it, draw it
rick-rubin ab <dir> hatvel=35 hatvel=60 [--bars 81-88] [--tracks Hats] [--live] [--hits]   # candidates side by side (see Exploring)
rick-rubin --set bass=reese <command> ...    # any one command with an option() choice switched
rick-rubin compare <dir> a.wav b.wav ...     # audio files side by side (first is the baseline)
rick-rubin hits <dir> [file] --bars 81-84 --tracks Hats [--live]   # level of every 16th next to the written velocities
rick-rubin devices Compressor Saturator ...  # a Live device's parameters, ranges and choices, read from Live
rick-rubin reference compare <dir>           # the capture against released tracks: loudness, density, balance, width, pump, movement
rick-rubin eval <dir> --live [--bars ...]    # measurements of the last full capture (live.wav)
rick-rubin view <dir> --bars 65-80 [--tracks Bass Kick]
rick-rubin preview <dir> [--stems]
rick-rubin midi <dir>
rick-rubin install-bridge                    # once; then pick "RickRubin" control surface in Live
rick-rubin status                            # ping Live
rick-rubin push <dir> [--replace]            # build the arrangement in Live
rick-rubin watch <dir> [--bars 81-88] [--play]   # hot reload: every save of song.py lands in Live while it plays
rick-rubin push <dir> --update               # redo only what changed since the last push (a parameter: about a second)
rick-rubin remember <dir> --strategy ... --decisions ... --reasoning ... --outstanding ...
```

## Writing a song

A song is a Python file, `song.py`, that leaves a `Song` in a variable called `song`. You write it with your normal file tools; every command rebuilds from it. It is ordinary Python — use loops, functions and your own helpers freely.

```python
from rick_rubin import Song

song = Song("Night Bus", bpm=126, key="A minor", swing=56)

# tracks — sample= plays a one-shot from Simpler, audio=True holds loops, instrument= names a Live instrument or plug-in
kick = song.add_track("Kick", "kick", sample="samples/kick.wav", volume_db=-7)
hats = song.add_track("Hats", "hat", sample="samples/hat.wav", volume_db=-16,
                      groove={"swing": 58, "accent": [6, -18, 0, -12] * 4, "humanize": {"ms": 3, "vel": 5}})
bass = song.add_track("Bass", "bass", sample="samples/bass.wav", sample_root=36.0, volume_db=-8,
                      effects=[{"device": "Compressor", "sidechain": "Kick", "params": {"Threshold": -30, "Ratio": 5}}])
keys = song.add_track("Keys", "chords", instrument="Drift", volume_db=-13)

# patterns are variables. Step strings for one-pitch rhythms (16ths; x X o g 1-9 and . ; | between bars):
four = song.pattern("four", kick, "x...x...x...x...")
tick = song.pattern("tick", hats, "g.xgo.x.g.xgo.xo|g.xgo.x.g.xgoxxg")
# event lines for pitched parts — one string per bar: "<beat>.<sixteenth> <pitch or [chord]> <beats> [vVEL]"
line = song.pattern("line", bass, ["1.3 A0 0.35; 2.3 A0 0.35 v108; 3.3 A0 0.35; 4.4 G0 0.2",
                                   "1.3 F0 0.35; 2.3 F0 0.35 v108; 3.3 G0 0.35; 4.3 E0 0.3"])
stab = song.pattern("stab", keys, {1: "1.1 [A2 C3 E3 G3] 0.25 v90; 2.4 [A2 C3 E3 G3] 0.5", 2: "2.3 [F2 A2 C3 E3] 1.5"})

# derive: the original is untouched, the new pattern is its own variable
four_gap = four.variant("four_gap", bars={1: "x...x...x......."})            # replace a bar
line_busy = line.variant("line_busy", add={1: "2.2 A0 0.2 v80; 2.4 A1 0.2"}, mono=True)   # add notes
line8 = line.variant("line8", repeat=2, bars={4: "1.3 E0 0.35; 3.1 E1 0.5"})  # repeat, then change the last bar
stab_hi = stab.variant("stab_hi", transpose=12, drop=lambda n: n.dur < 0.4)   # transpose, filter notes

# sections place patterns on tracks; bar numbers inside a section are 1-based
intro = song.add_section("intro", 16, kind="intro", energy=3, parts={kick: four, hats: tick.at(9)}, fills={kick: four_gap})
drop = song.add_section("drop", 16, kind="drop", energy=9,
                        parts={kick: four, hats: tick, bass: line_busy, keys: stab.at(1, 8)},
                        fills={kick: four_gap.every(8)}, automation={keys: {"filter": [0.4, 1.0]}})
# reuse a block and extend it
drop2 = drop.variant("drop2", energy=10, add={keys: stab_hi, bass: line8}, without=[hats])
song.arrange(intro, drop, intro, drop2)      # listing a section twice plays it twice
```

- **Notation.** Positions are Ableton-style and 1-based: `2.3` is beat 2, third 16th. Off-grid: `@1.333` (beats from the bar start). Pitches use Ableton naming (C3 = 60); chords go in brackets. Lengths are beats. `score.md` prints patterns in the same notation, so what you read is what you write.
- **`pattern.at(first, last)`** plays it on those bars of the section; **`.up(12)`** transposes it there; **`.every(8)`** makes it a fill at the end of every 8-bar phrase (no argument: once, at the end of the section).
- **`pattern.variant(name, ...)`**: `repeat`, `length`, `bars={n: content}`, `add=`, `drop=`, `transpose`, `mono`. **`a.then(b, name)`** joins two patterns.
- **`section.variant(name, ...)`**: `add` (set or replace parts), `without` (remove tracks), `fills`, `automation`, `bars`, `energy`, `kind`. Because `song.py` re-runs on every build, changing the original changes every variant.
- **Groove is per track and explicit**: `swing` (% for that track), `timing` (16 offsets in ms, one per 16th of the bar; + is late), `accent` (16 velocity offsets), `gate` (note-length multiplier), `humanize` (`{"ms", "vel", "seed"}`, repeatable). There are no named grooves: decide where the clap sits against the kick, which 16ths the hats lean on, how much each part drifts — and write the numbers. Flat velocities and everything dead on the grid is the most common reason a beat sounds lifeless.
- **`sends`**, **`midi_effects`** — see "Returns, sends and the master" and "MIDI effects" below.
- **`delay_ms`** is Ableton's Track Delay: `delay_ms=-8` plays the whole track 8 ms early, `+12` late — notes and audio loops alike. Use it to seat a whole part against the kick (a clap or top loop a few ms late, a bass a few ms early); use `groove["timing"]` when only some 16ths should move. It is applied by shifting the track's clips, because Live does not let scripts set its own Track Delay.
- **Levels mean the same everywhere.** A sample track's velocity-100 note plays the file at its own level times the track fader — in Live (push sets Simpler's Volume to cancel its velocity boost) and in the preview — exactly like an audio-loop clip. Velocity then follows Simpler's own law, measured in Live: 0.14 dB per velocity step at the default 35 % `Vol < Vel` (velocity 64 is 5 dB under velocity 100), proportionally more at higher settings (at 80 %: 11.5 dB under). So ghost notes and accents measured offline are what Live plays. Serum tracks and loops are audio at file level.
- **`instrument_params`** sets the track instrument's own parameters by displayed value — for Simpler e.g. `{"Ve Attack": 4, "Ve Release": 60, "Vol < Vel": 75}`. Attack time and velocity sensitivity are per track; per-hit feel comes from velocity and timing.
- **Automation** values run 0..1 over the section: `[start, end]` or `[[fraction, value], ...]`. `filter` is a low-pass sweep (60 Hz–18 kHz), `volume` and `pan` are the mixer; `"Device:Parameter"` reaches anything else on MIDI tracks. On audio-loop tracks, `filter` and `volume` are rendered into the audio.
- Projects that are only a `song.json` (no `song.py`) can still be changed with JSON ops through `rick_rubin.edits`; a project with a `song.py` is always edited there.

## Exploring

Great tracks come from comparing options, not from accepting the first one. You cannot hear, so exploring means *measuring several things and reading the difference*. Budget most of a session for it.

- **Samples, per role.** Search more than once with different words (character, genre, era, gear: "rubbery", "909", "dusty", "tight short"). Download a shortlist — typically 4–8 for the sounds that define the track (kick, bass, main hook, vocal), 2–4 for supporting ones — into `samples/raw/` and run `audition` on them together. Read the table for what the role needs: a kick's fundamental and decay (does it leave room for the bass? is its pitch in key?), a hat's centroid and length, a clap's body vs. snap, a bass one-shot's octave and sustain. Then test the finalists **in context**: point the track at each in turn and compare a zoomed `eval`/`capture` of the same bars. Log every candidate in `samples/manifest.json` — used or rejected, with the reason.
- **Loops and vocals.** `transcribe`, `notes` and `width` each candidate before choosing; a loop that is late, flat or in the wrong key costs more to fix than to replace.
- **Instruments and presets.** `browse "sounds/<category>"` lists Live's presets, `browse plugins` the plug-ins, `serum list/show` reads Serum patches. Try several for each synth part: load each (`instrument="<name>"`), `capture --bars ... --tracks <that track>`, and compare spectrum, level and width.
- **Parts.** Write two or three genuinely different basslines / hooks / hat grooves as separate variables, swap them into the same section, and compare — score them against the vocal's syllables and notes, kick collisions, register, density. Keep the winner, note what the others taught you, delete the losers from `song.py` once the log has them.
- **Arrangement and mix.** Change one thing at a time, capture the affected bars, compare numbers.

**Candidates are `option()` choices.** Do not copy `song.py`, comment blocks in and out, or script your own build-push-capture loops: name the thing you are unsure about and let `ab` run the candidates.

```python
from rick_rubin import option
HAT_GHOST = option("hatghost", 60)          # the default is the song; a switched value takes the default's type, so give numbers as numbers (6.0, not "6")
BASS = option("bass", "muted")              # if BASS == "reese": ... elif BASS == "organ": ...
```

```
rick-rubin ab <dir> hatghost=35 hatghost=80 --bars 81-84 --tracks Hats --hits     # offline, seconds
rick-rubin ab <dir> bass=reese bass=organ wide:tops=pan,verb=short --bars 81-96 --live   # pushed to Live and recorded, one by one
```

`ab` prints one column per candidate (the song as it stands first, then each change against it): loudness, peak, crest, energy per band, side % overall / above 4 kHz / below 150 Hz, mono loss, transient contrast, clipped samples; `--hits` adds the per-step levels, `--reference` puts every candidate against the reference tracks (movement, repeats and texture changes are how arrangement candidates differ — plain loudness will not show a layer swapped for another). Files land in `ab/<label>.wav` for `reference compare`, `spectrum`, `width --png`. After a `--live` run Live holds the song as it stands again. Keep a winner by making it the option's default; `score.md` lists every option and its value. `--set name=value` in front of any command (`rick-rubin --set bass=reese capture <dir> --bars 81-96`) runs just that command with the choice switched.

**Did the groove survive?** `hits` prints the peak level of every 16th step of a soloed track, bar by bar, with the velocities you wrote underneath — from the preview, a file, or Live (`--live`). Simpler's velocity curve is steep: accents and ghosts that look 40 velocity steps apart can come out 25 dB apart, and a ghost more than ~18 dB under the accent is gone in a mix. Read `hits --live` once for every velocity-driven part.

Stop exploring a question when one option is clearly right for this track and you can say why — not when the first one passes lint.

## One vocabulary for how things sound

Every sample you import and every Serum preset in the index is measured the same way and described with the same words, so you can search either by character:

| | words |
|---|---|
| length | `short` (< 0.3 s) · `long` (> 2 s) |
| attack | `snappy` (< 5 ms) · `soft-attack` (30–120 ms) · `slow-attack` (> 120 ms) |
| decay | `tight` (< 120 ms) · `ringing` (> 600 ms) · `sustained` |
| brightness | `dark` · `warm` · `bright` · `airy` (spectral centroid under 400 Hz / to 1.2 k / to 4 k / above) |
| low end | `subby` (> 35% below 60 Hz) · `bassy` (> 60% below 200 Hz) · `no-low-end` |
| width | `mono` · `wide` · `very-wide` · `wide-low-end` |
| pitch | `pitched` · `unpitched` · `melodic` |
| dynamics | `punchy` (crest > 14 dB) · `dense` (crest < 8 dB) |

- **Samples.** `rick-rubin sample ...` prints the measured row and character on import and records it in `samples/manifest.json` (`analysis`); anything dropped into `samples/raw/` is measured the first time you run `rick-rubin samples <dir>`. Search and sort the whole project library: `samples <dir> snappy dark`, `samples <dir> --sort sub`, `samples <dir> pitched --not wide`, `samples <dir> --like samples/raw/kick_03.wav`. So when candidates come back from Splice: download, then read their character before you choose.
- **Serum presets.** `rick-rubin serum index` plays every installed preset once — on the key that makes it *sound* around C2, so a bass patch set two octaves down is measured in the same register as everything else — and records the same measurements plus patch facts and the patch's own octave offset; it takes a few minutes the first time and is incremental afterwards. Then `serum search bass subby mono --sort sub`, `serum search pad wide slow-attack --not reverb`, `serum search pluck snappy bright --folder Leads`, `serum search --like "BS Gunman Reese"`. Words can be character, folder, tag, `mono`/`poly`, engine (`wavetable sample granular spectral sub noise`), FX names (`reverb delay distortion chorus ...`) or macro names; `--not WORD ...` excludes. `oct -2` in the label means the patch sounds two octaves under the key you play: write its notes two octaves higher than you want to hear (or reset its oscillator octave with `serum_params`). Six presets do not render within 30 s and are left out.

The words are coarse on purpose: use them to narrow 700 options to 10, then compare those 10 with `audition`, `serum view` and in context.

## Does it sound like a record? `reference`

`check` and `eval` answer "is it correct?". A correct track can still sound flat. `reference` answers the other question by measuring your mix against released tracks in the genre, on the things a listener reacts to:

```
rick-rubin reference add ~/Music/some-released-track.wav ...   # once; any format; only measurements are kept, shared by all projects
rick-rubin reference list
rick-rubin reference compare <dir>                              # the Live capture (live.wav) against the shelf -> reference.md
```

It measures, on the loudest 30 seconds: loudness and crest (density), tonal balance per band and tilt, stereo side energy overall and per band, low-end pump (off-beat vs kick), transient contrast and top-end activity; and for development: how much the spectrum changes from one 2-bar block to the next, the share of near-identical blocks, texture changes per minute (2-bar blocks that differ clearly from the one before, in level or — with the level taken out — in which bands carry the energy, so a layer swapped for another at equal loudness counts) and loudness range. Each line is placed against the references' min–median–max, and whatever falls outside is listed.

Use it on a capture after the arrangement and balance are right, and treat every "outside the references" line as a question to answer — fix it, or write down why this track should differ. What it has shown so far on this library's own output, i.e. the ways an agent's track tends to come out flat:

- **Unmastered.** A balanced mix lands around −15 LUFS with 15 dB of crest; released tech house measures about −7.5 LUFS with 8.5 dB. Next to a record it is 7 dB quieter and far less dense, which reads as dull and weak however good the parts are. Finish with a master chain (`song.master_effects`) — gentle saturation, bus compression, then a Limiter doing real work — and iterate on captures until loudness and crest sit inside the references' range without clipped samples. Density on individual sounds (Saturator, compression on drums and bass) counts for more than limiter gain.
- **Mono top end.** References carry 4–29 % side energy above 4 kHz; a track built from centred one-shots has 2–3 %. Pan hats, percussion and tops apart, use stereo samples and loops for them, send them to a short reverb, widen with Utility `Stereo Width` — and keep everything below 150 Hz centred.
- **Too little change.** If movement sits at the bottom of the references' range or blocks repeat, the drop is a loop. Add and remove layers every 8 bars, vary fills, automate filters, change a Serum macro between sections (a second track with other `serum_params` works today), and make later drops measurably different from the first.
- **Velocity is steep.** At a high `Vol < Vel`, ghost notes disappear: at 80 % a velocity-23 hit is 30 dB under a velocity-116 one. Check the dB range your velocities produce (see "Levels mean the same everywhere") rather than assuming.

The offline preview cannot stand in for this: its stems are mono and it has no master chain. Compare captures.

## Pictures of the things producers look at

Tables are exact and stay the primary view; these pictures are for when a shape says more than numbers. Each command prints the PNG's path — Read it.

- `rick-rubin audition <dir> <files...> --png <name>` — **sample comparer**: every candidate's waveform on one time and level scale (length, punch, decay at a glance), their spectra overlaid, key numbers beside each.
- `rick-rubin spectrum <dir> [files...] [--tracks Kick Bass ...] [--bars A-B] [--mix]` — **spectrum analyzer**: overlaid spectra of files, of soloed tracks (at their real relative level), and/or the mix. Where two curves sit on top of each other they compete; decide EQ moves from it, then make them with Channel EQ / Auto Filter in `effects`.
- `rick-rubin width <dir> [file] [--bars A-B] --png` — **stereo imager**: vectorscope (a vertical line is mono, a round cloud is wide), correlation over time, width by band with wide-low-end and out-of-phase bands in red.
- `rick-rubin serum view "<preset>" --note F1 [--set macro_1=80] --out views/x.png` — **Serum patch panel**: the wavetable frame each oscillator plays, the envelopes, filters/voices/FX chain, macro values and what each moves, and a played note's level, waveform and spectrum.
- `rick-rubin view` — the arrangement: notes, audio clips, automation, the notes a vocal sings in a lane under its waveform, waveform and spectrogram of the mix.

## Zooming in

`view` draws a grid that follows the zoom: bar lines always, quarter-note lines at 16 bars or fewer, lighter eighth-note lines (and `.2 .3 .4` beat labels) at 8 or fewer, faint 16th lines at 4 or fewer. To judge timing — swing, pushed or late hits, a vocal against the grid — zoom to 4 bars or fewer.

`score`, `eval`, `view`, `width` and `capture` all take `--bars A-B`; all but `width` take `--tracks ...` too. Use the zoom whenever a question is local — "is the bass ducking under the kick in the drop?" is `eval --bars 41-48 --tracks Kick Bass` plus `view` on the same slice, not a re-read of the whole song. Bar numbers are always the song's. A solo render is normalised on its own, so compare shapes and ratios inside it, not its level against the full mix.

## Hearing what Live plays: `capture`

`preview.wav` is this library's own sketch render. `capture` is the real thing: it adds a temporary audio track set to **Resampling**, records the arrangement from Live's master in real time (the whole song, or just `--bars`; `--tracks` solos them), copies the take into the project (`live.wav`, or `zoom/live_bars_...wav`), removes the track and restores solo/metronome/loop. It then prints the same loudness table as `eval`, the stereo report, and a `view` drawn from Live's audio. Capture after every push you intend to present, and judge mix decisions — sidechain depth, compressor settings, master clipping, width — on it rather than on the preview. A zoomed capture of 8 bars takes ~15 s; use those while iterating and one full capture at the end.

## Live is the one source of truth for sound

There is one mixer, and it is Ableton's. The offline preview plays the notes and samples so that rhythm, harmony, arrangement and rough balance can be read in seconds — it does not run Live's devices (no Saturator, Compressor, Limiter, EQ, Utility; returns are a rough stand-in), and it never will: an imitation that differs from Live would be a second truth. So anything about *sound* — loudness, density, width, what an effect does, what the master does — is decided on audio recorded from Live (`capture`, `ab --live`, `hits --live`), and that loop is kept short instead:

- `push --update` (and every `ab --live` candidate) redoes only what changed since the last push: a device parameter, fader, pan or send is set in place; a changed part or instrument rebuilds that one track; returns and master only when they differ. The report's first line says what it did. Use it for every push after the first.
- `watch` is hot reload: it keeps running, and every time `song.py` is saved it rebuilds the song and applies just the change in Live without stopping playback (`--bars 81-88 --play` loops that range), printing one line per save — what was updated, how long it took, any warnings; a `song.py` that does not build is reported and Live is left as it was. It is for a person listening while the song is edited; an agent measuring should still `capture`.
- Capture the fewest bars that answer the question (`--bars 81-84`, `--tracks ...`): recording is real time.
- If someone changed the set by hand, `--update` notices and does a full push.

## Logic Pro instead of Live

`rick-rubin --daw logic push <dir>` (or `RICK_RUBIN_DAW=logic`) renders the same `song.py` into Logic Pro, and
`--daw logic capture` bounces it offline (a 5-minute track in about ten seconds) into `live.wav` for the same
measurements. What changes for you:

- Instruments: without `instrument=`, Logic picks a patch from the track's role (the push report says which,
  e.g. `Pulse Bass`, `SoCal`). `instrument="Retro Synth"` / `"Alchemy"` / `"Serum 2"` loads that instrument;
  any other string is a Library search and the first patch found is loaded (`"Deep House Kit"`). A Logic patch
  brings its own inserts (`patch fx` in the report) — your `effects` come after them. `instrument_params` sets
  the instrument's parameters by displayed value (Drum Synth: `{"Sound Category": "Kicks", "Sound Model":
  "Punch Kick", "Decay": 42}` — one Drum Synth per drum track is how electronic drums are done in Logic here;
  the role's default kit is Logic's acoustic Drum Kit Designer).
- Effects and parameters use Logic's names: `{"device": "Compressor", "params": {"Threshold": -28, "Ratio": 4,
  "Attack": 0.5, "Release": 120}}`, `"Channel EQ"`, `"AutoFilter"`, `"Limiter"`, `"ChromaVerb"`, `"Tape Delay"`.
  Units are the displayed ones. `sidechain: true` is a Compressor keyed from the Kick, as in Live.
- Returns become Bus 1, 2… with an Aux each; sends are in dB; `master_effects` go on Stereo Out.
- Every push is a full push (no `--update`, no `watch`); it takes one to four minutes. Section `volume` and
  `filter` automation is written only with `--automation` (it plays the automated bars in real time).
- Not built yet in Logic: sample one-shot tracks, Serum stems, MIDI effects. Their tracks exist and play the
  role's patch; the report lists each one. Audio loops are imported onto an audio track.
- Do not click in Logic during a push: it applies strip edits to every selected track, and the control
  surface state must not change. Keep projects in a visible folder (file panels cannot reach hidden ones).

- `rick-rubin split <dir> refs/track.wav` runs Logic's Stem Splitter on a recording (Logic Pro 11 on Apple silicon,
  no `--daw` needed): vocals, drums, bass, guitar, piano and other as `stems/track/<stem>.wav`, at the recording's
  rate, with each stem's level; one near silent means the recording has none of it. Use it to read a reference's
  parts on their own — `notes` on its bass stem, `transcribe` on its vocal, `width` and `reference` on its drums —
  instead of guessing them from the full mix. A 3-minute song takes about 40 s.

Details, setup (Accessibility permission, `pip install -e ".[logic]"`) and troubleshooting: `docs/LOGIC.md`.

## Effects and compressors

`rick-rubin devices <name> ...` loads a device in Live on a throwaway track and prints every parameter with its range, its menu choices and its default (remembered in `.cache/live-devices.json`, so it works without Live afterwards). Read it before writing an effect instead of guessing names.

A track's `effects` is an ordered list of Live audio effects placed after the instrument. Every parameter is set by the value Live displays, in Live's own names and units:

```json
{"op": "track", "name": "Bass", "set": {"effects": [
  {"device": "Compressor", "sidechain": "Kick", "sidechain_tap": "Post FX",
   "params": {"Threshold": -32, "Ratio": 6, "Attack": 0.1, "Release": 110, "Knee": 3,
              "Model": "Peak", "LookAhead": "1 ms", "Makeup": false, "S/C EQ On": false, "Dry/Wet": 100}}]}}
```

Numbers are dB, ms, Hz, % or the ratio's first figure (`"inf"` for a limiter); switches take true/false; menus take the option's name. Compressor parameters: Threshold, Ratio, Expansion Ratio, Attack, Release, Auto Release On/Off, Output, Makeup, Dry/Wet, Model (Peak | RMS | Expand), Env Mode (Lin | Log), Knee, LookAhead (0 ms | 1 ms | 10 ms), S/C Listen, S/C EQ On, S/C EQ Type, S/C EQ Freq, S/C EQ Q, S/C EQ Gain, S/C On, S/C Gain, S/C Mix. `sidechain` names the track that keys the device (a Compressor on the bass keyed from the kick is the house pump); `sidechain_tap` is Pre FX, Post FX or Post Mixer. The push report echoes what Live shows after setting each value and lists any name it did not find — an unknown parameter name is reported with the device's full parameter list, which is also how to discover the parameters of any other device (EQ Eight, Saturator, Reverb, Glue Compressor...). `sidechain: true` on a track remains the shorthand for a default kick-keyed Compressor (−28 dB, 4:1, 0.5 ms, 120 ms). The offline preview only models the ducking, not the compressor's exact curve: tune compressors against `capture`.

## MIDI effects

`midi_effects` is a chain in front of the instrument — real devices in Live, so the clip holds what you wrote and the device does the rest:

```python
keys = song.add_track("Keys", "chords", instrument="Drift",
                      midi_effects=[{"device": "Chord", "params": {"Shift1": 3, "Shift2": 7, "Shift3": 10, "Velocity3": 70, "Strum": 15}}])
stab = song.pattern("stab", keys, ["1.1 F3 0.25; 2.3 F3 0.25; 4.1 Eb3 0.5"])     # one finger; the Chord device makes each a min7
```

- **Chord**: `Shift1`–`Shift6` (semitones from the played note, ±36), `Velocity1`–`6` (%), `Strum` (ms, ± direction), `Chance1`–`6`. A fixed shape parallel-moved by a one-note line is a classic house/techno stab sound — and changing one number revoices the whole part.
- **Pitch** (`Pitch` semitones), **Note Length** (`Time Length` ms, `Gate` %), **Velocity** (`Out Low`, `Out Hi`, `Mode`), **Scale**, **Arpeggiator** (`Style`, `Synced Rate`, `Gate`, `Transp. Steps`…), **Random** — any Live MIDI effect by name, parameters by displayed value; an unknown parameter name comes back with the device's full list.
- Offline, the score lint, `eval`, `view` and Serum renders see the notes that will *sound* for Chord, Pitch, Note Length and Velocity. Arpeggiator, Random, Scale and chance/scale-degree settings are not emulated: lint says so (`H15-midi-fx`) and that track must be judged on a `capture`.
- On a `serum=` track the MIDI effects are applied before rendering (the result is in the audio); on audio-loop tracks they do not apply.

## Returns, sends and the master

One shared reverb or delay on a return track instead of one per track — Ableton's A and B:

```python
song.add_return("A", [{"device": "Reverb", "params": {"Decay Time": 1800, "Predelay": 20, "Dry/Wet": 100}}])
song.add_return("B", [{"device": "Delay", "params": {"L 16th": 3, "R 16th": 4, "Feedback": 35, "Dry/Wet": 100}}])
clap = song.add_track("Clap", "clap", sample="samples/clap.wav", sends={"A": -14, "B": -22})     # dB; unlisted sends are off
song.master_effects = [{"device": "Limiter", "params": {"Ceiling": -0.3}}]
```

- Return chains are effect chains like a track's `effects` (keep them 100% wet). `push` makes the return hold exactly that chain, sets every track's send levels, and puts `master_effects` on the master. Live Intro/Lite have two returns (A, B).
- Offline, the preview approximates a Reverb or Delay that is first on a return (tail length from `Decay Time`, echoes from the 16ths/feedback), enough for `eval` and `width` to notice the space; its exact sound is Live's — check on a `capture`.
- Keep kick and bass out of the reverb; send what needs depth (claps, vocals, stabs, FX) and check the low end stays centred with `width`.

## Using Splice / samples

Samples replace Live's stock instruments track by track. Two kinds:

- **One-shots → Simpler.** A track with `sample` plays that file from a Simpler instead of `instrument`. Drum roles use One-Shot mode (every hit plays the whole sample; the score keeps the readable drum-map pitches). Melodic roles use Classic mode and need `sample_root`, the MIDI pitch the file actually sounds at (fractional = cents); the bridge sets Simpler's Transpose/Detune from it so notes in Live show their true pitch.
- **Loops → audio tracks.** A track with `audio: true` holds audio patterns (`{"op": "pattern", "name": "top", "audio": "samples/top.wav", "bars": 8, "key": "F minor"}`). Parts, `start`/`end` and filter/volume automation work as for MIDI. Loops are **conformed on import**: tempo-matched to the song (pitch kept, needs ffmpeg) and cut to exact bars, then placed *unwarped* in Live — N bars of file is N bars of arrangement. `--align end` keeps the tail, so a riser's peak lands on the downbeat after it; if the file carries on past its peak (a tail, a second swell), measure where the peak is and pass `--end-at <seconds>`. Look at the loop in `view` after importing: FX names say little about their shape. Changing `bpm` later means re-importing the loops.

Workflow:

1. **Find** candidates. With the Splice MCP: `describe_a_sound` (`type` loop | oneshot, BPM filters). Prefer loops within ~6% of the song tempo and in the song key or its relative; any key for drums.
2. **Download** to `<project>/samples/raw/`. Splice download URLs expire in about two minutes — fetch immediately. A first download costs a credit (get the user's OK); re-downloads are free. Record name, asset id and pack in `samples/manifest.json`.
3. **Import** with `rick-rubin sample`. It prints the measured root or bar count and a ready-made edit op.
4. **Wire up** with `track` / `pattern` / `part` ops, then re-read `score.md`.
5. **Eval.** The preview plays the real samples (repitched like Simpler), so loudness and balance numbers now reflect them. Lint `H14-samples` flags notes more than two octaves from a sample's root and loops cut mid-pass; `H4-key` flags loops in a foreign key.

**Vocals: read the words, to the syllable.** `rick-rubin transcribe <dir> samples/vocal.wav [--text "the lyric"]` finds the words (a local Whisper model, or the lyric you give it — better whenever you know it), pins every letter to the audio with a forced aligner, groups letters into syllables and snaps each syllable to the audio itself. For every syllable you get where its sound starts (`cut at`), where it reaches full level (`vowel at` — what a listener hears as on or off the beat), its `bar.beat.sixteenth` and how many ms it is off that 16th. `score.md` prints them under the loop (`-na` continues a word, `?` = doubtful alignment, offsets from 10 ms shown). Read it before writing anything around a vocal: put hooks and fills in the gaps, keep stabs off the stressed syllables. A word that sits exactly between two 16ths is named after the nearer one; look at the offset before trusting the name.

**Loose vocal? `retime` it.** A whole loop that reads +30..+60 ms on most syllables is dragging; scattered signs mean a loose performance. `rick-rubin retime <dir> samples/vocal.wav --name vocal_q [--by word|syllable] [--grid 16] [--strength 0.7] [--move 7=3.3.3]` cuts the loop at each word's start and slides it so its attack lands on the grid, writing a new loop of the same length (and its word timings). `--by word` keeps each word's inner flow and is the default; `--strength` below 1 leaves some of the feel; `--move N=bar.beat.sixteenth` places a piece yourself when the nearest 16th is the wrong one. Check the result by transcribing or viewing the new file, not by assuming.

**Samples have notes: read them.** `rick-rubin notes <dir> samples/vocal.wav` follows the pitch through a single-voice sample (vocal, bassline, lead; use `--fmin 30` for bass) and lists its notes: pitch **with octave** (Ableton naming, C3 = 60) and Hz, cents sharp/flat, grid position, length, the syllable sung on it, and `!` if it is outside the song's key. The first line gives the register — lowest to highest note and the centre. `score.md` prints the notes under the loop and `view` draws them on the waveform. Use it to choose chords and a bass that agree with what the vocal actually sings, to keep leads out of the vocal's octave, and to spot a loop that is sold as "F minor" but leans on other notes. It hears one voice at a time: chords or full loops will read as nonsense or as nothing.

**Stereo image: read the width.** `rick-rubin width <dir> [file]` is a correlation meter and imager in table form: correlation (+1 mono, 0 very wide, negative = out of phase), side % (the share of energy that disappears in mono), L/R balance, loudness lost in mono, and side %/correlation in four bands — for the whole file and per section. Rules it checks: low end centred below 150 Hz, no negative correlation, under 3 LU lost in mono, no lean over 1.5 dB. Run it on samples before using them (wide risers and loops are common) and on audio captured from Live. The offline preview is built from mono stems, so its width only reflects panning.

**Serum 2 is a full instrument here — find, read, hear, play.** The library hosts the real Serum 2 plug-in in-process, loads any preset into it from the preset file, sets any of its ~2600 parameters by name, and renders notes to audio offline. Nothing needs Live or Serum's window.

- **Find:** `rick-rubin serum list [--folder Bass] [--tag Mono] [--search "reese"]` — folders, tags and words from the name/description.
- **Read:** `rick-rubin serum show "<preset>"` — a patch sheet: oscillators and wavetables, filters, envelopes/LFOs, FX, what each of the eight macros is wired to. `rick-rubin serum params "<preset>" --search macro` (or `filter_1`, `env_1`, `a_`…) lists parameter names, current values and ranges.
- **Hear (by measurement):** `rick-rubin serum render "<preset>" --note F0 --note F1 --secs 0.5 [--set macro_1=80] --out samples/raw/x.wav` renders it and prints its `audition` row (level, attack, decay, spectrum, pitch, width). Render several presets and `audition` them together; that is how you choose a patch. Mind the patch's own octave setting (the sheet shows it): play it in the register you will write in.
- **Play:** give a track `serum="<preset>"` (and optionally `serum_params={"macro_1": 60, "filter_1_freq_hz": 900}`) and write its notes like any other part:

  ```python
  bass = song.add_track("Bass", "bass", serum="BS Gunman Reese", serum_params={"macro_1": 35},
                        volume_db=-9, effects=[{"device": "Compressor", "sidechain": "Kick", "params": {"Threshold": -30, "Ratio": 5}}])
  ```

  The part is rendered through the plug-in (cached in `<project>/serum/`), so `eval`, `view`, `width` and the preview all measure Serum's real sound, and `push` places it in Live as one audio clip on an audio track — with the track's effects, sidechain and volume live in Live, and any `filter`/`volume` automation rendered in. Changing notes, preset or parameters re-renders on the next build.
- **Explore with it** like with samples: several presets per part, several macro settings per preset, compared by `audition` and in context.
- Limits: it reaches Live as audio, not as an editable Serum device (Live exposes no way to script a plug-in's preset); one preset and one set of parameter values per track (no parameter automation over time yet — use two tracks, or `filter`/`volume` automation on the result); macOS path of the VST3 is assumed.

Plug-ins: an `instrument` name is looked up in Live's instruments and sounds, then your User Library, then VST/AU plug-ins, so `instrument="Serum 2"` puts a live Serum device on the track — but on its init patch, since Live exposes no plug-in presets or parameters to scripts. To actually use a Serum sound, use `serum=` as above.

Presets are not samples: nothing here loads a third-party synth preset. Use a one-shot in Simpler, or name a Live instrument in `instrument`.

## The process

1. **Inventory.** If a project exists: read its `CLAUDE.md` and `project.md` (summarise the last session in one sentence), `song.py` and `score.md`. If not, ask what they want, then `init` — which copies the scaffold in `project-template/`.
2. **Converse.** Ask questions shaped by the brief: reference tracks/artists, subgenre, BPM, key/mood, club vs radio length, vocal?, which instruments/plugins they own, what the drop should feel like. No fixed checklist.
3. **Propose strategy** (4–8 sentences): tempo/key, arrangement with bar counts, groove, bass approach, harmony, hook, palette, what makes the drop land. **Wait for confirmation.**
4. **Write.** Run `rick-rubin check <dir>` after every edit (it catches misspelled names, wrong arguments, broken structure and music-lint errors before anything is rendered). Compose the parts in `song.py` — drums, bass, harmony, hook, arrangement, groove — by hand, for this brief. Re-read `score.md` after each round of changes; zoom with `--bars/--tracks` when the question is local.
5. **Self-eval.** `eval`. Read every line. Lint errors are correctness bugs — fix them. Audio checks catch contrast (breakdown ≥3 LU under the drop), a flat energy curve, a swamped or missing low end, dull tops. `view` the transitions that matter (end of build → drop, breakdown entry) and check: the gap before the drop, the roll, sidechain pump visible on the waveform, the filter sweep. Fix → re-eval, max 3 passes.
6. **Present.** Summarise the arrangement and what you changed and why. Offer the preview.wav as a sketch (not the final sound).
7. **Push and capture.** `status`, then `push` (`--replace` on re-push), then `capture` and judge the mix on Live's own audio (clipping on the master, sidechain depth, balance, width). Then `reference compare`, a master chain, and another round until nothing is outside the references without a reason. Read the push report: missing instruments and unrouted sidechains are listed as warnings — tell the user exactly what to fix by hand.
8. **Persist.** `remember` with strategy, decisions, reasoning log, outstanding items.

## House craft (what the genre does — knowledge, not parts to copy)

- **Tempo/feel:** deep 118–122 with heavy swing (56–58%); classic/garage-tinged 122–125 (53–55%); tech 124–128, nearly straight (50–53%).
- **Drums:** kick every beat; clap/snare on 2 and 4; open hat on every off-beat 8th; closed hats as swung 16ths with accent/ghost velocities; a syncopated rim/perc for movement. Fills on the last bar of 8-bar phrases. Drop the kick on beat 4 before a new phrase (`kick_gap`).
- **Bass:** off-beat 8ths (classic), rolling 16ths that skip the downbeat (tech), syncopated dub lines with octave pops and approach notes (deep). Roots sit around 40–80 Hz. Sidechain to the kick.
- **Harmony:** minor or dorian. Deep: held min7/min9 voicings, 2 bars per chord. Classic: piano/organ stabs on off-beats, 1 bar per chord. Tech: one chord stab, harmony mostly implied by the bass. Voice-lead and keep chords between ~F2 and G4.
- **Arrangement:** intro 16–32 (drums) → groove (clap, open hat, filtered bass) → main (chords in) → breakdown (drums & bass out; pad + hook) → build (4-bar roll accelerating to 16ths, riser, filters opening, silent last beat) → drop 32 (everything) → bridge 8 (breath) → drop 2 (one new layer or the hook up an octave) → outro 16–32 (strip back to drums).
- **Energy:** something enters or leaves every 8 bars; the breakdown must feel like a valley (≥3 LU quieter in eval) or the drop won't land.

## Anti-patterns

- Reaching for stock rhythms or progressions instead of writing for the brief. If two of your tracks share a bassline, something went wrong.
- Every hit at the same velocity, dead on the grid, with no per-track groove.

- Listening "by proxy" through constant `view` calls. Read the score; view only at decision points.
- Editing in Live and hoping it syncs back.
- Building before the plan is confirmed.
- Drops without a preceding tension section; static 32-bar loops with no fills or entries.
- Chords or pads below C2 fighting the bass; polyphonic bass.
- Looping eval forever — 3 passes, then report.
- Treating preview.wav as the sound. It is a sketch for comparing sections; loudness, density and width are judged on a Live capture with `reference compare`.
- Stopping at "0 errors". Lint and eval do not know whether it sounds like a record; `reference compare` is the closer you get to that question.
