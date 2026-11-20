# rick-rubin: next integrations — Serum 2 sound design, reference matching, Kickstart 2, Trackspacer

A hand-off plan for a fresh agent. Repo: `~/Documents/apps/rick-rubin` (clone of dadams22/rick-rubin; branch `logic-pro`
holds the Logic Pro render target, PR #1 upstream). Read `CLAUDE.md`, `PREFERENCES.md`, `SKILL.md`, `docs/LOGIC.md` and
`rick_rubin/serum.py` first. House rule that shapes everything below: **no canned musical content** — the tools find,
read, measure and render; the agent decides. A "sound design" feature therefore gives the agent *controls and
measurements*, never a preset generator.

Machine facts (checked 2026-10-09 on Rohil's Mac): Serum 2 (`Serum2.vst3` + `.component`), Kickstart 2 (VST3 + AU),
Trackspacer 2.5 (VST3 + AU) and Vital are installed. Logic Pro 11.2.2. Ableton Live is the primary target of the
toolkit; Logic is the second. Serum's factory presets live under `/Library/Audio/Presets/Xfer Records/Serum 2 Presets/`.

## What exists today for Serum (do not rebuild)

- `rick_rubin/serum.py`: reads `.SerumPreset` files (XferJson header + zstd/CBOR parameter tree) into a text patch
  sheet (`serum show`), lists/searches presets (`serum list`, `serum search` by measured character once `serum index`
  has rendered each preset), hosts the real plug-in in-process with pedalboard (`SerumHost.get()`, `load()`, `params()`
  — ~2600 parameters by name with ranges —, `set()`, `render()`), writes a `.vstpreset` (`write_vstpreset`), and renders
  a track's part to a stem (`track_stem`) that `push` places in Live as audio.
- `rick_rubin/pictures.py:serum_png`: a patch panel picture (wavetable frames, envelopes, chain, macros, a note's spectrum).
- `rick_rubin/samples.py:describe_audio` + `character_words`: the shared measured vocabulary (attack, decay, bright/dark,
  sub, width, …) used for samples *and* Serum presets. `audition_table` compares renders.
- `rick_rubin/reference.py`: profiles a whole mix against released tracks (loudness, density, balance, width, pump,
  movement). Mix-level, not sound-level.
- `rick_rubin/pitch.py`: notes inside a single-voice sample (pitch with octave, cents).
- Limits today: Serum reaches Live/Logic as rendered audio, one preset + one parameter set per track, no parameter
  automation over time, no way to *save* a designed sound as a `.SerumPreset` the user can open in Serum's UI.

## Feature 1 — Serum sound design by prompt (start here)

Goal: `rick-rubin serum design <project> --name "deep sub reese" --brief "..."` is *not* the interface. The interface is
the agent, reading `SKILL.md`, using small deterministic tools to go from a brief ("a warm detuned tech house bass with a
slow filter envelope and a touch of saturation") to a saved patch it has heard by measurement. The tools to add:

1. **A semantic parameter map** (`rick_rubin/serum_params.py`): the ~2600 raw names grouped and documented the way a
   producer thinks — oscillators (engine, wavetable/frame, unison voices/detune/width, octave/semi/fine, level, pan,
   warp mode), filters (type, cutoff Hz, resonance, drive, routing), envelopes (ADSR in ms/%), LFOs (rate sync/Hz,
   shape, amount), mod matrix slots (source, destination, depth), FX rack (each unit's on/off and main knobs), global
   (voices, glide, bend), macros 1-8 (names, what they modulate). Each entry: raw name(s), units, range, what it does
   in one line. Build it by *reading* `SerumHost.params()` and the factory presets' trees (`_patch_facts` already
   decodes some), not by guessing. Expose `serum params --group filter` views that an LLM can read in one screen.
2. **Patch editing as data** (`serum patch`): a patch is a dict of semantic settings; `apply(patch) -> raw param dict`
   and `read() -> patch`. `serum set "<preset>" osc_a.detune=0.18 filter_1.cutoff_hz=800 env_2.attack_ms=40
   fx.distortion.drive=35 --save "<name>"` edits and saves. Saving means **writing a real `.SerumPreset`** (extend
   `_pack`/`join_state` into `write_preset(tree, meta, path)`; verify by reopening the file in Serum's UI once, by hand,
   and by `read_preset` round-trip tests). Save into the project folder (`<project>/serum/presets/`) by default; only
   copy into Serum's user preset folder on request (CLAUDE.md: nothing is written into `~/Library` without the
   owner's say-so).
3. **Hear by measurement, iterate**: `serum render` already prints the audition row. Add `serum describe <wav|preset>`
   that measures the *sound-design* facts the brief uses — spectral centroid and tilt over the note, harmonic vs noise
   ratio, attack/decay/sustain/release estimate from the envelope, sub/bass/mid/high balance, stereo width per band,
   movement (LFO/filter sweep rate estimated from spectral flux), pitch stability, saturation (odd/even harmonic
   growth). Keep the output as a short table + the same vocabulary words as samples. This is what lets the agent say
   "too bright, cut 1.5 kHz of cutoff" and check it.
4. **An A/B loop that is cheap**: `serum ab "<preset>" --set filter_1.cutoff_hz=600 --set ...` renders base vs variants
   with the same notes and prints `compare_table`. Renders are ~1 s; the agent should try 5–10 variants per decision.
5. **SKILL.md section "Designing a Serum sound"**: the process — start from the three closest presets (`serum search
   --like` / by words), read their sheets, decide what to change, edit in small steps, measure each step, keep a log in
   `project.md` (what was tried, what won, numbers), save the result as a `.SerumPreset`, use it with `serum=` on a
   track and judge it in context on a capture/bounce. State the house rule: the agent writes the patch; no "style
   presets" in the library.
6. **Tests**: parameter map coverage (every raw name is in exactly one group or an explicit "ignored" list), patch
   round trip (edit → save → read → same values), `describe` on synthetic signals (a saw, a filtered saw, a noise
   burst) giving the expected words. Rendering tests need Serum installed: skip when absent.

Deliverable: an agent can be told "make me a tech house bass like the one in Night Shift but rounder, with a slow
filter open over 2 bars" and come back with `serum/presets/night-bass-round.SerumPreset`, a before/after table, and
the song using it.

## Feature 2 — Reference sound matching ("make a synth that sounds like this")

Goal: given a reference recording (a whole track plus a time range, or a stem), build a Serum patch that measures close
to the target sound, then let the agent finish it by ear-by-numbers.

1. **Isolate the target** (`rick_rubin/isolate.py`): `rick-rubin isolate <project> reference.wav --bars 33-36 --part
   bass|lead|pad|drums --out samples/raw/ref_bass.wav`. Use a stem separator (demucs via `pip install demucs` — heavy,
   optional extra `[separate]`), time-cropped; fall back to band-passing when demucs is not installed. Also accept a
   user-provided stem. Run `pitch.sample_notes` on the result to know what notes it plays (so the match renders the
   same notes).
2. **Describe the target** with the Feature-1 `serum describe` (same measurements, same words) — this makes target and
   candidate comparable.
3. **Shortlist by similarity**: `serum search --like-audio samples/raw/ref_bass.wav` — the index already measures every
   preset on a comparable register (`serum index`); reuse its feature vector distance (`samples.similar`). Return the
   10 nearest presets with their sheets.
4. **Fit**: `serum fit "<preset>" --target samples/raw/ref_bass.wav --notes from-target --params filter_1.cutoff_hz,
   osc_a.detune,env_2.decay_ms,fx.distortion.drive --iters 30`: coordinate descent / Nelder–Mead over a *small*
   chosen parameter set, minimising a weighted distance over the `describe` features (log-spectral distance, envelope
   shape, width, centroid). Each step is one offline render (~1 s), so 30–100 steps is minutes. Print the path it
   took and the final table; save as a `.SerumPreset`. Never fit all 2600 parameters: the agent picks the handful
   that the sheet says matter, the tool moves them.
5. **In context**: put the patch on a track with `serum=`, push/bounce, compare the captured track against the
   reference section with `reference compare`-style numbers (extend `reference.py` to compare two *stems*, not only
   full mixes).
6. **SKILL.md**: the process (isolate → describe → shortlist → fit → finish by hand → judge in context) and its
   honesty rules: say what distance was reached, what is still different (e.g. "the reference has a slower LFO than
   Serum's envelope can fake without a mod slot; added LFO 1 → cutoff at 1/4 bar").

## Feature 3 — Serum as a live device in the DAWs (optional, after 1 and 2)

Today Serum sounds reach the DAW as rendered audio. Live cannot load a `.SerumPreset` into a device from a script, but
it *can* set any exposed VST3 parameter by name (`device` command) — so a designed patch could be reproduced on a live
Serum device by setting its ~2600 parameters from the preset tree (slow; try `param.value` in a batch; measure how long).
Logic: the Mackie Control edit view shows Audio Unit parameters as "Control #n" when the plug-in gives no names
(Serum does give names in Logic's own parameter list — verify), so the same may work there but slower. Decide after
timing; keep the rendered-stem path as the default because it is exact.

## Feature 4 — Kickstart 2 (sidechain pump without routing)

Kickstart is an audio effect with a few parameters (Mix, Length/pattern choice, Curve/shape, Sync, Tempo, Offset).
It needs no side-chain routing, so it fits both DAWs directly:

- Live: `effects=[{"device": "Kickstart 2", "params": {"Mix": 80, "Length": "1/4"...}}]` through the existing `device`
  command (VST3 parameters by name). Read the exact names with `rick-rubin devices "Kickstart 2"`.
- Logic: the bridge inserts it like any plug-in (`insert_plugin` scrolls the surface's list; "Kickstart 2" is in it)
  and sets parameters in the Plug-in Edit view by displayed value.
- Model: add a `sidechain: "kickstart"` option to `Track.sidechain` (today a bool meaning "compressor keyed from the
  kick") that inserts Kickstart with a sensible default pattern and depth taken from the song's kick pattern (four-
  on-the-floor → the 1/4 shape). The preview already imitates sidechain ducking; reuse it for the offline sketch.
- Document in SKILL.md: when to prefer Kickstart (pumping pads/chords) vs a keyed compressor (bass).

## Feature 5 — Trackspacer 2.5 (spectral ducking)

Trackspacer carves the side-chain input's spectrum out of the track it sits on; it *needs* side-chain routing:

- Live: `{"device": "Trackspacer 2.5", "sidechain": "Vocal", "params": {"Amount": 60, ...}}` — the `device` command
  already routes `input_routing_type` for plug-ins with a side-chain input; verify Trackspacer exposes one in Live
  (if not, Live's "Sidechain" must be enabled in the device's expanded view — check the Live Object Model for that
  switch).
- Logic: insert + `set_side_chain` (the plug-in window's header pop-up, which the bridge already drives) + parameters
  in the edit view.
- Use cases to document: pads under a vocal, bass under a kick as an alternative to compression; measure the result
  with `capture --tracks` before/after (spectral balance of the ducked track in the kick's band).

## Order of work and time estimates

1. Feature 1 steps 1–3 (map, patch edit/save, describe): 1–2 days. Step 4–6: 1 day.
2. Feature 2: 2–3 days (demucs setup and the fitting loop are the long poles).
3. Feature 4 then 5: half a day each on Live (the device path exists), half a day each on Logic plus a bounce test.
4. Feature 3 only if 1 and 2 land and someone wants editable devices in the DAW.

## Working notes for the agent

- Serum renders are the ground truth for sound; the DAW is the ground truth for the mix. Measure, do not assume.
- Keep every new CLI command's output short enough to read in one screen; tables over prose.
- Add tests next to the code they test (`tests/test_serum_design.py`), skipping when Serum is not installed.
- Logic UI rules if the Logic path is touched: see `docs/LOGIC.md` troubleshooting and the memory note
  "logic-pro-automation-rules" — no global keystrokes while someone uses the Mac, one track selected before strip
  edits, the surface disconnected while a plug-in header pop-up is used.
- Report what was tried, kept, rejected and measured (PREFERENCES.md §6), in `project.md` of the song you work in.
