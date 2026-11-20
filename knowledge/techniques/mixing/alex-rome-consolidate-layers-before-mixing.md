---
title: Consolidate layered tracks into one before the mix starts
topic: mixing
genres: [any, tech house, bass house, progressive house]
source: Alex Rome — 10 Mixing Tips That Changed My Life (https://youtu.be/cU0tHoyJYjo?t=619)
status: untested
---
## What it is
Session preparation: any group of tracks that together make one sound (three hat layers, a clap and its layer) is
reduced to a single track before mixing, so the mixer shows instruments, not ingredients.

## When to use it
Between the writing day and the mix day, once the layers' relative levels are right and nobody will want to change
one layer on its own.

## How
1. Look for tracks doing the same job at the same time. His drum beat has three hat tracks playing the same pattern
   (shown [11:08](https://youtu.be/cU0tHoyJYjo?t=668): "main hat", "side hat", "short hat").
2. Make them one: he reduces the three to a single hat track (said).
3. For layers that must stay as they are, select the regions and bounce them to one audio file: right-click, Bounce
   and Join, Bounce in Place, Ctrl-B (shown [11:35](https://youtu.be/cU0tHoyJYjo?t=695)), done on the clap and its
   layer.
4. Result: five tracks became two (said). Do the same across the whole song.
5. Layers are fine; unconsolidated layers are the problem (said).

## In Rohil's setup
`rick-rubin logic inspect` shows every strip with its regions and inserts: same-role, same-pattern tracks are easy
to list from it. The agent proposes the list; Rohil does the Bounce in Place himself, because session mode has no
region commands and never deletes tracks. Tell him to keep the originals muted or in a folder until the mix is
approved. Alternative that keeps layers editable: a summing track stack, mixed as one fader.

## How to check it
Bounce the group before and after consolidating (`rick-rubin logic bounce ... --tracks <the layers>` then the new
track) and run `rick-rubin compare <dir> before.wav after.wav`: they should measure the same. `logic inspect` should
show fewer strips.

## Why it works
Every extra fader is a decision and a place for level and phase to drift. One track per instrument makes balance, EQ
and bus compression act on the sound as it is heard (inferred; he argues from speed and clarity).
