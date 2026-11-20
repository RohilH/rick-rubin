---
title: Draw a pitch-bend ramp over the bassline: fall into each bar, climb into the next one
topic: bass
genres: [tech house, bass house]
source: MOONBOY — HOW TO TECH HOUSE (John Summit, Dom Dolla, Chris Lake,) (https://youtu.be/_4qJSUFao50?t=193)
status: untested
---
## What it is

Instead of writing more notes, he draws one pitch-bend curve per bar across the bass clip, so the same
notes swoop down into the downbeat and slide up towards the next bar. On the lead he widens the synth's bend
range to more than an octave so the same gesture becomes a big slide.

## When to use it

When a one-note bassline is right rhythmically but sounds static, and as the cheapest "character" move on a
riff in a build or the last bar of a phrase.

## How

1. Open the clip's envelopes and choose MIDI control, pitch bend (said and shown,
   [3:13](https://youtu.be/_4qJSUFao50?t=193)).
2. The shape he draws, per bar (shown at [3:18](https://youtu.be/_4qJSUFao50?t=198)): full up-bend exactly
   on beat 1, a straight line down to centre reached on the "and" of beat 2, flat through beat 3, then from
   beat 4 a straight line back up to full bend at the next bar line. Repeat every bar.
3. Bend range on the bass: Serum's default of 2 semitones is what the patch showed when he built it (shown
   at [2:20](https://youtu.be/_4qJSUFao50?t=140)), so the bass starts each bar a whole tone sharp and settles
   (inferred: the range at the moment of drawing is not on screen).
4. For slides on a lead, extend the range: bend down −13 semitones, up 2 (shown at
   [4:50](https://youtu.be/_4qJSUFao50?t=290)); he calls the result a sliding effect.
5. Keep the patch mono so the bend acts on one voice (shown: Mono on in the lead patch).

## In Rohil's setup

- Range in Serum 2: `rick-rubin serum set <preset> global.bend_up=2 global.bend_down=-13 --save <name>
  --project <dir>` (both are real keys; −13 is his lead value, 2 the default).
- The curve: in Logic's piano roll open the automation/MIDI Draw area, choose Pitch Bend and draw the ramp;
  copy it per bar. Session mode has no command for this: draw it by hand, or ask Rohil to.
- The same in a patch, with no drawing: an LFO in Envelope mode on `osc_a.coarse` gives a fall into every
  note (as in `bass/moonboy-triangle-sub-with-distortion-and-pitch-bends`); the ramp here is per bar instead.

## How to check it

Bounce the bass alone for two bars and run `rick-rubin notes <dir> bounces/bass_bend.wav`: notes at the start
of each bar read sharp by up to the bend range (about +200 cents at range 2), notes in beat 3 read in tune,
notes in beat 4 drift sharp again. `rick-rubin eval`: no new out-of-key warnings in beat 3.

## Why it works

The ear takes the bar line from the place where the pitch lands. A slide that resolves on the downbeat and
winds up before the next one states the bar without any drum fill, and costs no extra notes.
