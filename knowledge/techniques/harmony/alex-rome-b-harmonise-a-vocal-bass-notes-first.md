---
title: Write chords under a vocal from the bottom up: bass notes first, then a third, then a pedal
topic: harmony
genres: [any, progressive house, tech house, bass house]
source: Alex Rome — My Insanely Simple System for Remixing Any Song (The 3-STEP FLIP) (https://youtu.be/bx8X7oiYhCg?t=62)
status: untested
---
## What it is
How Alex Rome finds chords for an existing vocal. He does not pick a progression; he tries single low notes
against the vocal until the pair sounds right, and only then stacks a little on top. He does the same thing in
three of the four videos digested here.

## When to use it
New chords for an acapella (Rohil's remix), or re-harmonising a hook whose original chords do not suit house.

## How
1. Loop the vocal phrase. Use the dullest sound available, a piano or one saw through a low-pass, so the notes
   are judged and not the sound (said, [1:02](https://youtu.be/bx8X7oiYhCg?t=62); shown
   [1:15](https://youtu.be/bx8X7oiYhCg?t=75): Serum, one saw, MG Low 24).
2. Stay in the vocal's key (said, [2:06](https://youtu.be/XlltkalLaU4?t=126)).
3. Write only the bottom notes, one long note per chord. They are what decides the harmony with the vocal (said,
   [1:23](https://youtu.be/bx8X7oiYhCg?t=83)). Try several sets, save every one, and choose afterwards; he will
   spend hours here (said, [2:46](https://youtu.be/XlltkalLaU4?t=166)).
4. Add a third above each bottom note, major or minor, whichever is in key (3 or 4 semitones; shown as an
   on-screen note at [2:20](https://youtu.be/kSXHTJJ7D34?t=140)). Leave the fifths out (said,
   [1:43](https://youtu.be/bx8X7oiYhCg?t=103)). In the trench video the third sits an octave higher, a tenth
   above the bottom note (shown [3:55](https://youtu.be/XlltkalLaU4?t=235)). His view: current dance chords are a root plus one or two notes,
   with the vocal or melody on top, not four- and five-note stacks (said,
   [3:51](https://youtu.be/XlltkalLaU4?t=231)).
5. Add a pedal: one note held across every chord, above the thirds, and perhaps a couple of passing notes. He says
   the pedal is what makes it serious (said, [2:03](https://youtu.be/bx8X7oiYhCg?t=123); shown
   [2:15](https://youtu.be/bx8X7oiYhCg?t=135) and [4:40](https://youtu.be/XlltkalLaU4?t=280): one unbroken note
   over four chords, each chord two bars).
6. Choose the octave last; if the voicing is too low, move all of it up (said,
   [4:13](https://youtu.be/XlltkalLaU4?t=253)).
7. Variant: start from the held top note, find bottom notes that sound good under it, then move the top notes to
   thirds (said, [0:55](https://youtu.be/kSXHTJJ7D34?t=55)).

In the remix the frame at 2:15 reads bottom notes F#, G#, F# under bars 3 to 8 with a major, minor and major third
and a D# held on top (the first bottom note is off screen): this looks like his VI–VII–i–VII loop in G# minor
(inferred; see `alex-rome-deep-serious-vi-vii-i-vii.md`).

## In Rohil's setup
`rick-rubin notes <dir> samples/vocal.wav` gives the vocal's pitches with octave and its key fit; `rick-rubin
transcribe` shows where the phrases start. A rapped verse is mostly unpitched, so it leaves the harmony almost
free: let the sung hook, or the key of the original's bass stem, set the scale (inferred). The writing sound is
`sound-design/alex-rome-filtered-saw-pad.md`. Write three or four sets of bottom notes as alternatives and bounce
each under the vocal (PREFERENCES §3).

## How to check it
`rick-rubin notes` on the vocal against `rick-rubin score <dir> --tracks Chords`: the vocal's long notes are chord
tones or the pedal note, and nothing sits a semitone from a held chord tone. Which set to keep is his verdict.

## Why it works
The ear hears a melody note against the lowest note first, so the bottom line fixes most of the harmony; the third
adds major or minor; the fifth adds weight but little colour, and leaving it out keeps room for the vocal (the
last clause is inferred).
