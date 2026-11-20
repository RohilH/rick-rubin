---
title: Choose the bass octave on an analyzer: the strongest peak belongs between 40 and 80 Hz
topic: bass
genres: [tech house, bass house, progressive house, any]
source: Alex Rome — This Producer's Bass Was Weak. Here's the Fix. (https://youtu.be/HLCi1uYq8r0?t=368)
status: untested
---
## What it is
A rule he repeats in three videos: write the bass notes, open an EQ with its analyzer on the bass track, and move the
part by octaves until its strongest peak sits between 40 and 80 Hz for every note.

## When to use it
Every time bass notes are written or transposed, when a key change moves the bassline, and when a bass "does not sound
like a bass" or cannot be heard on some speakers.

## How
1. Write the notes (chord roots, or a line around the tonic) at any octave.
2. Put an EQ with an analyzer on the track and keep it open while writing (said,
   [6:25](https://youtu.be/Uazkku5yuM8?t=385)).
3. Play it. If the peak is above 80 Hz, drop an octave and look again (said,
   [5:46](https://youtu.be/HLCi1uYq8r0?t=346)).
4. Target: the strongest frequencies between 40 and 80 Hz "consistently", meaning for every note of the line (said,
   [6:08](https://youtu.be/HLCi1uYq8r0?t=368)). He says this range sounds best on all speaker systems (said,
   [6:35](https://youtu.be/Uazkku5yuM8?t=395)).
5. What it looks like: Channel EQ's analyzer with a fundamental just above 50 Hz for G#0 in Logic's naming and smaller
   harmonics above it (shown [6:18](https://youtu.be/HLCi1uYq8r0?t=378)); in another track one clean peak near 75 Hz
   (shown [6:42](https://youtu.be/Uazkku5yuM8?t=402)).
6. The same check is used when a chord sound is converted to bass (said, [3:58](https://youtu.be/u8ozR9cnCTU?t=238)).
7. The arithmetic (ours): 40 to 80 Hz is one octave, roughly E0 to E1 in Logic's naming (41 to 82 Hz). So each pitch
   class has exactly one octave that qualifies, and a line that spans more than an octave cannot keep every note
   inside: the low notes go under 40 Hz or the high ones over 80 Hz.

## In Rohil's setup
Channel EQ is Logic's own; its analyzer is the picture he uses. Without opening Logic: `rick-rubin notes <dir> <bass
bounce>` prints each note's pitch with octave, and `rick-rubin serum describe "<preset>" --note G#0` gives the band
split for one note of the patch. In `song.py`, write bass roots between E0 and E1 (Logic naming) and treat a note
outside that as a decision to justify. A sub in this octave is inaudible on a phone by itself: add harmonics
(`../sound-design/alex-rome-sine-sub-with-distortion.md`) or a mid layer.

## How to check it
`rick-rubin spectrum <dir> bounces/bass.wav`: the tallest peak for each note between 40 and 80 Hz. `rick-rubin serum
describe` on the lowest and highest note of the line: sub-band share should dominate on both. In the mix, `rick-rubin
reference compare`: sub and bass shares inside the range of the references for that genre.

## Why it works
Below about 40 Hz most systems reproduce little, and above 80 Hz the note leaves the sub and crowds the kick's punch
and the low mids; one octave in between is where a club system has power and the kick leaves room (inferred; he states
only that it translates best).
