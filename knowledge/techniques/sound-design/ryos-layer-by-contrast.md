---
title: Layer by contrast: each layer brings what the others lack
topic: sound-design
genres: [progressive house, any]
source: RYOS — Giving Feedback On YOUR Tracks! (https://youtu.be/3I7jJyVczPQ?t=4742)
status: untested
---
## What it is
A rule for choosing layers: pair a sound with its opposite in character, register or width, instead of stacking
more of the same.

## When to use it
A piano that is bright but thin when soloed; a supersaw that sounds generic; a lead that is wide but hollow; a
chord stack that does not feel big when the vocal stops.

## How
1. Name what the main sound is: harsh or soft, synthetic or organic, wide or centred, low-mid or bright.
2. Add the opposite. A hard 90s dance piano gets a softer, more organic grand under it for richness and body
   (said, [1:19:02](https://youtu.be/3I7jJyVczPQ?t=4742)).
3. For a chord stack: a plain saw, plus a supersaw, plus one organic or odd layer (keys, a distorted organ).
   "Don't just layer ten saws that sound the same" (said, [2:03:31](https://youtu.be/3I7jJyVczPQ?t=7411)).
4. A generic supersaw in solo gets a second stack of a "fuzzy", crisp saw that is not heavily detuned (said,
   [2:01:31](https://youtu.be/3I7jJyVczPQ?t=7291)).
5. A wide, characterful lead gets a thick centre layer (said, [2:54:40](https://youtu.be/3I7jJyVczPQ?t=10480)).
6. A clicky key sound: filter the click off and, if a transient is still wanted, add a softer pluck or electric
   piano for it (said, [2:00:02](https://youtu.be/3I7jJyVczPQ?t=7202)).
7. The same idea across parts: a chaotic lead over a simple offbeat bass works because of the contrast (said,
   [2:43:15](https://youtu.be/3I7jJyVczPQ?t=9795)).

## In Rohil's setup
Shortlist candidates for the second layer with `rick-rubin serum search <words>` and read each with `rick-rubin
serum describe "<preset>" --note C4`: choose the one whose numbers differ most from the first layer where it is
weak (brightness, harmonic count, side percentage, attack). For organic layers use a Logic Library piano or a
Splice one-shot. Put each layer on its own track (`rick-rubin logic add-serum "<preset>" --name "Chords saw"`)
so levels can be set separately.

## How to check it
`rick-rubin spectrum <dir> layer1.wav layer2.wav`: the two curves should cover different regions, not lie on top
of each other. `rick-rubin serum describe` rows for the two should differ in at least two of brightness, width
and attack. Then bounce the stack and let Rohil say whether it sounds like one instrument.

## Why it works
Layers that occupy the same space only add level and phase smear; layers that differ fill the spectrum and the
stereo field, so the stack sounds bigger at the same loudness.
