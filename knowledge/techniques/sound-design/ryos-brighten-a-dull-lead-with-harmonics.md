---
title: Brighten a dull lead by adding harmonics, not only by boosting treble
topic: sound-design
genres: [progressive house, bass house, any]
source: RYOS — Giving Feedback On YOUR Tracks! (https://youtu.be/3I7jJyVczPQ?t=1472)
status: untested
---
## What it is
A lead or chord sound whose spectrum stops early sounds muffled and sits at the back. An EQ can only raise
what is there; an exciter or a multiband distortion creates the missing top.

## When to use it
The sound is good but dull, especially in a high-energy drop. He said this to five tracks, and called the
sender lucky when brightness was the only thing wrong.

## How
1. Look at the sound on an analyser. If the content falls away in the upper mids, it needs harmonics up there
   (said, [41:31](https://youtu.be/3I7jJyVczPQ?t=2491)).
2. First move for a beginner: a high shelf, and turn the lead up (said, [25:30](https://youtu.be/3I7jJyVczPQ?t=1530)).
3. Then an exciter. He names Noveltech Character and Ozone's exciter; on one track he says the Character preset
   "Techno Synth" at about 50% (said, [3:09:00](https://youtu.be/3I7jJyVczPQ?t=11340)).
4. Or a distortion with separate bands, with the high mids pushed. Not a fuzzy one; he names Thermal, and
   Decapitator if set so it does not sizzle (said, [42:00](https://youtu.be/3I7jJyVczPQ?t=2520),
   [45:00](https://youtu.be/3I7jJyVczPQ?t=2700)).
5. For a characterful low-mid sound (keys, organ) that would drown under supersaws: duplicate it, distort the
   copy so it lives in the high mids and highs, and layer it in. He describes an organ distorted until it sat
   above roughly 800 Hz inside a chord stack (said, [2:02:40](https://youtu.be/3I7jJyVczPQ?t=7360)).
6. A brightened vocal needs a de-esser after it (said, [3:23:50](https://youtu.be/3I7jJyVczPQ?t=12230)).
7. Reference: he points to producers whose futuristic, non-supersaw leads are far brighter than the
   submission's, and says to compare against them.

## In Rohil's setup
Inside Serum 2, drive is `fx.distortion.drive` (see the unit's other keys with `rick-rubin serum params --group
fx`); compare settings with `rick-rubin serum ab "<preset>" --note C4 --try "fx.distortion.drive=..."`. In
Logic: the stock Exciter, or ANIMATE, on the lead; for step 5, a duplicate track with a high-pass and Logic's
distortion, since he owns no multiband distortion (what is lost: one plug-in doing it per band). Noveltech
Character is not installed; its preset number does not transfer.

## How to check it
`rick-rubin serum describe` before and after: the count of harmonics within 30 dB should rise and spectral tilt
should flatten, with the level in the body range unchanged. On a bounce, `rick-rubin spectrum <dir> lead_before.wav
lead_after.wav` shows more energy above about 4 kHz. Watch for harshness: this is one for Rohil's ears.

## Why it works
Brightness is harmonic content; a filter-closed or dark patch has little to boost. New upper harmonics also cut
through reverb and other layers, which is what brings the sound forward.
