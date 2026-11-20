---
title: Filtered saw pad, widened with unison
topic: sound-design
genres: [progressive house, any]
source: Alex Rome — How To Make Any Sound From Scratch (https://youtu.be/p1-WmITJqBk?t=103)
status: untested
---
## What it is
The first sound he builds: a raw saw through a steep low-pass, which he calls one of the most used pads in
electronic music, then made wide by raising unison.

## When to use it
Breakdown chords, a bed under a lead, the sustained layer of a chord stack. It is also the starting point for the
pluck and swell cards.

## How
1. Init Serum; OSC A on the default saw; play chords (said; shown [1:40](https://youtu.be/p1-WmITJqBk?t=100)).
2. Filter 1 on, OSC A routed to it, type MG Low 24 (shown [2:12](https://youtu.be/p1-WmITJqBk?t=132)).
3. Bring the cutoff down by ear until the fizz is gone (said). The frame at
   [2:12](https://youtu.be/p1-WmITJqBk?t=132) reads 2770 Hz mid-sweep.
4. Raise unison for width: ten voices (said [5:16](https://youtu.be/p1-WmITJqBk?t=316); the counter shows 10 to 13
   between [5:00](https://youtu.be/p1-WmITJqBk?t=300) and [6:24](https://youtu.be/p1-WmITJqBk?t=384)). Detune and
   blend are left at Serum's defaults (inferred: never touched).
5. Watch a stereo meter while doing it: one voice is a thin vertical line, ten fill the half-circle (shown
   [5:00](https://youtu.be/p1-WmITJqBk?t=300), Ozone Imager 2).
6. For a slow, washy version: longer ENV 1 attack and release with a long reverb (shown
   [8:55](https://youtu.be/p1-WmITJqBk?t=535): attack 29 ms, release 6.1 s; ValhallaVintageVerb Concert Hall, mix
   about 30 %, decay 7.1 s).

## In Rohil's setup
```
rick-rubin serum set init filter_1.on=on "filter_1.type=MG Low 24" filter_1.cutoff_hz=2770 osc_a.unison=10 \
    env_1.attack_ms=29 env_1.release_ms=6000 --save saw-pad --project <dir>
```
Ozone Imager 2 is on this Mac for the same picture. Reverb: Supermassive or ChromaVerb on a send instead of
VintageVerb (its hall character is what is lost). Unison widens the lows too, so keep pad notes above C2 and low-cut
the track (see the low-cut card), or add `--fx-add utility` with `fx.utility.lfmono=1 fx.utility.lfxover=150`.

## How to check it
`rick-rubin serum describe` on a C3. One offline render here (cutoff 2770, unison 10): harmonics within 30 dB fell
from 31 to 10, brightness from 786 to 479 Hz, side energy went from 0 to about 50 % in every band, low band
included. Not yet heard by Rohil: `rick-rubin serum audition`, then `verdict`.

## Why it works
A saw has every harmonic, so the filter has something to remove at any cutoff. Detuned copies drift in and out of
phase differently in each ear, which the ear reads as width (the second sentence is inferred).
