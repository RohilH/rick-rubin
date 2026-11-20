---
title: A complextro-style drop section: one-shots from five sources, one sound per grid slot
topic: arrangement
genres: [bass house]
source: MOONBOY — HOW TO BASS HOUSE (Knock2, Skrillex, Porter Robinson) (https://youtu.be/3-0JCDyiPaw?t=607)
status: untested
---
## What it is
The second half of his drop. Instead of one bass playing a riff, the riff is assembled from single hits of
different sounds (a bass stab, a vocal chop, synth stabs, an arp blip), each on its own lane, so the rhythm
and the melody come from the order in which the sounds take turns. He cites Daft Punk, Madeon and early
Skrillex.

## When to use it
As the B section answering a held or riffing bass in the A section, or as a fill in the last two bars of a
phrase. It suits bass house and anything aiming at "ear candy"; it is too busy for a minimal tech house drop.

## How
1. Collect one-shots: resample single notes of the track's own bass and synths, and cut single syllables from
   the vocal (said: creative chops with synths and vocals, [10:20](https://youtu.be/3-0JCDyiPaw?t=620)).
2. Five lanes, labelled on screen ([10:43](https://youtu.be/3-0JCDyiPaw?t=643)): 1 bass one-shot, 2 vocal
   chop, 3 synth one-shot, 4 arp one-shot, 5 another synth one-shot.
3. Placement shown: the bass stab and a vocal chop land together at the start of each cycle (four cycles
   across the phrase), then the next slots go to lane 3, lane 4 and lane 5 in turn; at the end of every
   second cycle the synth and arp lanes play longer, overlapping phrases as a turnaround. No slot is empty
   and no two lead sounds share a slot, apart from that turnaround. The grid length is not readable.
4. His three tips, on screen: every synth and vocal chop must be in key; compress everything together so it
   becomes one sound; sidechain adds the bounce.
5. Send all lanes to one group and treat the group as a single instrument (shown: a "Drop B" group).

## In Rohil's setup
- Make the one-shots from the project: `rick-rubin logic bounce bounces/bass_bar.wav --bars 33-34 --tracks
  Bass` and cut one note, or `rick-rubin serum render "<preset>" --note E2 --secs 0.5 --out
  samples/raw/bass_shot.wav` for single notes of the drop's patches; vocal syllables from the
  transcription (`rick-rubin transcribe` gives where each one starts).
- Check each chop's pitch before using it: `rick-rubin notes <dir> samples/chop.wav` (pitch with octave,
  cents, key fit); retune or drop what is off.
- In Logic: one audio track per lane inside a summing stack; on the stack a Compressor and
  `rick-rubin logic insert "Drop B" "Kickstart 2" Mix=0.6`.
- The order of sounds is written for the track; this card gives the rule, not the pattern.

## How to check it
`rick-rubin hits <dir> --tracks "Drop B" --bars A-B`: energy on every slot of the grid used, at a similar
level (the bus compression working). `reference compare`: texture changes per minute should rise sharply in
this section against the A section. And a bounce: this is judged by ear more than anything else here.

## Why it works
The ear follows the change of timbre from slot to slot as if it were a melody, so a simple rhythm sounds
intricate; one bus compressor and one sidechain make the collage move as a single part.
