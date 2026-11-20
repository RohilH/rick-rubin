---
title: Skinny wide: a one-voice pad for eight bars, then an eight-voice copy fades in on the next phrase
topic: sound-design
genres: [progressive house, any]
source: Alex Rome — 7 Useful Layering Techniques and Why They Work (https://youtu.be/u8ozR9cnCTU?t=500)
status: untested
---
## What it is
Two copies of the same filtered-saw pad, one with a single voice (dead centre), one with unison (wide). The narrow one
plays alone first; the wide one joins at the phrase boundary with its filter opening into it. Under a vocal the
listener hears energy arrive without being able to say what changed.

## When to use it
Verses and breaks where the chords repeat and something should grow every eight bars without a new part.

## How
1. Narrow pad: Serum init saw, filter on, MG Low 24 (he clicks the type twice to get the steeper one), cutoff low
   (said, [8:39](https://youtu.be/u8ozR9cnCTU?t=519); 220 Hz in the automation lane at
   [10:30](https://youtu.be/u8ozR9cnCTU?t=630)). Unison 1.
2. On a stereo meter this is a thin vertical line (said, [8:52](https://youtu.be/u8ozR9cnCTU?t=532)).
3. Duplicate the track. On the copy set unison to 8 and leave detune at its default (said; shown
   [9:42](https://youtu.be/u8ozR9cnCTU?t=582)). The meter now fills out (said,
   [9:50](https://youtu.be/u8ozR9cnCTU?t=590)).
4. Narrow pad plays bars 1 to 8; the wide copy plays the second eight bars (said,
   [9:07](https://youtu.be/u8ozR9cnCTU?t=547)).
5. Entry: let the wide region start early, overlapping the end of the narrow-only phrase, and automate its cutoff from
   fully closed (8 Hz) up to the pad's value (220 Hz), the ramp ending on the boundary (shown
   [10:30](https://youtu.be/u8ozR9cnCTU?t=630); the ramp looks about half a region long).
6. For a hotter entry raise the automation's end value a little (said, [10:48](https://youtu.be/u8ozR9cnCTU?t=648)).
7. The narrow pad's own cutoff also drifts up later (shown at 10:30: 220 Hz rising to 476 Hz). A slower, wetter second
   layer is a different card: `alex-rome-b-airy-pad-layer-over-tight-chords.md`.

## In Rohil's setup
```
rick-rubin serum set init filter_1.on=on "filter_1.type=MG Low 24" filter_1.cutoff_hz=220 --save pad-narrow \
    --project <dir>
rick-rubin serum set init filter_1.on=on "filter_1.type=MG Low 24" filter_1.cutoff_hz=220 osc_a.unison=8 \
    --save pad-wide --project <dir>
```
A `serum=` track holds one cutoff, so the ramp is the section's `filter` automation on the wide track, or, with a live
Serum in Logic (`rick-rubin logic add-serum`), Rohil draws the cutoff ramp himself. Low-cut the wide copy: unison
widens the lows too.

## How to check it
One offline render here (`rick-rubin serum describe`, C3): narrow, side energy 0 % in every band; wide, about 50 %
side in low, low-mid and mid, 22 % in the highs. In the track: `rick-rubin width <dir> bounce.wav --bars` for the two
phrases; the second should show clearly more side energy. Not yet heard by Rohil.

## Why it works
Width is only noticed as a change. Holding the centre-only version first sets the baseline that makes the unison copy
feel like the room opening (inferred from his "narrow, then wide" framing).
