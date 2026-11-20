---
title: A wide bass layer: duplicate the bass, chorus at full mix, cut the sub out of the copy
topic: sound-design
genres: [progressive house, bass house]
source: Alex Rome — 7 Useful Layering Techniques and Why They Work (https://youtu.be/u8ozR9cnCTU?t=270)
status: untested
---
## What it is
A second copy of the bass, made wide with a chorus and high-passed so it has no sub, sits around the mono bass. He
describes the result as the bass cradling the chords.

## When to use it
A drop that is heavy in the centre but small at the sides. Skip it in tech house grooves that depend on a tight, dry
low end. He warns it is hard to pull off; it only works if the phase holds.

## How
1. Duplicate the bass track with its notes (said, [4:41](https://youtu.be/u8ozR9cnCTU?t=281)).
2. On the copy add a chorus from the DAW's modulation effects and turn its mix all the way up (said,
   [4:50](https://youtu.be/u8ozR9cnCTU?t=290)). Any widening method would do; chorus is his choice here.
3. Adjust rate and depth by ear (said). The settings are not shown in a captured frame.
4. Compare: without the chorus the copy is "a very thin sound", with it "really wide" (said,
   [5:10](https://youtu.be/u8ozR9cnCTU?t=310)).
5. Low-cut the copy so everything in the sub region is gone: that zone belongs to the original bass (said,
   [5:20](https://youtu.be/u8ozR9cnCTU?t=320)).
6. Check for phasing on headphones (said, [5:23](https://youtu.be/u8ozR9cnCTU?t=323)). Ozone Imager 2 is open on the
   bass at [5:05](https://youtu.be/u8ozR9cnCTU?t=305).
7. A/B the drop with and without the layer ([5:44](https://youtu.be/u8ozR9cnCTU?t=344)).
8. Ours, inferred: cut at about 150 Hz, and bring the layer in well under the main bass.

## In Rohil's setup
Logic's Chorus or Ensemble on the duplicate with Mix at 100 %, then Channel EQ low cut. `rick-rubin logic insert "Bass
Wide" "Chorus"`, then `rick-rubin logic params "Bass Wide" Chorus` for the names before setting the mix. Inside Serum
instead: `rick-rubin serum set "<bass preset>" fx.chorus.wet=100 fx.utility.hpf=150 --fx-add chorus --fx-add utility
--save bass-wide --project <dir>`. Ozone Imager 2 and STEREOVAULT are his for the picture. The reese layer in
`../bass/ryos-pg-four-layer-bass-stack.md` does the same job with unison instead of chorus.

## How to check it
`rick-rubin width <dir> bounces/bass_stack.wav`: low band side energy stays near zero and correlation stays positive;
low-mid and mid side energy rise. Mono loss on the bass stack should be small (a large mono loss is the phasing he
warns about). `rick-rubin spectrum` on the copy alone: nothing below the cut.

## Why it works
A chorus mixes in delayed, pitch-wobbled copies that differ left and right, which the ear reads as width. Width in the
sub cancels in mono, so the wide copy is kept above it (second sentence inferred).
