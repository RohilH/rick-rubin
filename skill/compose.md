# Writing a song as code

For making a track from a brief: the song is `song.py`, every note written by you, checked, measured and then rendered into the DAW (`skill/logic.md`). Read `skill/genres.md` for what the genre does and which checks apply.

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

## The process

1. **Inventory.** If a project exists: read its `CLAUDE.md` and `project.md` (summarise the last session in one sentence), `song.py` and `score.md`. If not, ask what they want, then `init` — which copies the scaffold in `project-template/`.
2. **Converse.** Ask questions shaped by the brief: reference tracks/artists, subgenre, BPM, key/mood, club vs radio length, vocal?, which instruments/plugins they own, what the drop should feel like. No fixed checklist.
3. **Propose strategy** (4–8 sentences): tempo/key, arrangement with bar counts, groove, bass approach, harmony, hook, palette, what makes the drop land. **Wait for confirmation.**
4. **Write.** Run `rick-rubin check <dir>` after every edit (it catches misspelled names, wrong arguments, broken structure and music-lint errors before anything is rendered). Compose the parts in `song.py` — drums, bass, harmony, hook, arrangement, groove — by hand, for this brief. Re-read `score.md` after each round of changes; zoom with `--bars/--tracks` when the question is local.
5. **Self-eval.** `eval`. Read every line. Lint errors are correctness bugs — fix them. Audio checks catch contrast (breakdown ≥3 LU under the drop), a flat energy curve, a swamped or missing low end, dull tops. `view` the transitions that matter (end of build → drop, breakdown entry) and check: the gap before the drop, the roll, sidechain pump visible on the waveform, the filter sweep. Fix → re-eval, max 3 passes.
6. **Present.** Summarise the arrangement and what you changed and why. Offer the preview.wav as a sketch (not the final sound).
7. **Push and capture.** `status`, then `push` (`--replace` on re-push), then `capture` and judge the mix on Live's own audio (clipping on the master, sidechain depth, balance, width). Then `reference compare`, a master chain, and another round until nothing is outside the references without a reason. Read the push report: missing instruments and unrouted sidechains are listed as warnings — tell the user exactly what to fix by hand.
8. **Persist.** `remember` with strategy, decisions, reasoning log, outstanding items.

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
