---
title: Lead melody: build the drop first, loop it, and write many candidate hooks over it
topic: melody
genres: [progressive house, bass house, any]
source: Alex Rome — 5 Melody Styles Every Hit Song Uses (https://youtu.be/cjyEdyEWXbQ?t=1020)
status: untested
---
## What it is
The lead is the line that sits on top of the drop and is what people remember. His method is about order and volume of
attempts, not a formula: chords first, then the rest of the drop, then many melodies tried against the loop, in more
than one kind of sound.

## When to use it
For the main hook of a progressive house or big-room style drop. Not for sections driven by a bass melody or a pulse
(see `alex-rome-c-five-melody-roles-overview.md`).

## How
1. Start from a chord progression (said, [17:54](https://youtu.be/cjyEdyEWXbQ?t=1074)). His is F, G, A minor, C,
   voiced as open intervals, which he calls his chord style.
2. Build out the drop around the chords before writing the lead: drums, bass, chord sound (said,
   [18:20](https://youtu.be/cjyEdyEWXbQ?t=1100)).
3. Loop the drop and "lock into it": ask what kind of melody the section wants (said,
   [18:40](https://youtu.be/cjyEdyEWXbQ?t=1120)).
4. Write melodies, "tons of them". Play on the keyboard for ideas; work on rhythm as much as pitch (said,
   [18:50](https://youtu.be/cjyEdyEWXbQ?t=1130), [19:20](https://youtu.be/cjyEdyEWXbQ?t=1160)).
5. Try the hook in different kinds of sound. A synth lead is one option; he finds it harder to make work now (his
   opinion, [19:32](https://youtu.be/cjyEdyEWXbQ?t=1172)). The other he tries on the same drop is a vocal stutter (see
   `../sound-design/alex-rome-c-vocal-stutter-lead-with-a-trance-gate.md`).
6. A lead should be the easiest part of the track to remember (said, [17:34](https://youtu.be/cjyEdyEWXbQ?t=1054)).
   His references are Avicii leads, including "Levels".
7. What makes a candidate memorable (ours, inferred; he does not say here): few distinct pitches, a rhythm that
   repeats, chord tones on strong beats. Note-level methods: `alex-rome-b-dotted-rhythm-melody-that-resolves.md`,
   `ryos-melody-rhythm-symmetry.md`, `ryos-pg-two-rhythm-cells-melody.md`.

## In Rohil's setup
This is PREFERENCES section 3 applied to the hook. In `song.py` keep the drop fixed and write the lead as several
`option()` choices; `rick-rubin ab` builds and measures each in context, and each gets an audition file for Rohil.
Keep the rejected ones in the file with a line on why. In his own Logic project: loop the drop, record takes onto one
MIDI track, and keep them as take folders or muted regions instead of overwriting.

## How to check it
Measurement can only rule candidates out: `rick-rubin check` for key and range, `rick-rubin score` to see that the
lead's onsets do not all coincide with the chord stabs. The choice is by ear: an audition of each candidate over the
same eight bars, Rohil's verdict recorded with `rick-rubin verdict`. A hook he cannot recall an hour later is a draft.

## Why it works
A melody is judged against what it sits on, so writing it over the finished drop tests the real thing; and the odds of
a memorable hook go up with the number tried (inferred).
