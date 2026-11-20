---
title: The "pro sound" audit: lead sound, chords under the melody, bass, drums, in that order
topic: workflow
genres: [progressive house, tech house, bass house, any]
source: Alex Rome — How To Get That 'Pro Sound' (as a beginner producer) (https://youtu.be/Uazkku5yuM8?t=46)
status: untested
---
## What it is
The order in which he diagnoses a beginner's track that has a good melody and "lacks that pro sound". Four questions,
each with the usual failure and the usual fix. None of them is a mixing move: his point is that the professional sound
is mostly decided by sound, voicing, note and sample choices.

## When to use it
When Rohil says a track does not sound complete or professional and cannot say why. Run it before any mixing, and
before concluding the idea is weak.

## How
1. **Lead: is the sound right for the notes?** Failure: a "powerless" held supersaw on a sparse melody. Fix: a pluck,
   delay and reverb to fill the gaps, a layer or two for character (said, [0:46](https://youtu.be/Uazkku5yuM8?t=46);
   card `../sound-design/alex-rome-c-pluck-lead-with-delay-to-fill-the-gaps.md`).
2. **Chords: do they lift the melody?** Play melody and chords together (said,
   [4:01](https://youtu.be/Uazkku5yuM8?t=241)). Failures: all notes low and bunched; plain triads; a static sound.
   Fixes: third up an octave, a held note through the changes (`../harmony/alex-rome-ten-progressions-overview.md`),
   and an envelope that decays (`../sound-design/alex-rome-c-chords-that-decay-like-a-piano.md`).
3. **Bass: can it be heard, does it follow the chords, does it support the melody?** (said,
   [5:54](https://youtu.be/Uazkku5yuM8?t=354)). Fixes: bottom note of each chord for melodic music, or a line on the
   key's tonic; the 40 to 80 Hz octave (`../bass/alex-rome-c-bass-octave-by-the-analyzer-40-80hz.md`); a sound that
   suits the genre (`../bass/alex-rome-c-eighth-note-arp-on-a-pluck-bass.md`); passing notes in the melody's gaps
   (`../bass/alex-rome-c-bass-passing-notes-in-the-melody-gaps.md`).
4. **Drums: are the samples from the right genre, and is the main pattern there?** Failure: a short hip-hop kick in a
   house track; no hat between the kicks. Fixes: a genre kick with a full tail
   (`../drums/alex-rome-c-kick-with-a-full-tail-half-a-beat-long.md`), the offbeat hat (said,
   [8:45](https://youtu.be/Uazkku5yuM8?t=525)).
5. Keep what works: he keeps the student's melody, hat loop and original supersaw (as a layer).
6. A/B the result against the original version ([10:07](https://youtu.be/Uazkku5yuM8?t=607)).

## In Rohil's setup
On an open project: `rick-rubin logic inspect` for the track list, then answer the four questions in order and tell
Rohil which one fails first, naming the card. Change one thing, bounce (`rick-rubin logic bounce`), keep the before.
For a `song.py` track, run the audit on the score (`rick-rubin score`) and on `eval` before a mix pass
(`../mixing/alex-rome-c-four-pass-mix-eq-ott-sidechain-reference.md`). Ryos's finished-track checklist
(`ryos-finished-track-checklist.md`) covers arrangement and detail after this.

## How to check it
`rick-rubin compare <dir> before.wav after.wav` after each fix, and `rick-rubin reference compare` at the end:
movement, low-end share and punch should each move toward the references as questions 1 to 4 are fixed. The audit is
passed by ear: Rohil hears before and after, and his words go in `rick-rubin verdict`.

## Why it works
Each question depends on the one before: chords are judged against the lead, bass against the chords, drums against
the bass. Fixing them in that order avoids redoing work (inferred; he says the chords govern the bass).
