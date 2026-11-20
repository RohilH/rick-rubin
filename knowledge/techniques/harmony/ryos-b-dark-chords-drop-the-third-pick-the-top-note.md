---
title: Darker chords: take the third out of each triad, then pick the top note by inverting
topic: harmony
genres: [progressive house, bass house, any]
source: RYOS — Pro Secrets for Creating EDM Breakdowns (https://youtu.be/l_XjHmumqQk?t=574)
status: untested
---
## What it is
A way to make a minor progression sound creepy and mean instead of emotional: play each chord as root and
fifth only, then move notes by octaves until the highest notes of the chords form the line you want to hear.

## When to use it
A break or intro that should feel dark, tense or mysterious, and any time full triads sound too pretty for the
track. Not for an emotional progressive house break, where the third carries the feeling.

## How
1. Start from the bassline and its plain triads. His: G minor for two bars, then D sharp major and C minor for
   one bar each (said, [9:56](https://youtu.be/l_XjHmumqQk?t=596); lengths shown,
   [8:25](https://youtu.be/l_XjHmumqQk?t=505)).
2. Delete the middle note, the third, of every triad. Root and fifth are left: a power chord. His reason: for
   a darker vibe, less harmony is better (said, [10:17](https://youtu.be/l_XjHmumqQk?t=617)).
3. Listen to the highest note of each chord as a melody; he says to always check this. After step 2 his top
   line was D, A sharp, G. He wanted D, D sharp, C: a semitone up, then down (said,
   [11:00](https://youtu.be/l_XjHmumqQk?t=660)).
4. Get that line by inversion: take the top note of each chord that is wrong down an octave, so the root ends
   up on top. No new notes are added (said, [11:40](https://youtu.be/l_XjHmumqQk?t=700)).
5. Final voicings, low to high (shown, [8:25](https://youtu.be/l_XjHmumqQk?t=505)): G, G, D; then D sharp,
   A sharp, D sharp; then C, G, C. The octave numbers on screen are not readable.
6. It is played by one mid-range sound with nothing above about 1 kHz (see
   `sound-design/ryos-b-break-chords-high-cut-then-ott-for-the-tail.md`).

## In Rohil's setup
In a `song.py` write the three voicings out note by note; the rule is the card, the notes are the song's. In
his own Logic project the regions are his to edit: offer the revoiced chords as a file with
`rick-rubin logic add-midi chords_dark.mid --bar N --name "Chords dark"` beside the original, so he can compare.

## How to check it
`rick-rubin score <dir> --tracks Chords`: every chord holds two pitch classes (root, fifth), and the top voice
reads as the intended line. "Darker" has no number: bounce the triad version and the power-chord version of
the same bars for Rohil and record his verdict.

## Why it works
The third is the note that says major or minor and gives a chord its warmth; without it the chord is hollow
and ambiguous. The ear follows the highest note, so the top line is the real melody of a chord part, and a
semitone step in it is the tense interval.
