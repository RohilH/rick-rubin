---
title: Bring the drums in over several sections: kick and one hat first, the layers later, and count the layers as one change
topic: drums
genres: [any, tech house, progressive house]
source: Alex Rome — An Insanely Simple Arrangement System (escape the loop trap) (https://youtu.be/ZkRds6iTfhQ?t=314)
status: untested
---
## What it is
In his arrangement demo the drum kit is never dropped in whole. It arrives in stages tied to the section changes,
and each stage is sized against what else enters at that moment.

## When to use it
Building up from a loop toward a full section; an intro or first verse where the full kit arrives too early and
leaves nothing for later.

## How
1. First entry, together with the bass: only a kick and one hat, plain four on the floor. Because the bass also
   arrives here, the section needs no more drums than that (said, [5:14](https://youtu.be/ZkRds6iTfhQ?t=314)).
2. Leave them unchanged through the next join if they have not "expired"; they have room to be layered later
   (said, [6:58](https://youtu.be/ZkRds6iTfhQ?t=418)).
3. Next section, three additions that together count as one change (said,
   [7:39](https://youtu.be/ZkRds6iTfhQ?t=459)):
   - a 16th-note hat line ([7:18](https://youtu.be/ZkRds6iTfhQ?t=438));
   - a backbeat sound on every other kick, and he picks a rimshot over a clap to keep the deep mood of the chords
     and vocal (said, [7:18](https://youtu.be/ZkRds6iTfhQ?t=438); the file he places is named as a clap one-shot
     in the frame at [7:20](https://youtu.be/ZkRds6iTfhQ?t=440), so judge the sound, not the label);
   - a top loop, which he likes for the "mushiness" that blends the separate hits into one kit (said,
     [7:39](https://youtu.be/ZkRds6iTfhQ?t=459)).
   Shown at [7:50](https://youtu.be/ZkRds6iTfhQ?t=470): all three start on the same bar line, under the kick and
   hat that have been running for eight bars.
4. A further percussion part starts two loops later (shown [11:40](https://youtu.be/ZkRds6iTfhQ?t=700); not
   mentioned).
5. The remix drop is built in a similar order in one go: kick, layered hat, clap, then a shaker loop that makes
   the kit sound "complete" (said, [6:19](https://youtu.be/bx8X7oiYhCg?t=379) to
   [7:03](https://youtu.be/bx8X7oiYhCg?t=423)).

## In Rohil's setup
Each stage is its own track (or its own section entry in `song.py`), so a stage can be muted or moved a section
earlier or later while comparing. The parts are written for the track; the card only says which role enters
when. Samples: shortlist with Splice and `rick-rubin audition`. A top loop carries low junk: low-cut it
(`mixing/alex-rome-low-cut-everything-but-kick-and-bass.md`) and check that its hits do not flam against the
programmed hat (`rick-rubin hits`). For tech house, where the kit carries the track, the stages can be shorter
(inferred). Related: `drums/moonboy-b-shakers-and-top-loop-enter-halfway.md`, `drums/ryos-pg-drop-drums-in-order.md`.

## How to check it
`rick-rubin eval <dir> --bars` (or `rick-rubin spectrum` on bounces) section by section: top-end activity steps
up at each stage and never falls back before the peak. `rick-rubin reference compare <dir>`: drum-entry timing
and top-end activity within the references' range.

## Why it works
Every drum layer held back is a change still available later, and a small kit under a new bass keeps the low end
readable at the moment the listener is taking the bass in.
