---
title: Write one chord progression first, then hand its bottom note, top note and full chord to different parts
topic: harmony
genres: [progressive house, bass house, any]
source: MOONBOY — HOW TO MELODIC HOUSE (Knock2, Kx5, John Summit) (https://youtu.be/woNtFzXYB5Y?t=105)
status: untested
---
## What it is

He starts a melodic track with a chord progression on a piano and calls it the building block of the song:
the bottom note of each chord becomes the note of every pad bass, sub or reese; the top note becomes the
lead; the whole chord becomes the supersaw, choir or arp. In this video the same eight bars feed a trance
pluck, a mega saw, a bass layer, and later a bass house drop.

## When to use it

At the very start of a progressive or melodic house idea, and whenever a new layer is needed later: take it
from the progression instead of inventing new notes.

## How

1. Choose the feeling first; his is nostalgic old-school trance (said,
   [2:05](https://youtu.be/woNtFzXYB5Y?t=125)). Tempo 126 BPM (said).
2. His eight bars, in G minor (shown at [2:15](https://youtu.be/woNtFzXYB5Y?t=135) and
   [5:50](https://youtu.be/woNtFzXYB5Y?t=350)): G minor for six beats, D minor for two; E flat major for two
   bars; F for one bar; B flat major for two beats, D minor for two; E flat major for two bars. In numerals:
   i, v, VI, VII, III, v, VI.
3. Every chord is three notes spread wide: root, the fifth above it, and the third an octave higher
   (G2 D3 A#3; D2 A2 F3; D#2 A#2 G3; A#2 F3 D4; D3 A3 F4). The F chord has no third at all (F2 C3 C4)
   (shown).
4. The chord lengths are uneven (6 + 2 beats, 2 + 2 beats): the short chords act as pick-ups into the long
   ones (inferred from the lengths).
5. Roles (said, [2:20](https://youtu.be/woNtFzXYB5Y?t=140)): bottom notes for pad, bass and sub; top notes
   for the saw lead and the melody; all three for chords, choirs and arps.
6. Then convert, one layer at a time: copy the clip to a new instrument and keep only the notes that layer
   needs (shown for the pluck at [3:27](https://youtu.be/woNtFzXYB5Y?t=207) and the bass at
   [7:15](https://youtu.be/woNtFzXYB5Y?t=435)).

Use the method and the voicing shape; the progression itself is his, write one for the track.

## In Rohil's setup

In a `song.py`, hold the progression as one variable (chord name, length, the three voiced notes) and derive
each track from it: `roots`, `tops`, full chords. That keeps every layer in agreement when a chord changes.
In Logic: one MIDI region on a piano track, duplicated to each instrument track and thinned. Other voicing
cards: `harmony/ryos-open-voicings-simple-triads-in-key`, `harmony/alex-rome-ten-progressions-overview`.

## How to check it

`rick-rubin score <dir> --bars 1-8`: on every chord the bass track's pitch class equals the chord root and
the lead's long notes equal the chord's top note. `rick-rubin check`: nothing out of key. `rick-rubin
spectrum <dir> --tracks Bass Chords`: only the bass below about 120 Hz.

## Why it works

Root, fifth and tenth leave an octave of air in the middle, so each note can be given to a different sound
without the layers crowding each other, and because every part comes from the same three notes nothing can
clash.
