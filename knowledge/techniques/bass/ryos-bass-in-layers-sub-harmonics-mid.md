---
title: Build the bass in layers so it has both sub weight and harmonics, under a kick it does not swallow
topic: bass
genres: [progressive house, bass house, tech house, any]
source: RYOS — Giving Feedback On YOUR Tracks! (https://youtu.be/3I7jJyVczPQ?t=1663)
status: untested
---
## What it is
Separate bass layers, each with one job (sub, sometimes a low-mid layer, the aggressive mid bass), balanced so
the listener feels the kick's weight and then the bass's weight as a push and pull.

## When to use it
A drop that sounds powerful but does not feel powerful; a bass with a hole in it; a bass that buries the kick.
Low-end notes of this kind came up in eight tracks.

## How
1. Split the bass: a sub on its own track, the mid-range bass on another, and sometimes a low-mid layer between
   them. One layer asked to do everything cannot give warmth and bite together (said,
   [28:01](https://youtu.be/3I7jJyVczPQ?t=1681)).
2. Check where the weight is. A bass that rings at 80 to 120 Hz sounds strong because of its harmonics but lacks
   the rumble; he wants to feel about 60 Hz as well (said, [51:10](https://youtu.be/3I7jJyVczPQ?t=3070)).
3. Check the opposite fault: a good sub with nothing above it leaves a hole. Add harmonics to the sub with a
   bass enhancer, or add a layer with a ringing, harmonic quality (said,
   [2:50:05](https://youtu.be/3I7jJyVczPQ?t=10205)).
4. Kick and sub need not match; each has its own weight (said, [51:30](https://youtu.be/3I7jJyVczPQ?t=3090)).
5. Sidechain the bass so it really dips out when the kick hits, without the whole mix sounding pumpy; if the
   groove does not bounce, the sidechain is too shallow (said, [38:01](https://youtu.be/3I7jJyVczPQ?t=2281),
   [1:16:02](https://youtu.be/3I7jJyVczPQ?t=4562)).
6. A bass that is a harmonic sub, not a top bass, is tucked under the kick: bring it down (he says at least
   3 dB in one case) before any EQ (said, [2:38:32](https://youtu.be/3I7jJyVczPQ?t=9512)).
7. Judge it on speakers or good headphones: it is a feeling (said, [28:31](https://youtu.be/3I7jJyVczPQ?t=1711)).

## In Rohil's setup
Three Serum 2 tracks, or Serum's own sub oscillator for the sub (`sub.on`; see `rick-rubin serum params --group
sub`). Harmonics on the sub: drive inside the patch (`fx.distortion.drive`) or Logic's Overdrive on a duplicate;
he names a bass enhancer Rohil does not own, and nothing is lost by saturating instead. Kick-keyed ducking:
`rick-rubin logic insert Bass Compressor Threshold=-28 Ratio=4 --sidechain Kick` (the repo's default pump
numbers, not his), or `rick-rubin logic insert Bass "Kickstart 2" Mix=0.8`. BASSROOM can compare the low-end
balance with a reference track.

## How to check it
`rick-rubin spectrum <dir> sub.wav midbass.wav kick.wav` on bounces: the bass group should show energy at its
fundamental (near 50 to 60 Hz for most house keys) and a continuous run of harmonics up into the mids, with no
gap. In `rick-rubin reference compare`, the low-end pump figure (off-beat against kick) should sit inside the
references' range, and the low band should stay centred in `rick-rubin width`.

## Why it works
Small speakers reproduce only the harmonics and big systems reproduce the fundamental; a bass needs both to
translate. Separate layers let each be levelled, saturated and ducked on its own.
