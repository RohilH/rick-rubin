---
title: An intro that previews the track filtered, and a structure that gets to the point
topic: arrangement
genres: [progressive house, any]
source: RYOS — Giving Feedback On YOUR Tracks! (https://youtu.be/3I7jJyVczPQ?t=1050)
status: untested
---
## What it is
Two linked habits. In the intro, tease the track's parts but hold back their full top and bottom. In the
structure as a whole, reach the vocal and the hook early, and imagine a DJ mixing the track in.

## When to use it
When laying out the arrangement, and when an intro "goes on a little long". Three tracks were told they took
too long to arrive.

## How
1. Preview elements in the intro, but filtered: no full high end or low end this early. A vocal ad-lib can be
   louder than you think if its top is filtered off (said, [18:02](https://youtu.be/3I7jJyVczPQ?t=1082)).
2. The break's bass in the intro: high-pass it at about 80 Hz, so the warmth is there and the sub is saved for
   later (said, [18:40](https://youtu.be/3I7jJyVczPQ?t=1120)).
3. If the intro still drags, add one thing or shorten it. A vocal that enters 30 seconds in is late; he
   re-cuts one track so the mood is set and the vocal arrives at about 9 to 10 seconds (said,
   [1:58:50](https://youtu.be/3I7jJyVczPQ?t=7130)).
4. Do not preview the hook late in a quiet section: where the build begins, open the pluck's filter and bring
   the big saws in for real (said, [3:04:30](https://youtu.be/3I7jJyVczPQ?t=11070)). His build for a vocal
   remix: 16 bars, vocal over the first 8, wind-up riser over the last 8 (said,
   [3:05:01](https://youtu.be/3I7jJyVczPQ?t=11101)).
5. Avoid a short burst of full energy followed straight away by a slow break; it reads as a rollercoaster. Tease
   the vocal through a telephone-style filter over the kick instead, then go to the breakdown (said,
   [3:02:00](https://youtu.be/3I7jJyVczPQ?t=10920)).
6. Always picture it live: where does a DJ mix in and out, and is the piano entry or the drop an event when it
   comes? (said, [1:20:00](https://youtu.be/3I7jJyVczPQ?t=4800), [3:01:45](https://youtu.be/3I7jJyVczPQ?t=10905)).
7. Keep the mood the intro promised: a floaty intro wants a sustained bass in the break, not a stop-start one
   (said, [21:30](https://youtu.be/3I7jJyVczPQ?t=1290)).

## In Rohil's setup
The 80 Hz high-pass and the vocal's low-pass are Logic Channel EQ or AutoFilter on the intro's copy of the part
(a separate track for the intro version is simplest, since rick-rubin cannot write automation in his project):
`rick-rubin logic insert "Bass intro" "Channel EQ"`, then set the low-cut band after reading its name with
`rick-rubin logic params`. In a `song.py`, section `filter` automation does this (`push --automation`). Rohil
DJs, so step 6 is his own test: would he mix this intro out of another record?

## How to check it
Bounce the intro alone: `rick-rubin spectrum <dir> intro.wav drop.wav` should show the intro with clearly less
energy below 80 Hz and above roughly 8 kHz than the drop. Time to the first vocal and to the first drop, read
from the arrangement, compared with two or three reference tracks in the genre.

## Why it works
Holding back the spectrum's extremes leaves the drop something to reveal, and a listener or a DJ who hears the
track's identity early has a reason to stay for it.
