---
name: ableton-use
description: Produce house / EDM tracks by conversation and render them into Ableton Live. Generate, read, edit, self-evaluate and push full arrangements (drums, bass, chords, pads, hooks, builds, drops, automation, sidechain). Ask, confirm the plan, execute, self-eval, persist. Production-correctness rules are hard; everything else is artistic freedom.
---

# ableton-use

## Principle

1. **You never listen. You read.** The track lives in `song.json`; `score.md` is its packed reading view (arrangement map, energy curve, every pattern as step strings / note events — ~6 KB for a 5-minute track). `eval.md` adds *measured* loudness, crest factor and spectral balance per section from an offline preview render. `view` draws piano roll + waveform + spectrogram for a bar range — **on demand, at decision points only**, never as a scan.
2. **Rhythm and arrangement are primary; sound design follows.** House lives or dies on the groove and on 8/16/32-bar phrasing. Get those right in the score, then let Live's instruments do the timbre.
3. **Ask → confirm → execute → self-eval → push → persist.** Never build until the user has approved a plain-English plan.
4. **song.json is the source of truth; Ableton is a render target.** Edits go into the song, then get re-pushed (`--replace`). Never "fix" things inside Live and expect them to come back.
5. **Artistic freedom is the default.** Every value in `ableton_use/house.py` (patterns, templates, voicings, volumes) is a worked example of idiomatic house, not a mandate. Deviate whenever the brief calls for it — invent sections, parts, grooves.
6. **Verify before you present.** If `eval` fails, you are not done.

## Hard rules (production correctness — non-negotiable)

1. **Phrasing:** section lengths are multiples of 8 bars (a 4-bar pickup at most). Something changes every 8 bars, something big every 16.
2. **DJ-friendly edges:** intro and outro ≥ 16 bars, drums-led; no bass/chords/hook in the first or last 8 bars (unless the user explicitly asks for a radio edit).
3. **One tempo, 118–130 BPM.** No tempo changes inside a track.
4. **In key.** Melodic notes stay in `song.key`; a chromatic note must be deliberate and mentioned in your reasoning.
5. **Low end:** bass is monophonic, roughly C0–G2 (MIDI 24–55), sidechained to the kick, and mostly avoids kick hits. Nothing but kick and bass below C2 (MIDI 48).
6. **Drops earn their impact:** every drop follows a build or breakdown and starts with the kick on bar 1. A beat of silence (`kick_gap`, the roll's silent last beat) before the drop is the classic move.
7. **Pitch convention is Ableton's:** C3 = MIDI 60, C1 = 36 (kick), Drum Rack pads start at C1.
8. **Edit through ops or the Python API, then re-read `score.md`.** Never hand-edit flattened MIDI.
9. **Self-eval before showing or pushing:** `ableton-use eval <dir>` must have 0 errors. Cap at 3 eval passes — then report what's left instead of looping.
10. **Push only after eval passes, and only with the bridge connected** (`ableton-use status`). Re-pushes use `--replace`.
11. **Strategy confirmation before execution.**
12. **All outputs in the project folder.** Never write inside the ableton-use repo.
13. **Measure sample pitch; never trust filenames.** Sample packs disagree on octave naming (a "C2" bass is often MIDI 36 = Ableton's C1) and are rarely dead in tune. Import melodic one-shots with `--melodic` and use the `sample_root` it prints.

## Setup

First-time install lives in `install.md`. On cold start just verify: `ableton-use templates` runs (package installed), and — before any push — `ableton-use status` reaches Live. You drive everything through the `ableton-use` CLI (or `from ableton_use import Project` in a Python snippet) with your own shell and file tools; there is no separate agent runtime. Run `view` and Read the PNG it prints to look at it.

## Directory layout

```
<project>/
├── song.json      ← source of truth (tracks, patterns, sections)
├── score.md       ← packed score — your primary reading view
├── eval.md        ← latest self-eval
├── project.md     ← memory; append one section per session
├── preview.wav    ← offline sketch render (numpy synth)
├── midi/          ← song.mid + per-track .mid (manual fallback)
├── views/         ← on-demand timeline PNGs
├── samples/       ← imported one-shots and conformed loops (`sample`); raw downloads in samples/raw/
└── history/       ← snapshot before every edit batch (`undo`)
```

## Commands

```
ableton-use templates                         # subgenres + arrangement templates
ableton-use new <dir> --subgenre deep|classic|tech --template club|radio|dj_tool [--key "A minor"] [--bpm 122] [--seed N] [--progression "1 6 4 5"]
ableton-use score <dir> [--bars 33-48] [--tracks Bass Kick]   # print/refresh score.md; with a zoom, print just that slice
ableton-use edit <dir> ops.json               # or '-' for stdin; see ops below
ableton-use undo <dir>
ableton-use transcribe <dir> samples/vocal.wav [--model small.en]   # words -> bar.beat.16th, cached, shown in score.md
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

Python: `from ableton_use import Project, generate`; `Project(dir).edit(ops)`, `.evaluate()`, `.view((65, 80))`, `.push(replace=True)`.

## Edit ops (JSON)

```json
{"ops": [
  {"op": "set", "field": "bpm", "value": 123},
  {"op": "generate", "what": "bass", "name": "bass_roll", "options": {"style": "rolling", "progression": [1, 6, 4, 5]}},
  {"op": "pattern", "name": "perc2", "track": "Perc", "pitch": "D2", "steps": "..x...x...x..x.x"},
  {"op": "pattern", "name": "hook", "track": "Lead", "bars": 2, "notes": [["A3", "1.1.3", 0.5, 100], ["C4", "1.2.3", 0.25, 90]]},
  {"op": "part", "section": "drop2", "track": "Bass", "pattern": "bass_roll"},
  {"op": "part", "section": "drop", "track": "Lead", "pattern": "lead", "start": 8, "transpose": 12},
  {"op": "part", "section": "bridge", "track": "Chords", "pattern": null},
  {"op": "fill", "section": "drop", "track": "Clap", "pattern": "clap_fill", "every": 8},
  {"op": "automation", "section": "build", "track": "Pad", "param": "filter", "points": [0.4, 1.0]},
  {"op": "insert_section", "index": 4, "section": {"name": "break2", "kind": "breakdown", "bars": 8, "energy": 4, "parts": {"Pad": "pad"}}},
  {"op": "track", "name": "Vox", "set": {"role": "vocal", "instrument": ["Simpler"], "volume_db": -10}}
]}
```
Full reference: docstring of `ableton_use/edits.py`. `generate` kinds: bass (offbeat|rolling|syncopated), chords (stab|held|single), pad, lead, hats (straight|shuffle|busy), perc, roll. Automation params: `filter` (0..1, maps to an Auto Filter the bridge inserts), `volume`, `pan`, or `"Device:Parameter"`.

Step strings: one char per 16th, `|` separates bars. `x`=100 `X`=127 `o`=72 `g`=45 (ghost) `1-9` scaled, `.` rest. Note positions: `"bar.beat.sixteenth"` (1-based, Ableton style) or float beats.

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

**Vocals: read the words.** `ableton-use transcribe <dir> samples/vocal.wav` runs a local Whisper model, tightens each word against the audio's own envelope and lists every word with its `bar.beat.sixteenth` position, its offset from that 16th in ms and the model's confidence. `score.md` then prints the words under the loop's pattern (`?` = doubtful word). Use it to decide where a phrase starts and ends before cutting a loop with `start`/`end`, to keep the hook word on a downbeat, and to keep leads out of the way of the lyric. Short chopped vocals transcribe roughly: trust positions more than spellings.

**Stereo image: read the width.** `ableton-use width <dir> [file]` is a correlation meter and imager in table form: correlation (+1 mono, 0 very wide, negative = out of phase), side % (the share of energy that disappears in mono), L/R balance, loudness lost in mono, and side %/correlation in four bands — for the whole file and per section. Rules it checks: low end centred below 150 Hz, no negative correlation, under 3 LU lost in mono, no lean over 1.5 dB. Run it on samples before using them (wide risers and loops are common) and on audio captured from Live. The offline preview is built from mono stems, so its width only reflects panning.

Plug-ins: an `instrument` name is looked up in Live's instruments and sounds, then your User Library, then VST/AU plug-ins, so `["Serum 2"]` loads Serum. Live exposes no plug-in presets or parameters to scripts, so it arrives on its default patch; save patches as Live presets or racks in the User Library to load them by name.

Presets are not samples: nothing here loads a third-party synth preset. Use a one-shot in Simpler, or name a Live instrument in `instrument`.

## The process

1. **Inventory.** If a project exists: read `project.md` (summarise the last session in one sentence) and `score.md`. If not, ask what they want, then `new` with the closest subgenre/template as a sketch.
2. **Converse.** Ask questions shaped by the brief: reference tracks/artists, subgenre, BPM, key/mood, club vs radio length, vocal?, which instruments/plugins they own, what the drop should feel like. No fixed checklist.
3. **Propose strategy** (4–8 sentences): tempo/key, arrangement with bar counts, groove, bass approach, harmony, hook, palette, what makes the drop land. **Wait for confirmation.**
4. **Execute.** Generate a starting point, then edit. Re-read `score.md` after every edit batch.
5. **Self-eval.** `eval`. Read every line. Lint errors are correctness bugs — fix them. Audio checks catch contrast (breakdown ≥3 LU under the drop), a flat energy curve, a swamped or missing low end, dull tops. `view` the transitions that matter (end of build → drop, breakdown entry) and check: the gap before the drop, the roll, sidechain pump visible on the waveform, the filter sweep. Fix → re-eval, max 3 passes.
6. **Present.** Summarise the arrangement and what you changed and why. Offer the preview.wav as a sketch (not the final sound).
7. **Push.** `status`, then `push` (`--replace` on re-push). Read the push report: missing instruments and unrouted sidechains are listed as warnings — tell the user exactly what to fix by hand.
8. **Persist.** `remember` with strategy, decisions, reasoning log, outstanding items.

## House craft (worked examples — not mandates)

- **Tempo/feel:** deep 118–122 with heavy swing (56–58%); classic/garage-tinged 122–125 (53–55%); tech 124–128, nearly straight (50–53%).
- **Drums:** kick every beat; clap/snare on 2 and 4; open hat on every off-beat 8th; closed hats as swung 16ths with accent/ghost velocities; a syncopated rim/perc for movement. Fills on the last bar of 8-bar phrases. Drop the kick on beat 4 before a new phrase (`kick_gap`).
- **Bass:** off-beat 8ths (classic), rolling 16ths that skip the downbeat (tech), syncopated dub lines with octave pops and approach notes (deep). Roots sit around 40–80 Hz. Sidechain to the kick.
- **Harmony:** minor or dorian. Deep: held min7/min9 voicings, 2 bars per chord. Classic: piano/organ stabs on off-beats, 1 bar per chord. Tech: one chord stab, harmony mostly implied by the bass. Voice-lead and keep chords between ~F2 and G4.
- **Arrangement:** intro 16–32 (drums) → groove (clap, open hat, filtered bass) → main (chords in) → breakdown (drums & bass out; pad + hook) → build (4-bar roll accelerating to 16ths, riser, filters opening, silent last beat) → drop 32 (everything) → bridge 8 (breath) → drop 2 (one new layer or the hook up an octave) → outro 16–32 (strip back to drums).
- **Energy:** something enters or leaves every 8 bars; the breakdown must feel like a valley (≥3 LU quieter in eval) or the drop won't land.

## Anti-patterns

- Listening "by proxy" through constant `view` calls. Read the score; view only at decision points.
- Editing in Live and hoping it syncs back.
- Building before the plan is confirmed.
- Drops without a preceding tension section; static 32-bar loops with no fills or entries.
- Chords or pads below C2 fighting the bass; polyphonic bass.
- Looping eval forever — 3 passes, then report.
- Treating preview.wav loudness as a master. It's a sketch; compare sections with each other only.
