---
title: Give a vocal a world: a width-delay-reverb-compress rack, plus a copy turned into a pad underneath
topic: sound-design
genres: [bass house, progressive house]
source: MOONBOY — HOW TO BASS HOUSE (Knock2, Skrillex, Porter Robinson) (https://youtu.be/3-0JCDyiPaw?t=455)
status: untested
---
## What it is
Two effect racks on one vocal. The first keeps the vocal clear but wide and in a space. The second runs in
parallel and smears a copy of the vocal into a sustained pad, so the phrase sits in a drone made of itself.
He points to Fred again.. as someone who leans on the second effect.

## When to use it
On the main vocal phrase of a breakdown or an ethereal drop, where a dry sample would sound pasted on. Not
on a rhythmic tech house vocal, which wants to stay dry and tight.

## How
1. **Clean rack**, in his order (shown at [7:43](https://youtu.be/3-0JCDyiPaw?t=463); said at
   [7:40](https://youtu.be/3-0JCDyiPaw?t=460)): hyper (4 voices) and dimension for width; EQ with a low cut;
   delay, tempo-synced, 1/4 on both sides, ping-pong, its filter around 710 Hz; hall reverb; compressor last
   to bring it forward. Macros named Clean EQ, Compress, Reverb.
2. **Pad rack** (shown at [8:10](https://youtu.be/3-0JCDyiPaw?t=490)): a filter of the "Reverb" type; a delay
   with both sides linked at an unsynced time (1.21 shown) for a smear rather than an echo; flanger; hall
   reverb; compressor; EQ. Macros named Padify, Prefilter, BP Width, Movement. He says it makes a pad out of
   anything.
3. **Parallel**: both racks sit as two chains of one effect rack, the first at −1.8 dB and the second at
   0.0 dB (shown at [8:20](https://youtu.be/3-0JCDyiPaw?t=500)), so the clean vocal and its pad play together
   (said: layered underneath the clean vocal).
4. Mix amounts inside the racks are not readable.

## In Rohil's setup
He has no SerumFX rack presets, so build it from what is installed:
- Clean chain on the vocal track: Channel EQ (low cut near 120 Hz), then Ozone Imager 2 for width, then
  Compressor. Delay and reverb as sends so they can be automated: `rick-rubin logic send Vocal 1 -14` to a
  bus with Stereo Delay (1/4, ping-pong) and `rick-rubin logic send Vocal 2 -12` to one with ChromaVerb.
- Pad chain: a third bus (`rick-rubin logic send Vocal 3 -6`) with ValhallaSupermassive 100 % wet (long
  decay, high feedback, some modulation), then a Channel EQ cutting below 200 Hz and above 6 kHz, then a
  Compressor. Read its parameter names with `rick-rubin logic devices ValhallaSupermassive` first.
- Bus numbers and send levels are ours; check what the project already uses with `rick-rubin logic inspect`.

## How to check it
Bounce the vocal with and without the pad bus (`rick-rubin logic bounce ... --tracks Vocal`). With it,
`rick-rubin audition` should show a much longer decay and `rick-rubin width` more side energy in the mids;
`rick-rubin transcribe` must still find every word. The pad bus alone should have no clear syllables.

## Why it works
A long, filtered, modulated wash of the vocal has the vocal's own pitch and vowel colour, so it supports the
phrase like a chord in the right key without anyone having to write that chord.
