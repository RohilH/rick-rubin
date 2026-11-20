---
title: Pulsing melody: one note in a repeating rhythm on a saw pluck, with the chords moving under it
topic: melody
genres: [progressive house, tech house, any]
source: Alex Rome — 5 Melody Styles Every Hit Song Uses (https://youtu.be/cjyEdyEWXbQ?t=380)
status: untested
---
## What it is
A "melody" that never changes pitch. All its interest is rhythm and tone, and the emotion comes from what the chords
do to that fixed note. He places it in Afro house and melodic house and calls the effect meditative.

## When to use it
Breaks and long builds in melodic and progressive house; a hypnotic layer over a tech house groove; any time a moving
lead would be too much. Also the fastest way to get a melodic idea down.

## How
1. Pick any one note and give it a rhythm (said, [6:38](https://youtu.be/cjyEdyEWXbQ?t=398)). He describes a
   dotted-eighth rhythm that resets every two bars; the frame shows onsets on sixteenths 0, 3, 6, 8, 11 and 14 of the
   bar, notes two sixteenths long (shown [6:58](https://youtu.be/cjyEdyEWXbQ?t=418)).
2. Any rhythm works if it locks with the drums and the other parts (said, [7:24](https://youtu.be/cjyEdyEWXbQ?t=444)).
3. Sound: a saw pluck is easiest (said, [7:00](https://youtu.be/cjyEdyEWXbQ?t=420)); he uses Serum 2's factory preset
   "PL - Alive".
4. Now write chords under it. Because the note does not move, many progressions fit (said,
   [7:45](https://youtu.be/cjyEdyEWXbQ?t=465)). His first set: B minor, F# minor, E major, D major (on-screen caption,
   [8:25](https://youtu.be/cjyEdyEWXbQ?t=505)); he then swaps in other sets and keeps the pulse.
5. Why those fit (inferred from the frame): the pulse looks like F#, which is the fifth of B minor, the root of F#
   minor, the ninth of E and the third of D. A note that belongs to most of the chords, and is a mild colour on the
   rest, can stay put.
6. Choosing the note (ours, inferred): the tonic or the fifth of the key are the safest, since they belong to the most
   chords in the key.

## In Rohil's setup
`rick-rubin serum search "PL - Alive"` finds the preset (Factory/Pluck; its notes say to use the mod wheel). The
from-scratch version is `../sound-design/alex-rome-filter-envelope-pluck.md`. In `song.py` write the pulse as its own
track and keep two or three chord progressions as alternatives beneath it (`rick-rubin ab`). Related: MOONBOY's
three-sixteenth cell (`moonboy-trance-melody-in-three-sixteenth-cells.md`), which adds an answering second note.

## How to check it
`rick-rubin score <dir> --tracks Pulse`: one pitch; check by hand that it is a chord tone or a ninth of every chord
under it. `rick-rubin hits` on a bounce of drums plus pulse: the pulse's onsets should fall on steps the percussion
also accents, not between them. On an audition, Rohil judges the progression alternatives, since the pulse is the same
in each.

## Why it works
A held pitch is reheard against each new chord: it is a root in one bar and a third or a ninth in the next, so the
harmony seems to change the melody's meaning while the melody stays still (inferred).
