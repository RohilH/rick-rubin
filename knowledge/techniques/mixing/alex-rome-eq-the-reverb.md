---
title: EQ the reverb, low cut to about 500 Hz and a high cut to taste
topic: mixing
genres: [any, tech house, bass house, progressive house]
source: Alex Rome — 10 Mixing Tips That Changed My Life (https://youtu.be/cU0tHoyJYjo?t=373)
status: untested
---
## What it is
Filtering the reverb itself, not the dry sound: the low end and the hiss of the tail are removed so the reverb adds
space without filling the spectrum and the stereo field.

## When to use it
On every reverb, always. He says he almost never leaves one full range. Most urgent on claps, snares and vocals, and
whenever a mix will not get loud for no obvious reason.

## How
1. Listen to the reverb alone and look at it: a clap's tail covers the whole stereo image and the whole spectrum
   (shown [7:10](https://youtu.be/cU0tHoyJYjo?t=430): Ozone Imager 2 and Channel EQ on the soloed reverb).
2. Use the reverb's own EQ section (said: every reverb has one).
3. Low cut up to 500 Hz (said; shown [7:56](https://youtu.be/cU0tHoyJYjo?t=476) in ValhallaVintageVerb: LowCut from
   10 Hz to 500 Hz).
4. High cut down until the hiss is tamed, by ear (said; shown [8:06](https://youtu.be/cU0tHoyJYjo?t=486): HighCut
   from 20 kHz to about 9 kHz).
5. Then set the reverb's level for the part (said).
6. His reverb for the demo: Room mode, 1970s colour, decay 0.62 s, predelay 20 ms (shown
   [7:00](https://youtu.be/cU0tHoyJYjo?t=420)).

## In Rohil's setup
He has Valhalla Supermassive and Logic's ChromaVerb, not VintageVerb; what is lost is only that plug-in's colour
modes. Simplest route that works with any reverb: reverb on a bus (`rick-rubin logic send Clap 1 -14`), then a
Channel EQ after it on the Aux with a low cut near 500 Hz and a high cut near 9 kHz. Supermassive also has its own
cut controls; read their names with `rick-rubin logic params <aux> ValhallaSupermassive --pages 2` first. Changes on
an Aux bring Logic to the front.

## How to check it
Bounce the part with its reverb before and after and overlay: `rick-rubin spectrum <dir> a.wav b.wav`. Energy below
500 Hz should fall to the dry sound's own. On the full mix, `rick-rubin width` side energy in the low and low-mid
bands should drop, and `reference compare` crest and loudness should have more room.

## Why it works
Reverb is the widest, most full-range thing in a mix. Its lows mask the kick and bass and its width costs headroom,
while the sense of space lives mostly in the mids (said in substance; the last clause is inferred).
