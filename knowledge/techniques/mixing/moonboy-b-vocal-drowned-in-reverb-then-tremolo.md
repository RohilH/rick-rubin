---
title: The euphoric vocal chop: tune it, drown it in reverb, wobble the volume, then OTT lightly
topic: mixing
genres: [progressive house, bass house, any]
source: MOONBOY — 13 Insane Ways to Make Any Vocal Sound MAGICAL (https://youtu.be/7wcJShg8tn4?t=40)
status: untested
---
## What it is

His first and simplest vocal trick, in three words: melody, reverb, tremolo. A sung phrase is tuned, sent
through a reverb that is almost entirely wet, and the result is given a gentle volume wobble; a light OTT
at the end pulls the tail up. The vocal stops being a lyric and becomes a floating lead.

## When to use it

For a held or melodic vocal phrase in a break, intro or melodic drop. For a rap or spoken vocal in a tech
house remix, use it on one long ad-lib or the last word of a line, not on the whole verse: it erases
consonants.

## How

1. Start with a clean vocal melody (said, [0:40](https://youtu.be/7wcJShg8tn4?t=40)).
2. Tuner first: Auto-Tune Artist is open next to the reverb in his "advanced look" (shown at
   [1:15](https://youtu.be/7wcJShg8tn4?t=75); its key and speed settings are not readable).
3. "Lots of reverb" as an insert: ValhallaRoom, Large Room mode, mix 97 % (100 % in the chain view), decay
   5.57 s, pre-delay 3.9 ms, high cut 13 kHz, depth 46.8 % (shown at
   [0:50](https://youtu.be/7wcJShg8tn4?t=50)).
4. Tremolo after the reverb: Ableton Auto Pan, amount 23 %, rate 1/4 synced, sine, shape 0 % (shown at
   1:15). The phase reads about 200°, so it is partly a pan wobble too (shown, small text).
5. OTT last, gently: amount 31 %, time 100 %, output −7.7 dB (shown at 1:15).
6. Order matters: the tremolo and OTT act on the reverb tail, not on the dry voice (shown: reverb, Auto Pan,
   OTT left to right).

## In Rohil's setup

- `rick-rubin logic insert Vocal "Pitch Correction"` (key of the track), then a reverb as an insert:
  `rick-rubin logic insert Vocal ChromaVerb` (read names with `rick-rubin logic params Vocal ChromaVerb`; decay
  near 5.5 s, wet near 100 %, dry near 0), or `rick-rubin logic insert Vocal ValhallaSupermassive Mix=1.0` for
  a bigger, less natural wash.
- `rick-rubin logic insert Vocal Tremolo`, then set a 1/4 rate and a depth near 25 % after
  `rick-rubin logic params Vocal Tremolo`. `rick-rubin logic insert Vocal OTT Depth=31`.
- Do it on a copy of the vocal track so the dry one stays for the parts that need words. What is lost:
  ValhallaRoom's exact character; he does not own it.

## How to check it

`rick-rubin logic bounce bounces/vox_wash.wav --bars A-B --tracks "Vocal wash"`, then `rick-rubin audition
<dir> bounces/vox_dry.wav bounces/vox_wash.wav`: decay several seconds longer, crest lower. `rick-rubin
notes`: the same pitches, in key. `rick-rubin width`: side energy up in the mids, correlation not negative.

## Why it works

A fully wet long reverb turns syllables into sustained pitch, which is what a pad or lead is; the tremolo
puts back a pulse the wash has lost, and OTT keeps the quiet tail audible in a dense mix.
