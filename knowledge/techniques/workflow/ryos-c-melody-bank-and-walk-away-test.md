---
title: Keep a bank of melodies, start a track from one, and judge it by whether it survives a break
topic: workflow
genres: [progressive house, any]
source: RYOS — Making Progressive House MAGIC | Studio Time with Ryos EP. 51 (https://youtu.be/srkGlUWW3pg?t=42)
status: untested
---
## What it is
Writing melodies and producing tracks are separate jobs for him. Melodies are made on their own, saved, and
often forgotten; a session starts by auditioning one on sounds that are already loaded. Doubt about a melody
is handled by stepping away, not by rewriting on the spot.

## When to use it
Blank-page sessions; and the moment mid-session when the idea suddenly seems weaker than an hour ago.

## How
1. Sometimes just write melodies and stop there. Save each one (said,
   [0:42](https://youtu.be/srkGlUWW3pg?t=42)). His folder shows them as numbered MIDI files with a nickname
   and the key in the name (shown, [1:15](https://youtu.be/srkGlUWW3pg?t=75)).
2. Open the session with sounds ready: a lead stack saved from the last project and a plain piano
   ([0:20](https://youtu.be/srkGlUWW3pg?t=20)).
3. Audition a banked melody on the piano, adjust the chords, and within two minutes play it on the big lead
   to hear whether it holds up there ([1:45](https://youtu.be/srkGlUWW3pg?t=105)).
4. Hold a checkpoint part-way through and say what bothers you. His two items: the melody, and kick against
   sub ([19:03](https://youtu.be/srkGlUWW3pg?t=1143)).
5. The walk-away test: after a short break the tune was stuck in his head, which he takes as proof the idea
   is good even though some notes need work; what to change usually becomes clear on coming back (said, 19:03).
6. Change the smallest thing that fixes it. He replaces only the opening notes
   ([20:37](https://youtu.be/srkGlUWW3pg?t=1237)).
7. Rest the ears by switching section: after a long stretch on the drop he goes back to the break
   ([21:23](https://youtu.be/srkGlUWW3pg?t=1283)).

## In Rohil's setup
A bank can be a `melodies/` folder inside a project: `rick-rubin midi <dir>` exports `song.mid` and one file
per track from a `song.py`; name the keeper with its key. Bring one into his open Logic project with
`rick-rubin logic add-midi melodies/idea-07-Amin.mid --bar 1 --name Piano`, and onto the lead with
`rick-rubin logic add-serum "<lead preset>" --name Lead`. The bank holds ideas the agent or Rohil wrote for
him; it is not a library of stock parts (CLAUDE.md). After his break, write down what he says:
`rick-rubin verdict`, and `rick-rubin remember` for the session note.

## How to check it
No measurement decides this. The record is the check: the checkpoint items are written down, the verdict
after the break exists, and the change made afterwards is small enough to name in one line.

## Why it works
A melody judged on the day it was written is judged by a tired ear. Separating the two jobs means each
session starts from an idea that has already survived being forgotten.
