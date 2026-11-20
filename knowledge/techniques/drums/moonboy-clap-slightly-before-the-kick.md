---
title: Start the clap a few milliseconds before the kick it lands on
topic: drums
genres: [bass house, tech house, any]
source: MOONBOY — HOW TO BASS HOUSE (Knock2, Skrillex, Porter Robinson) (https://youtu.be/3-0JCDyiPaw?t=106)
status: untested
---
## What it is
The clap on beats 2 and 4 is nudged slightly early, so its noise begins just ahead of the kick instead of
exactly with it. His on-screen note says this gives the beat more depth.

## When to use it
When kick and clap on 2 and 4 sound like one flat hit, or the clap seems to vanish behind the kick. Works
best with a clap that has a soft, spread front.

## How
1. Zoom in on a beat where kick and clap coincide (shown at [1:49](https://youtu.be/3-0JCDyiPaw?t=109)).
2. Drag the clap clip left so it starts a little before the kick; the kick stays on the grid (shown; he
   says "offsetting your clap slightly to the left", the caption says "before the kick").
3. How far: no number is given. Measured against the kick's own wave on screen it is a fraction of one
   cycle of the kick, roughly 5 to 10 ms at 126 BPM (inferred).
4. Do it to every clap, not just one (shown: all claps sit the same way in the wide view).

## In Rohil's setup
- In a `song.py`: `delay_ms=-8` on the clap track moves the whole part 8 ms early (`skill/compose.md`).
  Try a few values: `rick-rubin ab <dir> ...` with the clap's delay as the variable, on the drop's bars.
- In a Logic project: the clap region's Delay in the Region inspector (negative value), or drag the regions
  with snap off. There is no session command for region timing: do it by hand or ask him to.
- skill/compose.md suggests a clap a few ms late for a laid-back feel; early is the opposite choice (tighter,
  more aggressive). Let him hear both.

## How to check it
`rick-rubin view <dir> --bars 1-2 --tracks Kick Clap` (16th grid visible at this zoom): the clap's onset is
left of the kick's by the amount set. `rick-rubin ab ... --hits`: the level on steps 5 and 13 should not
drop (if it does, the two are cancelling; try another offset). Then a bounce of both versions for his ear.

## Why it works
Two transients at the same instant mask each other and the louder one wins. A few milliseconds apart, the
ear still hears one hit but gets both fronts, and the clap reads as wider and nearer.
