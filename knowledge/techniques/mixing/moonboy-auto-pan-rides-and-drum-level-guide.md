---
title: A starting drum balance (kick 0, clap 0, crash −12, rides −16) and auto-panned rides for width
topic: mixing
genres: [bass house, tech house]
source: MOONBOY — HOW TO BASS HOUSE (Knock2, Skrillex, Porter Robinson) (https://youtu.be/3-0JCDyiPaw?t=103)
status: untested
---
## What it is
Two mix moves for the drum kit: a fader guide that keeps cymbals far under kick and clap, and an auto-panner
on the ride layer so the only wide drum element is the quiet one at the top.

## When to use it
As the first balance of any house kit, before anything else is mixed against it; and whenever the top end
measures mono or the cymbals make the drop harsh.

## How
1. Faders, from his on-screen guide ([1:59](https://youtu.be/3-0JCDyiPaw?t=119)): kick 0 dB, clap 0 dB,
   crashes −12 dB, rides −16 dB (shown). He adds that cymbals and hats should never be loud (said).
2. For comparison, the tech house video puts ghost snare and crash at −6 dB (shown there,
   [4:22](https://youtu.be/JqKaSvHImB0?t=262)). The numbers assume his samples; the order is what carries
   over: kick = clap > ghost hits > crash > rides.
3. Auto Pan on the rides ([1:47](https://youtu.be/3-0JCDyiPaw?t=107), all shown): amount 43.7 %, rate 1/2
   synced, phase 180°, shape 15.9 %, offset 83.1°, sine wave, Invert on.
4. With one ride per beat and one pan cycle every two beats, consecutive rides land on opposite sides
   (inferred from the settings).

## In Rohil's setup
- Faders: `rick-rubin logic set Kick volume=0`, `rick-rubin logic set Clap volume=0`,
  `rick-rubin logic set Crash volume=-12`, `rick-rubin logic set Rides volume=-16`, then
  `rick-rubin logic inspect` to read them back. A fader number means nothing across different samples: use
  it as a first pass, then measure.
- Auto-pan: Logic's Tremolo with its phase at 180° is an auto-panner. `rick-rubin logic insert Rides
  Tremolo`, read the names with `rick-rubin logic params Rides Tremolo`, set the rate to 1/2 note and the
  depth to about 45 %. Simpler and equivalent for one-shots: pan alternate ride hits left and right by hand.
- Ozone Imager 2 on the rides is the alternative if movement is not wanted.

## How to check it
`rick-rubin hits <dir> --tracks Kick Clap Crash Rides --bars 1-4`: ride steps about 16 dB under the kick's.
`rick-rubin width <dir> --bars 1-4`: side % above 4 kHz inside the references' 4 to 29 % (`skill/mix.md`),
correlation never negative, nothing wide below 150 Hz.

## Why it works
Cymbals are dense and bright, so they sound loud at low level and mask the vocal and bass tops when they are
not. Putting the width in a layer that is 16 dB down gives the stereo meter something without moving the
centre of the mix.
