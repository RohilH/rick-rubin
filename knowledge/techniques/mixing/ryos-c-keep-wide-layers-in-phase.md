---
title: Keep wide layers in phase: pull the sides down until correlation stays at or above zero, and narrow the lows more than the highs
topic: mixing
genres: [progressive house, tech house, bass house, any]
source: RYOS — KSHMR asked me to remix his song.. here's how I did it (https://youtu.be/mvZPg8zv_ig?t=547)
status: untested
---
## What it is
A per-track width check. A very wide sample sounds impressive alone and causes "a slew of problems" later,
so each wide layer is watched on a correlation meter and narrowed until it stops going negative.

## When to use it
Every atmosphere, pad, vocal bed or arp from a sample pack or an old stem, before it is balanced. He says
the width of a song has to be managed constantly.

## How
1. Look at the track on a stereo field / correlation meter (an old iZotope Insight here). +1 is mono, 0 is
   fully wide, below 0 is heading out of phase (said, [9:30](https://youtu.be/mvZPg8zv_ig?t=570)).
2. His limit: the sound may "hang around zero at max"; anything that dips toward -1 is brought back
   (said, [9:51](https://youtu.be/mvZPg8zv_ig?t=591)).
3. Simple fix: a mid/side utility with the side gain lowered. On the vocal atmosphere bed: Voxengo MSED,
   side -5.3 dB, mid 0 (said and shown, [9:50](https://youtu.be/mvZPg8zv_ig?t=590)). He likes it for using
   almost no CPU; the tip came from Hardwell (said, [8:46](https://youtu.be/mvZPg8zv_ig?t=526)).
4. Finer fix: a multiband imager with phase limiting per band (Acustica SpaceControl). On the arp: three
   bands split at 200 Hz and 1 kHz, width 100 each, phase limit 50 on the lows, 34.7 on the mids, 28 on the
   top band (shown, [17:30](https://youtu.be/mvZPg8zv_ig?t=1050)). With it bypassed the arp is clearly out
   of phase (said, [17:22](https://youtu.be/mvZPg8zv_ig?t=1042)).
5. The shape to aim for: the image opens "like a flower or a tree" going up the spectrum. Lows are limited
   more than mids, mids more than highs (said, [17:44](https://youtu.be/mvZPg8zv_ig?t=1064)).
6. Do it on the track, last in its chain, not on the master (shown: last insert on arp and pad).

## In Rohil's setup
Measure first: `rick-rubin width <dir> bounces/atmos.wav --png` gives correlation, side share and mono loss
per band. Simple fix: Ozone Imager 2 with its width lowered, or Logic's Direction Mixer with Spread below
1 (`rick-rubin logic insert "Vocal bed" "Direction Mixer"`; read names with `rick-rubin logic devices
"Direction Mixer"`). Per band: STEREOVAULT, or a Channel EQ switched to Side-only processing with a low cut
on the sides near 200 Hz (set that mode by hand). Lost against SpaceControl: a limiter that acts only when
the phase goes bad. Inside Serum 2, `osc_a.width` and `fx.utility.width` narrow a patch at the source.

## How to check it
`rick-rubin width` on the track before and after: correlation in every band at or above 0, mono loss
smaller, side share in the low band near zero and rising with frequency. On the full mix,
`rick-rubin width <dir> --bars A-B` for the break: no band negative. `rick-rubin reference compare` for
width against the references. How wide it should feel is an ear call for Rohil.

## Why it works
Out-of-phase content cancels when the mix is summed to mono, on club systems and phones, and wide lows
weaken the centre where kick, bass and vocal live. Narrow below, wide above keeps both.
