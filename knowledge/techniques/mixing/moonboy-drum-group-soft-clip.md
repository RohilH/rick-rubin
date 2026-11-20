---
title: Group the drums and soft clip the group to make them loud without mud
topic: mixing
genres: [tech house, bass house, any]
source: MOONBOY — HOW TO TECH HOUSE | Full Tutorial (Odd Mob, Chris Lake, Mau P) (https://youtu.be/JqKaSvHImB0?t=217)
status: untested
---
## What it is
All drum tracks go to one group, are balanced there, and the group's peaks are shaved by a soft clipper
rather than squeezed by a compressor. He calls it the cleanest way to get loud drums.

## When to use it
As soon as the beat has more than two lanes, and before bass and vocal come in, so the drums already sit at
a fixed peak level when everything else is balanced against them.

## How
1. Put every drum track in one group (said, [3:37](https://youtu.be/JqKaSvHImB0?t=217)).
2. Balance the faders by ear first; his example: ghost snare and crash about 6 dB under kick and clap (said
   and shown, [4:19](https://youtu.be/JqKaSvHImB0?t=259)).
3. Put a Glue Compressor on the group and switch Soft Clip on (said). Everything else stays at its default:
   threshold 0 dB, make-up 0 dB, dry/wet 100 % (shown at [4:35](https://youtu.be/JqKaSvHImB0?t=275)). So the
   compressor itself does nothing; the device is used only as a clipper (inferred).
4. Put fill and transition effects on the same group (see the band-pass card).

## In Rohil's setup
- The drums become a summing Track Stack in Logic. Logic's Compressor has a Distortion switch (Soft, Hard,
  Clip) in its output section: `rick-rubin logic insert Drums Compressor`, then read the real parameter names
  with `rick-rubin logic params Drums Compressor` before setting them; keep the threshold high enough that
  the gain-reduction meter stays at 0 and set Distortion to Soft.
- What is lost: Ableton's clipper has a fixed ceiling just under 0 dB; in Logic the amount of clipping
  depends on how hard the stack hits the Compressor, so drive it with the make-up or the stack's input level.
- Mastering The Mix LIMITER on the stack is the cleaner alternative if clipping sounds harsh.

## How to check it
Bounce the drum stack before and after: `rick-rubin logic bounce bounces/drums_clip.wav --bars 9-16 --tracks
Drums`, then `rick-rubin audition <dir> bounces/drums_dry.wav bounces/drums_clip.wav`. The peak should drop
by 1 to 3 dB at the same loudness (crest falls); attack times should not get longer. If "transient contrast"
in `reference compare` falls below the references, it is clipping too much.

## Why it works
Drum peaks are a few milliseconds long and set the headroom of the whole mix. Clipping them is inaudible in
small amounts and lets the body of every hit come up, where a compressor would pump and soften the attacks.
