---
title: Two checks before the next step: does the new part fit the others, and is the transition a satisfying change
topic: workflow
genres: [any]
source: Alex Rome — An Insanely Simple Arrangement System (escape the loop trap) (https://youtu.be/ZkRds6iTfhQ?t=547)
status: untested
---
## What it is
The two stop-and-listen habits that run through his systems. One is vertical: a new instrument is tested against
the parts already there before anything else is added. The other is horizontal: each section change is played
across before the next section is written.

## When to use it
Always, but especially for Rohil's stated problem, tracks that do not sound complete: parts stacked without the
first check, or sections joined without the second, are the usual cause in these videos.

## How
1. After adding an instrument, play it with the others, and in pairs (new part and chords, new part and drums).
   Ask: do they sound like the same song, and do they fit dynamically? (said,
   [7:03](https://youtu.be/XlltkalLaU4?t=423)).
2. Mute the chords and listen to bass, drums and melody alone; they must stand up without the pad covering them
   (said, [11:07](https://youtu.be/XlltkalLaU4?t=667)).
3. If something does not fit, fix or replace it now. Nothing added on top of parts that do not work together adds
   value, however impatient you are to get ideas down (said, [9:11](https://youtu.be/XlltkalLaU4?t=551)).
4. Judge the rough idea with no processing on it (said, [8:49](https://youtu.be/bx8X7oiYhCg?t=529)).
5. After each section boundary, a "transition check": play from before the join to after it. The only test is
   whether the change is satisfying. If not, go back to work on it before writing further (said,
   [5:35](https://youtu.be/ZkRds6iTfhQ?t=335), [9:07](https://youtu.be/ZkRds6iTfhQ?t=547)).
6. His reason: a loop or a drop is a section, not a song. Anyone can write a melody and chords; the skill is
   moving one piece of music into the next so it stays one song (said,
   [9:27](https://youtu.be/ZkRds6iTfhQ?t=567), [13:36](https://youtu.be/XlltkalLaU4?t=816)).

## In Rohil's setup
The agent cannot hear, so each check becomes a bounce for Rohil plus a measurement. Fit:
`rick-rubin logic bounce pair.wav --bars 1-8 --tracks Lead Chords`; `rick-rubin notes` on the new part for key
fit, `rick-rubin hits` for timing against the drums, `rick-rubin spectrum` on the new part and the part nearest
it in pitch to see whether they pile up in one band. Transition: bounce four bars either side of the join
(`--bars 13-20`). What he says goes in `rick-rubin verdict`, and a rejected part is replaced before the next
one is written (PREFERENCES §3 and §5).

## How to check it
There is a bounce and a verdict for every added part and every join, not only for the finished track. A join
passes when `rick-rubin eval <dir> --bars` either side shows a real difference (a band that appears or
disappears, a level step) and Rohil calls it satisfying.

## Why it works
A clash found when there are three parts costs one replacement; found at thirty parts it is buried under
everything built on it. And joins are where a listener decides whether to keep listening.
