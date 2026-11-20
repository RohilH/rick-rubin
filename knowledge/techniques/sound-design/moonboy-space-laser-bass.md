---
title: A "laser" mid bass: two detuned saws with a high-pass swept down on every note, then a big effect chain
topic: sound-design
genres: [bass house]
source: MOONBOY — HOW TO BASS HOUSE (Knock2, Skrillex, Porter Robinson) (https://youtu.be/3-0JCDyiPaw?t=305)
status: untested
---
## What it is
The anthem bass of the drop's A section. The identity is one move: a low cut whose frequency starts high and
falls fast at the start of every note, which makes each note say "pew". Everything after that is standard
effects that make it large. It plays in the mid range; a separate sub plays underneath.

## When to use it
For a festival-style bass house drop where the bass is also the lead. Not for a tech house groove bass.

## How
1. Two saw oscillators: A with 2 voices, B with 16 voices, detuned (said "one with two voices and one with
   a ton"; shown at [5:26](https://youtu.be/3-0JCDyiPaw?t=326)).
2. In Serum's effects add an EQ; make its first band a low cut (shown at
   [5:35](https://youtu.be/3-0JCDyiPaw?t=335); he says high pass).
3. Drag LFO 1 onto that band's frequency. Redraw the LFO as a curve that starts at the top and falls
   steeply to zero within the first quarter of the cycle (shown at [5:40](https://youtu.be/3-0JCDyiPaw?t=340)).
4. Rate 1/4, synced; mode ENV so it restarts on every note (said and shown). His finished preset uses 1/8,
   amp attack 5 ms, release 18 ms (shown at [6:03](https://youtu.be/3-0JCDyiPaw?t=363)).
5. Then make it big (said, [5:47](https://youtu.be/3-0JCDyiPaw?t=347)). Chain on screen, in order: EQ, filter,
   phaser, chorus, hyper (4 voices) with dimension, compressor in multiband mode, plate reverb, delay at 1/8
   both sides, distortion (SoftClip, after the chain) (shown at 6:03 and
   [6:07](https://youtu.be/3-0JCDyiPaw?t=367)).
6. Part: two 16ths and an 8th on every beat, the pitch stepping up E2, F#2, G#2 over two bars (shown at
   [5:10](https://youtu.be/3-0JCDyiPaw?t=310)).

## In Rohil's setup
The EQ band's shape is not yet a named value in our Serum map, so use Filter 1 as the high-pass (same sound):

```
rick-rubin serum set init osc_a.unison=2 osc_b.on=on osc_b.unison=16 \
  filter_1.on=on filter_1.type="High 12" filter_1.cutoff_hz=150 \
  lfo_1.rate=1/4 lfo_1.mode=Envelope lfo_1.shape="Basic/Saw Down Curved" \
  fx.hyper.unison=4 fx.compressor.multiband=1 fx.distortion.mode=SoftClip fx.reverb.wet=15 fx.delay.wet=15 \
  --fx-add chorus --fx-add hyper --fx-add compressor --fx-add reverb --fx-add delay --fx-add distortion \
  --mod lfo_1:filter_1.cutoff_hz:55 --save space-laser --project <dir>
```

Cutoff, depth and wet amounts are ours. OTT after Serum can stand in for the multiband compressor.

## How to check it
`rick-rubin serum ab <preset> --note E2 --bpm 126 --try "mod_1.amount=0"`. A first run (2026-11-20, not
heard): with the sweep, early brightness 1325 Hz against 1020 Hz without, and the note takes about half a
second to reach full level as the lows return. It measures `very-wide` with wide low end: high-pass the
track near 150 Hz and check `rick-rubin width` shows nothing wide below that.

## Why it works
A falling high-pass is a filter sweep compressed into a tenth of a second; repeated on every note it becomes
part of the timbre. Sixteen detuned voices give the size, and the chain glues sweep and tail into one sound.
