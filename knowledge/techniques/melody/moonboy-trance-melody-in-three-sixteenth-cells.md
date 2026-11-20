---
title: A trance-style melody from one root note repeated every three 16ths, with a second note answering it
topic: melody
genres: [bass house, progressive house]
source: MOONBOY — HOW TO BASS HOUSE (Knock2, Skrillex, Porter Robinson) (https://youtu.be/3-0JCDyiPaw?t=175)
status: untested
---
## What it is
A way to get a euphoric plucked melody without knowing the melody in advance: fix the rhythm first (a low
note and a high note in cells of three 16ths), loop it for eight bars, then move the high notes to make the
tune and the low notes to make the bass movement.

## When to use it
For the breakdown or intro of a bass house track that needs emotion, and directly for progressive house,
where this rolling pluck figure is the main texture. It needs a pluck sound with delay to work.

## How
1. Choose the key and switch scale highlighting on; he uses F# minor (said and shown,
   [3:15](https://youtu.be/3-0JCDyiPaw?t=195)).
2. Root note, one 16th long, every three 16ths from the downbeat: steps 1, 4, 7, 10, 13, 16 of the bar, then
   start again on the next downbeat (shown at [3:06](https://youtu.be/3-0JCDyiPaw?t=186), F#2; he calls it a
   triplet pattern, but it is straight 16ths grouped in threes).
3. A second, higher note on the 16th right after each root, so every cell is low, high, rest (shown; E3
   over F#2, the seventh of the scale; he says the fifth or seventh, whatever fits the key).
4. Repeat the bar and duplicate to eight bars (said).
5. Now move the top notes around inside the scale until a tune appears; they are the melody (said,
   [3:21](https://youtu.be/3-0JCDyiPaw?t=201)). His first bars go E, E, E, F#, F#.
6. Move the bottom notes in longer blocks to make a progression; his climb is F# for two bars, G# for one,
   then A and C# (shown at [3:33](https://youtu.be/3-0JCDyiPaw?t=213)).
7. An existing melody can be poured into the same rhythm (said).
8. Under it, a pad or bass holds one long note per chord: his are D, E, then F# (shown at
   [3:56](https://youtu.be/3-0JCDyiPaw?t=236)).

## In Rohil's setup
Write it in `song.py` as two voices on one pluck track (the rhythm is the method; the pitches are written
for the track, in his key). In Logic's piano roll, Scale Quantize or the key signature guides the notes.
Sound: the pluck lead card. Delay on the pluck at 1/4 or dotted 1/8 fills the rests.

## How to check it
`rick-rubin score <dir> --bars 1-8 --tracks Pluck`: onsets on steps 1, 2, 4, 5, 7, 8, 10, 11, 13, 14, 16 only;
`rick-rubin check` reports no out-of-key notes; the top voice changes pitch at least every bar while the
bottom voice changes every one or two bars.

## Why it works
Six cells of three against a bar of sixteen never line up with the kick except on the downbeat, so the line
rolls across the beat, and restarting each bar keeps it anchored. Splitting it into a slow low voice and a
faster high voice gives harmony and tune from one monophonic-sounding part.
