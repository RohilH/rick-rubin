---
title: A trance pluck lead: stacked unison oscillators, a gentle low-pass snapped shut per note, then space
topic: sound-design
genres: [bass house, progressive house]
source: MOONBOY — HOW TO BASS HOUSE (Knock2, Skrillex, Porter Robinson) (https://youtu.be/3-0JCDyiPaw?t=154)
status: untested
---
## What it is
His "cosmic lead". He names two things as the key: a pluck-style envelope on both filter and volume, and
reverb and delay for space. The preset on screen shows how: two unison oscillators an octave apart, a 6 dB
low-pass, and one falling LFO in envelope mode doing the pluck.

## When to use it
For the rolling melody of a breakdown (see the three-16th-cells card) in bass house, and as the standard
pluck of progressive house.

## How
1. Oscillator A: 7 unison voices. Oscillator B: a saw, one octave up, 4 voices. Sub oscillator on, one
   octave down. A noise layer on (shown at [2:47](https://youtu.be/3-0JCDyiPaw?t=167), preset
   "PLUCK - Cosmic").
2. Filter: MG Low 6, a soft slope, with A, B and the sub routed through it (shown).
3. LFO 1 drawn as a curve falling from full to zero, mode ENV (plays once per note), rate 1/4, smooth 32.6;
   it has three targets, the cutoff among them (shown; he says the pluck envelope is on filter and volume).
4. Amp envelope left almost at init (attack 0.5 ms, decay 1 s, sustain 0 dB, release 15 ms: shown), so the
   LFO, not the envelope, shapes each note.
5. Effects in this order: hyper/dimension, chorus, delay at 1/4 on both sides with its filter near 1.3 kHz,
   hall reverb, phaser; a compressor sits in the rack switched off (shown at
   [2:52](https://youtu.be/3-0JCDyiPaw?t=172)). Mix amounts are not readable.

## In Rohil's setup
```
rick-rubin serum set init osc_a.unison=7 osc_a.detune=0.15 osc_b.on=on osc_b.octave=1 osc_b.unison=4 \
  sub.on=on sub.octave=-1 filter_1.on=on filter_1.type="MG Low 6" filter_1.cutoff_hz=300 \
  env_1.decay_ms=350 env_1.sustain_db=-30 env_1.release_ms=200 \
  lfo_1.rate=1/4 lfo_1.mode=Envelope lfo_1.smooth=32.6 lfo_1.shape="Basic/Saw Down Curved" \
  fx.delay.wet=25 fx.reverb.type=Hall fx.reverb.wet=25 \
  --fx-add hyper --fx-add chorus --fx-add delay --fx-add reverb --fx-add phaser \
  --mod lfo_1:filter_1.cutoff_hz:50 --save cosmic-pluck --project <dir>
```

Here the amp envelope does the volume pluck (simpler than his LFO on level; ours), and detune, cutoff, wet
amounts and depth are ours too. Compare with what is installed first: `rick-rubin serum search pluck trance`.

## How to check it
`rick-rubin serum describe <preset> --note F#3 --bpm 126`: the word `closes`, sustain 20 dB or more under
the peak, wide above the low mids. A first run (2026-11-20, not heard): decay 590 ms, sustain −27 dB,
bright 1213→787 Hz; without the amp decay it measured `sustained`, so that part is not optional. In the
melody (`rick-rubin serum audition ... --track Pluck --bars 1-8`) the delay should fill each cell's rest.

## Why it works
A 6 dB filter never fully closes, so the tail keeps some air while the front is bright; unison gives the
width; and because each note is short, reverb and delay supply the sustain between notes.
