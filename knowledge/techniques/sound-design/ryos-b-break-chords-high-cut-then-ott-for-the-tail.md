---
title: A dark break chord sound: bell preset with its top cut off, then OTT to bring up the tail
topic: sound-design
genres: [progressive house, bass house, any]
source: RYOS — Pro Secrets for Creating EDM Breakdowns (https://youtu.be/l_XjHmumqQk?t=721)
status: untested
---
## What it is
His "vibey chords": a bell preset turned into a warm, dark chord bed by removing everything above about 1 kHz
as a sound-design choice, then compressing so the body and release are as loud as the attack.

## When to use it
A chord part that should sit under a vocal or chop without sparkle, and any pluck or bell that is all attack.

## How
1. Preset: Analog Lab V "Bouncy Bells" (shown, [12:13](https://youtu.be/l_XjHmumqQk?t=733)).
2. EQ 1, a steep high cut. He disliked the bell texture on top and loved what was below about 1 kHz, and calls
   it a sound-design decision, not a mixing one (said, [12:21](https://youtu.be/l_XjHmumqQk?t=741)).
3. FocusOne to beef it up: its focus band on the extreme setting, plus a little drive and width. He describes
   it as OTT-like compression that shapes and brightens (said, [12:42](https://youtu.be/l_XjHmumqQk?t=762)).
4. EQ 2, the mixing move: a low cut around 145 Hz (said) and the high cut again at about 1.28 kHz, 36 dB per
   octave, so nothing bleeds over (shown, [13:32](https://youtu.be/l_XjHmumqQk?t=812)).
5. OTT at depth 58 % with some highs reduced, to bring out the tail: he was hearing lots of attack and too
   little body and release (said, [13:47](https://youtu.be/l_XjHmumqQk?t=827)).
6. Last two slots, here and on most of his channels: a volume plug-in for hard-cut automation and a filter
   plug-in for filter automation (said, [14:07](https://youtu.be/l_XjHmumqQk?t=847)).

## In Rohil's setup
- In Serum 2: `rick-rubin serum search bell`, then `rick-rubin serum set "<preset>" filter_1.on=on
  filter_1.type="Low 24" filter_1.cutoff_hz=1200 --fx-add compressor fx.compressor.multiband=1
  fx.compressor.wet=58 --save vibe-chords --project <dir>`. Check that the oscillators pass through filter 1
  (`rick-rubin serum params "<preset>" --group routing`).
- Or in Logic on any instrument: Channel EQ (high cut 1.2 kHz at 36 dB/oct, low cut 145 Hz), then OTT, which
  he owns: `rick-rubin logic insert Chords "OTT" Depth=58`; turn its high band down with `Gain H`.
- FocusOne is not installed; OTT plus Logic's Exciter is the nearest, and step 5 already uses OTT.
- For step 6: Logic's Gain and AutoFilter. Their automation is drawn by hand; the bridge cannot write it.

## How to check it
`rick-rubin serum describe` before and after: the high and air shares fall to near zero, brightness drops
to around 1 kHz or below, and decay gets longer. `rick-rubin compare` on two bounces: lower crest at the same
peak level. If the low band rises, raise the low cut.

## Why it works
Cutting the top changes the character from bell to pad-like pluck. Upward compression lifts the quiet tail
towards the attack, so short notes fill the bar like a sustained chord.
