---
title: Turn a vocal phrase into a playable, stuttering lead: granular sustain, a rhythmic volume gate, reverb, OTT
topic: sound-design
genres: [any, progressive house, bass house, tech house]
source: Alex Rome — My Insanely Simple System for Remixing Any Song (The 3-STEP FLIP) (https://youtu.be/bx8X7oiYhCg?t=205)
status: untested
---
## What it is
The hook of his remix: a short piece of the original vocal loaded into a granular synth so that a held key gives a
sustained note with the singer's tone, then chopped by a tempo-synced volume shape into a stutter. The remix keeps
the artist's voice but gets a new melody and more energy.

## When to use it
When the remix needs its own lead and the vocal should stay recognisable. Two other cards gate a vocal that
sustains through reverb or its own length (`alex-rome-c-vocal-stutter-lead-with-a-trance-gate.md`,
`moonboy-b-stutter-vocal-with-synced-tremolo.md`); this one adds the granular step, which lets the voice be
played at new pitches from the keyboard. For a rap vocal, a sung ad-lib or one
long vowel is the best source (inferred: a granular engine needs a steady pitch to hold).

## How
1. Copy one phrase of the vocal to its own track and bounce it to a file (said,
   [3:25](https://youtu.be/bx8X7oiYhCg?t=205)).
2. Load the file into a granular synth, Arturia Pigments for him, so a key held down plays the phrase as an
   endless note (said, [3:46](https://youtu.be/bx8X7oiYhCg?t=226); shown
   [3:55](https://youtu.be/bx8X7oiYhCg?t=235): sample engine in granular mode with the phrase loaded, a 24 dB
   low-pass after it; the grain density and size values are not readable).
3. After the synth, an LFO-style volume tool turns the held note into a stutter (said,
   [4:08](https://youtu.be/bx8X7oiYhCg?t=248); shown [4:15](https://youtu.be/bx8X7oiYhCg?t=255): a drawn curve
   with 40 % smoothing; "ShaperBox" is partly visible on the channel strip; the rate is not readable).
4. Reverb to "dress it up" and OTT to make it strong (said). Shown at 4:15: OTT depth 48 %, time 100 %; a Valhalla
   reverb with mod rate 2.53 Hz, mod depth 38 %, high cut 8 kHz, low cut 10 Hz (the lane later reads "ValhallaVin:
   Mix", so VintageVerb).
5. Play with it for a minute until a melody appears, then put the chords under it (said,
   [4:08](https://youtu.be/bx8X7oiYhCg?t=248), [4:31](https://youtu.be/bx8X7oiYhCg?t=271)).
6. In the arrangement it enters low-passed and wet, and dries out toward the drop (see
   `arrangement/alex-rome-b-opposite-automation-handoff.md`).

## In Rohil's setup
He does not own Pigments. Serum 2 has a granular oscillator: `rick-rubin logic add-serum` a blank patch, switch
OSC A to Granular in Serum's window and drag the bounced phrase in (the key `osc_a.engine` exists, but loading a
sample from the command line is not documented, so do this step in the window). Logic's Alchemy also has a
granular source; Quick Sampler with a short loop on a vowel is the simple fallback (what is lost: the smear that
hides the loop point). The stutter without ShaperBox: Logic's Tremolo, synced, phase 0, full depth (settings in the MOONBOY
card), or write the stutter as short notes in the MIDI; what is lost is drawing a custom shape. OTT he owns (`rick-rubin logic
devices OTT` for the parameter names, then `rick-rubin logic insert "Stutter Lead" OTT ...` at about half depth).
Reverb: Valhalla Supermassive or ChromaVerb.

## How to check it
Bounce the part alone. `rick-rubin notes <dir> stutter.wav`: steady pitches, the notes played, in key, within a
few cents. `rick-rubin hits <dir> stutter.wav`: onsets on the gate's grid. Then the lead against the original
vocal phrase for Rohil: is it still that singer?

## Why it works
Granular playback separates the voice's tone from its timing, so the tone can be held and re-pitched like a synth;
the gate then supplies a rhythm the original phrase never had.
