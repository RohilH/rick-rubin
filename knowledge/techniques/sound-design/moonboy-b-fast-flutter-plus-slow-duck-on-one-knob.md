---
title: Two volume shapes on one vocal: a 1/16 flutter under a 1/4 duck, with one knob for the amount of both
topic: sound-design
genres: [bass house, progressive house, tech house]
source: MOONBOY — 13 Insane Ways to Make Any Vocal Sound MAGICAL (https://youtu.be/7wcJShg8tn4?t=661)
status: untested
---
## What it is

The "advanced" version of the stutter vocal. Two LFOs control the same volume at different speeds: a fast
one makes the flutter, a slow one shaped like a sidechain makes the whole thing swell once per beat. A
macro is mapped to both depths, so one knob takes the vocal from clean to fully stuttered.

## When to use it

When the plain tremolo stutter sounds mechanical or fights the kick. The slow duck leaves a hole for the
kick, and the macro is the thing to automate in a build: clean at the start, full stutter at the top.

## How

1. SerumFX on the vocal track. Noise oscillator set to the audio input, Note Latch on, so the incoming audio
   is the "oscillator" and the LFOs run in time with the project (said and shown at
   [11:40](https://youtu.be/7wcJShg8tn4?t=700); the acapella is 135 BPM).
2. LFO 1 onto the noise level, level turned down, depth up: rate 1/16, synced, plain triangle (shown at
   11:40).
3. LFO 2 onto the amp envelope's sustain: sustain turned all the way down (−89 dB on screen), decay at 0 ms,
   depth up (said, [12:01](https://youtu.be/7wcJShg8tn4?t=721); shown at
   [12:40](https://youtu.be/7wcJShg8tn4?t=760)).
4. LFO 2's rate is 1/4 and its shape is a ramp that rises through the beat and stays up: quiet on the beat,
   loud after it, "like a sidechain" (said and shown at 12:40). Drums on top then fit (said).
5. Drag one macro onto both the level and the sustain: it now sets how much flutter and duck there is (said,
   [12:43](https://youtu.be/7wcJShg8tn4?t=763)).
6. He says the same patch works on synths and almost anything else.

## In Rohil's setup

- Two inserts in series do the same job: `rick-rubin logic insert Vocal Tremolo` (phase 0°, rate 1/16, depth
  high; names from `rick-rubin logic params Vocal Tremolo`) and then `rick-rubin logic insert Vocal
  "Kickstart 2" Mix=0.8`, whose shape is exactly the 1/4 duck.
- The "one knob": there is no macro across two Logic plug-ins. Nearest: put both on a copy of the vocal
  track and automate that track's volume against the clean track (a crossfade from clean to stuttered), by
  hand.
- Serum 2 FX is installed on this Mac and has LFOs and macros; it loads as a MIDI-controlled effect on an
  instrument track with the vocal as its side-chain input. Whether its audio input can be modulated the way
  SerumFX version 1 does it has not been tried here.

## How to check it

`rick-rubin hits <dir> bounces/vox_flutter.wav` on a bounce: the lowest level on steps 1, 5, 9, 13, rising
across each beat, with a 16th ripple on top. With the kick: `rick-rubin eval --bars A-B --tracks Kick Vocal`
shows no clash on the beat. Bounce clean, half and full for his ear.

## Why it works

Two rhythms multiplied together are less regular than either alone, which reads as "organic", and making
the slow one a kick-shaped duck means the effect clears space exactly where the drums need it.
