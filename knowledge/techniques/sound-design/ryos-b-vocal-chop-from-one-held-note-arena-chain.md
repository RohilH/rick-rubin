---
title: A break vocal chop from one held note, made huge with a tape delay and Supermassive
topic: sound-design
genres: [progressive house, bass house, any]
source: RYOS — Pro Secrets for Creating EDM Breakdowns (https://youtu.be/l_XjHmumqQk?t=125)
status: untested
---
## What it is
The "creepy" vocal riff that opens his break. One sampled vocal phrase played on a single key, restarted every
bar, then brightened and sent through a long quarter-note delay and a large reverb, all on the insert.

## When to use it
A break or intro that needs a hook and a sense of a big room before any lead has entered.

## How
1. Source: a vocal phrase instrument (Output Arcade) played on G the whole time. No slicing, no re-pitching
   (said, [2:05](https://youtu.be/l_XjHmumqQk?t=125); one long note shown, [2:30](https://youtu.be/l_XjHmumqQk?t=150)).
2. A held key makes the phrase loop, so he cuts the note at every bar line so the phrase restarts each bar, and
   cuts one small gap for space (said, [2:48](https://youtu.be/l_XjHmumqQk?t=168)).
3. Brighten first. Dry it is dull; a multiband distortion (DST) with its low-mid, high-mid and high knobs raised
   does "the heavy lifting" (said, [3:31](https://youtu.be/l_XjHmumqQk?t=211); knob values not readable).
4. ValhallaDelay: mode Tape, style Dual, 1/4 note on both sides, mix 20.8 %, feedback 87.6 %, width 100 %,
   drive 18 dB, age 100 %, wow 63 %, flutter 66 %, low cut 530 Hz, high cut 20 kHz (shown,
   [4:52](https://youtu.be/l_XjHmumqQk?t=292)).
5. Valhalla Supermassive after it: mode Sagittarius, preset "Best Ballad Vocal", mix 24.4 %, width 100 %,
   delay 245.7 ms, warp 22.4 %, feedback 86 %, density 10 %, mod 0.32 Hz at 78.8 %, EQ high 4080 Hz, low
   400 Hz (shown, [5:18](https://youtu.be/l_XjHmumqQk?t=318)).
6. EQ last: a steep low cut, "a decent amount" (said; frequency not readable) and one dynamic band on a harsh
   frequency (see `mixing/ryos-b-dynamic-eq-for-one-harsh-frequency.md`).

## In Rohil's setup
- Source: a Splice vocal phrase in Quick Sampler, or an audio region repeated per bar. Check that it fits the
  root first: `rick-rubin notes <dir> samples/vox.wav`.
- Brightening: Logic's Exciter or ANIMATE (see `ryos-brighten-a-dull-lead-with-harmonics.md`).
- Delay: Logic's Tape Delay at 1/4, feedback near 85 %, low cut near 530 Hz, flutter on. Lost: Valhalla's two
  delay lines at full width; use Stereo Delay if `width` shows the echoes too narrow.
- Supermassive he owns: `rick-rubin logic insert "Vocal Chop" "ValhallaSupermassive" Mix=0.244 Fb=0.86
  Width=1 Densit=0.1` (the bridge sees these as 0 to 1). Mode, delay time, warp, mod and the EQ are also 0 to 1
  there with an unknown mapping: set those in the plug-in window and read back with `rick-rubin logic params`.

## How to check it
Bounce the chop dry and wet. `rick-rubin compare <dir> chop_dry.wav chop_wet.wav`: more top-band energy, lower
crest, wider. `rick-rubin width <dir> chop_wet.wav`: side share clearly up, low band still mono. `rick-rubin
spectrum`: nothing left under the low cut. Whether it "transports" is Rohil's call on the two bounces.

## Why it works
A bright source feeding long, filtered repeats and a diffuse reverb sounds like a large space without low-end
mud, and one held key guarantees the chop sits on the root of the progression.
