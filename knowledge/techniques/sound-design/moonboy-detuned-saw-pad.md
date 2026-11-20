---
title: A wide pad from one saw: many unison voices, detune, a low-pass, phaser and reverb
topic: sound-design
genres: [bass house, progressive house, any]
source: MOONBOY — HOW TO BASS HOUSE (Knock2, Skrillex, Porter Robinson) (https://youtu.be/3-0JCDyiPaw?t=238)
status: untested
---
## What it is
The supersaw recipe, which he calls one of the sound design tricks he uses most: stack voices of a saw,
detune them so they beat against each other, filter the top, then add slow movement and space.

## When to use it
For the pad that holds the chords or bass notes under a plucked melody in a breakdown; the same oscillator
setting is the starting point of his rave lead and laser bass, so learn it once.

## How
1. Init patch, oscillator A on the default saw, octave −1 (shown at [4:04](https://youtu.be/3-0JCDyiPaw?t=244)).
2. Raise unison: 13, then 15 voices on screen (shown; said "add multiple voices").
3. Detune them: the knob passes 0.47 and 0.19 while he turns it (shown at
   [4:08](https://youtu.be/3-0JCDyiPaw?t=248)); the final value is not shown. The detuning is what gives
   movement and width (said).
4. Filter on, MG Low 12, cutoff in the upper half so only the fizz goes (shown at
   [4:16](https://youtu.be/3-0JCDyiPaw?t=256); no number).
5. Effects: phaser (frequency 158 Hz shown) and a hall reverb (shown at
   [4:22](https://youtu.be/3-0JCDyiPaw?t=262)).
6. Play it as long single notes following the bass progression (D1, E1, F#1 under the melody: shown at
   [3:56](https://youtu.be/3-0JCDyiPaw?t=236)).

## In Rohil's setup
```
rick-rubin serum set init osc_a.octave=-1 osc_a.unison=15 osc_a.detune=0.19 \
  filter_1.on=on filter_1.type="MG Low 12" filter_1.cutoff_hz=2500 env_1.attack_ms=300 env_1.release_ms=800 \
  fx.phaser.freq=158 fx.reverb.type=Hall fx.reverb.wet=30 --fx-add phaser --fx-add reverb \
  --save cosmic-pad --project <dir>
```

Cutoff, envelope times and reverb amount are ours. Because the unison widens everything, cut the lows on the
track (Channel EQ low cut near 150 Hz) or let a mono sub carry the bottom.

## How to check it
`rick-rubin serum ab <preset> --note F#3 --secs 2 --try "osc_a.unison=1" --try "osc_a.detune=0.47"`. A first
run (2026-11-20, not heard): 15 voices measured about 50 % side energy in every band against 22 to 32 % with
one voice; detune 0.47 turned it `noisy` (harmonic-to-noise 0.2 dB against 26 dB at 0.19), so stay low.
`rick-rubin width` on the bounced track must show nothing wide below 150 Hz after the low cut.

## Why it works
Voices a few cents apart drift in and out of phase, which the ear hears as slow motion and, with the voices
spread left to right, as width. The filter removes the harshness that fifteen saws add up to.
