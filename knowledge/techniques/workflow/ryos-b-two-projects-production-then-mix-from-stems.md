---
title: Work in two projects: write in one, bounce to stems, mix and master in a new one
topic: workflow
genres: [any]
source: RYOS — Pro Secrets for Creating EDM Breakdowns (https://youtu.be/l_XjHmumqQk?t=450)
status: untested
---
## What it is
Ryos produces in two stages. All the music is made in a production project. When that is done, everything is
bounced to audio stems and the stems go into a fresh project where the mixing and mastering happen.

## When to use it
Once the arrangement and sounds are decided. Not while parts are still being rewritten.

## How
1. Stage one, the production project: instruments, MIDI, sound design, creative effects and automation. He
   says outright that this project is not the final master (said, [7:30](https://youtu.be/l_XjHmumqQk?t=450)).
2. When the production is finished, bounce everything to audio or stems (said, same place).
3. Stage two: a new project holding only those stems, for mixing and mastering (said).
4. Keep earlier project versions. His vocal chop is only audio in the latest project because the instrument was
   deleted to free resources; he opens an older save to show how it was made (said,
   [1:44](https://youtu.be/l_XjHmumqQk?t=104); the track reads "Vocal Chop (consolidated)", shown
   [12:13](https://youtu.be/l_XjHmumqQk?t=733)).
5. Decisions he labels "sound design" (a filter that defines the tone, OTT that shapes the envelope) belong to
   stage one and are printed into the stem; "mixing" EQ can wait for stage two (said,
   [12:21](https://youtu.be/l_XjHmumqQk?t=741), [13:02](https://youtu.be/l_XjHmumqQk?t=782)).

## In Rohil's setup
- Stems from his open project, one group at a time: `rick-rubin logic bounce stems/drums.wav --tracks Kick
  Clap Hats`, `rick-rubin logic bounce stems/bass.wav --tracks Sub Bass`, and so on. `rick-rubin logic
  inspect` lists the strips to group. The bridge never saves or closes his project.
- The mix project is his to create in Logic; stems can be placed in an open project with
  `rick-rubin logic add-audio stems/drums.wav --bar 1 --name Drums`.
- Before bouncing, decide what the master chain does: if he writes into a clipper (see
  `mastering/ryos-produce-into-a-clipper-kick-at-zero.md`), bounce stems with it bypassed so they are not
  clipped twice (inferred; Ryos does not say).
- Related: `mixing/alex-rome-consolidate-layers-before-mixing.md` (same idea within one project) and
  `mixing/alex-rome-mix-on-a-different-day.md`.

## How to check it
Sum check: bounce the full production project, then bounce the stem project with all faders at zero and no
new plug-ins; `rick-rubin compare <dir> production.wav stems_sum.wav` should measure the same loudness, bands
and width. A difference means a bus effect or sidechain was lost in the stems.

## Why it works
Audio stems stop the endless rewriting, free the computer from heavy synths, and put the mix in front of you
as a few faders. The cost is that changing a note means going back to stage one.
