---
title: Low-cut every track except the kick and the bass
topic: mixing
genres: [any, tech house, bass house, progressive house]
source: Alex Rome — 10 Mixing Tips That Changed My Life (https://youtu.be/cU0tHoyJYjo?t=20)
status: untested
---
## What it is
A high-pass (Logic calls it a low cut) on every channel that is not kick or bass, including ones that seem to have
no low end, so the sub region belongs to two sources only.

## When to use it
At the start of every mix, and on each new sample as it comes in. Hats, claps, tops, vocals, FX, pads, reverb
returns. Also when the sub sounds cloudy or the mix will not get loud.

## How
1. Open an EQ with its analyzer on and play the track alone: even a closed hat shows content under 500 Hz (shown
   [1:08](https://youtu.be/cU0tHoyJYjo?t=68), Channel EQ analyzer on a hat).
2. Switch on the low-cut band and raise it until everything in the sub region is gone. He names 40 to 80 Hz as the
   zone to protect (said). On the hat he ends up at 176 Hz, 12 dB/oct, Q 0.71 (shown
   [1:20](https://youtu.be/cU0tHoyJYjo?t=80)).
3. It should not change how the instrument sounds; if it does, back the frequency down (said for the hat).
4. Repeat on every non-bass track (said).
5. How high to go per source (ours, inferred): just under the lowest thing the part needs. Hats and tops can go to
   300 Hz or more; claps and snares around 120 to 200 Hz; pads and leads around 100 to 150 Hz.

## In Rohil's setup
Channel EQ is Logic's own and is what he uses. `rick-rubin logic inspect` lists every strip and its inserts, so the
tracks without an EQ are visible at once. `rick-rubin logic insert Hats "Channel EQ"` adds one; read its parameter
names with `rick-rubin logic devices "Channel EQ"` before setting the low cut with `logic tweak`. In a `song.py`
project the rule already exists as lint: nothing but kick and bass below C2.

## How to check it
Bounce the track alone before and after (`rick-rubin logic bounce bounces/hat_a.wav --tracks Hats`) and overlay
them: `rick-rubin spectrum <dir> bounces/hat_a.wav bounces/hat_b.wav`. Energy below the cut should drop and the rest
should not move. On the full mix, `rick-rubin width` low-band side energy should fall towards zero.

## Why it works
Sub energy eats headroom whether or not you can hear it, and many small amounts add up. Removing it leaves the
limiter working on the kick and bass only (inferred from his headroom argument).
