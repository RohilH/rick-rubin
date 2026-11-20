---
title: The stutter house vocal: a long held phrase chopped by a tempo-synced tremolo, with a few degrees of phase for width
topic: sound-design
genres: [bass house, progressive house, tech house]
source: MOONBOY — 13 Insane Ways to Make Any Vocal Sound MAGICAL (https://youtu.be/7wcJShg8tn4?t=577)
status: untested
---
## What it is

The fluttering vocal of stutter house (he names the genre, and Fred again.. earlier in the video). There is
no chopping of audio: an auto-panner with its phase turned to zero becomes a volume gate, synced to the
tempo, on a vocal phrase that is long and drawn out.

## When to use it

On sustained sung notes: the last word of a line, an "ooh", a hook held over a bar. It needs sustain to
chop; on fast rap syllables it only removes words. Good in a build (speed the rate up) or as the drop's hook.

## How

1. Choose a part of the vocal with a long, drawn-out melody; longer phrases give more to shape (said,
   [9:50](https://youtu.be/7wcJShg8tn4?t=590)).
2. Auto Pan on the vocal: raise the amount (86.5 % on screen), which at first pans left and right (said and
   shown at [10:25](https://youtu.be/7wcJShg8tn4?t=625)).
3. Turn the phase down to 0°, so both sides move together and it only changes the volume (said; 0.00°
   shown).
4. Switch the rate from Hz to tempo sync (said; the synced value he lands on is not readable, 1/8 and 1/4
   appear on his other vocal tracks).
5. Width: nudge the phase up slightly; left and right are then a little offset and the flutter spreads
   (said, [10:39](https://youtu.be/7wcJShg8tn4?t=639); about 14° on a similar track at
   [8:40](https://youtu.be/7wcJShg8tn4?t=520)).
6. Shape variants: sine is a soft flutter; a saw is a hard chop; an inverted saw sounds like ducking; a
   rising ramp sounds reversed (said of the Auto Pan saw at [8:31](https://youtu.be/7wcJShg8tn4?t=511) and of
   the drawn LFO version at [11:41](https://youtu.be/7wcJShg8tn4?t=701)).
7. The vocal he demonstrates on is already wet (file name ends "WET", shown), so the gate cuts reverb too.

## In Rohil's setup

- Logic's Tremolo is the same device idea: `rick-rubin logic insert Vocal Tremolo`, then
  `rick-rubin logic params Vocal Tremolo` for its names: phase 0° for a pure gate (180° is auto-pan), rate
  synced to 1/8 or 1/16, depth 85 to 100 %, and a few degrees of phase for width. Its symmetry and smoothing
  controls move it between soft and choppy.
- For the inverted-saw "duck" shape use Kickstart 2 instead (`rick-rubin logic insert Vocal "Kickstart 2"
  Mix=1.0`). Put the effect on a copy of the phrase on its own track, so the rest of the vocal stays whole.
- Rate changes over a build are automation: drawn by hand in Logic.

## How to check it

`rick-rubin logic bounce bounces/vox_stutter.wav --bars A-B --tracks "Vocal stutter"`, then `rick-rubin hits
<dir> bounces/vox_stutter.wav`: level peaks on every 8th (or 16th) and deep dips between, constant through
the phrase. `rick-rubin width`: correlation stays positive; a little more side energy with the phase raised.

## Why it works

A held note has no rhythm of its own, so any rhythm imposed on its volume is heard clearly, and because the
gate is locked to the grid the vocal becomes a percussion part that is always in time.
