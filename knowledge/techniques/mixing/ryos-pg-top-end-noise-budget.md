---
title: Treat high-frequency noise as a budget: if the leads already hiss, drop the hat; if a pad crowds, thin it
topic: mixing
genres: [progressive house, any]
source: RYOS — Making Beautiful Progressive House | Studio Time with Ryos EP. 50 (https://youtu.be/WnZ7GN1tpek?t=1428)
status: untested
---
## What it is
A subtractive habit while building a drop: before adding or keeping a bright or wide element, ask what already
fills that part of the spectrum, and remove or reshape the newcomer instead of turning things up.

## When to use it
Every time a layer is added to a drop that already has a big lead stack. Twice in this video.

## How
1. Big lead stacks carry a lot of noise-like top end of their own (supersaws, noise oscillators, exciters). He
   removes a closed hat from the drop because it adds white noise on top of the leads, and says the leads have
   enough (said, [23:48](https://youtu.be/WnZ7GN1tpek?t=1428)).
2. Keep the element only where it does a job nothing else does: the hat's short roll stays as an accent (said,
   [23:55](https://youtu.be/WnZ7GN1tpek?t=1435)).
3. Add top-end detail with something that has gaps, not a constant wash: a percussion loop, ducked on every
   beat (said and shown, [24:08](https://youtu.be/WnZ7GN1tpek?t=1448)).
4. Same test in the mids: a chord pad he likes is "taking up way too much space", so he keeps it but takes out
   the lows and some low mids and raises the high mids (said, [28:14](https://youtu.be/WnZ7GN1tpek?t=1694); done
   with the tone knobs of a distortion plug-in, shown at 28:36).
5. Same test when layering leads: a preset with a quality two other layers already have is deleted (said,
   [12:01](https://youtu.be/WnZ7GN1tpek?t=721)).

## In Rohil's setup
Find out what is already there by measurement: `rick-rubin spectrum <dir> leads.wav hats.wav pad.wav` on
bounces of the groups (`rick-rubin logic bounce leads.wav --bars 25-32 --tracks "Lead Bus"`). To test a removal
without deleting anything: `rick-rubin logic set "Closed hat" mute=on`, bounce, compare, and tell Rohil the
before and after. Thinning a pad: `rick-rubin logic insert Pad "Channel EQ"`, read its names with `rick-rubin
logic params Pad "Channel EQ"`, then set a low cut and a small high-mid lift with `rick-rubin logic tweak`.
MIXROOM can show where the top end is over target against a reference.

## How to check it
`rick-rubin reference compare <dir>` before and after the mute: the band above about 8 kHz should move toward
the references' median, and "top-end activity" (which rewards change over time) should not fall much when a
constant hat is replaced by a ducked loop. `rick-rubin spectrum` on the pad: less below about 300 Hz, more
around 2 to 4 kHz. The final call on hiss is by ear: bounce both versions for Rohil.

## Why it works
Noise from different sources adds up into a harsh, flat top where no single element is clear. Leaving that
band to the part that needs it most, here the leads, keeps the mix bright without fatigue.
