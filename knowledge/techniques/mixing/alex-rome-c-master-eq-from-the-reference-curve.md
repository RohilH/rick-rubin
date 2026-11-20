---
title: Close small tonal gaps to the reference with one broad EQ on the master
topic: mixing
genres: [any, progressive house, tech house, bass house]
source: Alex Rome — Give me 19 mins, and I'll Improve your mixing skills by 126% (https://youtu.be/XrGZPWuiJ7o?t=1047)
status: untested
---
## What it is
After the level-matched A/B has shown what differs, the differences that are small and broad (a little too much low
end, a little dull on top) are fixed with two shelves on the master instead of reopening every track.

## When to use it
Late in the rough mix, when the reference says "slightly darker and bass-heavy" rather than "the hat is missing". Not
when one instrument is wrong: that is fixed on its track (said, [17:27](https://youtu.be/XrGZPWuiJ7o?t=1047)).

## How
1. Choose the reference: same genre, same lead instrument, similar bassline (said,
   [15:00](https://youtu.be/XrGZPWuiJ7o?t=900)). His is a Kygo piano house track for a piano house drop.
2. Switch back and forth, letting the ear settle on each for a few seconds before switching (said,
   [15:40](https://youtu.be/XrGZPWuiJ7o?t=940)).
3. Ask three questions only: is mine as bright, are the levels as even, is the kick as present. Ignore that the
   reference has more instruments (said, [18:28](https://youtu.be/XrGZPWuiJ7o?t=1108)).
4. Read the plug-in's tonal curve. Before: about 4 dB too much near 100 Hz and up to 10 dB too little above 5 kHz
   (shown [14:55](https://youtu.be/XrGZPWuiJ7o?t=895), REFERENCE 2's Trinity Display).
5. Decide where to fix. Big or single-instrument gaps: in the mix (lead brighter with OTT or EQ, bass fader down).
   Small broad gaps: master EQ (said, [17:47](https://youtu.be/XrGZPWuiJ7o?t=1067)).
6. His master EQ: a low shelf at 86.1 Hz, −5.08 dB, Q 0.71, plus a shelf lifting everything above about 1 kHz by
   roughly 2.5 dB (shown [17:58](https://youtu.be/XrGZPWuiJ7o?t=1078); the second band's numbers are read off the
   curve). After it the tonal curve stays within about 2 dB (shown [18:45](https://youtu.be/XrGZPWuiJ7o?t=1125)).
7. A 5 dB low shelf is large for a master. It worked here because his bass was simply too loud; turning the bass down
   would be the cleaner fix (inferred).

## In Rohil's setup
REFERENCE is his and its curve is the same display. The numbers version: `rick-rubin logic bounce bounces/drop.wav
--bars 33-48`, `rick-rubin reference compare <dir> bounces/drop.wav`, which prints the band shares against the shelf
of released tracks. The shelves go on the Stereo Out in Channel EQ (Logic comes to the front for Stereo Out changes),
or use BASSROOM (lows) and MIXROOM (mids and highs), which he owns and which propose a curve toward a target. Keep
moves within about 3 dB.

## How to check it
Bounce again after the EQ and rerun `reference compare`: the tonal rows flagged before (sub and bass share high, high
and air share low) should now sit inside the references' min to max. If only one row moves and another leaves the
range, undo and fix the track instead.

## Why it works
A whole-mix tilt is one decision applied evenly, so the balance between parts that was set by ear is kept (inferred).
