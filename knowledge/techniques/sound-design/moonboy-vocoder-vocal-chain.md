---
title: Tune, vocode, then squash: a three-device chain that makes a vocal into a synth hook
topic: sound-design
genres: [tech house, bass house]
source: MOONBOY — HOW TO TECH HOUSE | Full Tutorial (Odd Mob, Chris Lake, Mau P) (https://youtu.be/JqKaSvHImB0?t=896)
status: untested
---
## What it is
His "three core" vocal effects in series: a tuner, a vocoder whose carrier follows the voice's own pitch,
and an OTT-style multiband compressor. The result is the robotic, synth-like vocal he ties to Daft Punk.

## When to use it
When the vocal should be the lead sound of the drop rather than a clean topline; also to make a dull sample
that everyone has sound like yours.

## How
1. **Tuner first**, so the vocoder gets a stable pitch (shown at [16:08](https://youtu.be/JqKaSvHImB0?t=968):
   Auto Shift in MIDI mode, attack and release 20 ms, formant −4.8 %, 100 % wet).
2. **Vocoder** (shown at [15:12](https://youtu.be/JqKaSvHImB0?t=912) and 16:08): carrier set to pitch
   tracking with a saw oscillator and Enhance on; tracking range 80 to 500 Hz; 20 bands from 80 Hz to
   12 kHz, bandwidth 100 %, Precise; depth 100 %; attack 1 ms; release 18 to 38 ms; stereo. In the combined
   chain the carrier is an octave down (pitch −12), formant −2.8 and the mix is 81 %, so a little dry voice
   keeps the words readable.
3. For a melodic version, feed the vocoder chords instead of the tracked pitch (said,
   [15:33](https://youtu.be/JqKaSvHImB0?t=933)).
4. **Compression last**: a three-band upward and downward compressor ("OTT" on screen, amount 100 %, time
   129 %). He says it fills the gaps, brings up the effects before it and makes the vocal stand out
   ([15:45](https://youtu.be/JqKaSvHImB0?t=945)).
5. Turn the three amounts against each other while it loops (the one-minute demo from 16:08).

## In Rohil's setup
- Tuner: Logic's Pitch Correction (see the tuned-vocal card).
- Vocoder: Logic's EVOC 20 TrackOscillator is the same idea as an insert effect: it follows the pitch of
  the incoming voice and vocodes it with its own oscillator, in up to 20 bands. For chords, EVOC 20
  PolySynth on an instrument track with the vocal as its side chain. Read names first:
  `rick-rubin logic devices "EVOC 20 TrackOscillator"`.
- Compression: he owns OTT itself: `rick-rubin logic insert Vocal OTT Depth=50` (its init is Depth 100,
  Time 100 %; `rick-rubin logic params Vocal OTT` reads it back). Start at 50, not 100.
- What is lost: Ableton's Enhance switch and the exact band shapes; the character will differ, the role
  will not.

## How to check it
`rick-rubin audition <dir> bounces/vox_dry.wav bounces/vox_chain.wav`: crest down by 6 dB or more, more
energy above 4 kHz. `rick-rubin notes` on the result: one steady pitch per syllable. `rick-rubin transcribe`
should still find the words; if it cannot, lower the vocoder mix.

## Why it works
The vocoder replaces the voice's irregular pitch with a synth wave but keeps the mouth shapes, and heavy
multiband compression makes every syllable the same loudness, so the phrase sits in a dense mix like a lead.
