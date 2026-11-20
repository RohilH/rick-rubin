---
title: Chill loop, VI–i–VII–i with a long VII, a held top note and a tonic drone
topic: harmony
genres: [progressive house, any]
source: Alex Rome — 10 Chord Patterns for 10 Different Emotions (https://youtu.be/_yw85rAb6cw?t=592)
status: untested
---
## What it is
A gentle loop that circles the minor tonic, where the relaxed feeling comes mostly from the sound (a soft piano), a
drone on the tonic and one note that stays on top of every chord. He says almost any progression is chill if the
sound is.

## When to use it
Intros, outros, and the quiet first half of a breakdown; anywhere the track should breathe.

## How
1. Natural minor; degrees 6, 1, 7, 1 (said). The captions give C minor, but the screen shows C# minor: A, C#m, B,
   C#m (overlay "A major" at [10:25](https://youtu.be/_yw85rAb6cw?t=625); notes read against the piano roll's C
   labels at [10:56](https://youtu.be/_yw85rAb6cw?t=656)).
2. Stretch the VII: lengths in the proportion 2 : 2 : 3 : 1 (shown [10:56](https://youtu.be/_yw85rAb6cw?t=656); the
   bar ruler is out of frame).
3. Revoice so the same note is on top of every chord: scale degree 3 (shown
   [10:56](https://youtu.be/_yw85rAb6cw?t=656): E is the fifth of VI, the third of i, and is left ringing over VII
   as a suspended fourth). Roots are doubled in octaves underneath.
4. Add a drone on the tonic from a separate atmospheric sound (said, [10:40](https://youtu.be/_yw85rAb6cw?t=640)).
5. A soft piano; then the same notes on a synth with a light beat to show it survives a change of sound (said,
   [11:00](https://youtu.be/_yw85rAb6cw?t=660)).
6. To vary it (ours): let the top note move only once per loop; replace the last i with VI to avoid closing.

## In Rohil's setup
The drone is its own long region on its own track, low in level, high-passed so it does not sit on the bass: Channel
EQ low cut, then a reverb send (`rick-rubin logic send <drone> 1 -12`). For a synth version, the filtered saw pad
card with a slow attack. Supermassive is the obvious tail for the piano.

## How to check it
`rick-rubin score <dir> --tracks <chords>`: the highest pitch should be the same in every bar. On a bounce,
`rick-rubin spectrum` of the drone alone: nothing below about 150 Hz.

## Why it works
A fixed top note and a fixed drone mean two of the things the ear tracks never move, so the chord changes feel like
light shifting rather than events. No chord in the loop pulls hard anywhere (inferred).
