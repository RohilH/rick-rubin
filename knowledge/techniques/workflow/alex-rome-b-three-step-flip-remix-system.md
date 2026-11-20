---
title: Remix in three steps: your own chords under the vocal, a direction proved by a finished drop, then arrange
topic: workflow
genres: [any, progressive house, tech house, bass house]
source: Alex Rome — My Insanely Simple System for Remixing Any Song (The 3-STEP FLIP) (https://youtu.be/bx8X7oiYhCg?t=41)
status: untested
---
## What it is
Alex Rome's order of work for a remix, which he calls the "3-step flip": (1) new chords under the original vocal,
(2) a one-line direction, tested by building the whole drop, (3) arrangement, where most of the effort goes into
the transitions. Each step has a pass/fail question, so you know when to move on.

## When to use it
Rohil's house remix of a hip-hop vocal, and any edit that starts from an acapella. Use it when a remix stalls:
find which of the three questions has not been answered yet.

## How
0. Pick the song. He asked the artists before starting (said, [0:21](https://youtu.be/bx8X7oiYhCg?t=21)).
1. **Chords under the vocal, first.** They set the mood of everything after (said,
   [0:41](https://youtu.be/bx8X7oiYhCg?t=41)). Plain sound (one saw through MG Low 24, shown
   [1:15](https://youtu.be/bx8X7oiYhCg?t=75)); bottom notes first, then thirds, then a pedal (see
   `harmony/alex-rome-b-harmonise-a-vocal-bass-notes-first.md`). Pass when the chords move you and support the
   vocal (said, [2:24](https://youtu.be/bx8X7oiYhCg?t=144)).
2. **Style and direction, proved by a drop.** Say the idea in one line: genre or not, and what happens to the
   vocal (his: chop it into a stutter for more energy; said, [3:05](https://youtu.be/bx8X7oiYhCg?t=185)). Then
   build the complete drop: the hook treatment, the same chords on an airier sound, kick, hats, clap, a shaker
   loop, a bass from the chords' bottom notes ([3:25](https://youtu.be/bx8X7oiYhCg?t=205) to
   [8:49](https://youtu.be/bx8X7oiYhCg?t=529)). Pass when the unprocessed drop is worth a whole song; only a
   finished drop can tell you (said, [7:23](https://youtu.be/bx8X7oiYhCg?t=443)).
3. **Arrange.** Rough blocks first: an intro of vocal over the plain chords, relaxed enough to run 16 bars; a
   breakdown whose job is to phase the intro's lead out and the drop's lead in (said,
   [9:29](https://youtu.be/bx8X7oiYhCg?t=569)), 8 bars, 17 to 24; the drop from bar 25 (shown
   [9:35](https://youtu.be/bx8X7oiYhCg?t=575)). Then the joins, because the energy "lives in the transitions"
   (said, [9:50](https://youtu.be/bx8X7oiYhCg?t=590)): automation on every part
   (`arrangement/alex-rome-b-opposite-automation-handoff.md`), one drop element borrowed into the intro (the
   shaker; said, [11:38](https://youtu.be/bx8X7oiYhCg?t=698)), transition effects last (said,
   [12:43](https://youtu.be/bx8X7oiYhCg?t=763)).

What plays where in his finished project (shown, [13:32](https://youtu.be/bx8X7oiYhCg?t=812); 126 BPM, key
signature B major; small frame, some track names unreadable):

| Bars | Enters | Leaves |
|---|---|---|
| 1–8 | original vocal, plain chords, pad layers, shaker loop | |
| 9–16 | a clap (the halfway change) | |
| 17–24 | the new lead (inferred: the stutter part), a drone, a hat | plain chords, shaker |
| 25–40 | kick, more clap layers, open hat, shaker, sustained bass; a vocal again from 33 | original vocal, pads |
| 41–48 | chopped vocal pieces over the lead and bass | kick and most drums |

## In Rohil's setup
Step 1: `rick-rubin split <dir> refs/track.wav --stems vocals --bpm 126`, then `rick-rubin notes` and
`transcribe` on the acapella (PREFERENCES §6). A rapped verse has little pitch, so take the key from the sung hook
or the original's bass stem (inferred). Step 2: write the direction down (`rick-rubin remember <dir> --strategy
"..."`), build 8 bars of drop, bounce it (`rick-rubin logic bounce bounces/drop.wav --bars 25-32`) and get his
verdict before arranging. Step 3: `rick-rubin logic inspect` cannot see region positions or automation, so the
agent proposes the bar map and the moves, and Rohil places them.

## How to check it
Each step ends in a bounce and a `rick-rubin verdict`. After step 3, `rick-rubin reference compare <dir>`: texture
changes per minute inside the references' range, no eight-bar block identical to the one before.

## Why it works
The vocal is fixed, so the harmony is the first real choice, and the drop is the cheapest full test of the idea.
Arranging before the drop exists means arranging something that may be thrown away.
