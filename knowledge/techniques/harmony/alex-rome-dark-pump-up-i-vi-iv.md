---
title: Dark pump-up loop, tonic for half the phrase then VI and iv, thirds doubled
topic: harmony
genres: [bass house, tech house, progressive house]
source: Alex Rome — 10 Chord Patterns for 10 Different Emotions (https://youtu.be/_yw85rAb6cw?t=434)
status: untested
---
## What it is
A four-bar loop that sits on the minor tonic for two bars, drops to VI for one and ends on the minor iv. It starts
and ends on minor chords, which he names as the way to get a "really deep minor sound" with some aggression.

## When to use it
Driving, darker drops and builds: gym-track energy. The long tonic leaves space for a bassline and a vocal chop.

## How
1. Natural minor; i for bars 1 and 2, VI for bar 3, iv for bar 4 (said; shown
   [7:42](https://youtu.be/_yw85rAb6cw?t=462) in G minor: Gm, Eb, Cm).
2. Voice them so neighbours share notes: every chord here has two notes in common with the one before (shown
   [7:42](https://youtu.be/_yw85rAb6cw?t=462): G and Bb stay through bar 3, G and Eb through bar 4).
3. Use a darker synth sound (said; Sylenth1 shown, no settings).
4. Lift the thirds an octave, then double that third on a second synth sound an octave higher (said; shown
   [8:12](https://youtu.be/_yw85rAb6cw?t=492): the second layer plays only Bb, then G, then Eb). Doubling any chord
   tone brings that tone forward (said).
5. Bass, drums and a vocal on top (said, [8:20](https://youtu.be/_yw85rAb6cw?t=500)).
6. To vary it (ours): swap the order of the last two bars; cut the chord to short stabs on the off-beats for tech
   house; filter the doubled layer in over 16 bars so the minor colour grows.

## In Rohil's setup
The doubled third is a separate track with its own patch: something thinner and brighter than the chord sound, so it
reads as a top line. Sidechain the chords, not necessarily the doubled line: `rick-rubin logic insert <chords>
"Kickstart 2" Mix=0.6`.

## How to check it
`rick-rubin score <dir> --tracks <chords> <double>`: the doubled track should hold exactly one note per chord and it
should be that chord's third. Bounce with the doubled layer muted and unmuted for Rohil.

## Why it works
The third is the note that says "minor", so doubling it makes the mode louder. Holding the tonic for half the loop
gives insistence, and ending on iv leans back into the tonic so the loop restarts with weight (inferred).
