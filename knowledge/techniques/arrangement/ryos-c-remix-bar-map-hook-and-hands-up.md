---
title: Bar map of a finished remix at 130 BPM: two different halves, the second with a stripped hook and a hands-up section
topic: arrangement
genres: [progressive house, any]
source: RYOS — KSHMR asked me to remix his song.. here's how I did it (https://youtu.be/mvZPg8zv_ig?t=975)
status: untested
---
## What it is
The section markers and the break-synth clips of his KSHMR remix, read from the playlist. Unlike
`ryos-pg-break-build-drop-bar-map.md` (a demo with one drop) this is a full arrangement, and its second half
is not a copy of the first.

## When to use it
Laying out a remix once a break and a drop exist; deciding what the second break does differently.

## How
Markers (shown, [16:15](https://youtu.be/mvZPg8zv_ig?t=975); read from a 720p ruler, give or take a bar;
only the break synths are visible, not drums, bass or vocal):

| Section | Bars | Break synths playing |
|---|---|---|
| Intro | 1–16 | flutter bed, slides, arp (thinned by an automated EQ), one vocal throw; bars before 10 not in view |
| Break | 17–34 | vocal atmosphere bed fades in; flutter bed from 19; slides at 24 and 32; throws late in 22 and 30; a half-bar gap in every bed before 27; from 27 the arp, a saw pad and a washed supersaw pad |
| Build | 35–42 | arp and flutter bed continue and are filtered away |
| Drop | 43–58 | none of these |
| 2nd Break | 59–74 | beds and slides again; arp and both pads from 67 |
| Hook | 75–82 | only the vocal bed and one pad |
| Hands Up | 83–90 | both pads, a dance piano, a distorted horn, flutter bed, a buzzy top bass; a wind-up siren leads in from 82 |
| Build | 91–98 | arp and flutter bed |
| Drop | 99– | not visible |

1. The first break is 18 bars, not 16: the first two hold almost nothing but a bed fading in (shown,
   [5:00](https://youtu.be/mvZPg8zv_ig?t=300); the reason is not given).
2. Each break changes at its midpoint: bar 27 and bar 67 are where the arp and the chords enter, which is
   where the vocal repeats with harmonies (said, [19:50](https://youtu.be/mvZPg8zv_ig?t=1190)).
3. After the second break the energy dips to a hook, then rises to "hands up": big, floaty, with three
   sounds saved for this moment plus a driving buzzy bass (said, [22:02](https://youtu.be/mvZPg8zv_ig?t=1322),
   [26:18](https://youtu.be/mvZPg8zv_ig?t=1578)).
4. The intro previews break material thinned out, which matches
   `ryos-intro-previews-filtered-gets-to-the-point.md`.
5. At 130 BPM a bar lasts 1.85 s, so the second drop starts about 3:01 in (our arithmetic).

## In Rohil's setup
Put the same kind of markers in Logic by hand (session mode cannot create markers), or name the sections in
a `song.py` and read them back with `rick-rubin score`. Hold back two or three sounds for the second half
when choosing sounds for the first. For a vocal remix, set the midpoint entries from the acapella:
`rick-rubin transcribe <dir> samples/vocal.wav` shows where a phrase repeats.

## How to check it
`rick-rubin logic inspect` lists regions per track: each section should have at least one track that starts
or stops at its boundary, and the second half should contain tracks that have no region in the first.
`rick-rubin reference compare`: section lengths and texture changes per minute against the references.

## Why it works
A listener who has heard break, build and drop once expects them again; a hook and a new section before the
last drop spend that expectation, so the final drop arrives fresh.
