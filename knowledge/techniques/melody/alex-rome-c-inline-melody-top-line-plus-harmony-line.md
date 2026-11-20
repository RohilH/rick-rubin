---
title: Inline melody: a top line plus a second line below in the same rhythm, so the harmony is in the melody
topic: melody
genres: [progressive house, tech house, any]
source: Alex Rome — 5 Melody Styles Every Hit Song Uses (https://youtu.be/cjyEdyEWXbQ?t=18)
status: untested
---
## What it is
A melody that carries its own harmony. Under the top line runs a lower line that copies its rhythm and changes pitch
slowly; the interval between the two implies the chord. Others call it an embedded or chordal melody. It is why a
piano-house riff sounds complete with nothing else playing.

## When to use it
A melody that sounds "out in thin air" on its own. Breaks and intros where the hook must stand alone, and any section
where a separate chord track would be too much.

## How
1. Write the top line first and get it to a point where it "speaks to you" (said,
   [2:13](https://youtu.be/cjyEdyEWXbQ?t=133)). His example repeats each pitch in a 3+3+2 sixteenth grouping and stays
   on one pitch for most of a bar (shown [0:58](https://youtu.be/cjyEdyEWXbQ?t=58)).
2. Copy only its rhythm to a lower octave (said, [2:33](https://youtu.be/cjyEdyEWXbQ?t=153)). In the frames the lower
   line sits well over an octave below the top line (shown [2:15](https://youtu.be/cjyEdyEWXbQ?t=135); the exact
   intervals are not legible).
3. Choose one lower pitch per bar (said, [3:00](https://youtu.be/cjyEdyEWXbQ?t=180)). Try several within the octave;
   keep one if it "brings life" to the top line, else try the next (said, [3:18](https://youtu.be/cjyEdyEWXbQ?t=198)).
   Spend more time here than on the top line (said, 2:13).
4. Different lower lines change the mood of the same top line: one of his tries turns it noticeably happier (said,
   [3:42](https://youtu.be/cjyEdyEWXbQ?t=222)).
5. It can stay as two lines, or each lower note can be treated as a chord root and filled out; his become F, G, A
   minor and C (said, [4:28](https://youtu.be/cjyEdyEWXbQ?t=268)).
6. How to choose the lower note (ours, inferred): it should make a third, fifth, sixth or octave with the top note
   that is sounding longest in that bar; a second or a seventh against a held top note will sound tense.

## In Rohil's setup
In `song.py` write the top line, then derive the lower line's onsets from it and write its pitches by hand, one
decision per bar, as two or three alternatives to compare (`rick-rubin ab`). Both lines go to the same sound first;
later they can be split onto two sounds (`../sound-design/alex-rome-c-line-layering-one-sound-per-line.md`). In Logic:
duplicate the region, select all, transpose down an octave, then drag each bar's notes to one pitch.

## How to check it
`rick-rubin score <dir> --tracks Lead --bars <section>`: both lines should have identical onsets; `rick-rubin check`
runs the music lint on them. By ear, on an audition file: mute everything else; the two lines alone should suggest the
progression. If Rohil cannot hum where the chords change, the lower line is not doing its job.

## Why it works
Two notes a consonant interval apart are enough for the ear to infer a chord, and because the lower line moves with
the melody's rhythm it is heard as part of the melody, not as accompaniment (inferred; he says the bottom line
"grounds" the top line).
