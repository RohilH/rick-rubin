---
title: Bar map of a progressive house demo: 8 bars chords, 8 bars melody, 8 bars build, 32-bar drop
topic: arrangement
genres: [progressive house]
source: RYOS — Making Beautiful Progressive House | Studio Time with Ryos EP. 50 (https://youtu.be/WnZ7GN1tpek?t=2060)
status: untested
---
## What it is
What enters in which bar in the finished demo, read from the playlist at the end of the video. It is a demo
layout (break first, one drop), not a full DJ arrangement with intro and outro.

## When to use it
Sketching a melodic idea into a shape that can be judged: enough to hear the break, the build and the drop.

## How
All shown at [34:20](https://youtu.be/WnZ7GN1tpek?t=2060) and [35:35](https://youtu.be/WnZ7GN1tpek?t=2135) unless marked.
1. Bars 1 to 8: piano chords alone (the 4-bar progression twice) over the drone. An atmosphere swell starts
   around bar 3. A reverse synth shot leads into bar 9.
2. Bars 9 to 16: the piano adds the melody; the simple break bass enters with one root per bar; a hat loop
   starts here so the section has pulse (said, [33:31](https://youtu.be/WnZ7GN1tpek?t=2011)). Second swell from
   about bar 11; second reverse shot into bar 17.
3. Bars 17 to 24: the build. A pad track and the analog drone line start at 17 and run on through the drop
   (that the pad track, named "Flutter Pad", is the gated pad is our inference);
   the lead stack plays the melody behind a filter; kick and clap repeat; the snare roll comes in about
   halfway; the piano and break bass are filtered out (see `ryos-pg-build-by-filtering-everything-away.md`).
4. Bar 25: the drop. Lead stack, dance piano, chord synth, four bass layers with the pitch-bend clip repeating
   every 4 bars, kick, rides, claps, shaker, top loop.
5. The drop runs to bar 57: 32 bars, with a short fill at the end of every fourth bar and a clap-fill clip
   repeating every 8 (shown, 35:35). The melody repeats unchanged; what changes between blocks in the
   finished track is left for later (said, [34:13](https://youtu.be/WnZ7GN1tpek?t=2053)).
6. Markers are used as a to-do list on the timeline ("add dance piano"; said,
   [22:05](https://youtu.be/WnZ7GN1tpek?t=1325)).

## In Rohil's setup
In `song.py` these are four sections of 8, 8, 8 and 32 bars; the sections and every part in them are written
for the song, this card only gives the proportions one producer used. A release needs more: a DJ intro and
outro and a second break and drop (`skill/genres.md` has the full house form), and his rule of something
significant every eight bars (`ryos-something-significant-every-eight-bars.md`) applies to the 32-bar drop. In
an open Logic project, `rick-rubin logic inspect` lists the regions per track but not their positions, so
check the layout in Logic's window.

## How to check it
`rick-rubin score <dir>` prints the sections and what plays in each. On a capture, `rick-rubin reference
compare` reports the share of near-identical 2-bar blocks and texture changes per minute: a 32-bar drop built
by copying 8 bars four times will show too many identical blocks, which is the next thing to fix.

## Why it works
Eight-bar phrases match how DJs and dancers count. Starting on the break puts the idea's emotional core first,
which is the right order for deciding whether a demo deserves to be finished.
