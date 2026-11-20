---
title: Set the fader balance with the master in mono
topic: mixing
genres: [any, tech house, bass house, progressive house]
source: Alex Rome — 10 Mixing Tips That Changed My Life (https://youtu.be/cU0tHoyJYjo?t=494)
status: untested
---
## What it is
Summing the whole mix to mono while setting levels, so wide sounds cannot fool the ear into thinking they are louder
than they are. He calls the effect "fake loudness".

## When to use it
For the static balance pass, and especially for drums (said). Go back to stereo for panning, width and reverb.

## How
1. Notice the illusion first: the same melody in mono and in stereo sounds bigger in stereo without being louder
   (said and played, [8:35](https://youtu.be/cU0tHoyJYjo?t=515)).
2. On the master, insert a plug-in that can collapse to mono. In Logic: Imaging > Direction Mixer, Spread pulled
   down to mono (said; the menu is shown [9:12](https://youtu.be/cU0tHoyJYjo?t=552)).
3. With the whole mix in mono, go through the faders one by one and set each against the kick (said; the anchor is
   our reading).
4. Bypass the plug-in when the balance is done (inferred; he does not say).

## In Rohil's setup
Direction Mixer is in Logic's list: `rick-rubin logic insert "Stereo Out" "Direction Mixer"`, then read its names
with `rick-rubin logic params "Stereo Out" "Direction Mixer"` and set the spread to zero with `logic tweak`. It must
sit after everything else on the Stereo Out, and it must be bypassed before any bounce Rohil will keep: say so when
inserting it. Work on the Stereo Out brings Logic to the front.

## How to check it
With the plug-in on, `rick-rubin width <dir> bounces/mono.wav` should report no side energy in any band. With it
bypassed, the same bounce should show the mix's width back, and parts that vanished in mono (wide pads, stereo hats)
will show as high side percentages: those are the ones whose level was being misjudged.

## Why it works
Loudness judgement and width judgement interfere. Mono removes one variable, and anything that only works in stereo
is exposed (said in substance).
