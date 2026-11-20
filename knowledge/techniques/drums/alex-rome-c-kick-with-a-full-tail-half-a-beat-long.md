---
title: Judge a kick by its tail: full-bodied for about half a beat, and replace the sample if it is not
topic: drums
genres: [tech house, bass house, progressive house]
source: Alex Rome — This Producer's Bass Was Weak. Here's the Fix. (https://youtu.be/HLCi1uYq8r0?t=127)
status: untested
---
## What it is
A quick visual and listening test for why a kick vanishes in a mix even though its meter reads loud: its body fades
too early, so only the click is heard. His fix is a different sample, not processing.

## When to use it
When the kick is "tiny" or "weak" against the other parts, before reaching for EQ or compression, and before writing
the bass (the bass is sized to the kick).

## How
1. Solo the drums. A club track needs the kick to dominate; if it does not, look at the sample (said,
   [1:46](https://youtu.be/HLCi1uYq8r0?t=106)).
2. Zoom into the waveform. A weak kick is tall at the front and its body shrinks steadily to nothing (shown
   [2:18](https://youtu.be/HLCi1uYq8r0?t=138)). You hear the attack and not the tail (said).
3. Do not stack plug-ins to rebuild the tail. Swap in a kick known to work (said,
   [2:28](https://youtu.be/HLCi1uYq8r0?t=148)).
4. The replacement looks "round": close to full height for most of its length, about half a beat long (said; shown
   [2:48](https://youtu.be/HLCi1uYq8r0?t=168)). At 126 BPM half a beat is about 240 ms (our arithmetic).
5. Compare the two back to back at the same meter level: the round one is audible, the tapered one is not (said,
   [2:49](https://youtu.be/HLCi1uYq8r0?t=169)).
6. Same test in another video: a hip-hop kick against a house kick. The house sample is about twice as long with a
   sustained body (shown [9:18](https://youtu.be/Uazkku5yuM8?t=558)); until you are experienced, use drum samples made
   for your genre (said, [8:57](https://youtu.be/Uazkku5yuM8?t=537)).
7. He does not discuss the kick's pitch or key.

## In Rohil's setup
`rick-rubin audition <dir> samples/raw/kick_a.wav samples/raw/kick_b.wav ...` compares candidates by length, punch and
spectrum before listening; pass every candidate for the role together. In his Logic project the kick's region waveform
shows the same shapes. Ryos's card (`ryos-kick-that-fits-the-genre.md`) chooses the character by genre; this card is
the check on body and length. A long tail and a held bass need the sidechain
(`../mixing/alex-rome-c-kickstart-on-the-instrument-group-keyed-by-the-kick.md`).

## How to check it
`rick-rubin audition` on the old and new kick: the new one should be longer (toward 200 to 250 ms at house tempos)
with more sub and bass band energy late in the sample. In the mix: `rick-rubin reference compare` punch and low-end
rows move toward the references, and `rick-rubin hits` shows the on-beat steps clearly above the rest.

## Why it works
Perceived loudness follows energy over time, not the peak; a kick whose body lasts carries far more low energy at the
same peak level, and that body is what a club system reproduces (inferred).
