---
title: A vocal stutter lead: a sustained vocal with reverb, chopped by a trance gate
topic: sound-design
genres: [progressive house, tech house, bass house]
source: Alex Rome — 5 Melody Styles Every Hit Song Uses (https://youtu.be/cjyEdyEWXbQ?t=1172)
status: untested
---
## What it is
A lead made from a held vocal note or phrase instead of a synth. Reverb turns the vocal into a continuous tone and a
step gate cuts that tone into a rhythm, so the rhythm is the hook. He offers it as the currently more popular
alternative to a synth lead.

## When to use it
A drop where synth leads sound dated or fight the chords; tracks that already have a vocal sample whose tone can be
reused as the lead.

## How
1. Take a vocal sample with a long note or a smooth phrase and make it sustain (said,
   [19:54](https://youtu.be/cjyEdyEWXbQ?t=1194)).
2. Add reverb so the gaps in the vocal are filled (said, 19:54).
3. Put a trance gate after the reverb, so the tail is gated too (order shown by what is heard; inferred).
4. Shown at [20:12](https://youtu.be/cjyEdyEWXbQ?t=1212), Kilohearts Trance Gate (free): pattern 1 of 8, 16 steps,
   resolution 1/32, mix 78 %. The pattern has runs of open steps of different lengths with single closed steps between
   them, so the chops are uneven, not a steady tremolo.
5. Mix below 100 % lets some ungated signal through, which softens the cuts (shown: 78 %).
6. Tune the vocal to the track first (ours; the sample names on screen carry their keys).
7. The gate's attack, decay, sustain and release knobs are not readable.
8. Related: `alex-rome-b-vocal-phrase-to-stutter-lead.md` is his granular version, playable from the keyboard.

## In Rohil's setup
He does not own a step gate. Options, nearest first: (a) Kilohearts Trance Gate is free, if he wants to install it;
(b) Logic's Tremolo with a square shape, synced to 1/16 or 1/8, depth near 100 %: a regular chop only, no pattern; (c)
cut the bounced, reverbed vocal into slices on the grid and delete the ones that should be silent, which gives the
uneven pattern exactly and is how a `song.py` part would be written (the vocal as a sample, triggered on chosen
steps). For (c): `rick-rubin logic bounce bounces/vox_wet.wav --tracks Vocal`, then edit by hand. Before any of it:
`rick-rubin notes <dir> <vocal>` for pitch and key fit, `rick-rubin transcribe` to see where the syllables land.

## How to check it
`rick-rubin hits <dir> bounces/stutter.wav` (its `--grid` option sets the step size): the open and closed steps should
show as a repeating level pattern, with closed steps at least 10 dB down. `rick-rubin width`: the reverb makes it
wide, so keep the low band mono and low-cut it. Against the drop, `reference compare`: the lead's band (1 to 5 kHz)
inside the references.

## Why it works
A voice has a richer, less static tone than a saw, and gating a sustained sound imposes a precise rhythm on it without
the note attacks of a played part (inferred).
