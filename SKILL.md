---
name: ableton-use
description: Write house / EDM tracks as Python code — every note, rhythm, groove and section written by you — then read, measure and render them into Ableton Live (samples, instruments, effects, sidechain, automation) and check the result on audio recorded back from Live. No templates or generators. Ask, confirm the plan, write, self-eval, push, capture, persist.
---

# ableton-use

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
9. **Self-eval before showing or pushing:** `ableton-use eval <dir>` must have 0 errors. Cap at 3 eval passes — then report what's left instead of looping.
10. **Push only after eval passes, and only with the bridge connected** (`ableton-use status`). Re-pushes use `--replace`.
11. **Strategy confirmation before execution.**
12. **All outputs in the project folder.** Never write inside the ableton-use repo.
13. **Measure sample pitch; never trust filenames.** Sample packs disagree on octave naming (a "C2" bass is often MIDI 36 = Ableton's C1) and are rarely dead in tune. Import melodic one-shots with `--melodic` and use the `sample_root` it prints.

## Setup

First-time install lives in `install.md`. On cold start just verify: `ableton-use --help` runs (package installed), and — before any push — `ableton-use status` reaches Live. You drive everything through the `ableton-use` CLI (or `from ableton_use import Project` in a Python snippet) with your own shell and file tools; there is no separate agent runtime. Run `view` and Read the PNG it prints to look at it.

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
ableton-use init <dir> --title "..." --bpm 126 --key "A minor"   # a song project from project-template/: CLAUDE.md, empty song.py, project.md, manifest
ableton-use audition <dir> samples/raw/kick_*.wav   # candidates side by side: punch, decay, spectrum, pitch+octave, width
ableton-use browse "sounds/Bass" [--search sub]     # what Live offers: instruments, presets, effects, plug-ins
ableton-use build <dir>                       # run song.py -> song.json + score.md (every other command does this when song.py changed)
ableton-use score <dir> [--bars 33-48] [--tracks Bass Kick]   # print/refresh score.md; with a zoom, print just that slice
ableton-use transcribe <dir> samples/vocal.wav [--text "lyric"]   # syllables -> bar.beat.16th + ms off the grid
ableton-use retime <dir> samples/vocal.wav --name vocal_q          # audio-quantize a loose vocal loop, word by word
ableton-use notes <dir> samples/vocal.wav                          # the notes inside a sample: pitch+octave, cents, position
ableton-use width <dir> [file]                # stereo image: correlation, side %, mono loss, per band and section
ableton-use sample <dir> <file> --name N --oneshot [--melodic]                       # Simpler one-shot; --melodic measures its pitch
ableton-use sample <dir> <file> --name N --loop --src-bpm B [--bars N] [--align end] [--end-at S] # audio loop, conformed to the song tempo
ableton-use eval <dir>                        # lint + preview render + measurements -> eval.md (exit 1 on errors)
ableton-use eval <dir> --bars 33-48 --tracks Bass Kick   # zoom: measure a bar range and/or a solo of some tracks
ableton-use capture <dir> [--bars 33-48] [--tracks Bass Kick]   # record Live's real output (real time), measure it, draw it
ableton-use eval <dir> --live [--bars ...]    # measurements of the last full capture (live.wav)
ableton-use view <dir> --bars 65-80 [--tracks Bass Kick]
ableton-use preview <dir> [--stems]
ableton-use midi <dir>
ableton-use install-bridge                    # once; then pick "AbletonUse" control surface in Live
ableton-use status                            # ping Live
ableton-use push <dir> [--replace]            # build the arrangement in Live
ableton-use remember <dir> --strategy ... --decisions ... --reasoning ... --outstanding ...
```

## Writing a song

A song is a Python file, `song.py`, that leaves a `Song` in a variable called `song`. You write it with your normal file tools; every command rebuilds from it. It is ordinary Python — use loops, functions and your own helpers freely.

```python
from ableton_use import Song

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
- **`instrument_params`** sets the track instrument's own parameters by displayed value — for Simpler e.g. `{"Ve Attack": 4, "Ve Release": 60, "Vol < Vel": 75}`. Attack time and velocity sensitivity are per track; per-hit feel comes from velocity and timing.
- **Automation** values run 0..1 over the section: `[start, end]` or `[[fraction, value], ...]`. `filter` is a low-pass sweep (60 Hz–18 kHz), `volume` and `pan` are the mixer; `"Device:Parameter"` reaches anything else on MIDI tracks. On audio-loop tracks, `filter` and `volume` are rendered into the audio.
- Projects that are only a `song.json` (no `song.py`) can still be changed with JSON ops through `ableton_use.edits`; a project with a `song.py` is always edited there.

## Exploring

Great tracks come from comparing options, not from accepting the first one. You cannot hear, so exploring means *measuring several things and reading the difference*. Budget most of a session for it.

- **Samples, per role.** Search more than once with different words (character, genre, era, gear: "rubbery", "909", "dusty", "tight short"). Download a shortlist — typically 4–8 for the sounds that define the track (kick, bass, main hook, vocal), 2–4 for supporting ones — into `samples/raw/` and run `audition` on them together. Read the table for what the role needs: a kick's fundamental and decay (does it leave room for the bass? is its pitch in key?), a hat's centroid and length, a clap's body vs. snap, a bass one-shot's octave and sustain. Then test the finalists **in context**: point the track at each in turn and compare a zoomed `eval`/`capture` of the same bars. Log every candidate in `samples/manifest.json` — used or rejected, with the reason.
- **Loops and vocals.** `transcribe`, `notes` and `width` each candidate before choosing; a loop that is late, flat or in the wrong key costs more to fix than to replace.
- **Instruments and presets.** `browse "sounds/<category>"` lists Live's presets, `browse plugins` the plug-ins, `serum list/show` reads Serum patches. Try several for each synth part: load each (`instrument="<name>"`), `capture --bars ... --tracks <that track>`, and compare spectrum, level and width.
- **Parts.** Write two or three genuinely different basslines / hooks / hat grooves as separate variables, swap them into the same section, and compare — score them against the vocal's syllables and notes, kick collisions, register, density. Keep the winner, note what the others taught you, delete the losers from `song.py` once the log has them.
- **Arrangement and mix.** Change one thing at a time, capture the affected bars, compare numbers.

Stop exploring a question when one option is clearly right for this track and you can say why — not when the first one passes lint.

## Zooming in

`score`, `eval`, `view`, `width` and `capture` all take `--bars A-B`; all but `width` take `--tracks ...` too. Use the zoom whenever a question is local — "is the bass ducking under the kick in the drop?" is `eval --bars 41-48 --tracks Kick Bass` plus `view` on the same slice, not a re-read of the whole song. Bar numbers are always the song's. A solo render is normalised on its own, so compare shapes and ratios inside it, not its level against the full mix.

## Hearing what Live plays: `capture`

`preview.wav` is this library's own sketch render. `capture` is the real thing: it adds a temporary audio track set to **Resampling**, records the arrangement from Live's master in real time (the whole song, or just `--bars`; `--tracks` solos them), copies the take into the project (`live.wav`, or `zoom/live_bars_...wav`), removes the track and restores solo/metronome/loop. It then prints the same loudness table as `eval`, the stereo report, and a `view` drawn from Live's audio. Capture after every push you intend to present, and judge mix decisions — sidechain depth, compressor settings, master clipping, width — on it rather than on the preview. A zoomed capture of 8 bars takes ~15 s; use those while iterating and one full capture at the end.

## Effects and compressors

A track's `effects` is an ordered list of Live audio effects placed after the instrument. Every parameter is set by the value Live displays, in Live's own names and units:

```json
{"op": "track", "name": "Bass", "set": {"effects": [
  {"device": "Compressor", "sidechain": "Kick", "sidechain_tap": "Post FX",
   "params": {"Threshold": -32, "Ratio": 6, "Attack": 0.1, "Release": 110, "Knee": 3,
              "Model": "Peak", "LookAhead": "1 ms", "Makeup": false, "S/C EQ On": false, "Dry/Wet": 100}}]}}
```

Numbers are dB, ms, Hz, % or the ratio's first figure (`"inf"` for a limiter); switches take true/false; menus take the option's name. Compressor parameters: Threshold, Ratio, Expansion Ratio, Attack, Release, Auto Release On/Off, Output, Makeup, Dry/Wet, Model (Peak | RMS | Expand), Env Mode (Lin | Log), Knee, LookAhead (0 ms | 1 ms | 10 ms), S/C Listen, S/C EQ On, S/C EQ Type, S/C EQ Freq, S/C EQ Q, S/C EQ Gain, S/C On, S/C Gain, S/C Mix. `sidechain` names the track that keys the device (a Compressor on the bass keyed from the kick is the house pump); `sidechain_tap` is Pre FX, Post FX or Post Mixer. The push report echoes what Live shows after setting each value and lists any name it did not find — an unknown parameter name is reported with the device's full parameter list, which is also how to discover the parameters of any other device (EQ Eight, Saturator, Reverb, Glue Compressor...). `sidechain: true` on a track remains the shorthand for a default kick-keyed Compressor (−28 dB, 4:1, 0.5 ms, 120 ms). The offline preview only models the ducking, not the compressor's exact curve: tune compressors against `capture`.

## Using Splice / samples

Samples replace Live's stock instruments track by track. Two kinds:

- **One-shots → Simpler.** A track with `sample` plays that file from a Simpler instead of `instrument`. Drum roles use One-Shot mode (every hit plays the whole sample; the score keeps the readable drum-map pitches). Melodic roles use Classic mode and need `sample_root`, the MIDI pitch the file actually sounds at (fractional = cents); the bridge sets Simpler's Transpose/Detune from it so notes in Live show their true pitch.
- **Loops → audio tracks.** A track with `audio: true` holds audio patterns (`{"op": "pattern", "name": "top", "audio": "samples/top.wav", "bars": 8, "key": "F minor"}`). Parts, `start`/`end` and filter/volume automation work as for MIDI. Loops are **conformed on import**: tempo-matched to the song (pitch kept, needs ffmpeg) and cut to exact bars, then placed *unwarped* in Live — N bars of file is N bars of arrangement. `--align end` keeps the tail, so a riser's peak lands on the downbeat after it; if the file carries on past its peak (a tail, a second swell), measure where the peak is and pass `--end-at <seconds>`. Look at the loop in `view` after importing: FX names say little about their shape. Changing `bpm` later means re-importing the loops.

Workflow:

1. **Find** candidates. With the Splice MCP: `describe_a_sound` (`type` loop | oneshot, BPM filters). Prefer loops within ~6% of the song tempo and in the song key or its relative; any key for drums.
2. **Download** to `<project>/samples/raw/`. Splice download URLs expire in about two minutes — fetch immediately. A first download costs a credit (get the user's OK); re-downloads are free. Record name, asset id and pack in `samples/manifest.json`.
3. **Import** with `ableton-use sample`. It prints the measured root or bar count and a ready-made edit op.
4. **Wire up** with `track` / `pattern` / `part` ops, then re-read `score.md`.
5. **Eval.** The preview plays the real samples (repitched like Simpler), so loudness and balance numbers now reflect them. Lint `H14-samples` flags notes more than two octaves from a sample's root and loops cut mid-pass; `H4-key` flags loops in a foreign key.

**Vocals: read the words, to the syllable.** `ableton-use transcribe <dir> samples/vocal.wav [--text "the lyric"]` finds the words (a local Whisper model, or the lyric you give it — better whenever you know it), pins every letter to the audio with a forced aligner, groups letters into syllables and snaps each syllable to the audio itself. For every syllable you get where its sound starts (`cut at`), where it reaches full level (`vowel at` — what a listener hears as on or off the beat), its `bar.beat.sixteenth` and how many ms it is off that 16th. `score.md` prints them under the loop (`-na` continues a word, `?` = doubtful alignment, offsets from 10 ms shown). Read it before writing anything around a vocal: put hooks and fills in the gaps, keep stabs off the stressed syllables. A word that sits exactly between two 16ths is named after the nearer one; look at the offset before trusting the name.

**Loose vocal? `retime` it.** A whole loop that reads +30..+60 ms on most syllables is dragging; scattered signs mean a loose performance. `ableton-use retime <dir> samples/vocal.wav --name vocal_q [--by word|syllable] [--grid 16] [--strength 0.7] [--move 7=3.3.3]` cuts the loop at each word's start and slides it so its attack lands on the grid, writing a new loop of the same length (and its word timings). `--by word` keeps each word's inner flow and is the default; `--strength` below 1 leaves some of the feel; `--move N=bar.beat.sixteenth` places a piece yourself when the nearest 16th is the wrong one. Check the result by transcribing or viewing the new file, not by assuming.

**Samples have notes: read them.** `ableton-use notes <dir> samples/vocal.wav` follows the pitch through a single-voice sample (vocal, bassline, lead; use `--fmin 30` for bass) and lists its notes: pitch **with octave** (Ableton naming, C3 = 60) and Hz, cents sharp/flat, grid position, length, the syllable sung on it, and `!` if it is outside the song's key. The first line gives the register — lowest to highest note and the centre. `score.md` prints the notes under the loop and `view` draws them on the waveform. Use it to choose chords and a bass that agree with what the vocal actually sings, to keep leads out of the vocal's octave, and to spot a loop that is sold as "F minor" but leans on other notes. It hears one voice at a time: chords or full loops will read as nonsense or as nothing.

**Stereo image: read the width.** `ableton-use width <dir> [file]` is a correlation meter and imager in table form: correlation (+1 mono, 0 very wide, negative = out of phase), side % (the share of energy that disappears in mono), L/R balance, loudness lost in mono, and side %/correlation in four bands — for the whole file and per section. Rules it checks: low end centred below 150 Hz, no negative correlation, under 3 LU lost in mono, no lean over 1.5 dB. Run it on samples before using them (wide risers and loops are common) and on audio captured from Live. The offline preview is built from mono stems, so its width only reflects panning.

**Serum 2: read the patch.** `ableton-use serum list [--folder Pad] [--tag Poly] [--search "warm"]` searches the installed presets by folder, tag and words in the name or description; `ableton-use serum show "<name>"` prints a patch sheet — oscillators and their wavetables, filters, envelopes and LFOs, the FX rack, what each of the eight macros is wired to, and global settings. Only values that differ from Serum's init patch are listed. Read the sheet instead of asking for a screenshot of the plug-in: it says which macro opens the filter or brings in the reverb, which is what you need to suggest a preset or tell the user what to automate. What it cannot do yet is load the preset into the plug-in — tell the user which preset to pick in Serum's browser, or have them save it as a Live preset.

Plug-ins: an `instrument` name is looked up in Live's instruments and sounds, then your User Library, then VST/AU plug-ins, so `["Serum 2"]` loads Serum. Live exposes no plug-in presets or parameters to scripts, so it arrives on its default patch; save patches as Live presets or racks in the User Library to load them by name.

Presets are not samples: nothing here loads a third-party synth preset. Use a one-shot in Simpler, or name a Live instrument in `instrument`.

## The process

1. **Inventory.** If a project exists: read its `CLAUDE.md` and `project.md` (summarise the last session in one sentence), `song.py` and `score.md`. If not, ask what they want, then `init` — which copies the scaffold in `project-template/`.
2. **Converse.** Ask questions shaped by the brief: reference tracks/artists, subgenre, BPM, key/mood, club vs radio length, vocal?, which instruments/plugins they own, what the drop should feel like. No fixed checklist.
3. **Propose strategy** (4–8 sentences): tempo/key, arrangement with bar counts, groove, bass approach, harmony, hook, palette, what makes the drop land. **Wait for confirmation.**
4. **Write.** Compose the parts in `song.py` — drums, bass, harmony, hook, arrangement, groove — by hand, for this brief. Re-read `score.md` after each round of changes; zoom with `--bars/--tracks` when the question is local.
5. **Self-eval.** `eval`. Read every line. Lint errors are correctness bugs — fix them. Audio checks catch contrast (breakdown ≥3 LU under the drop), a flat energy curve, a swamped or missing low end, dull tops. `view` the transitions that matter (end of build → drop, breakdown entry) and check: the gap before the drop, the roll, sidechain pump visible on the waveform, the filter sweep. Fix → re-eval, max 3 passes.
6. **Present.** Summarise the arrangement and what you changed and why. Offer the preview.wav as a sketch (not the final sound).
7. **Push and capture.** `status`, then `push` (`--replace` on re-push), then `capture` and judge the mix on Live's own audio (clipping on the master, sidechain depth, balance, width). Read the push report: missing instruments and unrouted sidechains are listed as warnings — tell the user exactly what to fix by hand.
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
- Treating preview.wav loudness as a master. It's a sketch; compare sections with each other only.
