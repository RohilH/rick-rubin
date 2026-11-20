---
title: Chords: every part in one key, start from triads on the bassline, open the voicing
topic: harmony
genres: [progressive house, bass house, any]
source: RYOS — Giving Feedback On YOUR Tracks! (https://youtu.be/3I7jJyVczPQ?t=2080)
status: untested
---
## What it is
Ryos's fixes for chords that sound muddy, "funky" or not to his taste. None involves harder theory: stay in the
scale everywhere, keep the chord simple, and move its notes away from the bass.

## When to use it
A synth that sounds too warm or muddy over the bass; a remix where the lead fits and the chords do not; a
progression that is busy without being better. Six tracks had a note about notes.

## How
1. **One scale for every part.** Pick the key (a remix inherits the original's) and use only its notes in the
   lead, the chords and the bass. His example: A minor is the white keys. A lead in key over chords and bass
   that are not is what sounds wrong in a beginner's remix (said, [1:33:01](https://youtu.be/3I7jJyVczPQ?t=5581),
   [1:36:50](https://youtu.be/3I7jJyVczPQ?t=5810)).
2. **The bass follows the chord instrument's progression** (said, [1:42:40](https://youtu.be/3I7jJyVczPQ?t=6160)).
3. **Move the chord up.** If a chord sound is too warm over a heavy bass, transpose it up, or consider
   an open voicing before changing the patch (said, [34:40](https://youtu.be/3I7jJyVczPQ?t=2080)).
4. **Keep the third away from the bass.** A third close above the root or the bassline sounds muddy even in
   key; spread the notes so the bass has room (said, [35:50](https://youtu.be/3I7jJyVczPQ?t=2150)).
5. **Start simple.** If the bassline is good and the chords are not, rebuild from the bassline: basic triads
   first, then simple inversions, and add notes only if it is still boring (said,
   [2:25:45](https://youtu.be/3I7jJyVczPQ?t=8745)).
6. **Take a chord out.** Where a phrase has one chord too many, delete it and let the previous one ring (said,
   [24:05](https://youtu.be/3I7jJyVczPQ?t=1445)).
7. **Fit a sample to the key.** He finds the track's key, then pitches an atmosphere by semitones to match
   (three semitones down in his example) before using it (said, [2:28:50](https://youtu.be/3I7jJyVczPQ?t=8930)).

## In Rohil's setup
`rick-rubin logic inspect` gives the project's key. For any audio part or sample, `rick-rubin notes <dir>
<file>` prints its pitches with octave, cents and key fit, which is the check he does with a key-detection
plug-in. In a `song.py`, write the voicing out note by note and keep the lowest chord note well above the bass
note (inferred rule of thumb: thirds from about C3 upward). Chords in his own Logic regions are his to edit;
offer the revoiced version as a MIDI file with `rick-rubin logic add-midi`.

## How to check it
`rick-rubin notes` on bounces of lead, chords and bass: all in the same key, no out-of-scale pitches.
`rick-rubin spectrum <dir> chords.wav bass.wav`: after revoicing, less chord energy in the octave above the
bass fundamental. Read the chord track in `rick-rubin score` to confirm the interval above the bass.

## Why it works
Low intervals beat against each other and against the bass's own harmonics; the same notes an octave higher are
clear. A triad on a strong bassline already states the harmony, so extra notes must earn their place.
