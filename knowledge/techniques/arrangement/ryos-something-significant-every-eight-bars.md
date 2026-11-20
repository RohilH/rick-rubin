---
title: Make something significant happen every eight bars, and lift the second half of the drop
topic: arrangement
genres: [progressive house, tech house, bass house, any]
source: RYOS — Giving Feedback On YOUR Tracks! (https://youtu.be/3I7jJyVczPQ?t=8870)
status: untested
---
## What it is
Ryos's rule of thumb for holding attention: at every eight-bar boundary something the listener can name has
changed. Adding only a kick does not count.

## When to use it
A section that "feels like more of the same"; a drop whose energy sags in its second half; drums that play one
pattern throughout. Four tracks got this note.

## How
1. Walk the arrangement in eight-bar blocks and write down what is new in each. If the answer is "the kick" or
   "nothing", the block needs an element (said, [2:27:50](https://youtu.be/3I7jJyVczPQ?t=8870)).
2. In a break, the new thing can be one melodic sound in the high mids: an atmosphere, a pad, a piano, an arp.
   He drops in an atmosphere, pitches it to the key and shelves it so only its high-mid energy remains (said,
   [2:29:06](https://youtu.be/3I7jJyVczPQ?t=8946)).
3. Or a supersaw pad playing the chord progression with a 16th-note volume rhythm on it, for a flutter (said,
   [2:30:40](https://youtu.be/3I7jJyVczPQ?t=9040)).
4. Second half of a drop: add an offbeat ride, or a long offbeat hat for bounce (said,
   [40:30](https://youtu.be/3I7jJyVczPQ?t=2430), [2:56:10](https://youtu.be/3I7jJyVczPQ?t=10570)).
5. Let the drums develop: the hat carries on, shakers join, occasional extra hat hits ("hat throws") lead into
   fills. In a drum-led style make hats and shakers louder (said, [38:45](https://youtu.be/3I7jJyVczPQ?t=2325),
   [3:17:10](https://youtu.be/3I7jJyVczPQ?t=11830)).
6. Break a repeating bass rhythm with a call and response: stop the bass stab for a beat and let a vocal phrase
   answer (said, [3:24:10](https://youtu.be/3I7jJyVczPQ?t=12250)).
7. Let a background part open up from the first half of the drop to the second, and around a very simple lead
   put the interest in drums and stabs (said, [2:57:40](https://youtu.be/3I7jJyVczPQ?t=10660),
   [3:21:30](https://youtu.be/3I7jJyVczPQ?t=12090)).

## In Rohil's setup
In a `song.py` the sections are written out, so each eight-bar block's new element is a line the agent writes
and can list back from `rick-rubin score`. In his own Logic project, regions and automation cannot be read or
moved from outside (`skill/logic.md`): describe the block-by-block plan and let him place it. The 16th-note
flutter without ShaperBox: Logic's Tremolo synced to 1/16 on the pad, or an LFO inside the Serum patch (rate
names: `rick-rubin serum params --group lfo`). What is lost against ShaperBox is drawing a custom shape.

## How to check it
`rick-rubin reference compare <dir>`: texture changes per minute should rise and the share of near-identical
two-bar blocks should fall, toward the references' range. The drop's second half should measure busier in the
top end than its first (`rick-rubin eval <dir> --live --bars A-B` on each half, or `rick-rubin spectrum`).

## Why it works
Dance music repeats by design; a regular, audible change gives the listener a reason to stay without breaking
the loop the dancer relies on.
