---
title: Dynamic lead layering: state the hook on a gentle sound, then hand it to high-energy layers
topic: sound-design
genres: [progressive house, bass house]
source: Alex Rome — 7 Useful Layering Techniques and Why They Work (https://youtu.be/u8ozR9cnCTU?t=366)
status: untested
---
## What it is
The same melody and chords exist twice: once on a soft sound, once on a stack of expressive, loud layers. The soft
version runs for a few loops, then the stack takes over. He dates it to big room house and shows it on a remake of
Avicii and Nicky Romero's "I Could Be the One".

## When to use it
Break into drop, or the first and second half of a drop, when the hook should arrive twice: once to be learned, once
to hit. It needs a hook strong enough to survive on a plain sound.

## How
1. Write the hook (melody with chords under it) on a soft, gentle sound (said,
   [6:18](https://youtu.be/u8ozR9cnCTU?t=378)).
2. Copy only the melody notes, without the chords, to a high-energy, expressive lead (said,
   [6:30](https://youtu.be/u8ozR9cnCTU?t=390)).
3. Copy the chords to a second expressive sound and give them a rhythm instead of holding them (said,
   [6:53](https://youtu.be/u8ozR9cnCTU?t=413)).
4. Add to the chords a piano layer and another synth layer (said, [7:13](https://youtu.be/u8ozR9cnCTU?t=433)).
5. Add a second layer to the lead as well (said, [7:34](https://youtu.be/u8ozR9cnCTU?t=454)).
6. Arrange: the gentle version for a couple of loops, then switch to the stack (said,
   [7:40](https://youtu.be/u8ozR9cnCTU?t=460)). The gentle sound stops or drops under when the stack enters (inferred
   from the playback; not stated).
7. The sounds are not named and no settings are shown; "high energy" in the remake means bright, sustained saw leads
   (inferred).

## In Rohil's setup
The stack is the lead stack already described by Ryos: `ryos-pg-lead-stack-six-roles.md` (which layers) and
`ryos-lead-stack-centre-anchor-then-widen.md` (centre first, then width). The new part here is the staging in time. In
`song.py`: one set of note variables, a soft `serum=` track active in the first section and the stack's tracks active
from the hand-over; the melody-only layer takes the top line, the chord layers get a written rhythm. For the soft
sound start from a pluck or keys patch (`rick-rubin serum search "soft keys"`), for the loud lead a supersaw:
`rick-rubin serum set init osc_a.unison=7 osc_a.detune=0.2 --save hook-saw --project <dir>`.

## How to check it
`rick-rubin compare <dir> soft_section.wav stack_section.wav`: the stack should be louder, brighter (more high and air
share) and wider. If the two sections measure nearly the same, the contrast that makes the technique work is missing.
Then Rohil hears the hand-over bar on a bounce.

## Why it works
The listener already knows the tune when the big sound arrives, so the change is heard as energy, not as new
information to process (inferred).
