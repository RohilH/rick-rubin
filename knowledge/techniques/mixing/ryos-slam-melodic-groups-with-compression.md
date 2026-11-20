---
title: Compress pianos and melodic groups hard so they hold their place over the bass
topic: mixing
genres: [progressive house, any]
source: RYOS — Giving Feedback On YOUR Tracks! (https://youtu.be/3I7jJyVczPQ?t=1173)
status: untested
---
## What it is
A soft piano, a lead group or a break's arp and vocal played with natural dynamics disappear in a dance mix.
Ryos evens them out with heavy compression on the group, then adds warmth and brightness. That short chain is,
he says, what most of his chains amount to.

## When to use it
A break where the piano is "drowned out" by the bass; a lead that sounds underpowered; a break that needs "more
power and to be cleaner". Five tracks got this note.

## How
1. Keep the soft sound; fix its dynamics. On the piano (or the group), compress until loud and quiet notes sit
   in "a more even package", so the bass can sit under it and the piano on top (said,
   [20:30](https://youtu.be/3I7jJyVczPQ?t=1230)). No ratio or threshold is given.
2. For leads and synth groups use "EDM style" compression, not a classic levelling compressor: he names
   CamelCrusher, OTT, Soundgoodizer and Sausage Fattener, and says not a CLA-76 (said,
   [2:48:30](https://youtu.be/3I7jJyVczPQ?t=10110)).
3. Then the rest of the chain, in his words simple: make sure there is enough warmth, clean up excess mud, add
   one brightening tool (EQ or exciter) (said, [1:21:01](https://youtu.be/3I7jJyVczPQ?t=4861)).
4. A harsh dance piano (the Korg M1 kind): tame the stray resonances first with EQ or a resonance suppressor
   (he names Soothe), then compress the piano group (said, [1:20:31](https://youtu.be/3I7jJyVczPQ?t=4831)).
5. One part that sticks out past the limiter (a growl on the downbeat): compress that part instead of turning it
   down, so it keeps its weight on the one (said, [3:06:30](https://youtu.be/3I7jJyVczPQ?t=11190)).
6. Do not confuse this with a crushed master: the same stream tells a beginner to turn a template limiter off.

## In Rohil's setup
OTT is on this Mac and is one of the tools he names: `rick-rubin logic insert Lead OTT` (read its controls with
`rick-rubin logic devices "OTT"`; start with its depth low, since full OTT is very bright). For pianos, Logic's
Compressor: `rick-rubin logic insert Piano Compressor Threshold=-24 Ratio=4` as a starting point (inferred, not
his numbers), then lower the threshold until quiet notes stop vanishing. RESO stands in for Soothe; what is
lost is Soothe's continuous, per-moment suppression. CamelCrusher is not installed; OTT plus Logic's
Compressor covers it.

## How to check it
Bounce the part alone before and after. Crest (peak minus loudness) should fall by several dB, and in a bounce
of the full break `rick-rubin spectrum <dir> piano.wav bass.wav` should show the piano no longer under the bass
in its own range. Rohil's ear decides whether it still sounds like a soft piano.

## Why it works
In a dense mix only the loud moments of a dynamic part are audible; raising the quiet ones makes the whole part
audible at a lower peak level, which reads as power.
