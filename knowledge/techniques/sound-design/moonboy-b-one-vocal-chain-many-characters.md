---
title: One vocal chain, several voices: the five knobs he rides on the tuner and the vocoder
topic: sound-design
genres: [tech house, bass house]
source: MOONBOY — 5 Ways To Process Tech House Vocals in Ableton (https://youtu.be/vDgVqHKPBIM?t=209)
status: untested
---
## What it is

His tuner, vocoder and OTT chain (see `sound-design/moonboy-vocoder-vocal-chain`) stays in place for the whole
track. Different "voices" come from five controls only: the tuner's octave and formant, the vocoder carrier's
octave, the vocoder's formant, and its dry/wet. This card is his one-minute demo read frame by frame.

## When to use it

When one vocal has to carry a whole remix: a readable voice for the verse, a low robot for the drop hook, a
thin one for the build, all from the same acapella, so the sections differ without a second sample.

## How

1. Fixed part (shown at [3:35](https://youtu.be/vDgVqHKPBIM?t=215)): tuner in MIDI mode, attack and release
   20 ms, mono, 100 % wet; vocoder pitch-tracking 80 to 500 Hz, saw carrier, Enhance on, 20 bands, depth 100 %;
   OTT amount 96 to 100 %, time 129 to 134 %. OTT's high band is adding 16 to 24 dB (its meter, shown).
2. Voice 1 (shown 3:35): tuner pitch 0, formant −4.8 %; carrier −12; vocoder formant −2.8; release 38 ms;
   mix 81 %.
3. Voice 2 ([3:48](https://youtu.be/vDgVqHKPBIM?t=228), shown): as voice 1 but tuner formant −21 %.
4. Voice 3 ([4:00](https://youtu.be/vDgVqHKPBIM?t=240), shown): tuner pitch −12 st, formant −11 %; carrier back
   to 0; vocoder formant −6.3; release 10 ms; mix 79 %.
5. Voice 4 ([4:12](https://youtu.be/vDgVqHKPBIM?t=252), shown): tuner pitch 0, formant +1.6 %; carrier −24;
   mix 70 %.
6. Voice 5 ([4:22](https://youtu.be/vDgVqHKPBIM?t=262), shown): tuner −12 st, formant −14 %; carrier −24;
   mix 71 %.
7. What never happens (shown): the vocoder mix stays between 70 and 81 %, never 100, and the tuner formant
   stays between −21 % and +2 %. Which voice he prefers is not said.

## In Rohil's setup

- Octave and formant: Logic's Vocal Transformer (`rick-rubin logic insert Vocal "Vocal Transformer"`; Pitch −12,
  Formant a little below 0). Vocoder: EVOC 20 TrackOscillator (`rick-rubin logic devices "EVOC 20
  TrackOscillator"` for its tune and formant names). Squash: `rick-rubin logic insert Vocal OTT Depth=50`.
- Session mode cannot draw automation. Simpler in Logic anyway: duplicate the vocal track once per voice,
  give each copy its own settings, and cut the phrases onto the track whose voice that section needs.
- What is lost: Ableton's Enhance switch and the exact percent scale of its formant knob; set those by ear.

## How to check it

Bounce each voice (`rick-rubin logic bounce bounces/vox_v3.wav --bars A-B --tracks "Vocal low"`).
`rick-rubin notes`: the −12 voices read one octave under the others, same pitch classes. `rick-rubin
transcribe`: every word still found (if not, lower the vocoder mix towards 70 %). Then both for his ear.

## Why it works

Octave and formant change who seems to be speaking while the words and rhythm stay, so the vocal can answer
itself across sections like two different samples would.
