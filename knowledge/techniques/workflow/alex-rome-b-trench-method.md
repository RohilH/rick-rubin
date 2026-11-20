---
title: The trench method: vocal and chords first, then drums, melody and bass each checked, then arrange
topic: workflow
genres: [any, progressive house, tech house, bass house]
source: Alex Rome — A Simple System For Making Songs in 2026 (https://youtu.be/XlltkalLaU4?t=20)
status: untested
---
## What it is
Alex Rome's three-step order for a whole song, which he teaches to beginners. The "trench" is the vocal plus the
core chords: the foundation everything else is dug from. Step 2 adds the other fundamentals one at a time, each
tested against what exists. Step 3 arranges, and by then nothing can go badly wrong.

## When to use it
Starting a track from a vocal (or from a lead melody if there is none), and when a project has many parts but
does not hold together: go back and ask whether the trench was ever strong.

## How
1. **Build the trench** ([0:20](https://youtu.be/XlltkalLaU4?t=20)).
   - Vocal first (his: a Splice hook in A minor; said, [2:06](https://youtu.be/XlltkalLaU4?t=126)).
   - Chords by harmonising the vocal, not by writing chord after chord: plain saw through a low-pass (shown
     [1:50](https://youtu.be/XlltkalLaU4?t=110): Serum 2 init, MG Low 24), bass notes first, then thirds, a pedal,
     then the octave (see `harmony/alex-rome-b-harmonise-a-vocal-bass-notes-first.md`).
   - Spend the time here: he tries sets of harmony notes for hours, saves every one, keeps the best (said,
     [2:46](https://youtu.be/XlltkalLaU4?t=166)).
   - Keep the chord sound simple, since it glues the harmony; one small character move is enough
     (`sound-design/alex-rome-b-pitch-envelope-on-chord-notes.md`).
2. **Expand the trench**: drums, melody, bass, all right before any arranging (said,
   [5:58](https://youtu.be/XlltkalLaU4?t=358)).
   - Drums: a kit of samples in one sampler, programmed as MIDI ([6:20](https://youtu.be/XlltkalLaU4?t=380)).
   - Melody: a plucky preset, a dotted rhythm, the chords' contour, a resolving second half
     ([7:45](https://youtu.be/XlltkalLaU4?t=465)).
   - Bass: the chords' bottom notes on a low saw filtered to the sub ([9:57](https://youtu.be/XlltkalLaU4?t=597)).
   - After every addition, play it against the others; with the chords muted, bass, drums and melody must still
     work (said, [7:03](https://youtu.be/XlltkalLaU4?t=423), [11:07](https://youtu.be/XlltkalLaU4?t=667)).
3. **Arrange the trench** ([11:48](https://youtu.be/XlltkalLaU4?t=708)). He has three blocks: a vocal verse, a
   vocal hook, a drop idea. The hook cannot cut straight to the drop, so a crossover goes between (see
   `arrangement/alex-rome-b-crossover-section-with-partial-parts.md`), and filters move on every part (said,
   [14:58](https://youtu.be/XlltkalLaU4?t=898)).

What plays where (shown [14:50](https://youtu.be/XlltkalLaU4?t=890); no bar numbers in the frame, so lengths are
inferred from proportions and from the ruler at [9:00](https://youtu.be/XlltkalLaU4?t=540), where the vocal ends
at bar 17):

| Section (inferred length) | Playing |
|---|---|
| verse (8 bars) | vocal, chords |
| hook (8) | vocal, chords, bass enters |
| crossover and build (8) | lead melody hinted, bass, high drums only; chords and vocal out |
| drop (8) | lead, chords back, bass, full drums with kick |

## In Rohil's setup
`rick-rubin split` for an acapella, `rick-rubin notes` and `transcribe` before writing around it. He works in
Ableton with Serum 2; nothing here depends on Ableton. Step 1: write three or four sets of bass notes (variables
in `song.py`, or takes in Logic), bounce each with the vocal, record which he keeps with `rick-rubin verdict`
(PREFERENCES §3). Step 2's checks are bounces of a few tracks: `rick-rubin logic bounce b.wav --bars 1-8 --tracks
Vocal Chords Bass` (`workflow/alex-rome-b-two-checks-before-moving-on.md`).

## How to check it
Trench: `rick-rubin notes` on the vocal against the chord tones (long vocal notes are chord tones or the pedal).
Expansion: `notes` on bass and lead bounces shows them in key. Arrangement: `rick-rubin reference compare <dir>`.
Whether the trench is "strong" is for his ears only.

## Why it works
Every later part is derived from the vocal and its chords (the bass from the bottom notes, the melody from the
contour), so a weak foundation is multiplied and a strong one makes the later steps close to mechanical.
