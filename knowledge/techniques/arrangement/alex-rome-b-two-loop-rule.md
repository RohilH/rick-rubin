---
title: The two-loop rule: lay the main loop out as a timeline and make two changes every two loops
topic: arrangement
genres: [any, tech house, bass house, progressive house]
source: Alex Rome — An Insanely Simple Arrangement System (escape the loop trap) (https://youtu.be/ZkRds6iTfhQ?t=129)
status: untested
---
## What it is
Alex Rome's way out of a loop that will not become a song. One part is repeated along the timeline as a ruler;
at every second repeat the arrangement must change, by a small fixed budget, and each join is tested before the
next is written.

## When to use it
There is a loop Rohil likes (a vocal and chords, a drop) and nothing either side of it. Also as a check on a
finished arrangement: count the changes at each boundary.

## How
1. Pick a main instrument, usually the chords, and repeat its loop six times in a row. That is the timeline
   (said, [2:09](https://youtu.be/ZkRds6iTfhQ?t=129); shown [2:40](https://youtu.be/ZkRds6iTfhQ?t=160): six
   four-bar clips, so 24 bars). Colour each pair of loops so the sections are visible.
2. Every two loops something changes: every eight bars with a four-bar loop (said,
   [2:50](https://youtu.be/ZkRds6iTfhQ?t=170)).
3. There are only four kinds of change: add an instrument, remove one, add expression to one that is already
   playing (open its filter, layer it), or take expression away (said,
   [6:37](https://youtu.be/ZkRds6iTfhQ?t=397)).
4. Budget: start with two changes per boundary. More overloads the section, fewer leaves it flat; adjust later
   (said, [4:54](https://youtu.be/ZkRds6iTfhQ?t=294)). Several small additions of one kind count once: three
   drum layers are one change (said, [7:39](https://youtu.be/ZkRds6iTfhQ?t=459)).
5. Choose by "simple math" and feel: list what the track does not have yet (no drums, no bass), then pick what
   the section seems to want (said, [3:10](https://youtu.be/ZkRds6iTfhQ?t=190)). A part that has not "expired"
   stays: he repeats the vocal and leaves the first drums alone (said,
   [6:58](https://youtu.be/ZkRds6iTfhQ?t=418)).
6. Early on, add. Removing layers comes later, once the track is full enough for the emptiness to feel natural
   (said, [6:17](https://youtu.be/ZkRds6iTfhQ?t=377), [10:10](https://youtu.be/ZkRds6iTfhQ?t=610)).
7. After each boundary a "transition check": play across it. It only has to be a satisfying change; if not, fix
   it before going on (said, [5:35](https://youtu.be/ZkRds6iTfhQ?t=335),
   [9:07](https://youtu.be/ZkRds6iTfhQ?t=547)).

His demo, by section (said in order; layout shown [11:40](https://youtu.be/ZkRds6iTfhQ?t=700)):

| Loops | Change 1 | Change 2 |
|---|---|---|
| 1–2 | chords and the vocal: the starting loop | |
| 3–4 | bass, from the chords' bottom notes in the chords' rhythm | kick and one hat, four on the floor |
| 5–6 | more drums: a 16th hat, a rimshot, a top loop | short vocal chops answering the main vocal |
| 7–8 | chord layer an octave up in another sound | the chords' cutoff opened |

At loops 7–8 the frame also shows the main vocal stopping and one more percussion part starting; he does not
mention either. He planned six loops and ended with eight.

## In Rohil's setup
In Logic: loop the chord region (L), colour the regions (Option-C), arrangement markers every eight bars.
`rick-rubin logic inspect` cannot see region positions, so the agent writes the table of changes and Rohil places
the regions; in a `song.py`, `rick-rubin score <dir>` lists the sections back. Same cadence as
`arrangement/ryos-something-significant-every-eight-bars.md`; this card adds the budget, the four kinds of change
and the check at each join. It yields a build of about 32 bars, not a whole track: after the peak the rule runs
in reverse (inferred).

## How to check it
Write the table for the real project: every boundary has one or two named changes, none has zero. `rick-rubin
reference compare <dir>`: texture changes per minute up, near-identical blocks down, toward the references. Each
join bounced four bars either side (`rick-rubin logic bounce j.wav --bars 7-10`) for his ears.

## Why it works
A fixed ruler turns "what next?" into a small repeated question with four possible answers, and the budget stops
both common failures: everything arriving at once, or nothing arriving at all.
