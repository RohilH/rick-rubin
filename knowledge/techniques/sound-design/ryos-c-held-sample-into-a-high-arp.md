---
title: Turn one held note of an atmosphere into a thin, crisp arp: volume shape, dirt, flange, OTT, then cut it down to the highs
topic: sound-design
genres: [progressive house, any]
source: RYOS — KSHMR asked me to remix his song.. here's how I did it (https://youtu.be/mvZPg8zv_ig?t=673)
status: untested
---
## What it is
His "Sick Arp" is not an arpeggio. It is a single sustained note of a sampled atmosphere, chopped into
sixteenth pulses by a volume shaper and then processed until it is a bright rhythmic texture that lives only
in the high mids and highs.

## When to use it
A break that needs motion and top end at its midpoint without a new melody. The tremolo cards
(`ryos-pg-gated-pad-movement-after-the-synth.md`, `ryos-b-tremolo-that-deepens-toward-the-peak.md`) pulse a
chord pad; this one makes a new part out of a texture.

## How
The chain, in order (names shown, [12:05](https://youtu.be/mvZPg8zv_ig?t=725)):
1. Source: one held note from Output Arcade ([11:13](https://youtu.be/mvZPg8zv_ig?t=673)).
2. Motion: ShaperBox 3 volume, a drawn curve of four fast-decaying spikes per quarter note, the second
   spike lower, mix 79 % (shown 12:05; levels approximate).
3. "Sauce": RC-20 on a guitar preset ("Lush & Crunch Guitar 1", shown
   [12:45](https://youtu.be/mvZPg8zv_ig?t=765)) for a little distortion and space.
4. Bit-crush: Thermal, preset "Vapor Waiver" (said), chosen to add crisp high-end excitement
   ([12:36](https://youtu.be/mvZPg8zv_ig?t=756)).
5. Multiband distortion used as an EQ (DST): lows and low mids down a little, high mids and highs up a lot.
   He calls this the step that brings it from "dead" to "alive" ([13:20](https://youtu.be/mvZPg8zv_ig?t=800)).
6. Stereo flange (ValhallaUberMod) for extra movement; OTT for squeeze and polish; Kickstart 2, light and
   constant, as bounce more than ducking ([14:02](https://youtu.be/mvZPg8zv_ig?t=842) to 15:11).
7. Tilt shelf at 900 Hz, +2.4 dB: brighter and less low mid in one move (shown,
   [15:45](https://youtu.be/mvZPg8zv_ig?t=945)). Then a low cut at 344 Hz, 24 dB/oct (shown,
   [16:15](https://youtu.be/mvZPg8zv_ig?t=975)): the arp should be heard, not felt, and sit at a distance.
8. Width control last (`ryos-c-keep-wide-layers-in-phase.md`), then filter and volume automation for the
   build ([18:47](https://youtu.be/mvZPg8zv_ig?t=1127)).

## In Rohil's setup
Source: a long Splice atmosphere or one held Serum 2 note. If the source is a Serum patch the pulse can be
in the patch: `lfo_1.shape="Basic/Saw Down" lfo_1.rate="1/16"` with `--mod lfo_1:osc_a.level_db:-40` (the
depth is our guess, as in the gated-pad card). On audio: Logic's Tremolo at 1/16 with a sharp shape (lost:
the drawn accent pattern). Then Logic's Bitcrusher, ChromaGlow or Overdrive for steps 3 and 4 (lost: the
RC-20 and Thermal presets), Exciter or ANIMATE for step 5, Logic's Flanger, OTT, Kickstart 2
(`rick-rubin logic insert Arp "Kickstart 2" Mix=0.2`), and Channel EQ for step 7. Read parameter names with
`rick-rubin logic devices <plug-in>` before setting any.

## How to check it
`rick-rubin hits` or a zoomed `rick-rubin view` on the bounced track: four pulses per beat. `rick-rubin
spectrum <dir> arp_before.wav arp_after.wav`: almost nothing below about 350 Hz and clearly more above 3 kHz
after. `rick-rubin width <dir> arp_after.wav`: correlation not negative. Then before and after for Rohil.

## Why it works
A volume shape gives any sustained sound a rhythm, and distortion plus bit-crushing create highs the sample
never had, so a dull texture becomes the break's top-end pulse without adding a note.
