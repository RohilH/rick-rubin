---
title: Lead group chain: exciter, a taste of enhancement, a gentle harshness cut, a band-limited quarter-note delay
topic: mixing
genres: [progressive house]
source: RYOS — Making Beautiful Progressive House | Studio Time with Ryos EP. 50 (https://youtu.be/WnZ7GN1tpek?t=838)
status: untested
---
## What it is
Four inserts on the bus that carries all the lead layers. They brighten and glue the stack and add space,
while leaving its dynamics alone.

## When to use it
As soon as the lead layers are chosen, before the drop is built around them.

## How
1. Route every lead layer to one group (said, [13:58](https://youtu.be/WnZ7GN1tpek?t=838)).
2. First insert: an exciter-style enhancer for "a nice little boost". He uses Noveltech Character; the preset
   name in the title bar reads TechnoSynth (shown, small text, [14:46](https://youtu.be/WnZ7GN1tpek?t=886)).
3. Second: a multi-effect (FocusOne: focus, boost, drive, widen, pulse faders) with the faders barely raised:
   "just a taste", because the leads should stay "dynamic and beautiful" and not be squashed (said,
   [14:25](https://youtu.be/WnZ7GN1tpek?t=865); fader values not readable).
4. Third: EQ the whole group for harshness. Shown at 14:46: one wide bell in the upper mids, about -1.2 dB. The
   frequency label was not readable; the bell sits where the stack's harmonics are densest (inferred, a few kHz).
5. Fourth: a "big delay". Shown at [14:54](https://youtu.be/WnZ7GN1tpek?t=894): ValhallaDelay, a digital stereo
   quarter-note preset, repeats filtered to 330 Hz to 5.59 kHz, slow modulation (0.08 Hz, depth 32 %).
6. Chain order as shown at 14:54: Character, FocusOne, Pro-Q 3, ValhallaDelay. No compressor, no reverb insert.
7. Single layers get their own fixes before the group: the guitar its dip at 3.1 kHz, the plain synth layer a
   distortion and an EQ (shown, [15:05](https://youtu.be/WnZ7GN1tpek?t=905)).

## In Rohil's setup
Make the group in Logic as a summing stack or a bus (session mode cannot create stacks; do that by hand, then
address the Aux by name). Inserts: Logic's Exciter or ANIMATE for step 2; skip step 3 or use a few percent of
FUSER/ANIMATE (what is lost: FocusOne's one-fader blend); Channel EQ for step 4 (`rick-rubin logic insert "Lead
Bus" "Channel EQ"`, then `rick-rubin logic params "Lead Bus" "Channel EQ"` to read names before `logic tweak`);
Logic's Stereo Delay at 1/4 with its low cut near 330 Hz and high cut near 5.6 kHz for step 5 (read its
names with `rick-rubin logic devices "Stereo Delay"`). RESO can find the harsh frequency instead of guessing.
This differs from the existing card `ryos-slam-melodic-groups-with-compression.md` (from his feedback stream):
here he says not to squash the leads. Try both on a bounce.

## How to check it
Bounce the group before and after (`rick-rubin logic bounce leads_after.wav --bars 25-32 --tracks "Lead Bus"`).
`rick-rubin spectrum` should show more energy above about 5 kHz and slightly less in the band of the cut; in
`rick-rubin reference compare` the crest of the mix should not fall because of this chain. `rick-rubin width`
should show more side energy in the mids and highs from the stereo delay, none below 150 Hz.

## Why it works
A stack of presets is already dense, so heavy compression mostly removes the swell that makes a progressive
lead feel alive. Band-limiting the delay keeps the repeats out of the bass and out of the hats' range.
