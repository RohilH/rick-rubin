---
title: A house track from one chord progression written twice: a relaxed 16 bars, then a high-energy 16 bars
topic: arrangement
genres: [progressive house, tech house, any]
source: Alex Rome — The Simplest Strategy for Building House Songs (it's like cheating) (https://youtu.be/kSXHTJJ7D34?t=284)
status: untested
---
## What it is
Alex Rome's simplest song skeleton. The same chords exist in two forms, a low-energy one and a high-energy one.
Each form gets its own 16-bar block, each block is dressed only with instruments of its own energy, and something
new enters halfway through each block. The result is a verse-like section and a drop.

## When to use it
A first arrangement for a chord idea, deep or melodic house especially. For the remix: the relaxed block is where
he says a vocal verse belongs (said, [10:38](https://youtu.be/kSXHTJJ7D34?t=638)).

## How
1. Write the progression in its low-energy form: a deep filtered-saw pad holding two notes per chord (said,
   [0:21](https://youtu.be/kSXHTJJ7D34?t=21); see `harmony/alex-rome-b-one-progression-at-two-energy-levels.md`).
2. Write the same notes again in a high-energy form: a pluckier sound and a rhythm (said,
   [2:57](https://youtu.be/kSXHTJJ7D34?t=177)).
3. Give each form a 16-bar block, relaxed first (said, [4:44](https://youtu.be/kSXHTJJ7D34?t=284)).
4. Add to each block only what matches it: atmospheric pads, relaxed percussion and effects in the first; drums
   and bass in the second (said, [5:06](https://youtu.be/kSXHTJJ7D34?t=306)).
5. Halfway through each block something comes in, his "eight-bar rule" (said,
   [7:30](https://youtu.be/kSXHTJJ7D34?t=450), [9:57](https://youtu.be/kSXHTJJ7D34?t=597)).
6. The sounds are free; only the two-block shape is the system (said, [0:00](https://youtu.be/kSXHTJJ7D34?t=0)).

What plays where (shown [10:15](https://youtu.be/kSXHTJJ7D34?t=615), Ableton arrangement, bars 1 to 33):

| Bars | Playing | Entering here |
|---|---|---|
| 1–8 | held pad chords, an airy pad layer, a distorted pad | |
| 9–16 | the same | two hat loops (an open and a 16th closed), a wider chord layer; a short effect leads into bar 9 and a long one runs from about bar 13 into 17 |
| 17–24 | the pluck chords in their rhythm, almost alone | pads, hats and effects all stop at 17 |
| 25–32 | pluck chords | bass in the chords' rhythm, kick, layered open hat, closed hat, clap, a quiet percussion loop |

So the first half of the high-energy block works as the build: he says nothing more is needed there (said,
[11:03](https://youtu.be/kSXHTJJ7D34?t=663)), and the drums and bass arriving at bar 25 are the drop.

## In Rohil's setup
In a `song.py` the two forms are two tracks holding the same pitches, and the four eight-bar sections are written
out; in Logic, two regions on two tracks. He says this is the whole song and that a full arrangement follows from
it, but shows only these 32 bars: a DJ-length track still needs an intro and outro and a second pass through the
pair with something changed (inferred; see `arrangement/alex-rome-b-two-loop-rule.md` for how to vary it). The
tempo field appears to read 120 (shown [9:05](https://youtu.be/kSXHTJJ7D34?t=545), small); Rohil's genres sit at
124 to 130. Related cards: the airy layer (`sound-design/alex-rome-b-airy-pad-layer-over-tight-chords.md`), the
bass (`bass/alex-rome-b-bassline-from-the-chords-bottom-notes.md`), the hidden percussion
(`sound-design/alex-rome-c-hidden-percussion-loop-under-the-music.md`).

## How to check it
`rick-rubin spectrum` or `rick-rubin eval <dir> --bars` on each eight-bar section: low-band energy (under 120 Hz)
near nothing until bar 25; top-end activity stepping up at bar 9 and again at 25. `rick-rubin reference compare
<dir>` for the contrast between sections against released tracks. The energy difference between the two chord
forms is for his ears: bounce bars 9–16 and 17–24 back to back.

## Why it works
Keeping the notes and changing only sound and rhythm makes the two sections plainly one song, while the split by
energy gives contrast for free; the halfway entries stop each 16 bars from standing still.
