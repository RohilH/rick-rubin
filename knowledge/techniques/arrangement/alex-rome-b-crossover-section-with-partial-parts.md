---
title: Bridge the vocal section and the drop with a crossover: partial versions of both sides, then a build that implies the drop
topic: arrangement
genres: [any, progressive house, bass house, tech house]
source: Alex Rome — A Simple System For Making Songs in 2026 (https://youtu.be/XlltkalLaU4?t=774)
status: untested
---
## What it is
His definition of a breakdown: the place where the old lead (the vocal) is broken off and the new lead (the drop
melody) is brought in. He also calls it a build-up or a crossover, because elements of the drop cross in while
elements of the verse cross out, overlapping.

## When to use it
A vocal hook and a drop both exist and cutting from one to the other sounds wrong. In the remix: between the last
vocal phrase and the drop.

## How
1. Accept that the hook cannot go straight into the drop; a section is needed between (said,
   [12:54](https://youtu.be/XlltkalLaU4?t=774)).
2. Overlap the two sides: bring drop elements in early and let verse elements run on (said,
   [13:16](https://youtu.be/XlltkalLaU4?t=796)).
3. A crossover "likes partial versions" of the instruments (said, [13:16](https://youtu.be/XlltkalLaU4?t=796)):
   - drums: he keeps the kit as two layers, high and low, and uses only the high layer here, no kick (said,
     [13:36](https://youtu.be/XlltkalLaU4?t=816));
   - lead: hinted, audibly building in under the last of the vocal (said,
     [13:36](https://youtu.be/XlltkalLaU4?t=816), [14:17](https://youtu.be/XlltkalLaU4?t=857)).
4. Build-up: the best ones imply what the drop will sound like. He removes the chords and lets the bass go low
   (said, [14:37](https://youtu.be/XlltkalLaU4?t=877)).
5. Keep things moving with automation: a filter on every instrument (said,
   [14:58](https://youtu.be/XlltkalLaU4?t=898)). Shown at [15:10](https://youtu.be/XlltkalLaU4?t=910): cutoff
   lanes ramping up across the section, one point reading 270 Hz; at [16:00](https://youtu.be/XlltkalLaU4?t=960)
   the bass synth's filter frequency has a point at 42 Hz with a short bump before the drop.
6. A swell effect straddles the join (shown, 16:00: a cymbal transition swell sample starting before the vocal
   ends and ending after it).
7. Test the join: if the transition is satisfying, move on (said, [13:36](https://youtu.be/XlltkalLaU4?t=816)).

Shown at [14:50](https://youtu.be/XlltkalLaU4?t=890) (proportions only, no bar numbers): the chords stop where
the vocal ends and return at the drop; the lead and the high drums start where the vocal ends; the bass has been
in since halfway through the vocal part; the low drums start only at the drop. The crossover is half as long as
the vocal part (inferred: 8 bars after 16).

## In Rohil's setup
Split the kit into two track stacks in Logic, kick and low percussion in one and tops in the other, so the
crossover is a mute of one stack. The filter moves are drawn by Rohil (rick-rubin cannot write automation into
his project); the agent gives lane, bars and target values. A swell: Splice, checked with `rick-rubin audition`.
Companion cards: `arrangement/alex-rome-b-opposite-automation-handoff.md` (what to automate on the two leads),
`arrangement/ryos-pg-build-by-filtering-everything-away.md` and
`arrangement/ryos-transition-details-reverses-cuts-risers.md` (the build and its details).

## How to check it
`rick-rubin spectrum` (or `rick-rubin eval <dir> --bars`) on the crossover against the drop: energy under 120 Hz
much lower in the crossover, then a clear step at the drop; brightness rising through the crossover. A bounce
from four bars before the crossover to four bars into the drop for his verdict.

## Why it works
The listener meets the drop's lead and top end before the drop, so the drop arrives as something half-known, and
holding back the kick and the chords leaves the drop two large things to add at once.
