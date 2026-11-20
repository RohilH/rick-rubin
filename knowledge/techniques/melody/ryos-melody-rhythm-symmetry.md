---
title: Give a four-bar melody rhythmic symmetry, and build it from its best bar
topic: melody
genres: [progressive house, any]
source: RYOS — Giving Feedback On YOUR Tracks! (https://youtu.be/3I7jJyVczPQ?t=5858)
status: untested
---
## What it is
A catchy lead repeats its rhythm in a pattern the listener can predict while the pitches change. Ryos names
two patterns and a way to get there from a draft melody that starts well and then wanders.

## When to use it
When a melody "has potential" but does not stick; when every bar of it has a different rhythm; when writing a
lead from scratch.

## How
1. Find the strongest bar of the draft. Often it is the first (said, [1:37:38](https://youtu.be/3I7jJyVczPQ?t=5858)).
2. Highlight it by repetition: copy that bar forward, then change one note or remove one, and work from there
   (said, [1:38:10](https://youtu.be/3I7jJyVczPQ?t=5890)).
3. Pattern one, which he calls the "1 3 2 4" combination: bars 1 and 3 share a rhythm, bars 2 and 4 share a
   different rhythm (said, [1:39:40](https://youtu.be/3I7jJyVczPQ?t=5980)).
4. Pattern two: bars 1, 2 and 3 share a rhythm, and bar 4 changes (said,
   [1:40:40](https://youtu.be/3I7jJyVczPQ?t=6040)).
5. In both, only the rhythm is fixed; the notes are free. The repeated rhythm is the anchor (said,
   [1:40:20](https://youtu.be/3I7jJyVczPQ?t=6020)).
6. Keep it simple: a melody that is "just the right amount of interesting" beats a complicated one, and offbeat
   stutters added for interest are usually too much (said, [52:45](https://youtu.be/3I7jJyVczPQ?t=3165),
   [2:50:35](https://youtu.be/3I7jJyVczPQ?t=10235)).
7. Exceptions exist: he says one of his own best melodies has a different rhythm in every bar. Treat symmetry
   as the default, not a law (said, [1:38:40](https://youtu.be/3I7jJyVczPQ?t=5920)).
8. Use only notes of the track's scale, in the lead and in every part under it (see the chords card).

## In Rohil's setup
This is a way of writing, not a setting. In a `song.py` the agent writes the notes: write the lead as four
one-bar variables so the shared rhythm is visible, try both patterns as alternatives (PREFERENCES section 3),
and read them back with `rick-rubin score <dir> --tracks Lead`. In his own Logic project the notes inside a
region cannot be edited from outside: write the alternative as MIDI and bring it in beside his
(`rick-rubin logic add-midi line.mid --bar 9`) for him to compare. No pattern here is a stock part: the rhythm
itself is still composed for the song.

## How to check it
Read the lead in `rick-rubin score`: the onset positions of bars 1 and 3 (and 2 and 4), or of bars 1 to 3,
should be identical while the pitches differ. Then the only real test: Rohil can hum it after two listens
(`rick-rubin verdict`).

## Why it works
Listeners remember rhythm before pitch. A rhythm that returns lets them predict the next bar, and a prediction
that comes true with new notes is what "catchy" feels like.
