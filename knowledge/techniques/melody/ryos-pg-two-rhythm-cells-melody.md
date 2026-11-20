---
title: Build an 8-bar lead melody from two alternating one-bar rhythm cells
topic: melody
genres: [progressive house]
source: RYOS — Making Beautiful Progressive House | Studio Time with Ryos EP. 50 (https://youtu.be/WnZ7GN1tpek?t=362)
status: untested
---
## What it is
The melody alternates a calm bar and a busy bar. Each has a fixed rhythm; only the pitches change from one
pair of bars to the next. The same two rhythms are later copied by the bass, the piano stabs and the fill.

## When to use it
Writing the main hook of a progressive house track, on a piano over the chords, before any sound design.

## How
1. Calm cell (bars 1, 3, 5, 7): four notes at 16th positions 0, 6, 8, 14 of the bar, lengths quarter, eighth,
   quarter, eighth. In beats: on 1, the "and" of 2, on 3, the "and" of 4 (shown,
   [6:02](https://youtu.be/WnZ7GN1tpek?t=362)).
2. Busy cell (bars 2, 4, 6, 8): six notes at 16th positions 0, 2, 4, 7, 10, 13. Two short repeated notes, then
   four notes a dotted eighth apart, which lands the next bar's first note exactly on the bar line (shown, 6:02).
3. Pitches: the calm bars rock between two chord tones a third apart (the fifth and third of the G chord, then
   the same shape a third higher over D). The busy bars open on a repeated note (in bar 2 a sixth above the
   calm bar's top note, the highest point of the phrase), and their last note steps up into the first note of
   the next bar (shown, 6:02).
4. Bars 5 to 8 repeat bars 1 to 4; only the end of bar 8 changes. He wants bar 8 to go higher, tries it, and
   leaves the choice for later instead of forcing it (said, [5:44](https://youtu.be/WnZ7GN1tpek?t=344),
   [6:34](https://youtu.be/WnZ7GN1tpek?t=394)).
5. Play the melody on a big lead sound early to check it carries the drop, before investing in the break
   (said, [10:12](https://youtu.be/WnZ7GN1tpek?t=612)).
6. His test of a hook: it was still in his head after a break away from the desk (said,
   [20:55](https://youtu.be/WnZ7GN1tpek?t=1255)).

## In Rohil's setup
Write the two cells as two patterns in `song.py` (16th positions 0, 6, 8, 14 are `1.1 2.3 3.1 4.3`; positions
0, 2, 4, 7, 10, 13 are `1.1 1.3 2.1 2.4 3.3 4.2`) and write the pitches for this song; do not reuse his. Write
two or three pitch versions as variables and compare them in context. See also the existing card
`ryos-melody-rhythm-symmetry.md` for his general rule that a melody's rhythm should repeat.

## How to check it
`rick-rubin score <dir>` should print the same onset positions in bars 1, 3, 5, 7 and in bars 2, 4, 6, 8. The
bass and stab tracks that copy the rhythm should show the same onsets (`rick-rubin hits` on their bounces).
Whether it is a hook is Rohil's call: `rick-rubin verdict`.

## Why it works
A repeated rhythm is what makes a melody memorable; alternating a sparse and a dense bar gives a question and
answer feel. The dotted-eighth run in the busy bar pushes across the beat and resolves on the next downbeat.
