---
title: OTT by role: more on the lead, a touch on secondary parts and the drum group, none on the sub
topic: mixing
genres: [any, progressive house, tech house, bass house]
source: Alex Rome — Give me 19 mins, and I'll Improve your mixing skills by 126% (https://youtu.be/XrGZPWuiJ7o?t=373)
status: untested
---
## What it is
OTT (a three-band compressor that pushes loud parts down and quiet parts up) used as one dial, Depth, set differently
for each part's role. He calls the result stronger single sounds and tighter, glued groups.

## When to use it
After the low cuts, on a mix whose parts sound separate or weak. Not as a fix for a wrong sound.

## How
1. Put OTT on the lead instrument first and raise Depth from 0 while it plays; Time stays at 100 % and both strength
   knobs at 100 % (shown [7:05](https://youtu.be/XrGZPWuiJ7o?t=425)). The lead gets the most (said,
   [7:38](https://youtu.be/XrGZPWuiJ7o?t=458)). On a pluck lead in another video he lands on Depth 64 % (shown,
   [2:08](https://youtu.be/Uazkku5yuM8?t=128)).
2. Secondary parts (arps, counter-melodies): "just a little", for glue only (said,
   [8:02](https://youtu.be/XrGZPWuiJ7o?t=482)).
3. Sub bass: none (said, [8:02](https://youtu.be/XrGZPWuiJ7o?t=482)).
4. Group every drum including the kick and put one OTT on the group. Depth 80 % is his "too much" demo (shown
   [10:18](https://youtu.be/XrGZPWuiJ7o?t=618)); he keeps 14 % (shown [10:45](https://youtu.be/XrGZPWuiJ7o?t=645)).
5. Budget it: if the lead is bright and heavily OTT'd, everything else must be light or the track is tiring (said,
   [8:23](https://youtu.be/XrGZPWuiJ7o?t=503)).
6. Starting figures (ours, inferred from the two readable settings): lead 40 to 65 %, secondary 10 to 20 %, drum group
   10 to 15 %.

## In Rohil's setup
He owns OTT and its Logic parameter names are already cached (`Depth`, `Time`, `InGain`, `OutGai`, `UpwStr`,
`DnwStr`). `rick-rubin logic insert Piano "OTT" Depth=50`, `rick-rubin logic insert Arps "OTT" Depth=15`. For the
drums, insert on the drum group's strip by name; an Aux or summing-stack strip needs Logic in front. Depth raises
level, so match loudness before judging: lower `OutGai` until the before and after bounces read the same LUFS.

## How to check it
`rick-rubin compare <dir> before.wav after.wav` on a bounce of the one track: crest should fall and the high and air
band shares rise. If the low band share rises on a part that was low-cut, the cut belongs after OTT or Depth is too
high. On the drum group, `rick-rubin hits` should still show the kick as the loudest step.

## Why it works
Upward compression lifts the quiet detail (tails, room, upper harmonics) and downward compression holds the peaks, so
the part is audible at a lower fader position (inferred; he describes it as squeezing and expanding at once).
