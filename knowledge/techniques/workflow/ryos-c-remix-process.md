---
title: Ryos's remix process as a checklist: stars first, one key and tempo, the vocal's structure, recycle, grow, control
topic: workflow
genres: [progressive house, tech house, bass house, any]
source: RYOS — KSHMR asked me to remix his song.. here's how I did it (https://youtu.be/mvZPg8zv_ig?t=237)
status: untested
---
## What it is
What his KSHMR "Wild Ride" remix shows about remixing, in working order. The video is one course chapter (the
break synths), so steps 1, 2 and 9 lean on what is visible in the project; where he is silent it says so.

## When to use it
Rohil's house remix of a hip-hop vocal, at the start and whenever it stalls. For choosing chords and proving
the drop first, pair it with `alex-rome-b-three-step-flip-remix-system.md`.

## How
1. **Separate the original from your own.** His mixer has buses named ACAPELLA, INSTRUMENTAL, MIX BUS and
   Refs (shown, [1:40](https://youtu.be/mvZPg8zv_ig?t=100)): the vocal, everything he made, and references.
2. **One tempo and one key for everything.** The project is at 130 BPM (shown). Every borrowed sample is
   moved "to the key of the track": +2, +2 and +1 semitones (said, [1:02](https://youtu.be/mvZPg8zv_ig?t=62),
   [3:36](https://youtu.be/mvZPg8zv_ig?t=216), [8:46](https://youtu.be/mvZPg8zv_ig?t=526)). How he chose the
   tempo and key is not in this chapter.
3. **Name the stars per section.** Break: the vocal plus one new sound of his, a break bass he calls the
   "main character". Everything else may only enhance them (said, [3:57](https://youtu.be/mvZPg8zv_ig?t=237)).
4. **Mark the sections on the timeline.** Intro, Break, Build, Drop, 2nd Break, Hook, Hands Up, Build, Drop
   (shown, [16:15](https://youtu.be/mvZPg8zv_ig?t=975); bars in `ryos-c-remix-bar-map-hook-and-hands-up.md`).
5. **Let the vocal decide when things enter.** Where the vocal repeats and its harmonies arrive, the first
   chords arrive too (said, [19:50](https://youtu.be/mvZPg8zv_ig?t=1190)).
6. **Mine the acapella for ear candy.** A stutter in the vocal is sliced out and made into an atmospheric
   throw: exciter, bright multiband distortion, OTT at depth 33 %, a dotted-eighth tape delay (mix about
   24 %, feedback 80 %), Supermassive (mix 32 %, low cut 140 Hz) (said,
   [4:38](https://youtu.be/mvZPg8zv_ig?t=278); shown 6:08 and 6:20). Used three times, not looped (shown 5:00).
7. **Recycle your own stems** before designing anything new: slides from an old release, a vocal bed from an
   unreleased song, pack samples ([3:36](https://youtu.be/mvZPg8zv_ig?t=216), 8:26).
8. **Grow each section**: something new about every eight bars, thin and spacious first, more frequency
   content later ([8:05](https://youtu.be/mvZPg8zv_ig?t=485); `ryos-c-break-entries-ordered-by-frequency.md`).
9. **Make the second half different**: its break leads to a stripped hook and a "hands up" section with
   sounds not heard before ([22:02](https://youtu.be/mvZPg8zv_ig?t=1322)).
10. **Keep control while adding**: utility plug-ins on every track, width checked on a correlation meter,
    supporting sounds cut down to their one band (the other `ryos-c-` cards from this video).
11. **Finish.** Mixing and mastering are in the paid course, not here (said, 0:21). Use
    `ryos-finished-track-checklist.md` and `ryos-b-two-projects-production-then-mix-from-stems.md`.

## In Rohil's setup
Step 1 and 2: `rick-rubin split <dir> refs/original.wav --stems vocals --bpm <tempo>` gives the acapella at
the project tempo through Logic; read it before writing (`rick-rubin transcribe`, `rick-rubin notes`,
PREFERENCES §6). Retune borrowed samples with `rick-rubin conform <dir> samples/x.wav --transpose 2`. Keys
within one Camelot step; he chooses any transposition of the vocal (§8). Step 6: cut the slice by hand in
Logic, then `rick-rubin logic add-audio slice.wav --bar 22 --name "Vocal candy"`, `rick-rubin logic insert
"Vocal candy" OTT`, Logic's Tape Delay at a dotted eighth, `"Valhalla Supermassive"`; Exciter or ANIMATE
stands in for the two brighteners. Two vocals never overlap: the candy goes in gaps of the lead vocal (§8).

## How to check it
`rick-rubin notes` on each borrowed sample: in key within about 10 cents. `rick-rubin transcribe` on the
acapella against the candy's bar positions: no overlap with sung words. `rick-rubin reference compare`:
texture changes per minute in range. A list of what is new in each eight-bar block, with no empty lines.

## Why it works
The vocal already fixes mood and phrase lengths, so decisions that answer to it are fast, and material cut
from the original keeps the remix recognisably the same song.
