---
title: Let the bass answer the melody: passing notes placed where the melody rests
topic: bass
genres: [progressive house, tech house, bass house]
source: Alex Rome — How To Get That 'Pro Sound' (as a beginner producer) (https://youtu.be/Uazkku5yuM8?t=470)
status: untested
---
## What it is
A melody with big gaps leaves blank space. Instead of filling it with another instrument, the bass leaves its root for
a moment in exactly those gaps, so melody and bass take turns. He calls it the bass "melodically communicating" with
the lead and offers it as a pro tip.

## When to use it
A bassline that sits on chord roots and feels like wallpaper, under a melody that has clear rests. Skip it when the
melody is continuous: there is no gap to answer in.

## How
1. Look at the melody's piano roll and find the rests between its groups of notes (said,
   [8:00](https://youtu.be/Uazkku5yuM8?t=480)).
2. Keep the bass on the chord's bottom note while the melody plays (said, [6:04](https://youtu.be/Uazkku5yuM8?t=364)).
3. Where the melody takes a break, add passing notes in the bass (said, [8:11](https://youtu.be/Uazkku5yuM8?t=491)).
4. What his look like (shown [8:28](https://youtu.be/Uazkku5yuM8?t=508)): one long root per chord, plus a few very
   short notes on the same track, well above the root, one mid-chord and one just before the next chord. With the
   arpeggiator on the track each short note becomes one or two quick higher hits.
5. Which pitches: not said, and not legible in the frame. Ours, inferred: notes of the current chord or scale steps
   that lead to the next root; an octave or a fifth above the root is the safe first try.
6. Keep them short and few. The root must still be what the ear hears as the bass (inferred from the note lengths
   shown).
7. Listen with only melody and bass: the two should alternate, not pile up (said in effect,
   [8:16](https://youtu.be/Uazkku5yuM8?t=496)).

## In Rohil's setup
In `song.py` derive the gap positions from the melody's notes (the steps where the lead is silent for an eighth or
more) and write the passing notes there by hand, as two or three `option()` variants to compare with `rick-rubin ab`.
In Logic, open the lead and bass regions together in the piano roll (select both regions) so the gaps are visible
while editing the bass. Passing notes an octave up leave the 40 to 80 Hz zone for a moment: that is fine for short
notes, and keeps the sub steady.

## How to check it
`rick-rubin score <dir> --tracks Lead Bass --bars <section>`: bass onsets other than the roots should fall where the
lead has rests, and lead onsets where the bass holds. `rick-rubin hits` on a lead-plus-bass bounce: fewer empty steps
than before. Then an audition for Rohil of lead and bass alone, before and after.

## Why it works
Call and response: two parts that take turns are both heard clearly, and the listener's attention is passed back and
forth instead of dropping in the gaps (inferred).
