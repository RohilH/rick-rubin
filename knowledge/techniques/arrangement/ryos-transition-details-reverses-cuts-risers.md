---
title: Transition details: a reverse into the hit, a hard cut under the vocal, a riser that fades in
topic: arrangement
genres: [progressive house, bass house, tech house, any]
source: RYOS — Giving Feedback On YOUR Tracks! (https://youtu.be/3I7jJyVczPQ?t=2220)
status: untested
---
## What it is
Small edits at section boundaries that Ryos says make him think the producer "went the extra mile". Each one
is a few minutes of work on audio or automation. Six tracks were asked for them.

## When to use it
After the arrangement is fixed, on every boundary where one section just stops and the next starts.

## How
1. **Reverse into the hit.** Duplicate the first piano chord (or first note) of a section, reverse it, and place
   it so it swells into that downbeat, where the bar before is empty (said,
   [23:10](https://youtu.be/3I7jJyVczPQ?t=1390)). Keep an obvious reverse to one bar, with no silent bar before
   it (said, [17:20](https://youtu.be/3I7jJyVczPQ?t=1040)).
2. **Hard cut under a vocal phrase.** When a vocal shot lands in the drop, automate the synth's volume to
   nothing for that moment, so no tail bleeds under the vocal; then let a reverb swell or reverse lead into the
   next chord (said, [37:00](https://youtu.be/3I7jJyVczPQ?t=2220)).
3. **One more riser in the build:** a simple tonal one (he likes detuned saws), mixed low, to signal tension
   once the snare roll has started (said, [1:24:34](https://youtu.be/3I7jJyVczPQ?t=5074)).
4. **Fade risers in.** A riser that enters at full level too early is distracting, a pure sine riser most of all
   (one sharp peak in the spectrum). Use a crisp, detuned one in the background and bring it up gradually (said,
   [2:04:20](https://youtu.be/3I7jJyVczPQ?t=7460)).
5. **Size the effects to the genre.** Mainstage and big room: large impacts, downlifters, sweeps, laser risers.
   Melodic progressive house: subdued (said, [54:50](https://youtu.be/3I7jJyVczPQ?t=3290)).
6. **Sometimes remove them.** For a solo piano entry he deletes the impact and downlifter and puts a pause or
   fill before it, so the piano alone is the event (said, [1:19:45](https://youtu.be/3I7jJyVczPQ?t=4785)).
7. **Reuse the track's own sounds for fills:** a slice of the break's reese, a chopped vocal, a short kick or
   bass roll (said, [3:19:31](https://youtu.be/3I7jJyVczPQ?t=11971)). Turn a good fill up.

## In Rohil's setup
In his open Logic project the bridge cannot cut, move or reverse regions or write automation (`skill/logic.md`,
"Limits today"): say which bar and which region, and he does it. By hand: bounce the chord in place, tick
Reverse in the region inspector, and drag it to end on the downbeat; for the hard cut, draw volume automation on
the synth track. A reversed file made outside Logic can be placed with `rick-rubin logic add-audio FILE --bar N`,
on a bar line only. In a `song.py` these are parts and section automation the agent writes.

## How to check it
There is no number for "finesse". Partial checks on a bounce of the two bars around the boundary: level rises
into the downbeat, and during the vocal shot the synth's stem is silent. The rest is Rohil's verdict on a before
and after bounce.

## Why it works
A swell points the ear at the next downbeat, and a moment of silence makes what follows sound larger; both add
contrast without adding parts.
