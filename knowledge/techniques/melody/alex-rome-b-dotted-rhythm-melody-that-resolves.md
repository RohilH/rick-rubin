---
title: A lead melody in three decisions: a dotted rhythm, the chords' contour, and a second half that resolves
topic: melody
genres: [any, progressive house, bass house]
source: Alex Rome — A Simple System For Making Songs in 2026 (https://youtu.be/XlltkalLaU4?t=465)
status: untested
---
## What it is
How he gets the drop melody of the trench-method song in about a minute: he does not search for notes. The rhythm
comes from one rule, the pitches from the chords, and the only composing is making the end of the phrase land.

## When to use it
A drop or hook needs a lead and the chords already exist. It gives a simple, singable line; a busier progressive
house lead can grow from it (see `melody/ryos-pg-two-rhythm-cells-melody.md`).

## How
1. Sound: a preset, not a patch from scratch (he says you do not always have to make your own), edited to be more
   plucky (said, [7:45](https://youtu.be/XlltkalLaU4?t=465)).
2. Rhythm: dotted. A dotted value is a grid value plus half of itself, so a dotted eighth is three 16ths (said,
   [8:07](https://youtu.be/XlltkalLaU4?t=487)). Shown at [9:00](https://youtu.be/XlltkalLaU4?t=540): notes of that
   length repeating across the bar.
3. Pitch: follow the contour of the chords, which he calls easy and musical (said,
   [8:28](https://youtu.be/XlltkalLaU4?t=508)). Shown at 9:00: one pitch repeated while a chord lasts, stepping to
   a neighbouring pitch when the chord changes, with a single higher note as an accent.
4. Second half: match the second half of the progression and resolve. A four-bar melody that only repeats gets
   dull (said, [8:28](https://youtu.be/XlltkalLaU4?t=508) to [8:49](https://youtu.be/XlltkalLaU4?t=529)). Shown
   at 9:00: the last bar drops to a lower note and returns, unlike bars 1 to 3.
5. Before the bass is added, check it against everything; he hears the end of his own as slightly off and moves
   on anyway (said, [9:11](https://youtu.be/XlltkalLaU4?t=551), [9:35](https://youtu.be/XlltkalLaU4?t=575)).
6. The same dotted-eighth rhythm, with passing notes, is how he energises chords in the house-song video (said,
   [4:02](https://youtu.be/kSXHTJJ7D34?t=242)).

## In Rohil's setup
The notes are written for the song, in `song.py` or his piano roll: the card gives the three decisions, not a
line to paste. Sound: `rick-rubin serum search pluck`, compare two or three presets on a bounce, or start from
`sound-design/alex-rome-filter-envelope-pluck.md`. A dotted-eighth cell against a four-beat bar drifts across the
beat; decide where it resets (every bar or every two) and compare both. The three-16th cell is also the basis of
`melody/moonboy-trance-melody-in-three-sixteenth-cells.md` and of his one-note version,
`melody/alex-rome-c-pulsing-one-note-melody.md`; this card adds the contour and the resolution.

## How to check it
`rick-rubin score <dir> --tracks Lead`: onsets three 16ths apart; the pitch changes where the chords change; the
last bar is not a copy of bar 2 and ends on a note of the chord the loop returns to (our working definition of
"resolves"; he gives none). `rick-rubin notes` on a bounce for key fit. Then his verdict.

## Why it works
A dotted rhythm crosses the beat, which gives motion from repeated notes alone; tying the pitches to the chords
guarantees they fit; a changed ending tells the ear where the phrase stops, so the repeat feels intended.
