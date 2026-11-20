---
title: All-major IV–V–I voiced as bare roots under a tonic pedal
topic: harmony
genres: [progressive house, any]
source: Alex Rome — 10 Chord Patterns for 10 Different Emotions (https://youtu.be/_yw85rAb6cw?t=680)
status: untested
---
## What it is
His favourite: the three major chords of a major key, four, five, one, with no minor chord anywhere. He then removes
the thirds and fifths altogether and lets a held tonic and octave roots imply the chords.

## When to use it
The brightest moment of a track: a final breakdown, a vocal hook, an outro that should feel like arrival.

## How
1. Major scale; IV, V, I (said; shown [11:53](https://youtu.be/_yw85rAb6cw?t=713) in D major: G, A, D).
2. Rhythm over two bars: IV for two and a half beats, V for one and a half, I for the whole second bar, so V pushes
   in early and I lands on the bar line (shown [11:53](https://youtu.be/_yw85rAb6cw?t=713) and
   [12:16](https://youtu.be/_yw85rAb6cw?t=736) on Logic's ruler).
3. Strip each chord to its root, doubled an octave up (said: remove third and fifth, bass notes up an octave; shown
   [12:16](https://youtu.be/_yw85rAb6cw?t=736)).
4. Hold the tonic above as a pedal, struck again with each chord, and double it (said; shown
   [12:16](https://youtu.be/_yw85rAb6cw?t=736): D on top).
5. What that leaves (inferred): the pedal is the fifth over IV, a suspended fourth over V, and the root over I. The
   V has no third, so its tension is the suspension, and it resolves when the bass reaches I.
6. He then runs the part through a granular effect, records the result, chops it, and adds vocals, a beat and a bass
   (said; Output Portal shown on the strip at [12:32](https://youtu.be/_yw85rAb6cw?t=752)).
7. To vary it (ours): give the thirds to a lead or vocal instead of the chords; end a phrase on V for a lift.

## In Rohil's setup
No Portal here. Nearest: bounce the part (`rick-rubin logic bounce bounces/chords.wav --tracks <chords>`), then
mangle the audio with what he owns: Supermassive at high feedback, or the bounce loaded by hand into Serum 2's
granular oscillator (no rick-rubin command for that). Chop the result in Logic by hand. Lost: Portal's grain
presets.

## How to check it
`rick-rubin score <dir> --tracks <chords>`: only two pitch classes per chord (root and tonic). Bounce the bare
version against full triads; the bare one should leave more room for the vocal (Rohil's ear, then `verdict`).

## Why it works
Four to five to one is the plainest cadence in major, and with no minor chord there is nothing to shade it. Leaving
the thirds out keeps it open and modern instead of nursery-bright (inferred).
