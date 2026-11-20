---
title: Line layering: split a chordal melody into its lines and give each line its own sound
topic: sound-design
genres: [progressive house, any]
source: Alex Rome — 7 Useful Layering Techniques and Why They Work (https://youtu.be/u8ozR9cnCTU?t=13)
status: untested
---
## What it is
A melody that is really two or three lines stacked (top, middle, bottom) is taken apart, and each line is played by a
different sound, sometimes with its own rhythm. He shows it on a remake of deadmau5's "The Veldt" and credits the
approach to deadmau5, Avicii and Martin Garrix.

## When to use it
A main hook that plays as chords or as an inline melody and sounds like one flat block. It needs a part with at least
two distinct lines; a single-line lead has nothing to split.

## How
1. Look at the part in the piano roll and name its lines. In his remake: a held top line, a moving middle line that is
   the tune, and a bottom line more than an octave below (shown [1:48](https://youtu.be/u8ozR9cnCTU?t=108)).
2. Keep the whole part on the core sound.
3. Copy the top and bottom lines only to a second, slightly different synth, and let that layer arpeggiate in eighth
   notes over the held original (said, [0:52](https://youtu.be/u8ozR9cnCTU?t=52)).
4. Copy the middle line, the tune, to a third sound chosen for character (said,
   [1:13](https://youtu.be/u8ozR9cnCTU?t=73)).
5. Double the entire part on a piano (said, [1:33](https://youtu.be/u8ozR9cnCTU?t=93); track "SY Cozy Keys" shown at
   [1:12](https://youtu.be/u8ozR9cnCTU?t=72)).
6. The bass takes the bottom line, here as repeating eighth notes (said, [1:53](https://youtu.be/u8ozR9cnCTU?t=113)).
7. Which sound goes on which line is not specified beyond "slightly different" and "sounds pretty good"; the preset
   names are not visible.

## In Rohil's setup
In Logic: duplicate the track with its region, then delete the notes that are not that layer's line (select by pitch
range in the piano roll). In a `song.py` project write the lines as separate variables and give each its own `serum=`
track, so the top, middle and bottom are layers by construction. Starting sounds from existing cards: the filter pluck
for the arpeggiating layer (`alex-rome-filter-envelope-pluck.md`), a saw pad for the core
(`alex-rome-filtered-saw-pad.md`); choose the third by contrast (`ryos-layer-by-contrast.md`). Compare candidates for
each line with `rick-rubin serum ab` and on a bounce.

## How to check it
`rick-rubin spectrum <dir>` on bounces of each layer alone: the layers should peak in different regions (bottom line
low-mid, tune mid, top line high) instead of stacking on one. `rick-rubin width` on the stack: keep the tune's layer
the most centred. Then an audition for Rohil: core alone against the full stack.

## Why it works
Each line gets a timbre that suits its register, so the ear can follow three things at once, and no single synth has
to sound good across three octaves (inferred; he says it gives a unique and full sound).
