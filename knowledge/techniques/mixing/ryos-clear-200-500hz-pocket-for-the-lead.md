---
title: Clear 200 to 500 Hz out of the bass and chords so the lead comes forward
topic: mixing
genres: [progressive house, bass house, any]
source: RYOS — Giving Feedback On YOUR Tracks! (https://youtu.be/3I7jJyVczPQ?t=4065)
status: untested
---
## What it is
The low mids are where a lead gets its body. Ryos calls 300 to 500 Hz "prime real estate" for any lead and takes
it away from the bass and chord groups, often only from their sides, instead of turning the lead up.

## When to use it
When the lead sounds behind the bass or "in a box" although its fader is high. He gave this to five tracks.

## How
1. Decide the order of loudness for the section: first, second, third. In progressive house the lead is first
   (said, [1:09:45](https://youtu.be/3I7jJyVczPQ?t=4185)). Cut from whatever ranks lowest first.
2. Start with the fader: a bass that swallows the kick and lead comes down "at least 3 dB" (said,
   [2:39:32](https://youtu.be/3I7jJyVczPQ?t=9572)).
3. On the chord group, then the bass group, dip the 200 to 500 Hz region and leave everything under 200 Hz alone,
   because that is where the fatness is (said, [2:17:50](https://youtu.be/3I7jJyVczPQ?t=8270)). For a first
   pass on a beginner's track he says 400 to 500 Hz out of the chords (said,
   [27:02](https://youtu.be/3I7jJyVczPQ?t=1622)). Depth is not stated; he warns that every dB removed is power
   lost, so stop when the lead clears.
4. Better: put the EQ in mid/side mode and make the cut on the side channel only, around 300 to 400 Hz. A bass
   rarely needs stereo information there, and the centre keeps its weight (said,
   [1:08:30](https://youtu.be/3I7jJyVczPQ?t=4110)).
5. Test the idea in ten seconds by dipping about 250 Hz on the whole master and listening for the lead lifting;
   then undo it and make the cut on the groups (said, [2:16:45](https://youtu.be/3I7jJyVczPQ?t=8205)).

## In Rohil's setup
Logic's Channel EQ has a Processing setting (stereo, mid only, side only): insert one on the bass or chord
summing track set to side only and dip around 350 Hz (`rick-rubin logic insert Bass "Channel EQ"`; read the band
names with `rick-rubin logic params Bass "Channel EQ"` before setting them). A dynamic alternative he owns:
`rick-rubin logic insert Chords "Trackspacer 2.5" Ratio=60 --sidechain Lead` with Low-cut near 200 and High-cut
near 600, which ducks only while the lead plays. He uses Pro-Q; nothing is lost with Channel EQ except the
per-band mid/side switch (one instance per mode instead).

## How to check it
`rick-rubin spectrum <dir> lead.wav bass.wav chords.wav` on bounces of the drop: in 200 to 500 Hz the lead should
no longer be under the other two. `rick-rubin width <dir> bass.wav` should show less side energy in the low-mid
band after a side-only cut, and the bass level below 200 Hz should not have moved.

## Why it works
Loudness is partly masking: a lead with nothing competing in its body range reads as louder and closer at the
same fader level, and stereo low mids on a bass add clutter without adding weight.
