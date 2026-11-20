---
title: Make a progressive drop bounce: shorter lead notes, a bass in the lead's rhythm with octave jumps, chords every bar
topic: bass
genres: [progressive house, bass house]
source: RYOS — Can I Fix My Subscribers Music? (https://youtu.be/23NY1XxOlbA?t=129)
status: untested
---
## What it is
How Ryos turned a subscriber's traditional, sustained progressive house drop into a "hybrid prog" drop with
bounce, keeping the same melody. Three note-level changes, no new material.

## When to use it
A drop whose melody is good but which feels slow or flat next to its break; a first step from progressive
house writing towards bass house energy.

## How
1. Shorten the lead's notes so there is air between them, and tidy a few pitches; the melody stays (said,
   [2:09](https://youtu.be/23NY1XxOlbA?t=129); short notes shown, [2:02](https://youtu.be/23NY1XxOlbA?t=122)).
2. Bass: copy the lead's rhythm and put every note on the chord's root, G under the first chord, D sharp under
   the next (said, [3:11](https://youtu.be/23NY1XxOlbA?t=191); shown, [3:35](https://youtu.be/23NY1XxOlbA?t=215)).
   This step alone is `bass/ryos-pg-bass-copies-melody-rhythm-with-slides.md`.
3. Move some of those bass notes up an octave: "spicier and bouncier" (said,
   [3:53](https://youtu.be/23NY1XxOlbA?t=233)). Which notes jump is chosen by ear.
4. Mid bass sound: a Serum patch of his named as a lead that "could be a bass", two saw-type oscillators
   through a High 12 filter (shown, [3:52](https://youtu.be/23NY1XxOlbA?t=232)). A sub goes on its own track.
5. Bass group: a little compression and drive (FocusOne), then Kickstart 2 (said,
   [4:13](https://youtu.be/23NY1XxOlbA?t=253); shown, [4:24](https://youtu.be/23NY1XxOlbA?t=264)).
6. Make the bass root change every bar instead of every two bars, so the pace feels faster (said,
   [4:13](https://youtu.be/23NY1XxOlbA?t=253)).

## In Rohil's setup
In a `song.py` the agent writes the bass by hand from the lead's rhythm and chooses the jumps for this song.
Mid bass in Serum 2: start from a bright saw lead, play it two octaves down, and set `global.mono=on` so
jumps do not overlap; compare candidates with `rick-rubin serum ab`. Sub: a sine on its own track. Bass
group in Logic: Compressor and Overdrive, then `rick-rubin logic insert "Bass Group" "Kickstart 2" Mix=1.0`
(the repo's own advice for a bass is a kick-keyed Compressor; try both and bounce).

## How to check it
`rick-rubin hits <dir> --tracks Lead Bass --bars A-B`: lead and bass sound on the same 16th steps, with
silent steps between them where the old version held notes. `rick-rubin score` shows the root changing each
bar. `rick-rubin reference compare <dir>`: punch and pump figures move towards the bass house references.

## Why it works
Gaps let the kick and the sidechain be heard, an octave jump is movement without a new note, and twice as
many chord changes per phrase feels like a faster track at the same tempo.
