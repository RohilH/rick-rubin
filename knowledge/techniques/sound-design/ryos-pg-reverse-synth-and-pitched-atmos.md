---
title: Break ear candy: an atmosphere swell pitched to the key and a reverse synth shot into each phrase
topic: sound-design
genres: [progressive house]
source: RYOS — Making Beautiful Progressive House | Studio Time with Ryos EP. 50 (https://youtu.be/WnZ7GN1tpek?t=230)
status: untested
---
## What it is
Two sample layers placed around the piano chords: a long tonal atmosphere swell retuned to a note of the key,
and a short reversed synth hit that ends exactly where a new 8-bar phrase starts, drenched in delay and reverb.

## When to use it
A break that has chords and a drone but feels static between phrase starts. He adds them right after the
chords, before the melody (said, [3:50](https://youtu.be/WnZ7GN1tpek?t=230)).

## How
1. Atmosphere: a long swelling sample (a brass-like texture from one of his tracks). Its name says D#; he
   pitches it down a semitone to D so it sits in the key (said, [4:13](https://youtu.be/WnZ7GN1tpek?t=253)).
2. Place the swells so they rise and fall across phrase boundaries; in the final layout they overlap bars 3 to
   10 and 11 to 18 (shown, [34:20](https://youtu.be/WnZ7GN1tpek?t=2060)).
3. Reverse synth: a one-bar reversed shot whose loudest point is its end; put the end on the bar where the next
   phrase begins, here bar 9 (melody in) and bar 17 (build in) (shown, 34:20; said,
   [4:38](https://youtu.be/WnZ7GN1tpek?t=278)).
4. Processing on the reverse shot, shown at [4:50](https://youtu.be/WnZ7GN1tpek?t=290): distortion, then a
   delay, then Valhalla Supermassive.
5. Swap the shot late if a better one turns up; he replaces it at the end (said,
   [33:09](https://youtu.be/WnZ7GN1tpek?t=1989)).
6. He jokes that the brass swell reminds him of a meme and keeps it anyway (said,
   [4:18](https://youtu.be/WnZ7GN1tpek?t=258)): the test is whether it suits the mood (inferred).

## In Rohil's setup
Splice for both samples. Read them first (PREFERENCES §6): `rick-rubin notes <dir> samples/atmos.wav` gives the
pitch with octave and cents; retune with `rick-rubin conform <dir> samples/atmos.wav --bpm 128 --transpose -1`
(Logic's own tools). Bring them in with `rick-rubin logic add-audio atmos.wav --bar 3 --name Atmos` and
`rick-rubin logic add-audio rev.wav --bar 8 --name "Rev synth"`; audio lands on the bar line, so trim or nudge
the reverse shot by hand until its end meets bar 9. Chain: Logic's Overdrive, Stereo Delay, then Supermassive,
which he owns: `rick-rubin logic insert "Rev synth" "Valhalla Supermassive"` (read its parameter names with
`rick-rubin logic devices "Valhalla Supermassive"` before setting any). Any Serum 2 note can be made into a
reverse shot by bouncing it and reversing the region in Logic.

## How to check it
`rick-rubin notes` on the retuned atmosphere: within about 10 cents of a scale note. `rick-rubin width --bars
1-16` on a bounce of the break: the low band still centred with the extra layers in. In `rick-rubin reference
compare`, texture changes per minute for the break should go up against the version without them.

## Why it works
A reversed sound is a small riser that points at one moment, so it announces a phrase without a drum fill. A
tonal swell in the key adds harmony-compatible movement in the gaps the piano leaves.
