---
title: Build the drop as two alternating two-bar ideas, A and B
topic: arrangement
genres: [bass house, tech house]
source: MOONBOY — HOW TO BASS HOUSE (Knock2, Skrillex, Porter Robinson) (https://youtu.be/3-0JCDyiPaw?t=695)
status: untested
---
## What it is
His way to keep a drop entertaining: write two different versions of the drop that complement each other
and let them take turns. In his track A is the laser bass riff with the sub, and B is the chopped one-shot
section with the full drums.

## When to use it
Whenever a drop is one loop repeated for sixteen bars. Also the simplest answer to a `reference compare`
that reports too little change or near-identical blocks.

## How
1. Think of the drop as an A section and a B section: two variations that answer each other (said,
   [11:40](https://youtu.be/3-0JCDyiPaw?t=700)).
2. His layout, from the markers on screen ([11:53](https://youtu.be/3-0JCDyiPaw?t=713)): Drop A at bar 89,
   Drop B at bar 91, A at 93, B at 95, a new marker "Drop 1.2" at 97. Two bars each, eight bars in all,
   before the next block starts.
3. What changes between them (shown, same frame): A carries the synth-and-bass group and the lead; B carries
   a separate "Drop B" group of chops. In the first A the drum group is almost empty until its last beats;
   from B onward the drums run through. So the first two bars of the drop are the hook alone, and the full
   beat lands with B (inferred from the lanes; he does not comment on it).
4. Each A and B ends with a small fill in its last beat (shown: extra clips at the end of each 2-bar block).
5. Groups on screen: Drums, Vocals, Synths & Basses, Synths, Drop B, Buildup FX, FX. The last five are routed
   into one track called "Sidechain" instead of the master; drums and vocals go to the master directly
   (shown). That suggests one ducking stage for everything that should pump (inferred).

## In Rohil's setup
- In a `song.py`: two sections of two bars, `drop_a` and `drop_b`, alternated in the arrangement, and
  variants for the second pass (`section.variant(...)` with `add`, `without`, `fills`) so A2 is not A1.
- In Logic: arrangement markers per two bars; a summing stack for everything that should pump with one
  `rick-rubin logic insert "Pump Bus" "Kickstart 2" Mix=0.6` on it, drums and vocal outside it.
- Read where the project stands first: `rick-rubin logic inspect` (regions and track outputs).

## How to check it
`rick-rubin reference compare <dir>`: the share of near-identical 2-bar blocks in the drop should fall and
"texture changes per minute" rise into the references' range. `rick-rubin eval <dir> --bars 89-96`: A and B
within about 1 LU of each other, so the alternation is a change of colour, not of level.

## Why it works
Two bars is short enough that neither idea wears out, and the return of A after B is heard as a repeat, so
the listener gets both novelty and a hook from eight bars of material.
