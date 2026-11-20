---
title: Take the click off a wide clap so its transient does not stack on the kick, then add a clap with a tail
topic: drums
genres: [progressive house, tech house, bass house, any]
source: RYOS — Making Progressive House MAGIC | Studio Time with Ryos EP. 51 (https://youtu.be/srkGlUWW3pg?t=946)
status: untested
---
## What it is
In house the clap lands on the same beat as a kick. He softens the first milliseconds of the clap with a
volume shaper so that only the kick supplies the hit, and gets the clap's size from width and from a second,
longer clap.

## When to use it
Beats 2 and 4 sound harsh or spiky; the kick seems to lose punch when the clap is unmuted.

## How
1. Choose the clap for width. He types "wide clap" into his sample browser and takes a wide one-shot
   ([15:24](https://youtu.be/srkGlUWW3pg?t=924)).
2. Its transient is "a bit harsh": put LFOTool on the clap with a shape that ramps the volume up from low to
   full, so the very start of each hit is turned down (said, [15:46](https://youtu.be/srkGlUWW3pg?t=946); a
   rising ramp in the graph, shown [16:05](https://youtu.be/srkGlUWW3pg?t=965)). His preset list contains one
   called "Transient Eraser"; which preset he loaded is not readable.
3. His reason: sometimes he does not want the clap's transient stacking with the kick's. Sometimes the stack
   "does sound cool"; here clean is better (said, [16:10](https://youtu.be/srkGlUWW3pg?t=970)). So it is a
   choice per track, made by listening to kick and clap together.
4. Layer a second clap that has more tail, for length ([16:10](https://youtu.be/srkGlUWW3pg?t=970)).
5. Another answer to the same problem is in `moonboy-clap-slightly-before-the-kick.md`: move the clap
   instead of softening it.

## In Rohil's setup
On an audio clap in Logic the simplest version is a fade-in of a few milliseconds on the region (by hand). As
a plug-in: Logic's Enveloper with the attack gain turned down (`rick-rubin logic insert Clap Enveloper`, then
`rick-rubin logic params Clap Enveloper` to read the names before `logic tweak`). Kickstart 2 is too slow for
this; it shapes a whole beat. Lost against LFOTool: drawing the exact ramp. Width: pick a clap that is
already wide (`rick-rubin audition <dir> <claps...>` reports width) before reaching for an imager.

## How to check it
`rick-rubin audition <dir> clap_before.wav clap_after.wav`: the punch (transient) figure of the clap falls,
its length and width do not. Bounce kick and clap together and run `rick-rubin hits <dir> --tracks Kick Clap`
or `rick-rubin compare <dir> kick.wav kick_clap.wav`: the peak on beats 2 and 4 should be no more than about
1 dB above the kick alone (inferred target). Then before and after for Rohil.

## Why it works
Two transients at the same instant add up to a taller peak that a clipper or limiter then flattens, costing
the kick its punch. With one clear transient per beat, the clap's body and width are heard after it.
