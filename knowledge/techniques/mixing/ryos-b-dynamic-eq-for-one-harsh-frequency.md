---
title: Tame one harsh frequency with a dynamic EQ band, not a deep static notch
topic: mixing
genres: [any]
source: RYOS — Pro Secrets for Creating EDM Breakdowns (https://youtu.be/l_XjHmumqQk?t=367)
status: untested
---
## What it is
A narrow EQ band that only cuts when the offending frequency gets loud, and backs off the rest of the time.
Ryos uses it wherever a sample has one "rogue" ringing frequency.

## When to use it
A vocal chop, lead or sample with one piercing resonance, most audible after distortion, brightening or OTT.
A static notch is still fine for a constant hum.

## How
1. Find the frequency on the analyser. On his vocal chop the band sits at about 1.78 kHz, narrow (shown,
   [6:18](https://youtu.be/l_XjHmumqQk?t=378)).
2. The easy fix is a tight band pulled all the way down. He avoids it: depending on the region it can leave the
   sound nasal and artificial (said, [6:29](https://youtu.be/l_XjHmumqQk?t=389)).
3. Make the band dynamic instead (FabFilter Pro-Q 3). It takes away only what is needed and leaves the rest
   (said, [6:50](https://youtu.be/l_XjHmumqQk?t=410)).
4. What that looks like on his chop: a deep dip on the first hit, which reads as about 9 dB in the captions,
   then resting around 3 to 6 dB of cut (said, [7:02](https://youtu.be/l_XjHmumqQk?t=422)).
5. It sits last in the chain, after the delay and reverb, in the same EQ as the low cut (shown,
   [6:18](https://youtu.be/l_XjHmumqQk?t=378)).

## In Rohil's setup
Logic's Channel EQ has no dynamic bands. Nearest tools he has:
- **DeEsser 2** (Logic), set to split mode with its frequency on the resonance: it turns down only that band
  and only when it is loud. `rick-rubin logic insert "Vocal Chop" "DeEsser 2"`, then `rick-rubin logic params
  "Vocal Chop" "DeEsser 2"` for its names. Lost against Pro-Q 3: the bell shape and Q are coarser.
- **RESO** (Mastering The Mix), a dynamic resonance suppressor: place a node on the frequency and set its
  depth. The bridge has so far failed to insert RESO, so Rohil loads this one by hand.
- Find the frequency by measurement: `rick-rubin spectrum <dir> chop.wav` and look for one peak standing well
  above its neighbours.

## How to check it
`rick-rubin spectrum <dir> before.wav after.wav`: the one peak comes down several dB, its neighbours do not
move. `rick-rubin compare`: overall level and brightness nearly unchanged. If the whole upper mid band drops,
the band is too wide or too deep. The nasal test is by ear: bounce a static-notch version too.

## Why it works
A resonance is only a problem at the moments it rings. A static notch also removes that frequency from every
quiet moment, which is what makes a sound thin or nasal.
