---
title: Put the sub a third below the bass lead instead of on the same note
topic: harmony
genres: [bass house]
source: MOONBOY — HOW TO BASS HOUSE (Knock2, Skrillex, Porter Robinson) (https://youtu.be/3-0JCDyiPaw?t=650)
status: untested
---
## What it is
In most heavy drops the sub doubles the lead bass an octave or two down. Here the sub and the lead play the
same rhythm on different notes of the scale, so together they imply chords. He describes it as almost a
power chord and as a way to keep a drop heavy while giving it feeling.

## When to use it
When a bass-led drop sounds strong but flat or cold, and the breakdown before it had harmony the drop then
abandons. It needs the sub and the mid bass on separate tracks.

## How
1. Write the lead bass riff first. His climbs by step: E2, then F#2, then G#2, in F# minor
   (shown at [11:03](https://youtu.be/3-0JCDyiPaw?t=663)).
2. Copy the rhythm to the sub track unchanged (shown: the two parts have identical note starts and lengths).
3. Move each sub note down to the scale tone a third below the lead's note, then down the octaves into sub
   range: C# under E, D under F#, E under G# (shown: C#1, D0, E0). So the lead is always the third of a
   chord whose root is in the sub: C# minor, D major, E major, all inside F# minor (inferred from the notes).
4. He calls the result "a sort of harmony" between low end and lead (said,
   [11:20](https://youtu.be/3-0JCDyiPaw?t=680)). The interval on screen is a third (a tenth or more with the
   octaves), not the fifth of a real power chord.
5. Level on screen: the sub track at −6 dB while he shows it (status bar at
   [11:12](https://youtu.be/3-0JCDyiPaw?t=672)).

## In Rohil's setup
Ableton and Logic name octaves the same way, so D0 and E0 here are the same keys in Logic (36.7 and
41.2 Hz); C#1 is 69 Hz, high for a sub, which is why his line jumps down after the first chord. In a
`song.py`, derive the sub from the lead with a scale-aware transpose and write both out; keep the sub
between about C0 and G1. Mid bass high-passed near 100 to 150 Hz so only the sub states the root.

## How to check it
`rick-rubin score <dir> --bars A-B --tracks Lead Sub`: same onsets, sub a third (plus octaves) under the lead
on every note, all notes in key. `rick-rubin spectrum <dir> --tracks Lead Sub`: the two do not overlap below
about 120 Hz. Then bounce the drop both ways (doubled and in thirds) for his ear: this is a taste decision.

## Why it works
The lowest note is heard as the root. Moving it under the lead by a third changes what chord the same lead
note belongs to, so the drop gets a chord progression without adding a single mid-range part.
