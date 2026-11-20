# Serum 2: find, read, hear, design, match

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
- **Tempo:** the offline host gives Serum no tempo, so on its own Serum runs at 120 BPM. Song stems (and `serum render/describe/ab/set --bpm N`) rewrite tempo-synced LFOs and delays as free-running at the song's tempo, so a 1/4 LFO at 126 BPM really moves at 2.1 Hz.
- In Logic the patch can also arrive inside a live Serum 2, editable: `push --serum-live` for a song, `rick-rubin logic add-serum` / `logic serum` in a project that is open (`skill/logic.md`).
- Limits: by default it reaches the DAW as audio, not as an editable Serum device (Live always; Logic unless asked as above); one preset and one set of parameter values per track (no parameter automation over time yet — use two tracks, or `filter`/`volume` automation on the result, or build the movement into the patch: an LFO or envelope on the filter); macOS path of the VST3 is assumed.

### Designing a Serum sound

A brief ("a warm tech house bass, rounder than this one, with the filter opening over two bars") becomes a saved `.SerumPreset` that you have heard by measurement. **You write the patch.** The tools read, change, measure and save; there are no style presets in this library and none should be added.

```
rick-rubin serum params --group filter ["<preset>"]     # the map: key, unit, range, init, (the preset's value), what it does
rick-rubin serum params --group fx | mod | env | lfo | osc | sub | noise | routing | macro | global   # one screen each
rick-rubin serum patch "<preset>"                        # the patch as key=value by group, its mod routings, its FX chain
rick-rubin serum describe "<preset>" [KEY=VALUE ...] --note F3 --secs 1 --bpm 126   # what one note does, in numbers
rick-rubin serum describe samples/raw/ref_bass.wav --secs 0.5   # the same numbers for any recording of one note
rick-rubin serum ab "<preset>" --note F3 --bpm 126 --try "filter_1.cutoff_hz=600" --try "osc_a.detune=0.1 osc_a.unison=3"
rick-rubin serum set "<preset>" KEY=VALUE ... [--mod SRC:DEST:AMOUNT] [--unmod DEST] [--fx-add UNIT] [--fx-remove fx.UNIT]
                     [--set KEY=VALUE] --save night-bass-round --project <dir>      # -> <dir>/serum/presets/night-bass-round.SerumPreset
rick-rubin serum tables [words] / serum shapes [words]   # wavetables (osc_a.wavetable=...) and LFO shapes (lfo_1.shape=...)
rick-rubin serum audition "<preset>" --project <dir> [--note F1 ...] [--track Bass --bars 9-16] [--bpm 126] [--as NAME]   # a file for him to hear
rick-rubin serum install <file.SerumPreset>             # into Serum's browser: User / rick-rubin
```

Settings come right after the preset name (or anywhere as `--set KEY=VALUE`); `init` is Serum's init patch. Keys are producer-facing: `osc_a.detune`, `osc_a.unison`, `osc_a.wavetable`, `osc_a.wt_pos`, `osc_a.warp_mode`, `sub.on`, `sub.shape`, `filter_1.type` ("MG Low 24"), `filter_1.cutoff_hz`, `filter_1.res`, `filter_1.drive`, `env_1.*` (amp: `attack_ms`, `decay_ms`, `sustain_db`, `release_ms`), `env_2..4.*` (`sustain_pct`), `lfo_1.rate` ("1/4", "2 bar"), `lfo_1.mode`, `lfo_1.shape` ("Basic/Saw Down" or points "0:1,1:0"), `macro_1.value`, `global.mono`, `global.glide_ms`, `global.volume_db`, and FX units as `fx.<unit>.<param>` (`fx.distortion.drive`, `fx.reverb#2.wet`, `fx_bus1.delay.wet`). Mod sources: `env_1..4`, `lfo_1..10`, `velocity`, `note`, `mod_wheel`, `random_1/2`, `alternate_1/2`, `macro_1..8`; the amount is −100..100 % of the destination's range. The same keys work in a track's `serum_params` (`{"filter_1.cutoff_hz": 900, "mod": ["lfo_2:filter_1.cutoff_hz:20"]}`) next to the plug-in's own names (`macro_1`).

`describe` measures what a brief talks about: attack, decay, sustain (dB under the peak), release; brightness early → late in the note (a filter opening or closing), spectral tilt, harmonic-to-noise ratio, how many harmonics stand within 30 dB and the odd−even balance (saturation and square-ish waves lift the odd ones; a saw is about −2.5 dB); energy per band and stereo side % per band; movement while held and its rate (Hz and, with `--bpm`, beats); pitch with octave, cents, wobble, pitch drop. It adds words to the shared vocabulary: `opens`/`closes`, `moving`, `noisy`, `pure`/`rich`, `odd-heavy`/`even-heavy`, `plucky`, `pitch-drop`, `drifting`. `ab` and `set` print a second table of what changed against the base (`bright early -18%, sustain -2.1 dB, side(low) +12pt, words +wide-low-end -mono`).

The process:

1. **Start from what is closest, not from nothing.** `serum search` by words and `--like "<preset>"`; shortlist three; `serum patch` and `serum show` each; `serum describe` each on the notes the part will play (mind the patch's own octave: `oct -2` means play two octaves higher than you want to hear). A brief that names a reference sound: `describe` the reference too, so you compare like with like.
2. **Decide what to change from the numbers**, then change one or two things at a time: `serum ab "<start>" --try ... --try ...` with 5–10 variants per decision (renders take about a second). Keep what moves the numbers the way the brief asks, and check what else moved (a wider unison often widens the low end; drive adds odd harmonics and loudness).
3. **Build the movement into the patch** when the brief asks for it: an envelope or a slow LFO (`lfo_1.rate="2 bar"`, `lfo_1.mode=Envelope`) on `filter_1.cutoff_hz` via `--mod`; check it with `describe --secs` long enough to hear it and `--bpm` set to the song's tempo.
4. **Keep a log in `project.md`**: what was tried, the numbers, what won and why, what was rejected.
5. **Save** with `serum set ... --save <name> --project <dir>`: a real `.SerumPreset` in `<project>/serum/presets/`. `rick-rubin serum install <dir>/serum/presets/<name>.SerumPreset` (or `--install` on the save) copies it into Serum's own browser, under User / rick-rubin, so Rohil can open and play it in Serum inside Logic. That writes outside the project: do it when he asks to have the sound in Serum.
6. **Let him hear it.** `rick-rubin serum audition serum/presets/<name>.SerumPreset --project <dir> --note F1 --note C2 --bpm 126` writes `auditions/<name>.wav` (and `.mp3`, and a picture of the patch) and logs it as waiting for a verdict; `--track Bass --bars 9-16` plays the track's own part instead of single notes. Send him the file with the before and after numbers. When he answers: `rick-rubin verdict <dir> <name> "what he said" --keep | --reject`. A sound nobody has heard is a candidate, not a result.
7. **Use it and judge it in context:** `serum="serum/presets/<name>.SerumPreset"` on the track, `eval`, then push and bounce (`--daw logic capture --tracks <track>`). A sound that measures right alone can still fight the kick or the pad; the bounce decides. In a project of his own, `rick-rubin logic add-audio` puts a rendered part on a new track.

Honesty: report the before/after numbers, what still differs from the brief, anything you could not do with Serum's controls, and whether he has heard it yet.

### Matching a sound from a record ("make a synth that sounds like this")

```
rick-rubin isolate <dir> refs/track.wav --part bass --bars 33-36 [--bpm 124] [--stem stems/bass.wav]   # -> samples/raw/ref_bass.wav + its notes
rick-rubin serum describe samples/raw/ref_bass.wav --secs 0.4          # the target in the same numbers as any patch
rick-rubin serum search --like-audio samples/raw/ref_bass.wav --folder Bass   # the presets that measure closest
rick-rubin serum fit "<preset>" --target samples/raw/ref_bass.wav --params filter_1.cutoff_hz,filter_1.res,env_2.decay_ms,fx.distortion.drive --iters 30 \
                     --save ref-bass-match --project <dir>
rick-rubin serum match samples/raw/ref_bass.wav samples/raw/try1.wav samples/raw/try2.wav   # distances and what differs
rick-rubin reference stems samples/raw/ref_bass.wav zoom/live_bars_9-16_Bass.wav --bpm 126   # the part in context, against the reference part
```

1. **Isolate** the part: a bar range (at the reference's tempo, estimated when not given) or `--from/--to` seconds. With demucs installed (`pip install -e ".[separate]"`, large) the part is separated; without it the fallback is a band-pass (bass 30–250 Hz, lead 300 Hz–8 kHz, pad 150 Hz–6 kHz), which keeps whatever else is in the band — the kick under a bass — and says so. A stem you already have (`--stem`) is only cut. It prints the notes the part plays.
2. **Describe** the target, then **shortlist** with `serum search --like-audio` (the index's measurements, on whatever register the recording plays). Read the sheets of the closest few.
3. **Fit**: pick the handful of keys the sheet says matter, and `serum fit` moves only those, by coordinate descent on a distance that compares the average spectrum, the level envelope, brightness early/late, width and the odd/even balance, after levelling both (loudness is a fader). Each step renders the target's notes (found from its onsets and pitch) through Serum, about a second each; the patch is played in the register the target sounds in. It prints the path, the distance before/after and its parts, and the describe table target / start / fitted. Never ask it to fit everything: 2–5 keys per run, then look, then decide the next keys.
4. **Finish by hand** with `serum ab`, then judge **in context**: put the patch on the track, capture or bounce, and `reference stems` the reference part against your track's part (`capture --tracks` / `--daw logic capture --tracks`). Pump and transient rows only mean something for a part with content in those bands.
5. **Say what was reached**: the distance and its parts, and what is still different and why (e.g. "the reference's filter moves with a slower LFO than any envelope here; added LFO 1 → cutoff at 1/4 bar").

Plug-ins: an `instrument` name is looked up in Live's instruments and sounds, then your User Library, then VST/AU plug-ins, so `instrument="Serum 2"` puts a live Serum device on the track — but on its init patch, since Live exposes no plug-in presets or parameters to scripts. To actually use a Serum sound, use `serum=` as above.

Presets are not samples: nothing here loads a third-party synth preset. Use a one-shot in Simpler, or name a Live instrument in `instrument`.
