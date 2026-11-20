---
title: The "infinite vocal choir": loop a sliver of a reverbed vocal in a sampler and play it as chords
topic: sound-design
genres: [progressive house, bass house]
source: MOONBOY — 13 Insane Ways to Make Any Vocal Sound MAGICAL (https://youtu.be/7wcJShg8tn4?t=362)
status: untested
---
## What it is

A playable pad built from a vocal. The vocal is washed in reverb and delay and recorded; the recording goes
into a sampler; a very short stretch of it is looped back and forth with a crossfade so one vowel sustains
for ever; then it is played from the keyboard, shaped with a tremolo, and doubled with a second copy looping
a different spot for harmony.

## When to use it

For the pad or choir of a melodic break when a synth pad sounds generic. In a remix: a choir made from the
original vocal sits behind the new drop and keeps the song recognisable.

## How

1. Vocal with space: reverb with a long decay (12.9 s, size 100, wet 52 %, shown at
   [6:30](https://youtu.be/7wcJShg8tn4?t=390)), its lows cut (said), plus a delay to fill gaps (said).
2. Record it to a new audio track (Ableton: input set to Resampling, arm, record) (said,
   [6:43](https://youtu.be/7wcJShg8tn4?t=403)).
3. New MIDI track with a sampler; drag the recording in and turn it up (said,
   [7:06](https://youtu.be/7wcJShg8tn4?t=426)).
4. Sustain loop mode back-and-forth, loop region dragged small; it clicks, so raise the loop crossfade until
   smooth (said). On screen: a loop of about 9,400 samples (roughly 0.2 s) with a crossfade of the same
   length (shown at [9:00](https://youtu.be/7wcJShg8tn4?t=540)).
5. Move the loop to different vowels for different colours (said, [7:46](https://youtu.be/7wcJShg8tn4?t=466)).
6. Rhythm: Auto Pan after the sampler, amount 100 %, synced (1/8 or 1/4 shown), phase near 0 so it is a
   volume gate (5.7° to 14.3° shown: a touch of stereo); for a ducking feel switch the shape to a saw and
   press Invert, and slow it down (said and shown at [8:40](https://youtu.be/7wcJShg8tn4?t=520) and 9:00).
7. Harmony: duplicate the track, move the second sampler's loop to another spot, give it a different
   tremolo rhythm; the two shapes can also be stacked on one track (said,
   [8:52](https://youtu.be/7wcJShg8tn4?t=532)).

## In Rohil's setup

- Steps 1 and 2: `sound-design/moonboy-b-vocal-reverb-pad-by-resampling` (bounce instead of resampling).
- Sampler: `rick-rubin logic add-instrument "Quick Sampler (Single Sample)" --name "Vox choir"`, then drag the
  bounce onto it by hand. In Quick Sampler choose Classic mode, loop mode Alternate, drag the loop markers
  around one vowel and pull the crossfade handle until the click goes. The root key must match the sample's
  pitch: read it with `rick-rubin notes <dir> bounces/vox_wash.wav`.
- Gate: `rick-rubin logic insert "Vox choir" Tremolo` (phase 0°, rate 1/8, full depth), or for the ducking
  version `rick-rubin logic insert "Vox choir" "Kickstart 2" Mix=1.0`.
- The chords are written for the track (the progression's notes), not taken from here.

## How to check it

Hold one note for four bars and bounce it: `rick-rubin audition` shows a level that never decays;
`rick-rubin notes` reads one steady pitch equal to the key played (if it is off, fix the root key). With
the gate on, `rick-rubin hits` shows energy on the gate's grid. Listen for the loop click before anything else.

## Why it works

A fraction of a second of a reverb tail has no attack and no words left, only pitch and vowel, so looped it
behaves like an oscillator with a human timbre.
