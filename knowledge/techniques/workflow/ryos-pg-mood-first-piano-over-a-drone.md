---
title: Set the mood first: write on a lightly processed piano over a drone, then build the drop before the build
topic: workflow
genres: [progressive house]
source: RYOS — Making Beautiful Progressive House | Studio Time with Ryos EP. 50 (https://youtu.be/WnZ7GN1tpek?t=62)
status: untested
---
## What it is
The order of work for a blank project: a pleasant piano and a background bed to write against, chords, a few
atmosphere sounds, the melody, and only then the drop sounds. The build is made last.

## When to use it
Starting a melodic track with no idea yet. It keeps the first half hour on writing, not on sound design.

## How
1. Pick a piano that sounds good at once and give it a small reverb and simple compression. Shown at
   [1:38](https://youtu.be/WnZ7GN1tpek?t=98): a plate with decay 0.55 s, predelay 10 ms, mix about 53 %, then a
   one-slider compressor at about -13.
2. Put a droning or atmospheric sample under it before writing; he says it helps create the mood (said,
   [1:45](https://youtu.be/WnZ7GN1tpek?t=105)). He reuses beds from his own earlier tracks.
3. Let the idea decide the key. He set out to write something happy, found an emotional idea, and moved the
   drone to B minor to follow it instead of forcing the plan (said, [2:26](https://youtu.be/WnZ7GN1tpek?t=146)).
4. Chords first, then one or two atmosphere sounds, then the melody (said, [4:38](https://youtu.be/WnZ7GN1tpek?t=278)).
5. Keep the piano idea as the intro and break as it is, and move on (said, [7:00](https://youtu.be/WnZ7GN1tpek?t=420)).
6. Order after that: supporting synths in the break, mark where the build starts, drop leads, drop support
   synths, bass stack, drop drums, extra energy layer, and the build last
   ([7:19](https://youtu.be/WnZ7GN1tpek?t=439) to [29:59](https://youtu.be/WnZ7GN1tpek?t=1799)).
7. Note ideas that arrive mid-task as a marker and finish the current job first; he writes "add dance piano" on
   the timeline while doing drums (said, [22:05](https://youtu.be/WnZ7GN1tpek?t=1325)).
8. Stop the demo when the idea is all there; detail work waits until the idea is chosen to be finished (said,
   [34:13](https://youtu.be/WnZ7GN1tpek?t=2053)).

## In Rohil's setup
In Logic: a piano from the Library with ChromaVerb (short plate) and Compressor after it, and a drone on an
audio track. Splice is the source for a drone or bed; read it before writing on it (`rick-rubin notes` for
its pitch and key fit, `rick-rubin width`), per PREFERENCES §6. If it is in the wrong key, `rick-rubin conform
<dir> drone.wav --bpm 128 --transpose N` moves it with Logic's tools. Supermassive can make a bed out of any
held chord. For a new song the same order works in `song.py`: chords and melody patterns first, drop section
before the build section.

## How to check it
There is no number for mood. Check the bed: `rick-rubin notes` should show it in the song's key, and
`rick-rubin width` should show the low band centred. Then play Rohil the piano and bed alone and record what
he says with `rick-rubin verdict`.

## Why it works
A sound that already feels good makes ideas come faster and tells you early what the track's emotion is.
Writing the drop before the build means the build has a known target to lead into.
