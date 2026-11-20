---
title: Build a lead stack with one centred, thick layer first, then widen the rest
topic: sound-design
genres: [progressive house, any]
source: RYOS — Giving Feedback On YOUR Tracks! (https://youtu.be/3I7jJyVczPQ?t=4261)
status: untested
---
## What it is
A "wall of sound" lead is several layers with separate jobs: one that is strong down the middle, others that are
wide. Width is added to the group only after the centre layer exists.

## When to use it
A lead that is wide but soft and far away ("mush"), or thin and "chintzy". Also for a vocal in a break: whatever
is the star of the section should be wide.

## How
1. Solo each layer and name its job. One must sit mostly in the centre of the stereo field. It need not be
   strictly mono, but its energy should be in the middle (said, [1:12:30](https://youtu.be/3I7jJyVczPQ?t=4350)).
2. That centre layer, and the lead group as a whole, need body: he says about 300 Hz is a safe place to look,
   never sub frequencies; progressive house wants less of it than big room (said,
   [1:13:40](https://youtu.be/3I7jJyVczPQ?t=4420)). A lead thinned by over-cutting gets its low mids back, or a
   "meaty" centre layer added under it (said, [2:54:40](https://youtu.be/3I7jJyVczPQ?t=10480)).
3. Only when step 1 passes, put a stereo imager on the lead group and widen (said,
   [1:11:40](https://youtu.be/3I7jJyVczPQ?t=4300)).
4. With the leads soloed, watch a correlation meter on the master while widening. Aim to hover around zero; a
   momentary dip below is fine, living below zero is out of phase (said,
   [1:12:00](https://youtu.be/3I7jJyVczPQ?t=4320)).
5. To thicken a thin lead, prefer saturation in the body range to a plain EQ boost; it generates harmonics instead
   of only raising what is there (said, [2:42:31](https://youtu.be/3I7jJyVczPQ?t=9751)).
6. Apply the same idea to a break vocal: widen it, keep the centre strong, stay in phase (said,
   [2:24:40](https://youtu.be/3I7jJyVczPQ?t=8680)).

## In Rohil's setup
Layers are separate Serum 2 tracks. Centre layer: one voice, no detune (`rick-rubin serum set "<preset>"
osc_a.unison=1 --save lead-centre --project <dir>`). Wide layers: more voices and detune (`osc_a.unison=7
osc_a.detune=0.2`, then adjust by `serum ab`). Sum them to one bus by hand, and put Ozone Imager 2 (it has a
correlation meter and a vectorscope) or STEREOVAULT on that bus. He names a different imager; nothing is lost.

## How to check it
`rick-rubin serum describe` on each layer: the centre layer's side percentage should be low in every band, the
wide layers' high above the low mids. `rick-rubin width <dir> bounces/leads.wav --png` on the soloed group:
correlation over time stays at or above about zero, and the low band stays centred. The group's energy around
300 Hz in `rick-rubin spectrum` should not be lower than the chords'.

## Why it works
Wide signals lose level and definition when summed and carry little punch; a centred layer gives the ear a
fixed point, so the wide layers read as size instead of blur.
