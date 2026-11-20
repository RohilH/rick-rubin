---
title: Ten chord loops by mood, and the three voicing moves that make them work
topic: harmony
genres: [any, progressive house]
source: Alex Rome — 10 Chord Patterns for 10 Different Emotions (https://youtu.be/_yw85rAb6cw?t=0)
status: untested
---
## What it is
A lookup of ten moods against the scale degrees Alex Rome uses for each, with the key he demonstrates in. It is a
vocabulary for choosing where a breakdown or a hook should sit emotionally, not a set of parts.

## When to use it
At the brief stage ("what should this section feel like?") and when a progression is correct but flat: find the row,
then go to its card for the voicing and rhythm, which is where the feeling comes from.

## How
| # | Mood | Degrees | Example (said key; chords shown) | Extra move | Card |
|---|---|---|---|---|---|
| 1 | uplifting, euphoric | v–VI–VII–i | D# minor: A#m B C# D#m | pedals on degrees 7 and 3 | [1](alex-rome-uplifting-v-vi-vii-i.md) |
| 2 | serious, or hopeful | VI–VII–i–VII | B minor: G A Bm A | melody picks minor or major | [2](alex-rome-deep-serious-vi-vii-i-vii.md) |
| 3 | tense | i | G minor: Gm, held | bass and sound move instead | [3](alex-rome-tense-one-chord.md) |
| 4 | sad | i–VII–iv–VI | G minor: Gm F Cm Eb | pedal on the tonic | [4](alex-rome-sad-i-vii-iv-vi.md) |
| 5 | feel-good | VI–III–VII–i | B minor: G D A Bm | pedals on 3 and 7; 3+5 beat rhythm | [5](alex-rome-feel-good-vi-iii-vii-i.md) |
| 6 | bittersweet | VI–i–VII–v | G# minor: E G#m F# D#m | pedals on 3 and 7; 5+2+7+2 beats | [6](alex-rome-bittersweet-vi-i-vii-v.md) |
| 7 | pumped, dark | i–i–VI–iv | G minor: Gm Gm Eb Cm | thirds doubled on a 2nd synth | [7](alex-rome-dark-pump-up-i-vi-iv.md) |
| 8 | pumped, happy | i–i–III–VI | G minor: Gm Gm Bb Eb | no thirds, fifths doubled | [8](alex-rome-happy-pump-up-i-iii-vi.md) |
| 9 | chill | VI–i–VII–i | C# minor: A C#m B C#m | tonic drone, held top note | [9](alex-rome-chill-vi-i-vii-i.md) |
| 10 | cheerful | IV–V–I (major) | D major: G A D | roots only + tonic pedal | [10](alex-rome-all-major-iv-v-i.md) |

The three moves he repeats (said throughout, shown in every piano roll):
1. Lift the third of each triad an octave, leaving root and fifth below (root, fifth, tenth).
2. Hold one or two scale notes above the chords through the whole loop (a pedal): degree 3, 7 or 1.
3. Double one chord tone on a second sound: the third for emotion, the fifth for power.

## In Rohil's setup
Nine of ten are natural minor, so they sit in the keys house already uses. Write the chords for the song in
`song.py` (or by hand in his Logic piano roll), with chord tones above C2 so they stay clear of the bass. The pedal
and the doubled tone are best as their own tracks, so each can have its own sound, filter and entry point.

## How to check it
`rick-rubin score <dir> --tracks <chords>` reads back what each bar holds. Then a bounce of plain triads against the
revoiced version for Rohil to compare, recorded with `rick-rubin verdict`. Nothing here is measurable as "right".

## Why it works
Row for row these are common diatonic loops; the moods come from which chords are major, where the loop ends, how
long each chord lasts, and the colour notes the pedals add (inferred from his ten examples).
