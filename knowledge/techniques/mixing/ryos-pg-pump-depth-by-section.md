---
title: Pump with a volume shaper last in the chain, and automate its depth by section
topic: mixing
genres: [progressive house]
source: RYOS — Making Beautiful Progressive House | Studio Time with Ryos EP. 50 (https://youtu.be/WnZ7GN1tpek?t=1478)
status: untested
---
## What it is
The sidechain in this project is not a compressor keyed from the kick. Each sustained or busy part has a
tempo-synced volume shaper at the end of its chain, and on the drone the shaper's mix is automated so the part
only pumps where there is a kick to pump against.

## When to use it
Any part that plays through both a kickless break and a drop: drones, pads, atmospheres, top loops.

## How
1. Put the shaper last, after reverb and delay, so the tails duck too. Shown on the analog drone (Decapitator,
   Supermassive, EQ, auto-pan, then Kickstart 2; [9:12](https://youtu.be/WnZ7GN1tpek?t=552)), on the dance piano
   bus (Kickstart 2 in the last slot, [29:54](https://youtu.be/WnZ7GN1tpek?t=1794)) and on the reese (LFOTool
   last, [20:52](https://youtu.be/WnZ7GN1tpek?t=1252)).
2. Quarter-note ducks, depth set by ear per part. The percussion loop gets the heaviest: 1/4, mix 100 % (said
   and shown, [24:38](https://youtu.be/WnZ7GN1tpek?t=1478)). The shaper's curve picker is visible there; which
   curve suits which part is not discussed.
3. Automate the shaper's mix on parts that span sections. The drone has a "Kickstart 2 mix level" automation
   clip from bar 1; it steps at bar 25, where the drop and its kick begin (shown,
   [34:20](https://youtu.be/WnZ7GN1tpek?t=2060)). Reading it as off in the break and on in the drop is our
   inference; the lane's values are not readable.
4. Nothing in the video shows a compressor keyed from the kick, so fills and kick gaps keep pumping (inferred).

## In Rohil's setup
He owns Kickstart 2 and it is the one plug-in here checked on a bounce: `rick-rubin logic insert Drone
"Kickstart 2" Mix=0.6`, `rick-rubin logic insert "Perc loop" "Kickstart 2" Mix=1.0`; insert it after the
reverb so it is last. From `skill/logic.md`: `Loop Length` 0.0 repeats every beat, `Used Wave` picks one of 16
curves, `Mix` is the depth. rick-rubin cannot write automation into his project: draw the Mix automation in
Logic by hand (0 in the break, the drop value from the drop's first bar), or use two tracks, one per section.
In a `song.py`, `sidechain="kickstart"` on the track does step 1; give the break and the drop separate tracks
if the depth should differ. For the bass, the repo's advice stands: a kick-keyed Compressor ducks only when
the kick really hits.

## How to check it
`rick-rubin reference compare <dir>`: the low-end pump figure (off-beat against kick) for the drop should sit
inside the references' range. Bounce the drone alone over bars 9-16 and 25-32 (`rick-rubin logic bounce
drone.wav --bars 9-16 --tracks Drone`): the break bounce should hold a steady level and the drop bounce
should dip on every beat. Depth is then an ear call: bounce two Mix values for Rohil.

## Why it works
A shaper gives the same duck every beat regardless of what the kick sample does, and placing it last makes
the whole wet signal breathe. In a break with no kick, pumping has nothing to answer and only weakens the pad.
