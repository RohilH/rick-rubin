---
title: Use the drop's chord and bass progression in the break, or change it only before the hook
topic: harmony
genres: [progressive house, bass house, tech house, any]
source: RYOS — Pro Secrets for Creating EDM Breakdowns (https://youtu.be/l_XjHmumqQk?t=512)
status: untested
---
## What it is
A safe rule for making break and drop sound like the same song: they share one progression. Variety then comes
from sounds and arrangement, not from new chords.

## When to use it
When laying out a track's sections, and when a finished break and drop feel like two different tracks.

## How
1. Let the break play the same chords and bass notes the drop plays. His whole track is variations of one
   three-chord progression (G, D sharp, C) (said, [8:11](https://youtu.be/l_XjHmumqQk?t=491)).
2. The fault he hears in amateur tracks: wildly different chords in the break and in the drop, so nothing
   holds them together (said, [8:32](https://youtu.be/l_XjHmumqQk?t=512)).
3. Know the cost: it can get repetitive. It works in his track because the arrangement is fast and a dramatic
   change is always happening (said, [8:53](https://youtu.be/l_XjHmumqQk?t=533)).
4. In longer, more melodic arrangements such as progressive house, one progression for the whole track is
   still fine; he says many successful tracks do it (said, [9:05](https://youtu.be/l_XjHmumqQk?t=545)).
5. The alternative for a vocal song: a verse on one progression, a pre-chorus on a different one, then a new
   progression under the hook, and that hook progression is the one the drop plays (said,
   [9:13](https://youtu.be/l_XjHmumqQk?t=553)).
6. Either way the drop's harmony has been heard with the hook before the drop arrives (inferred).

## In Rohil's setup
In a `song.py`, write the progression once as a variable and write the break voicing and the drop bass from
it by hand, so a later change of chord reaches both. In his Logic project: bounce the break chords and the
drop bass (`rick-rubin logic bounce break_chords.wav --bars A-B --tracks Chords`, same for the bass) and read
both with `rick-rubin notes <dir> <file>`.

## How to check it
`rick-rubin notes`: the roots of the break chords and of the drop bass are the same notes in the same order.
Then guard against the cost: `rick-rubin reference compare <dir>` should still show texture changes per minute
inside the references' range; if not, the shared progression needs more change of sound around it.

## Why it works
Harmony is what a listener remembers as "the song"; keeping it fixed lets the sound and energy change a great
deal without the track falling apart.
