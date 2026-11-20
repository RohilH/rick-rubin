---
title: Layer two hats, one for the click and one for the body, and move the closed hat slightly off the grid
topic: drums
genres: [any, progressive house, tech house, bass house]
source: Alex Rome — My Insanely Simple System for Remixing Any Song (The 3-STEP FLIP) (https://youtu.be/bx8X7oiYhCg?t=379)
status: untested
---
## What it is
Two small hat habits he uses in the remix and in the house-song video: the main hat is two samples with different
jobs, and the closed hat is deliberately not on the grid.

## When to use it
The offbeat hat sounds thin or has to be pushed loud to be heard; the top end feels stiff.

## How
1. Main hat as two layers on the same hits: one chosen for its transient, one for what he calls its "essence",
   the body and tail (said, [6:19](https://youtu.be/bx8X7oiYhCg?t=379)). Shown at
   [6:40](https://youtu.be/bx8X7oiYhCg?t=400): a very short one-shot stacked on a longer hat sample, hit for hit.
2. The same idea on the open hat in the house video: layered, it becomes more present without being turned up
   (said, [9:14](https://youtu.be/kSXHTJJ7D34?t=554)).
3. The closed hat is placed off the grid on purpose, which he says adds swing (said,
   [9:14](https://youtu.be/kSXHTJJ7D34?t=554)). Shown at [9:30](https://youtu.be/kSXHTJJ7D34?t=570): its region
   starts a little after a 16th line, roughly a fifth of a 16th late (he may be mid-drag in the frame, so treat
   the amount as approximate). The two layered open hats above it sit exactly on the offbeat.
4. Choose every drum for the mood of the track: for a deeper track a muffled kick and a darker clap (said,
   [9:14](https://youtu.be/kSXHTJJ7D34?t=554)); in the deep-house demo a rimshot instead of a clap (said,
   [7:18](https://youtu.be/ZkRds6iTfhQ?t=438)); in the remix a garage-style clap (said,
   [6:42](https://youtu.be/bx8X7oiYhCg?t=402)).

## In Rohil's setup
Shortlist several hats for each job from Splice and compare them (`rick-rubin audition <dir> <files...>`,
PREFERENCES §3). In Logic, two audio tracks in a track stack, or two pads in Drum Machine Designer triggered
together. The nudge: the region's Delay parameter in the inspector, late by 10 to 25 ms as a first try, compared with
on-grid and early (he says no number; the frame suggests about 25 ms at his tempo). When the balance is settled, bounce the pair in place to one
track (`mixing/alex-rome-consolidate-layers-before-mixing.md`). Related:
`drums/moonboy-clap-slightly-before-the-kick.md`, and for the quiet percussion loop he hides behind this kit in
the same video, `sound-design/alex-rome-c-hidden-percussion-loop-under-the-music.md`.

## How to check it
`rick-rubin spectrum <dir> hat_single.wav hat_layered.wav` on bounces: the layered hat has energy in two regions
(the click high up, the body below it) at a similar peak level. `rick-rubin hits <dir> closed_hat.wav`: every hit
the same few milliseconds from the grid. Whether it swings is for his ears.

## Why it works
One sample rarely has both a sharp front and a full tail; splitting the jobs lets each be chosen and balanced
alone. A constant small offset against a kick that is on the grid is the simplest form of swing.
