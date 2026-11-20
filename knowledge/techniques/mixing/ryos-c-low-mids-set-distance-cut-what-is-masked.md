---
title: Low mids decide how close a sound feels: keep them on the stars, cut them from supporting sounds that will be masked anyway
topic: mixing
genres: [progressive house, tech house, bass house, any]
source: RYOS — KSHMR asked me to remix his song.. here's how I did it (https://youtu.be/mvZPg8zv_ig?t=978)
status: untested
---
## What it is
Two rules he applies to every supporting sound in the remix. A sound with plenty of low mids feels close,
which is right for vocals and drop leads and wrong for an arp or a horn in the background. And frequencies
that other parts will cover are removed, because unheard energy still uses headroom.

## When to use it
Any layer that is "not the star of the show". It extends `ryos-clear-200-500hz-pocket-for-the-lead.md`
(clear the pocket for the lead) with a reason to cut much further on background parts, and a test for when
not to.

## How
1. Ask what the sound is for. His arp is "something you hear and not something you feel", meant to sit at
   a distance in the high mids and highs (said, [16:18](https://youtu.be/mvZPg8zv_ig?t=978)).
2. Fast reshape with a tilt shelf: one band that brightens and lowers the low mids together. On the arp:
   900 Hz, +2.4 dB (shown, [15:45](https://youtu.be/mvZPg8zv_ig?t=945); said 15:11).
3. Then a low cut that looks dramatic in solo: 344 Hz at 24 dB/oct on the arp (shown,
   [16:15](https://youtu.be/mvZPg8zv_ig?t=975)), because low-mid instruments are about to enter and need
   the room (said, [16:39](https://youtu.be/mvZPg8zv_ig?t=999)).
4. The closeness rule: abundant low mids pull a sound forward. Keep them on the vocal and the drop lead;
   take them from what should sit back (said, 16:39).
5. The masking rule, on the distorted horn: its lower content will be lost under other sounds anyway, so
   cutting it costs nothing audible and saves headroom for the sounds that are heard (said,
   [24:52](https://youtu.be/mvZPg8zv_ig?t=1492)).
6. The exception: if the sound were one of only a few playing at that moment, he would pull the cut back
   (said, 24:52). So the cut is set in context, per section; the arp even gets a thinner EQ automated for
   the intro (said, [18:26](https://youtu.be/mvZPg8zv_ig?t=1106)).
7. Compression can do the same job: the buzzy top bass has no EQ, only OTT squeezed hard, which scoops it,
   plus a high boost (said, [27:42](https://youtu.be/mvZPg8zv_ig?t=1662)).

## In Rohil's setup
Channel EQ on the supporting track: `rick-rubin logic insert Arp "Channel EQ"`, `rick-rubin logic params
Arp "Channel EQ"` to read the band names, then `logic tweak` for a low cut and a high shelf (Channel EQ has
no tilt band; a low shelf down plus a high shelf up at the same frequency is the nearest thing). MIXROOM
can suggest the balance; BASSROOM is for the low end only. For the hip-hop vocal remix the vocal is the
close sound: leave its 200 to 500 Hz alone and thin the pads and atmospheres under it. Section-dependent
cuts need automation, drawn by hand in Logic.

## How to check it
`rick-rubin spectrum <dir> vocal.wav arp.wav pad.wav` on bounced stems: between about 200 and 500 Hz the
star is at least several dB above each supporting part (inferred target). `rick-rubin compare <dir>
mix_before.wav mix_after.wav`: the same loudness with a lower peak or a higher crest means headroom came
back. Whether the arp now sits "behind" the vocal is for Rohil's ears.

## Why it works
Nearby sources reach us with more body and low-mid energy than distant ones, so thinning a part reads as
distance; and a mix bus limiter reacts to all energy, heard or not.
