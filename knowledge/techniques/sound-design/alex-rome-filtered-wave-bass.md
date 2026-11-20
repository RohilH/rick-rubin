---
title: The simplest bass, any wave through a steep low-pass, played low
topic: sound-design
genres: [tech house, bass house, progressive house]
source: Alex Rome — How To Make Any Sound From Scratch (https://youtu.be/p1-WmITJqBk?t=739)
status: untested
---
## What it is
His rule for a bass that always works under a melody or chords: write the notes in a low octave, take any basic
wave, and close a steep low-pass over it. The wave picks the character: square for a strong sub, saw for grit.

## When to use it
A first bass for any idea, a sub layer under a busier mid-bass, and as the practice sound he says to learn first.

## How
1. Put the bass notes low (shown [13:10](https://youtu.be/p1-WmITJqBk?t=790): the octave below Logic's C1,
   fundamentals roughly 40 to 60 Hz).
2. Init saw, Filter 1 on, MG Low 24, cutoff pulled towards the lows by ear (said,
   [12:41](https://youtu.be/p1-WmITJqBk?t=761)).
3. Square instead of saw for one of "the strongest" subs (said; shown [13:32](https://youtu.be/p1-WmITJqBk?t=812):
   square, unison 1, cutoff 512 Hz).
4. Saw for a thinner, grittier bass (said, [13:44](https://youtu.be/p1-WmITJqBk?t=824)).
5. Unison stays at 1 for these (shown [13:32](https://youtu.be/p1-WmITJqBk?t=812)).
6. ENV 1 stays at init: full sustain, 15 ms release (shown [13:32](https://youtu.be/p1-WmITJqBk?t=812)).
7. Ours, not in the video: mono, every note starting at the same phase, and a touch of release so notes do not
   click.

## In Rohil's setup
```
rick-rubin serum set init osc_a.wt_pos=128 filter_1.on=on "filter_1.type=MG Low 24" filter_1.cutoff_hz=512 \
    osc_a.rand_phase=0 global.mono=on --save square-sub --project <dir>
```
`osc_a.wt_pos=1` is the saw. `filter_1.cutoff_hz` is the one knob to compare: `rick-rubin serum ab init --note G0
--try "... filter_1.cutoff_hz=200" --try "... filter_1.cutoff_hz=500" --try "... filter_1.cutoff_hz=900"`. In a
song, sidechain it to the kick as usual (`skill/logic.md`).

## How to check it
`rick-rubin serum describe ... --note G0`: one render here of the square at 512 Hz gave 85 % of the energy in the
sub band, 10 % bass, 5 % low-mid, six odd-heavy harmonics, side energy 0. Opening the cutoff should move share from
sub to bass and low-mid; that is what makes it audible on small speakers. In context: `rick-rubin width` low band at
zero, and `reference compare` low-end share inside the references.

## Why it works
Every harmonic wave has a strong fundamental; the low-pass decides how much of the rest comes through. A square's
odd harmonics sit close above the fundamental, so even a low cutoff leaves something to hear (inferred).
