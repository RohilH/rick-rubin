---
title: A drop bass that plays the chord roots in the melody's rhythm, with pitch-bend slides into the changes
topic: bass
genres: [progressive house]
source: RYOS — Making Beautiful Progressive House | Studio Time with Ryos EP. 50 (https://youtu.be/WnZ7GN1tpek?t=955)
status: untested
---
## What it is
The drop bass does not hold notes and does not play offbeats. It repeats each chord's root in exactly the
rhythm of the lead melody, and a pitch-bend curve makes it slide into some chord changes.

## When to use it
A progressive house drop where the lead melody is rhythmic. He prefers a rhythmic bass to a sustained one
(said, [16:00](https://youtu.be/WnZ7GN1tpek?t=960)).

## How
1. Copy the melody's MIDI to the bass track and flatten every note to the root of the current chord (said,
   [16:16](https://youtu.be/WnZ7GN1tpek?t=976)). Shown at [16:30](https://youtu.be/WnZ7GN1tpek?t=990): G, B, D, A
   around G1 to D2 in Logic's naming (98 to 147 Hz), under the ghosted melody whose onsets it matches.
2. Because the melody anticipates, the bass changes root where the melody does: the B starts on the last eighth
   of bar 1, not on bar 2 (shown, 16:30).
3. Add a pitch slide with pitch-bend automation, not with new notes (said,
   [16:44](https://youtu.be/WnZ7GN1tpek?t=1004)). Shown at [16:52](https://youtu.be/WnZ7GN1tpek?t=1012): the bend
   ramps up over roughly the last beat before the third chord and snaps back at the bar line, and ramps down at
   the end of the fourth bar toward the repeat. The slides follow the direction the root is about to move.
   The bend depth is not readable.
4. Every other bass layer (the thin mid layer, the reese) gets the same rhythm; the patterns under the bass in
   the playlist are copies (shown, [22:16](https://youtu.be/WnZ7GN1tpek?t=1336)).
5. The break uses a different, simpler bass: one sustained root per bar (said,
   [4:58](https://youtu.be/WnZ7GN1tpek?t=298)).

## In Rohil's setup
In `song.py`, write the bass pattern on the melody's onsets (see `ryos-pg-two-rhythm-cells-melody.md`) with the
roots of this song's chords; compare it against an offbeat version and a sustained version on a bounce
(PREFERENCES §3). Slides: rick-rubin cannot write automation into a Logic project, so either draw pitch bend in
Logic's piano roll by hand, with the patch's range set by `global.bend_up` and `global.bend_down`, or build the
slide into the patch with `global.mono=on global.legato=on global.glide_ms=80` and overlap the last note of a
bar into the first note of the next (the glide time is our guess, to be tuned by ear).

## How to check it
`rick-rubin hits <dir> lead.wav` and `rick-rubin hits <dir> bass.wav` on bounces: the onset positions should
match. `rick-rubin notes <dir> bass.wav --fmin 30` should show the roots in the right octave, with notes that
start off-pitch and settle where a slide was drawn. The bass lands on beats 1 and 3 with the kick, so check on
a bounce of kick and bass that the duck covers those hits. The slide depth is for Rohil's ears.

## Why it works
Bass and lead hitting together make the drop read as one big instrument, which is the progressive house sound.
A slide into a change adds movement in the low end without adding notes that would clutter it.
