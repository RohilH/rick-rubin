---
title: A rolling one-root bassline: straight 8ths first, then a semitone neighbour and single octave pops
topic: bass
genres: [tech house]
source: MOONBOY — HOW TO TECH HOUSE (John Summit, Dom Dolla, Chris Lake,) (https://youtu.be/_4qJSUFao50?t=146)
status: untested
---
## What it is

His 2023 way to write a tech house bassline, different from the offbeat method in
`bass/moonboy-offbeat-bassline-and-its-variations`: the bass plays almost all the time on one low root, a
note one semitone above it gives the dark colour, and a single 16th an octave up gives the bounce.

## When to use it

For a driving, busy groove bass (John Summit, Dom Dolla style) where the offbeat line feels too empty. It
plays on the kick's beats too, so it needs sidechain; the offbeat method does not.

## How

1. Root on D or D sharp: his preference, because it hits the subs hard (said,
   [2:52](https://youtu.be/_4qJSUFao50?t=172)). On screen the notes are D1, with Serum's octave at 0 when the
   patch was made (shown; whether he lowered it later is not visible).
2. First draft: straight 8th notes on the root for two bars, but the first 8th of each bar is a semitone up
   (D#1, then D1 for the rest of the bar) (shown at [3:18](https://youtu.be/_4qJSUFao50?t=198)).
3. Then "play around with the rhythm" (said). The finished bar, in 16th steps (shown at
   [3:25](https://youtu.be/_4qJSUFao50?t=205)): root held for steps 1 to 3; root 4 to 5; one 16th an octave
   up on step 6; the neighbour (D#1) on 7 to 8; step 9 silent; root on 10; neighbour 11 to 12; root 13 to 14;
   root 15 to 16 with another octave-up 16th on step 16. Bar 2 repeats it.
4. So the only gap in the bar is the 16th on beat 3, and the octave pops sit on the 16th after beat 2 and
   the last 16th before the next bar (shown).
5. All velocities 100, no groove on the clip (shown).
6. Add pitch bends (next card) and, "if you're feeling crazy", more octave and rhythm changes (said).

Take the method (one root, one neighbour, pops on weak 16ths, one gap), not his steps.

## In Rohil's setup

Sound: the pluck bass card; here he starts from a square instead of a saw (Basic Shapes, MG Low 12, cutoff
205 Hz, LFO 1 as a one-shot falling curve at 1/4: shown at [2:05](https://youtu.be/_4qJSUFao50?t=125)). Mono
on, so repeated notes retrigger cleanly. Because notes land on the kick: `rick-rubin logic insert Bass
"Kickstart 2" Mix=0.7`. In a `song.py`, write this and the offbeat version as two variables and compare.

## How to check it

`rick-rubin score <dir> --bars 1-2 --tracks Bass`: three pitches only (root, root + 1 semitone, root + 12).
`rick-rubin hits <dir> --tracks Kick Bass --bars 1-4`: bass energy on nearly every step before the sidechain,
dips on steps 1, 5, 9, 13 after it. `rick-rubin eval`: no kick and bass collision warnings once it ducks.

## Why it works

A flat second above the root is the darkest step there is (inferred: D with E flat is the Phrygian colour),
so one extra note is enough to sound like a riff, and an octave pop is heard as rhythm rather than melody.
