---
title: Write the bassline on the offbeats first, then vary it four ways
topic: bass
genres: [tech house]
source: MOONBOY — HOW TO TECH HOUSE | Full Tutorial (Odd Mob, Chris Lake, Mau P) (https://youtu.be/JqKaSvHImB0?t=717)
status: untested
---
## What it is
A method for a tech house bassline: one note between every pair of kicks, then four small edits (double a
note, move a note by a step, jump one an octave, displace one) until the line has its own shape.

## When to use it
For the groove bass, once the drums loop and the bass sound exists. It keeps bass and kick out of each
other's way by construction, which matters most while there is no sidechain yet.

## How
1. Put one note on every offbeat 8th (the and of each beat), each an 8th long, all on the root. He calls it
   the Euro-dance pattern and starts on D#0 (said; shown at [12:15](https://youtu.be/JqKaSvHImB0?t=735),
   MIDI note 27).
2. **Double** some notes: split an 8th into two 16ths (said; shown at
   [12:48](https://youtu.be/JqKaSvHImB0?t=768) on the and of beat 4 in bars 1 and 3).
3. **Move** notes up or down for a different groove (said). On screen most of the line sits on E0 and each
   2-bar phrase begins with two notes a semitone lower on D#0: a lean into the home note.
4. **Octave jump**: one 16th an octave up (E1) right after a doubled note (said and shown, bar 2 beat 2).
5. **One surprise** near the end of bar 2: a note moved up to G#0 (shown; he says "bring one note over
   here").
6. All velocities 100; the clip has a 16th swing groove on it (shown, "Swing 16ths"; amount not readable,
   not mentioned).
7. Other shapes he shows for comparison ([12:57](https://youtu.be/JqKaSvHImB0?t=777)): one note in straight
   8ths with 16th runs; two 16ths on the downbeat, a jump up, then a held note; a note every three 16ths
   rolling across the bar line while the pitch walks down a minor triad.

Use the method, not his notes: the root, the doubled spots and the surprise are choices for each track.

## In Rohil's setup
Ableton and Logic both call MIDI 60 "C3", so D#0 and E0 mean the same in Logic (39 and 41 Hz). In a
`song.py`, write two or three variants as variables and compare them (`rick-rubin ab`). Swing is a number
per track there (`groove={"swing": ...}`); in Logic it is the region's Swing in the Region inspector.

## How to check it
`rick-rubin hits <dir> --tracks Kick Bass --bars 1-4`: bass energy on steps 3, 7, 11, 15 (and the doubled
16ths), nothing on the kick's steps 1, 5, 9, 13. `rick-rubin eval <dir> --bars 1-8 --tracks Kick Bass`
should report no kick and bass collisions. In `reference compare`, "low-end pump" should already read as
offbeat-heavy before any sidechain is added.

## Why it works
The kick owns the beat and the bass owns the gap, so the low end alternates and the track bounces. The
edits are small enough to keep that alternation while giving the ear a phrase to follow over two bars.
