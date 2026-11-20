---
title: Big reverb on a lead without pushing it back: send, pre-delay, duck, then glue
topic: mixing
genres: [progressive house, any]
source: RYOS — Giving Feedback On YOUR Tracks! (https://youtu.be/3I7jJyVczPQ?t=3180)
status: untested
---
## What it is
Reverb makes a lead sound huge and also moves it to the back of the room. This keeps the dry lead in front and
lets the wash arrive behind it.

## When to use it
A lead that sounds distant, smeared or "mushy" next to the kick. He gave this to three tracks, each time
blaming reverb used as an insert.

## How
1. Take the reverb off the lead's channel and put it on a send (said, [2:40:50](https://youtu.be/3I7jJyVczPQ?t=9650),
   [2:48:01](https://youtu.be/3I7jJyVczPQ?t=10081)).
2. Raise the reverb's pre-delay so the dry note lands first. His starting point is about 80 ms, depending on the
   melody (said, [53:50](https://youtu.be/3I7jJyVczPQ?t=3230)).
3. If the melody is busy and pre-delay alone is not enough, duck the reverb return with the dry lead: Trackspacer
   on the return, keyed by the lead; or a plain compressor with settings gentle enough not to pump (said,
   [2:40:40](https://youtu.be/3I7jJyVczPQ?t=9640)).
4. Route the dry lead and the reverb return to one group and compress that group hard, even limit it, so the tail
   sounds attached to the lead again (said, [2:41:31](https://youtu.be/3I7jJyVczPQ?t=9691)).
5. Aim: the lead level with the kick or slightly in front of it, never behind (said,
   [53:00](https://youtu.be/3I7jJyVczPQ?t=3180)).

## In Rohil's setup
`rick-rubin logic send Lead 1 -12` makes Bus 1 and its Aux. Put ChromaVerb on that Aux at 100% wet and set its
pre-delay near 80 ms (Valhalla Supermassive's Delay control may play the same role; not checked here, read
its names with `rick-rubin logic devices "Valhalla Supermassive"`). Then `rick-rubin logic insert "<the Aux's
name from logic inspect>" "Trackspacer 2.5" Ratio=60 --sidechain Lead`. Anything on an Aux brings Logic to the
front. Step 4 needs the lead's and the Aux's outputs set to a shared bus by hand in Logic (there is no rick-rubin command for output routing); then
`rick-rubin logic insert "<group Aux>" Compressor`. Remove the patch's own reverb: in Serum that is the reverb
unit's wet amount (find the key with `rick-rubin serum patch "<preset>"`).

## How to check it
Bounce the lead group alone before and after (`rick-rubin logic bounce bounces/lead.wav --bars A-B --tracks
Lead`). `rick-rubin reference stems bounces/lead_before.wav bounces/lead_after.wav`: the transient row should
rise (drier onsets) while the level between phrases, the tail, is still there. Then Rohil listens: is the lead
in front of the kick?

## Why it works
The ear places a sound by its first few tens of milliseconds. If those are dry, the sound is close; a tail that
starts later reads as the room around it instead of distance.
