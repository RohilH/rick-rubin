---
title: VI–VII–i–VII, a neutral loop whose melody decides serious or hopeful
topic: harmony
genres: [progressive house, tech house, any]
source: Alex Rome — 10 Chord Patterns for 10 Different Emotions (https://youtu.be/_yw85rAb6cw?t=86)
status: untested
---
## What it is
Two major chords stepping up to the minor tonic and back to the second one. He calls it one of the most common
progressions and "deep and serious", then shows the same chords sounding happy under a different melody.

## When to use it
When the chords should stay out of the way and the top line should carry the mood, or when one section should feel
darker and a later one brighter without changing the harmony.

## How
1. Natural minor; degrees 6, 7, 1, 7, one bar each (said; shown [1:40](https://youtu.be/_yw85rAb6cw?t=100) in B
   minor: G, A, Bm, A).
2. Third of each chord up an octave, as he "almost always" does (said; shown
   [2:30](https://youtu.be/_yw85rAb6cw?t=150): G–D–B, A–E–C#, B–F#–D).
3. For serious: build the melody on the minor tonic and its fifth (shown [2:30](https://youtu.be/_yw85rAb6cw?t=150):
   B and F# above the chords, the tonic repeated and the fifth as the last note of each bar).
4. For hopeful: the same rhythm moved to the relative major's tonic and fifth (shown
   [2:42](https://youtu.be/_yw85rAb6cw?t=162): D and A).
5. To vary it (ours): start the phrase on the i chord for a more settled feel, or stop on VII before a drop.

## In Rohil's setup
Write the two melodies as two variables in `song.py` and compare them in context (PREFERENCES section 3): the minor
one for the first breakdown, the major one for the second is one honest use. In tech house the same idea works with
a one-bar stab rhythm instead of held chords.

## How to check it
`rick-rubin score <dir> --tracks <lead>`: which pitches land on the strong beats and at phrase ends. Minor reading:
degrees 1 and 5 of the minor key. Major reading: degrees 3 and 7 of it (1 and 5 of the relative major). Then a
bounce of each for Rohil.

## Why it works
G, A and Bm are IV, V and vi in D major as much as VI, VII and i in B minor. Nothing in the chords settles which key
is home, so the notes the melody leans on do (inferred from his demonstration).
