---
title: Bass matching: make the bass from a copy of the chord sound, playing the chords' bottom notes
topic: sound-design
genres: [progressive house, bass house, tech house]
source: Alex Rome — 7 Useful Layering Techniques and Why They Work (https://youtu.be/u8ozR9cnCTU?t=140)
status: untested
---
## What it is
Instead of choosing a separate bass patch, duplicate the chord track, keep only the lowest note of each chord, and
drop it into the sub octave. The bass then has the same rhythm, the same envelope and the same movement as the chords,
so the two read as one heavy instrument.

## When to use it
A drop whose chords have a strong rhythm or modulation (his example is a wobbling chord pattern) and no bass yet, or a
bass that feels detached from the chords.

## How
1. Duplicate the chord track with its sound (said, [3:05](https://youtu.be/u8ozR9cnCTU?t=185)). Most chord sounds work
   as bass once converted (said).
2. In the copy, keep the bottom note of each chord so the rhythm is an exact replica (said; shown
   [3:25](https://youtu.be/u8ozR9cnCTU?t=205): the chord region above, a single-line region below it).
3. Remove what made it a chord sound: undo the low cut on its EQ, and take off every reverb, in the insert list and
   inside the synth. The bass must be dry (said, [3:37](https://youtu.be/u8ozR9cnCTU?t=217)).
4. Move it down by octaves until the analyzer shows it at 40 to 80 Hz (said,
   [3:58](https://youtu.be/u8ozR9cnCTU?t=238); Channel EQ open on the copy at
   [4:02](https://youtu.be/u8ozR9cnCTU?t=242)). See `../bass/alex-rome-c-bass-octave-by-the-analyzer-40-80hz.md`.
5. Compare the drop with and without it (said, [4:18](https://youtu.be/u8ozR9cnCTU?t=258)).
6. Not said, ours: a chord patch usually has unison and width. For the copy set unison to 1 and make it mono, or the
   sub will be wide and phasey.

## In Rohil's setup
If the chords are a Serum patch, make the bass version from it rather than by hand:
```
rick-rubin serum set "<chord preset>" osc_a.unison=1 osc_a.rand_phase=0 global.mono=on --fx-remove fx.reverb \
    --fx-remove fx.delay --fx-remove fx.chorus --save chords-as-bass --project <dir>
```
(`--fx-remove` only for units the patch has; `rick-rubin serum show "<preset>"` lists them.) In Logic: duplicate the
track, delete the upper notes, transpose the region down, bypass the reverb sends. In `song.py` the bass line is the
chord roots in the chords' rhythm, written out.

## How to check it
`rick-rubin serum describe chords-as-bass --note <root>`: most energy in the sub band, side energy 0 in the low band.
On a bounce of chords plus bass, `rick-rubin hits` should show the two tracks' onsets on the same steps, and
`rick-rubin width` low band side energy near zero.

## Why it works
Layers that start, move and stop together fuse into one sound for the ear; a bass with its own envelope is heard as a
second instrument (inferred from his "perfectly matching in rhythm" remark).
