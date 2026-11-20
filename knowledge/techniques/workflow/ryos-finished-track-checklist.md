---
title: Finished-track checklist according to Ryos (what he checks, in the order he raises it)
topic: workflow
genres: [progressive house, tech house, bass house, any]
source: RYOS — Giving Feedback On YOUR Tracks! (https://youtu.be/3I7jJyVczPQ?t=631)
status: untested
---
## What it is
The questions Ryos asks of a submitted track, in roughly the order he raised them across one stream. The count
after each is how many of the 12 criticised tracks failed it.

## When to use it
Before showing a track to anyone, and whenever a track is "correct" but does not sound finished.

## How
1. **Look at the waveform before pressing play.** Tiny means unmastered; a brick means crushed. Either way he
   says so first (3, plus 2 in passing; said, [10:31](https://youtu.be/3I7jJyVczPQ?t=631)).
2. **Basics that disqualify.** Every part in the same key, bass following the chords; everything on a 4/4 grid;
   the track gets to its point quickly (key 1, grid 1, structure 3; [1:31:45](https://youtu.be/3I7jJyVczPQ?t=5505)).
3. **Is the star at the front?** Usually the lead. Bright enough, thick enough around 300 Hz, wide with a centre
   layer, not washed in reverb (10; [1:06:50](https://youtu.be/3I7jJyVczPQ?t=4010)).
4. **Is the bass under the star?** Fader first ("at least 3 dB" down in one case, said), then 200 to 500 Hz out of
   the bass and chord groups (5; [2:38:05](https://youtu.be/3I7jJyVczPQ?t=9485)).
5. **Kick and bass.** Right kick for the genre, thick in solo; sub weight near 60 Hz and harmonics above it;
   the bass dips out when the kick hits (8; [51:01](https://youtu.be/3I7jJyVczPQ?t=3061)).
6. **Enough layers?** A mid-range driver between bass and lead, an atmosphere bed, a little sparkle on top (5;
   [2:19:01](https://youtu.be/3I7jJyVczPQ?t=8341)).
7. **Does it develop?** Something significant every eight bars; the second half of the drop has more than the
   first; drums audible and changing (4; [2:27:50](https://youtu.be/3I7jJyVczPQ?t=8870)).
8. **Transitions and fills.** A reverse into the section, a hard cut under a vocal phrase, risers that fade in,
   effects sized to the genre (6; [37:00](https://youtu.be/3I7jJyVczPQ?t=2220)).
9. **The break.** Piano or keys compressed enough to sit on the bass; chords no busier than needed; vocal bright,
   wide and de-essed (5 for compression, 6 for notes; [19:33](https://youtu.be/3I7jJyVczPQ?t=1173)).
10. **Does every sound belong to this mood and genre?** (6; [21:30](https://youtu.be/3I7jJyVczPQ?t=1290)).
11. **Picture a DJ playing it.** Where do they mix in, and what does the room get when the break arrives?
    ([3:01:40](https://youtu.be/3I7jJyVczPQ?t=10900)).

## In Rohil's setup
Bounce the drop and the break (`rick-rubin logic bounce bounces/drop.wav --bars 33-48`), then answer each line
with a measurement where one exists: step 1 and 7 with `rick-rubin reference compare <dir>` (loudness, crest,
texture changes per minute, share of near-identical blocks); step 2 with `rick-rubin notes <dir> <stem>` per
melodic stem; steps 3 to 5 with `rick-rubin spectrum <dir> lead.wav bass.wav kick.wav` and `rick-rubin width
<dir> lead.wav --png`. Steps 8 to 11 have no measurement: they are for Rohil's ears (`rick-rubin verdict`).

## How to check it
Every line answered with a number or a verdict, not "looks fine". The numbers to move are on the other cards.

## Why it works
The order runs from what a listener notices in the first second (level, key, the lead) to what only shows on a
second listen, so the cheapest, largest faults are fixed before the detail work.
