---
title: Before adding a part, tidy what is there: fix the kick, then put one melody in front of the others
topic: mixing
genres: [any, tech house, progressive house]
source: Alex Rome — This Producer's Bass Was Weak. Here's the Fix. (https://youtu.be/HLCi1uYq8r0?t=106)
status: untested
---
## What it is
His first step on a student's track that "needs bass" is not bass. He cleans the project so the new part can be
judged: a kick that holds its place, and a clear ranking among several melodies that were all at the same level.

## When to use it
Before writing any major new part into an existing project (bass, lead, vocal), and whenever a section has three or
four melodic lines and none of them reads as the main one.

## How
1. Listen once and name what is missing and what is loose. His notes: no bass; kick weak; "a very loose mix" (said,
   [1:02](https://youtu.be/HLCi1uYq8r0?t=62), [1:46](https://youtu.be/HLCi1uYq8r0?t=106)).
2. Fix the kick first, since the bass will be set against it
   (`../drums/alex-rome-c-kick-with-a-full-tail-half-a-beat-long.md`).
3. Go through the melodic parts one by one. Chords well voiced: leave them (said,
   [3:31](https://youtu.be/HLCi1uYq8r0?t=211)).
4. Count the melodies. He finds four playing together (said, [3:42](https://youtu.be/HLCi1uYq8r0?t=222)).
5. Choose the one you like most and keep it in front; balance the others under it so they do not clash (said,
   [4:18](https://youtu.be/HLCi1uYq8r0?t=258)). This is done with levels, off camera; no figures are shown.
6. Listen to the kick in the new balance: it should sound ready for a bass under it (said, 4:18).
7. Check whether the melodic parts leave the low end free. His did, so no EQ was needed (said and shown,
   [6:48](https://youtu.be/HLCi1uYq8r0?t=408)); when they do not, low-cut them
   (`alex-rome-c-find-the-low-cut-against-the-bass.md`).
8. Starting offsets (ours, inferred): front melody at its current level, second melody 3 to 4 dB under it, the rest 6
   dB or more under it, then adjust by ear.

## In Rohil's setup
`rick-rubin logic inspect` lists every strip with fader and inserts: the melodic tracks and their levels are the
starting picture. One change at a time, read back: `rick-rubin logic set "Lead city" volume=-9`. Bounce the section
before and after (`rick-rubin logic bounce bounces/before.wav --bars 43-50`). This is also the "one driver" rule of
`../melody/alex-rome-c-five-melody-roles-overview.md`, applied with faders instead of by deleting parts.

## How to check it
`rick-rubin compare <dir> before.wav after.wav`: crest should rise slightly and mid-band share fall a little as
competing lines drop. `rick-rubin spectrum` on the melodic group alone: little below about 150 Hz. Then the ear test
for Rohil: after eight bars, which melody does he remember? It should be the one chosen.

## Why it works
A new part is judged against the mix it joins. If that mix is ambiguous, every bass sounds wrong, and the bass gets
blamed for a balance problem (inferred from his order of work).
