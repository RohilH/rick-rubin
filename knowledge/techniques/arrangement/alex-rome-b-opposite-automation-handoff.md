---
title: Hand one lead over to the next with opposite automation: the old one drifts into reverb while the new one dries out
topic: arrangement
genres: [any, progressive house, tech house, bass house]
source: Alex Rome — My Insanely Simple System for Remixing Any Song (The 3-STEP FLIP) (https://youtu.be/bx8X7oiYhCg?t=610)
status: untested
---
## What it is
His way of making the intro, breakdown and drop of the remix flow: every part has one parameter moving, and the
outgoing lead and the incoming lead move in opposite directions, so one "flies away" as the other "flies in".

## When to use it
Any join where one main element is replaced by another: original vocal to a new hook, verse to drop. Also when a
16-bar section is correct but static.

## How
1. Rule first: everything in the song is moving at all times (said, [10:10](https://youtu.be/bx8X7oiYhCg?t=610)).
2. Outgoing lead (the original vocal): raise its reverb mix through the second half of the intro so it floats off
   (said, [10:30](https://youtu.be/bx8X7oiYhCg?t=630)). Shown at [10:45](https://youtu.be/bx8X7oiYhCg?t=645):
   ValhallaShimmer wet/dry 0.12 at bar 1, 0.25 at bar 9, about 0.52 to 0.56 through bars 17 to 24, back to 0.11
   at bar 25. Shimmer settings in the same frame: shift 12, feedback 0, diffusion 0.91, size 0.50, high cut 8 kHz.
3. Chords under it: automate the synth's cutoff so they open toward the join (said,
   [10:55](https://youtu.be/bx8X7oiYhCg?t=655)). Shown at [11:12](https://youtu.be/bx8X7oiYhCg?t=672): about
   220 Hz at bar 1, 196 Hz at bar 9, rising to 1087 Hz by the end of bar 16, then back near 270 Hz.
4. Incoming lead (the stutter): bring it in through a low-pass, and start its reverb high and take it away, the
   mirror of the vocal (said, [11:58](https://youtu.be/bx8X7oiYhCg?t=718),
   [12:23](https://youtu.be/bx8X7oiYhCg?t=743)). Shown at [12:35](https://youtu.be/bx8X7oiYhCg?t=755): reverb mix
   0.53 where its region starts, falling in a straight line to 0.08 at the region's end.
5. Borrow one drop element into the intro for groove, here the shaker (said,
   [11:38](https://youtu.be/bx8X7oiYhCg?t=698)).
6. Transition effects last, as seasoning (said, [12:43](https://youtu.be/bx8X7oiYhCg?t=763)).
7. When the original vocal returns later it comes back low-passed, "underwater" (said,
   [14:34](https://youtu.be/bx8X7oiYhCg?t=874); a high-cut automation lane on a second vocal track is visible at
   10:45).

## In Rohil's setup
rick-rubin cannot write automation into his Logic project, so the agent names the lane, the bars and the values
and Rohil draws them (A shows automation in Logic). Reverbs: Valhalla Supermassive or ChromaVerb with the Mix (or
the send level) automated; what is lost against Shimmer is the octave-up tail. The chords' cutoff: automate
Serum's Filter 1 Cutoff on a live Serum (`rick-rubin logic add-serum`), or Logic's Channel EQ high cut on a
rendered part. In a `song.py`, section `filter` and `volume` automation is written with `--automation`. For the
build that follows, see `arrangement/ryos-pg-build-by-filtering-everything-away.md`.

## How to check it
Bounce the four bars before the join and the four after (`rick-rubin logic bounce j.wav --bars 13-20`).
`rick-rubin spectrum` on the chords' first four bars against their last four: the last are brighter.
`rick-rubin width` on the vocal's last four bars: more side energy than its first four (reverb). The feel of the
hand-over is for Rohil's ears: with and without the automation.

## Why it works
Reverb pushes a sound back and a closed filter hides it, so moving the two leads in opposite directions swaps
which one is in front without either having to stop abruptly; a slow change the listener cannot name still reads
as the track going somewhere.
