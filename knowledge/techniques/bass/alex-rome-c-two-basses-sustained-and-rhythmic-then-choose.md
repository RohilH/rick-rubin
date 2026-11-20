---
title: Write a sustained bass and a rhythmic bass from the same roots, test each in stages, then choose
topic: bass
genres: [tech house, progressive house, bass house]
source: Alex Rome — This Producer's Bass Was Weak. Here's the Fix. (https://youtu.be/HLCi1uYq8r0?t=284)
status: untested
---
## What it is
For a track with chords and melodies but no bassline, he does not guess the bass style. He builds the two basic kinds
on the same notes, a held root per chord and a rhythmic line, and lets the track decide.

## When to use it
Whenever a bass is being added to existing music, and whenever the current bass feels wrong but it is unclear whether
the problem is the notes, the rhythm or the sound.

## How
1. Notes for both: the root of each chord, taken by copying the chord region and keeping the roots (said,
   [4:44](https://youtu.be/HLCi1uYq8r0?t=284); shown [5:12](https://youtu.be/HLCi1uYq8r0?t=312)).
2. **Sustained**: one long note per chord on the plain filtered-saw sub
   (`../sound-design/alex-rome-filtered-wave-bass.md`), in the octave that peaks at 40 to 80 Hz.
3. Sidechain it. On a held bass the duck is also the only movement: without it the part is static (said,
   [7:51](https://youtu.be/HLCi1uYq8r0?t=471)). Try a long pump and a quick one
   ([8:12](https://youtu.be/HLCi1uYq8r0?t=492)).
4. **Rhythmic**: the same roots in the rhythm of the busiest melody (said,
   [9:26](https://youtu.be/HLCi1uYq8r0?t=566)), on a plucked sound
   (`alex-rome-c-rhythmic-bass-needs-a-plucked-sound.md`). He says to always try this one in a deep, groovy track.
5. Test each bass in stages: with the drums only; with one lead; with the next melody; with the vocal; then from a few
   bars before the section, to hear the transition (said, [11:17](https://youtu.be/HLCi1uYq8r0?t=677),
   [12:20](https://youtu.be/HLCi1uYq8r0?t=740)). If it works with drums and a single instrument, it will work in the
   full mix (said, [11:39](https://youtu.be/HLCi1uYq8r0?t=699)). The same habit as a general rule:
   `../workflow/alex-rome-b-two-checks-before-moving-on.md`.
6. Choose, then switch to a released track and back to see whether it stands up (said,
   [12:41](https://youtu.be/HLCi1uYq8r0?t=761)). He picks the rhythmic bass and notes the sustained one is the
   mellower option, also valid.

## In Rohil's setup
In `song.py`: both lines as `option()` choices on the bass track, `rick-rubin ab` to build and measure each in
context, an audition of each for Rohil. In his Logic project: two bass tracks, one muted at a time (`rick-rubin logic
set "Bass sustained" mute=on`), and staged bounces for the comparison: `rick-rubin logic bounce bounces/a_drums.wav
--bars 43-50 --tracks Kick Tops "Bass sustained"`, then with a lead added.

## How to check it
`rick-rubin compare <dir> sustained.wav rhythmic.wav` on the full section: similar sub share (same notes, same
octave); the rhythmic one shows more movement and transient density, the sustained one a deeper pump. Neither is right
by measurement: the numbers show the difference, Rohil's verdict (`rick-rubin verdict`) picks.

## Why it works
Bass style changes the whole feel of a section, and it cannot be predicted from the chords alone. Two candidates on
identical notes isolate the one variable that matters, rhythm and envelope (inferred).
