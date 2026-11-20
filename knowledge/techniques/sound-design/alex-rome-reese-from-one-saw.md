---
title: Reese bass from one saw, high unison and a low cutoff
topic: sound-design
genres: [bass house, tech house]
source: Alex Rome — How To Make Any Sound From Scratch (https://youtu.be/p1-WmITJqBk?t=824)
status: untested
---
## What it is
The filtered saw bass with unison turned up: a dozen detuned saws beating against each other under a steep low-pass.
He names it as the famous reese (the captions garble the word).

## When to use it
Sustained, growling bass notes: bass house drops, darker tech house, the low layer of a build. Less suited to short,
punchy off-beat notes, because the beating makes every note start differently.

## How
1. From the filtered-wave bass: saw, MG Low 24, notes low (said, [13:44](https://youtu.be/p1-WmITJqBk?t=824)).
2. Unison up high: 12 voices (shown [14:10](https://youtu.be/p1-WmITJqBk?t=850)).
3. Cutoff low: 240 Hz in the frame (shown [14:10](https://youtu.be/p1-WmITJqBk?t=850)).
4. Detune and blend at Serum's defaults (inferred: not touched).
5. Ours, not in the video: the beating also happens in the sub, so the low end goes wide and uneven. Keep the lows
   mono inside the patch, or layer a separate mono sub and high-pass the reese.

## In Rohil's setup
```
rick-rubin serum set init osc_a.unison=12 filter_1.on=on "filter_1.type=MG Low 24" filter_1.cutoff_hz=240 \
    fx.utility.lfmono=1 fx.utility.lfxover=150 --fx-add utility --save reese --project <dir>
```
Variables worth an `ab`: `osc_a.detune` (0.1 to 0.4), `osc_a.unison` (5 to 12), `filter_1.cutoff_hz` (150 to 600),
`filter_1.drive`. Kickstart 2 or a kick-keyed compressor on the track as for any bass.

## How to check it
`rick-rubin serum describe ... --note G0`. One render here without the utility unit: side energy about 50 % in the
low band, 66 % of energy in sub and 34 % in bass, measured attack 815 ms because of the beating. With
`fx.utility.lfmono=1` at 150 Hz the low-band side fell from 49.8 % to 1.1 % while the bands above stayed wide. That
drop is the number to look for; then a bounce in context and Rohil's verdict.

## Why it works
Slightly detuned saws cancel and reinforce each other at slowly changing rates, which is heard as movement and growl
without any modulation. The low-pass keeps only the harmonics where that beating is slow enough to feel like weight
(inferred).
