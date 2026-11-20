---
title: A thin "robot" mid-bass layer: talking bass preset, barber-pole flanger, steep low cut, distortion
topic: sound-design
genres: [progressive house, bass house]
source: RYOS — Making Beautiful Progressive House | Studio Time with Ryos EP. 50 (https://youtu.be/WnZ7GN1tpek?t=1020)
status: untested
---
## What it is
A bass layer with no bass in it: a vocal-sounding patch made strange with a resonant moving flanger, cut off
below about 400 Hz, then distorted. It sits above the real bass and gives the drop a digital, talking edge.

## When to use it
A bass stack that is heavy but faceless. He hears it as a "true mid-range", almost high-mid, bass and expects
to add "a boatload of processing" to get there (said, [17:07](https://youtu.be/WnZ7GN1tpek?t=1027)).

## How
1. Start from a talking or formant bass preset; his is Spire's factory "BA Talking" (shown,
   [17:24](https://youtu.be/WnZ7GN1tpek?t=1044)). It plays the same notes as the main bass.
2. Flanger for weird movement, "as weird as possible" (said). Shown at
   [18:06](https://youtu.be/WnZ7GN1tpek?t=1086): ValhallaSpaceModulator, mode VariUp (one-directional barber-pole
   flanging), mix 43 %, rate 0.27 Hz, depth 5 ms, feedback 90 %, manual 0 ms.
3. EQ after the flanger so it also removes the lows the flanger creates (said,
   [18:09](https://youtu.be/WnZ7GN1tpek?t=1089)). Shown at [17:46](https://youtu.be/WnZ7GN1tpek?t=1066): low cut
   at 406 Hz, 48 dB/oct. Later a 12 dB/oct high cut is added in the upper mids (shown,
   [19:34](https://youtu.be/WnZ7GN1tpek?t=1174); frequency not readable).
4. Distortion last (Thermal, his favourite at the time; said, [18:13](https://youtu.be/WnZ7GN1tpek?t=1093)).
5. With the chain in place, swap the preset underneath until it sounds artificial and robotic enough (said,
   [18:25](https://youtu.be/WnZ7GN1tpek?t=1105)).

## In Rohil's setup
All inside one Serum 2 patch. This ran without error on this Mac (2026-11-20); the filter type, cutoff and
drive are our stand-ins for his preset and Thermal:
`rick-rubin serum set init filter_1.on=on filter_1.type="Formant-II" filter_1.cutoff_hz=900 fx.flanger.rate=0.27
fx.flanger.feedback=90 fx.flanger.wet=43 fx.utility.hpf=400 fx.distortion.drive=40 --fx-add flanger --fx-add
utility --fx-add distortion --save robot-mid --project <dir>` (settings go before the `--fx-add` flags; the rack
order came out flanger, utility, distortion). Measured on G1: bass band 76 % to 0 %, energy 64 % low-mid and
36 % mid. What is lost: Serum's flanger is a plain one, not a barber-pole; Supermassive cannot do it either.
The Valhalla plug-in he uses is a free download, not installed here. Start instead from a factory patch with
`rick-rubin serum list --search talk` if one exists.

## How to check it
`rick-rubin serum describe robot-mid --note G1 --secs 2 --bpm 128`: sub and bass shares 0 %, the word
`no-low-end`, movement at a slow rate from the flanger. On a bounce with the full bass stack,
`rick-rubin spectrum` should show this layer adding energy between about 400 Hz and 3 kHz only. Then
`rick-rubin serum audition` for Rohil: "robotic" is an ear call.

## Why it works
High feedback turns the flanger into a moving comb filter, which the ear reads as vowels. Cutting the lows
keeps it from fighting the sub and the main bass, so it can be loud enough to be heard as character.
