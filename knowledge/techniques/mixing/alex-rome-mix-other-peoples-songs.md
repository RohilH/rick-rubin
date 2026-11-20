---
title: Practise mixing on songs that are not yours
topic: mixing
genres: [any]
source: Alex Rome — 10 Mixing Tips That Changed My Life (https://youtu.be/cU0tHoyJYjo?t=852)
status: untested
---
## What it is
His closing tip: mixing is a logical process, and it is easier to be logical about a song you have no feelings
about. On your own tracks you protect favourite parts and chase details no listener will hear.

## When to use it
As regular practice alongside his own tracks, and as a way to look at his own track: treat it as if someone else had
sent it.

## How
1. Mix other people's songs (said). He does not say where to get them; public multitracks or a friend's stems both
   work (ours).
2. Work on the mix as a whole, not on details (said, [14:55](https://youtu.be/cU0tHoyJYjo?t=895)).
3. Still mix your own music; just know that attachment makes you a worse judge of it (said).
4. To get the same distance on his own song (ours, inferred): bounce every track to audio, open a clean project with
   only the stems, and mix that. The synth settings are out of reach, so only mix decisions remain.

## In Rohil's setup
Stems from a finished idea: `rick-rubin logic bounce bounces/<track>.wav --tracks <track>` per part, then
`rick-rubin logic add-audio` into a fresh project that Rohil opens. For practice material that is not his,
`rick-rubin split <dir> refs/track.wav` gives six stems of any recording to rebalance. This also combines with the
cards on consolidating layers and mixing on another day.

## How to check it
On a stem mix of someone else's track there is a known answer: `rick-rubin reference compare <dir> my_mix.wav`
against the original release in the shelf. Loudness, tonal balance and width lines should approach it.

## Why it works
Without attachment, the only question left is whether the whole thing sounds balanced, which is the question a
listener asks (said in substance).
