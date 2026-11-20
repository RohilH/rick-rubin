---
title: A fast melody from one bar-long cell that climbs a third each bar, with the long note on the chord's third
topic: melody
genres: [progressive house]
source: RYOS — Making Progressive House MAGIC | Studio Time with Ryos EP. 51 (https://youtu.be/srkGlUWW3pg?t=64)
status: untested
---
## What it is
The melody he pulls from his bank is four bars of one rhythm. Bars 1 to 3 repeat the same small figure, each
time a third higher; bar 4 keeps the rhythm and breaks the shape. It differs from the two-cell melody in
`ryos-pg-two-rhythm-cells-melody.md`: here the device is a sequence.

## When to use it
A lead that should feel busy and still be hummable after one hearing; a 4-bar loop for a drop at 126 to 130 BPM.

## How
1. Rhythm cell, the same in every bar: one note of six sixteenths, then five eighth notes (shown,
   [1:15](https://youtu.be/srkGlUWW3pg?t=75)). Six onsets per bar.
2. Pitch figure: the long note, down a scale step, back, down, back, then one step up. That last step leads
   into the next bar's long note (shown; Logic octaves): F4 E4 F4 E4 F4 G4, then A4 G4 A4 G4 A4 B4, then
   C5 B4 C5 B4 C5 D5.
3. So the long notes F, A, C rise in thirds, one per bar (inferred from the notes shown).
4. Bar 4 breaks the pattern: the long note falls (B4) and the eighths become wider leaps low down, E4 G4 E4 G4
   A4 (shown). Same rhythm, new contour: the ear hears the phrase end.
5. Each long note is the third of that bar's chord: F over D minor, A over F, C over A minor, B over G. In
   bars 2 to 4 the chord track holds only root and fifth, so the melody supplies the third (shown; the reading
   of it as a method is ours).
6. Under a line this busy he makes the chords slower (said, [1:25](https://youtu.be/srkGlUWW3pg?t=85)). Later he
   replaces the opening notes and likes it more (said, [20:37](https://youtu.be/srkGlUWW3pg?t=1237); not readable).

## In Rohil's setup
These are his notes, quoted to show the mechanism; a melody for Rohil is written fresh in `song.py`
(PREFERENCES §2). What transfers: one rhythm cell per bar, a figure small enough to sing, the figure moved up
by a chord tone each bar, a changed last bar, long notes on thirds. Write two or three candidates as variables
and compare them (§3). In his own Logic project, `rick-rubin logic add-midi melody.mid --bar 17 --name Lead`
brings a candidate in on a new track.

## How to check it
`rick-rubin score <dir> --tracks Lead --bars 1-4`: bars 1 to 3 have identical onset positions and identical
interval patterns; bar 4 keeps the onsets. Each bar's longest note is a chord tone of that bar. Then his own
test: is it still in your head after a break ([19:03](https://youtu.be/srkGlUWW3pg?t=1143))? That one is for
Rohil's ears (`rick-rubin verdict`).

## Why it works
A repeated rhythm lets the listener predict the line, so speed does not cost clarity. The rising sequence adds
tension without new material, and landing each bar on the third states the harmony even over bare fifths.
