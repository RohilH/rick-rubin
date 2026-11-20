---
title: Duck the sub with a volume curve traced from this kick's own shape, not a stock sidechain curve
topic: mixing
genres: [progressive house, tech house, bass house, any]
source: RYOS — Making Progressive House MAGIC | Studio Time with Ryos EP. 51 (https://youtu.be/srkGlUWW3pg?t=1164)
status: untested
---
## What it is
When the kick and the sub "aren't working the best together", he draws the kick's volume envelope in a
volume shaper on the sub and applies it upside down. The sub is silent while the kick is loud, creeps in
under the kick's tail and is at full level the moment the kick has ended.

## When to use it
A long kick over a sustained sub; a low end that is either muddy on the hit or has a hole after it.

## How
1. Put a volume shaper on the sub (Xfer LFOTool) and feed the kick to it only so the kick's waveform can be
   seen while drawing (said, [19:24](https://youtu.be/srkGlUWW3pg?t=1164)).
2. Rate: one cycle per beat (1/4, shown [20:25](https://youtu.be/srkGlUWW3pg?t=1225)).
3. Draw the kick: full level at the start, sloping to roughly three quarters a little past the middle of the
   beat, then a steep fall to zero at about 60 % of the beat, zero until the next beat (shown 20:25; read
   from the graph, so approximate).
4. Turn the shaper's volume amount the opposite way from usual, so the sub gets the mirror image of the
   drawn curve (said, [20:17](https://youtu.be/srkGlUWW3pg?t=1217)).
5. Test with kick and sub together; he is satisfied at once ([20:37](https://youtu.be/srkGlUWW3pg?t=1237)).
6. Arithmetic (ours): at 128 BPM a beat is 469 ms, so this sub is held back for about 280 ms. A shorter kick
   needs a shorter curve; the point is that the curve's length equals the kick's.

## In Rohil's setup
He has no drawable shaper. In order of closeness:
- Kickstart 2 on the sub: measure the kick first (`rick-rubin audition <dir> samples/kick.wav` gives its
  length), then pick the `Used Wave` whose recovery ends where the kick does and bounce two or three
  candidates: `rick-rubin logic insert Sub "Kickstart 2" Mix=1.0`. Lost: an exact mirror of the kick.
- Trackspacer 2.5 on the sub, keyed from the kick: it ducks by the kick's actual level and spectrum, so it
  follows this kick without drawing. Lost: a guaranteed full duck on every hit.
- Logic's Compressor keyed from the kick: `rick-rubin logic insert Sub Compressor --sidechain Kick`, release
  set near the kick's length.
In a `song.py` the sub's sidechain choice is one line; try `sidechain="kickstart"` against a keyed compressor.

## How to check it
Bounce kick and sub together and each alone (`rick-rubin logic bounce ks.wav --bars A-B --tracks Kick Sub`).
`rick-rubin compare <dir> kick.wav ks.wav`: the peak of the pair should be within about 1 dB of the kick
alone (inferred target), while the pair's low-band loudness is clearly higher. `rick-rubin reference compare`:
the low-end pump figure inside the references' range. Depth is then an ear call for Rohil.

## Why it works
Two sounds below 100 Hz add up to peaks and cancellations. Giving the sub exactly the time the kick does not
use keeps both at full strength with no overlap and no gap.
