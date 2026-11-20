---
title: Wash an atmosphere bed in a bright, thinning reverb to create the top end a dark section lacks
topic: sound-design
genres: [progressive house, bass house, any]
source: RYOS — KSHMR asked me to remix his song.. here's how I did it (https://youtu.be/mvZPg8zv_ig?t=126)
status: untested
---
## What it is
In a break whose main sound is a bass, the only bright element is the vocal. Instead of adding a bright
instrument he drowns a quiet atmosphere bed in a very bright reverb, on purpose, so the reverb itself is
the air.

## When to use it
A dark break or intro that feels "empty" or "lifeless" on top although nothing is missing musically; a
section where another instrument would crowd the vocal.

## How
1. Take a textured bed. His is a gated vocal atmosphere from his own pack, pitched up 2 semitones to the
   track's key (said, [1:02](https://youtu.be/mvZPg8zv_ig?t=62)).
2. Put a bright reverb on the insert and overdo it. He uses Dada Life's Endless Smile, a build-up effect,
   as a static reverb: intensity left at 50 %, never automated (said and shown,
   [2:30](https://youtu.be/mvZPg8zv_ig?t=150); preset "Fist in the Air").
3. Why that unit and not his usual room reverb: on its soft setting, raising the intensity thins the signal
   out and adds a bright reverb he finds unique to it (said, [2:28](https://youtu.be/mvZPg8zv_ig?t=148)).
4. The aim is stated plainly: lots of air and top-end energy from the reverb, because apart from the vocal
   few elements have highs; without it the break feels empty (said,
   [3:11](https://youtu.be/mvZPg8zv_ig?t=191)).
5. Let it arrive gradually: the bed begins behind a low-pass, close to inaudible, and opens over the
   section (said, [7:03](https://youtu.be/mvZPg8zv_ig?t=423)).
6. Utility plug-ins follow the reverb, so filter, level and pump act on the wet sound (shown,
   [1:40](https://youtu.be/mvZPg8zv_ig?t=100)).

## In Rohil's setup
He does not own Endless Smile. Nearest: Valhalla Supermassive or ChromaVerb on the insert at a high mix,
then a Channel EQ after it with a low cut around 300 to 500 Hz and a high shelf up, which does the
"thinning" by hand (our translation; lost: one knob that thins and brightens together). `rick-rubin logic
insert "Atmos bed" "Valhalla Supermassive"`, then `rick-rubin logic insert "Atmos bed" "Channel EQ"`; read
names with `rick-rubin logic devices` before `logic tweak`. Opening filter: AutoFilter, automated by hand.
This contradicts the usual advice in `alex-rome-eq-the-reverb.md` (cut the reverb's highs) on purpose: here
the reverb is the part.

## How to check it
`rick-rubin spectrum <dir> --mix --bars A-B` on the break with the bed muted and unmuted: energy above
about 8 kHz should rise with it in, and the 1 to 4 kHz band where the vocal sits should barely change.
`rick-rubin width <dir> bed.wav`: wide on top, correlation not negative. Then the two bounces for Rohil.

## Why it works
Reverb tails are diffuse and have no transients, so they add brightness without adding an event that
competes with the vocal for attention.
