---
title: Order a break's entries by frequency: spacious atmospheres first, a thin high arp next, chords when the vocal's harmonies arrive
topic: arrangement
genres: [progressive house, any]
source: RYOS — KSHMR asked me to remix his song.. here's how I did it (https://youtu.be/mvZPg8zv_ig?t=653)
status: untested
---
## What it is
His rule for what to add to a break and in which order: "slowly pack on the frequencies". It sharpens
`ryos-something-significant-every-eight-bars.md` (add something) and `ryos-b-strip-the-break-then-add-in-stages.md`
(return muted parts): here each addition is chosen for the band it fills and for staying clear of the stars.

## When to use it
A break built around a vocal and one strong sound, where each new layer either hides the vocal or changes nothing.

## How
1. Name the stars. Here a break bass is the "main character" and the vocal is the only bright element
   (said, [3:57](https://youtu.be/mvZPg8zv_ig?t=237), [3:11](https://youtu.be/mvZPg8zv_ig?t=191)).
2. Stage one, atmospheres only: a gated vocal bed, occasional horn-like slides, a vocal throw, a wide vocal
   bed. Atmospheres suit a dark mood and, being spacious, do not get in the bass's way (said, 3:57 to 4:38).
3. Let even stage one move: the bed starts behind a low-pass, almost absent, and opens over the break
   (said, [7:03](https://youtu.be/mvZPg8zv_ig?t=423)).
4. One-off sounds are placed, not looped, so that about every eight bars something new is heard; he says
   this matters in any genre and is what makes a track sound professional
   (said, [7:25](https://youtu.be/mvZPg8zv_ig?t=445) to 8:26).
5. Stage two, more bite: an arp that lives only in the high mids and highs, with a bit-crushed top
   ([10:53](https://youtu.be/mvZPg8zv_ig?t=653); `ryos-c-held-sample-into-a-high-arp.md`).
6. Stage three, harmony: the first chords of the break, a plain saw pad plus a washed supersaw pad, timed to
   the point where the vocal repeats and its harmonies come in. They add impact and warmth
   (said, [19:29](https://youtu.be/mvZPg8zv_ig?t=1169) to 20:56).
7. Compare the first and last bars of the synth group: the end should be clearly fuller and brighter than
   the start (said, [21:41](https://youtu.be/mvZPg8zv_ig?t=1301)).
8. If the break lacks top end because only the vocal is bright, generate it with a bright reverb instead of
   another instrument (`ryos-c-bright-washed-reverb-as-top-end.md`).

## In Rohil's setup
For the hip-hop vocal remix: stage one from Splice atmospheres retuned to the key (`rick-rubin notes`, then
`rick-rubin conform <dir> samples/atmos.wav --transpose N`) and from pieces of the acapella; stage two and
three from Serum 2. Find the vocal's repeat with `rick-rubin transcribe`. Opening a bed: Logic's AutoFilter
with its cutoff automated by hand (rick-rubin cannot write automation into his project). In a `song.py`,
give each stage its own tracks and start bars so `rick-rubin score` shows the order.

## How to check it
Bounce the break's first four and last four bars and run `rick-rubin compare <dir> break_start.wav
break_end.wav`: energy in the high-mid and top bands and overall loudness should rise, while the vocal's
own band (roughly 1 to 4 kHz) is not masked: `rick-rubin spectrum <dir> vocal.wav synths_end.wav`.
`rick-rubin reference compare`: texture changes per minute for the break inside the references' range.

## Why it works
Filling empty bands one at a time makes each entry audible as growth, and nothing new lands in the band the
stars already occupy.
