---
title: An old-school techno lead: one raw saw, heavy multiband compression, then reverb and delay
topic: sound-design
genres: [tech house, bass house]
source: MOONBOY — HOW TO TECH HOUSE (John Summit, Dom Dolla, Chris Lake,) (https://youtu.be/_4qJSUFao50?t=264)
status: untested
---
## What it is

The sound under his two-note riff. He describes it as a saw wave, heavily compressed, with reverb and delay
for space, and a wide pitch-bend range for slides. No filter, no unison: the aggression comes from the
compressor, not from layers.

## When to use it

For a rude, buzzy mono riff in a tech house intro, break or drop (the Benassi-style lead). Not for chords:
it is one voice.

## How

1. Serum's init patch: one saw, one voice, no filter (shown at [4:35](https://youtu.be/_4qJSUFao50?t=275):
   preset name "Init", only the compressor lit in the effect rack).
2. Compressor on, then its Multiband switch on (shown: the cursor on Multiband at 4:35). That is Serum's
   OTT-style mode; "heavily compressed" is his word. Threshold, ratio and gain values are not readable.
3. Add reverb (Hall type) and delay after it (said; shown at [4:50](https://youtu.be/_4qJSUFao50?t=290):
   delay synced, 1/4 on both sides, Normal mode, its filter at 849 Hz with Q 6.8).
4. Voicing: Mono on, legato off (shown at 4:50).
5. Pitch bend range: up 2, down −13 semitones (shown at 4:50), then bend moves are drawn in the clip for
   slides (see `bass/moonboy-b-pitch-bend-ramps-on-the-bassline`).
6. Amp envelope left at init: attack 0.5 ms, sustain 0 dB, release 0 ms (shown), so notes are as long as
   they are written. Mix amounts of reverb and delay are not readable.

## In Rohil's setup

```
rick-rubin serum set init global.mono=on global.bend_up=2 global.bend_down=-13 \
  fx.compressor.multiband=1 fx.reverb.type=Hall fx.reverb.wet=20 fx.delay.wet=20 \
  --fx-add compressor --fx-add reverb --fx-add delay --save techno-saw --project <dir>
```

The two wet amounts are ours. The command parsed on 2026-11-20 (not heard): against init it measured
brighter by about 70 %, 40 harmonics instead of 31, and a 1.5 s longer tail. OTT after Serum
(`rick-rubin logic insert Lead OTT Depth=60`) is the alternative to Serum's own multiband mode. Because the
tail is inside the patch, cut the track's lows (Channel EQ low cut near 150 Hz) and duck it with
`rick-rubin logic insert Lead "Kickstart 2" Mix=0.5`.

## How to check it

`rick-rubin serum ab techno-saw --note D2 --bpm 128 --try "fx.compressor.multiband=0"`: with multiband on the
brightness and loudness rise and crest falls. `rick-rubin width` on the bounced track: nothing wide below
150 Hz. Then `rick-rubin serum audition` so he hears it on the riff.

## Why it works

A bare saw already has every harmonic. Upward multiband compression lifts the quiet top harmonics to the
level of the fundamental, which is the "fizzing" techno tone; reverb and delay then give one dry voice a room.
