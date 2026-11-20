---
title: Turn each chord into a trance pluck: root on a 3+3+2 rhythm, top note one 16th behind it
topic: melody
genres: [progressive house, bass house]
source: MOONBOY — HOW TO MELODIC HOUSE (Knock2, Kx5, John Summit) (https://youtu.be/woNtFzXYB5Y?t=207)
status: untested
---
## What it is

A recipe for the rolling pluck line of a melodic breakdown that needs no melody writing: keep only the root
and the top note of each chord, give the root a dotted rhythm, and paste the same rhythm onto the top note
shifted by one step. A cousin of `melody/moonboy-trance-melody-in-three-sixteenth-cells`; here the cell is
3+3+2 and the notes come straight from the chords.

## When to use it

After the chord progression exists (`harmony/moonboy-b-one-progression-feeds-every-part`), for the first
eight bars of a break or intro, before the big chords enter.

## How

1. Copy the chord clip to a pluck patch and delete the middle note of every chord (said,
   [3:47](https://youtu.be/woNtFzXYB5Y?t=227)).
2. Root: 8th-long notes starting on 16th steps 1, 4 and 7 of every half bar, so 3 + 3 + 2 sixteenths, twice
   per bar (shown at [3:58](https://youtu.be/woNtFzXYB5Y?t=238); he calls it a dotted rhythm).
3. Copy that rhythm to the top note and move it "one space over" (said). In the first pass on screen the two
   voices still sound together, an octave apart (G2 with G3).
4. His worked version, per half bar of eight 16ths (shown at [5:03](https://youtu.be/woNtFzXYB5Y?t=303)):
   the root an octave below the chord's on steps 1, 4 and 7 (plus a pick-up 16th now and then); the top
   note an octave up on steps 2 and 5; the top note at its own octave once, on step 4; the chord's own root
   on step 7. Only root and top, each in two octaves, never more than two notes at once.
5. Paste the pattern through the whole progression, changing only the pitches per chord (said,
   [4:09](https://youtu.be/woNtFzXYB5Y?t=249)). The top voice can be improvised on.
6. Automate the pluck's filter cutoff to rise over the eight bars, with a curved line rather than a straight
   one (said and shown at [4:29](https://youtu.be/woNtFzXYB5Y?t=269); start and end values not readable).
7. Other rhythms are fine: the dotted one is a starting point (said).

## In Rohil's setup

Sound: `sound-design/moonboy-pluck-lead-with-filter-envelope`. In `song.py` write the cell once as step
positions and map it over the progression's roots and tops; keep the step numbers as the technique and the
pitches as the song. The cutoff rise is a section automation there; in Logic draw the Serum cutoff lane by
hand (no session command for automation).

## How to check it

`rick-rubin score <dir> --bars 1-8 --tracks Pluck`: root onsets on steps 1, 4, 7, 9, 12, 15 of each bar; the
top voice one step later. A bounce of bars 1 to 8: `rick-rubin eval` should show the pluck's brightness
higher in bars 7 to 8 than in bars 1 to 2.

## Why it works

3+3+2 puts two of three accents off the beat while still landing on every half bar, so the line pushes
forward over a four-on-the-floor kick. Offsetting the top note by a 16th turns two notes into an arpeggio.
