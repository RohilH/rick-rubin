---
title: An 8-bar build made mostly of filter automation, then sweep, late snare roll, impact, riser, pre-drop hit
topic: arrangement
genres: [progressive house]
source: RYOS — Making Beautiful Progressive House | Studio Time with Ryos EP. 50 (https://youtu.be/WnZ7GN1tpek?t=1799)
status: untested
---
## What it is
The build has no new musical material. The drop's lead stack plays early behind a filter, a small kick and
clap repeat, and every part from the break is filtered away just before the drop. A few FX samples go on top.

## When to use it
After the drop is finished, so the build can lead into known material. "The name of the game with buildups"
is "a lot of filtering" (said, [30:58](https://youtu.be/WnZ7GN1tpek?t=1858)).

## How
1. Mark the build's first bar and add a small kick, tail shortened, and small claps (said,
   [9:07](https://youtu.be/WnZ7GN1tpek?t=547)). Here the build is bars 17 to 24 and the drop starts at 25 (shown,
   [34:20](https://youtu.be/WnZ7GN1tpek?t=2060)).
2. Start with the leads: the lead pattern plays through the build with a filter plug-in on the lead group
   (said, [29:59](https://youtu.be/WnZ7GN1tpek?t=1799)). Lanes shown at [30:08](https://youtu.be/WnZ7GN1tpek?t=1808):
   two filter frequencies, the filter's output and mix (the mix drops out at the drop), and the intensity of a
   build-up effect (Endless Smile) rising toward the last bars.
3. Repeat the kick and the clap through the build and filter them too, two filter lanes each (said,
   [30:15](https://youtu.be/WnZ7GN1tpek?t=1815); shown [31:12](https://youtu.be/WnZ7GN1tpek?t=1872)). The hits
   get denser at the end; the exact subdivision is not readable.
4. Filter out what remains from the break: the break bass and the main piano each get a filter lane that
   closes them over the last bars, which he calls magic right before the drop (said,
   [31:10](https://youtu.be/WnZ7GN1tpek?t=1870); shown [31:33](https://youtu.be/WnZ7GN1tpek?t=1893)).
5. A short sweep sample ending on the drop (said, [31:33](https://youtu.be/WnZ7GN1tpek?t=1893)).
6. Snare roll with its first part muted, so only kick and clap play at first (said,
   [32:05](https://youtu.be/WnZ7GN1tpek?t=1925)); it enters around bar 21 and has pitch and filter lanes (shown,
   [32:22](https://youtu.be/WnZ7GN1tpek?t=1942)).
7. An impact, a riser stretched to fit, and a big pre-drop snare or fill in the last half bar (said,
   [32:28](https://youtu.be/WnZ7GN1tpek?t=1948) to [33:09](https://youtu.be/WnZ7GN1tpek?t=1989)).

## In Rohil's setup
In a `song.py` this is a build section with `automation={track: {"filter": [start, end]}}` per part (values 0
to 1 over the section; `rick-rubin push --automation` writes it into Logic) and a section variant whose roll
starts halfway. In his own Logic project rick-rubin cannot write automation: insert the filter (`rick-rubin
logic insert "Lead Bus" AutoFilter`), then he draws the cutoff lane. FX samples from Splice, placed with
`rick-rubin logic add-audio sweep.wav --bar 24 --name Sweep`. Endless Smile is not installed; a rising reverb
send plus a high-pass does the same job more plainly. See also `ryos-transition-details-reverses-cuts-risers.md`.

## How to check it
`rick-rubin eval <dir> --bars 17-24` or a bounce split in 2-bar blocks: low-band energy should fall and
brightness rise bar by bar, with the lowest low-band level in the last bar and a clear jump at bar 25.
`rick-rubin reference compare` reports how much the spectrum changes between 2-bar blocks; the build should
score higher than the drop.

## Why it works
Taking energy away makes the drop feel bigger than adding more ever can, and hearing the lead early behind a
filter makes the drop sound like an arrival, not a surprise.
