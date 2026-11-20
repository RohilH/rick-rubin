---
title: Tension from one held minor chord
topic: harmony
genres: [tech house, bass house, any]
source: Alex Rome — 10 Chord Patterns for 10 Different Emotions (https://youtu.be/_yw85rAb6cw?t=169)
status: untested
---
## What it is
A "progression" of a single minor chord held for the whole phrase. He uses G minor and says any root works.

## When to use it
Builds, intros and drops where harmony should create suspense rather than tell a story. It is the normal state of a
tech house or bass house drop, where a moving bassline does the talking.

## How
1. One minor triad, held long (said; shown [3:08](https://youtu.be/_yw85rAb6cw?t=188): one sustained note being
   drawn on G in Ableton, then the chord).
2. Choose a sound that already has the mood: he reaches for a dark synth patch (said; Sylenth1 shown).
3. Put a bass under it and let the bass move while the chord stays (said: "drop a bass down").
4. To keep one chord alive (ours): change its voicing every eight bars, open a filter over 16, add and remove the
   fifth or the minor seventh, or chop it into a rhythm against the kick.

## In Rohil's setup
One chord means the interest has to be designed elsewhere. A slow LFO or envelope on `filter_1.cutoff_hz` in the
Serum patch gives the movement inside the sound (see the filter swell card); section `filter` automation in
`song.py` gives it over the arrangement. Kickstart 2 on the chord track makes it breathe with the kick: `rick-rubin
logic insert <track> "Kickstart 2" Mix=0.6`.

## How to check it
`rick-rubin reference compare <dir>` on a bounce: the "movement" and "near-identical blocks" lines should sit inside
the references' range even though the harmony never changes. If they do not, the chord is a loop, not tension.

## Why it works
Nothing resolves because nothing moves, so the ear keeps waiting. Any change in bass, brightness or rhythm is then
heard as an event (inferred).
