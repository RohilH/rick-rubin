---
title: Load the drum sounds into one sampler kit and program the beat as MIDI, not as audio hits on the timeline
topic: drums
genres: [any, tech house, bass house, progressive house]
source: Alex Rome — A Simple System For Making Songs in 2026 (https://youtu.be/XlltkalLaU4?t=380)
status: untested
---
## What it is
His current way of building a drum loop in any DAW: collect a batch of one-shots, put them on the pads of one
sampler instrument, and write the beat in a single MIDI region. In his older videos (and in two of the four
digested here) each hit is an audio file on its own track.

## When to use it
Starting the drums for a new track; when a beat made of audio clips has become slow to change.

## How
1. Pick a set of drum sounds, for him a kit and extra one-shots from Splice, and build one drum rack from them
   (said, [6:20](https://youtu.be/XlltkalLaU4?t=380)). Shown at [6:30](https://youtu.be/XlltkalLaU4?t=390): about
   sixteen pads, among them three kicks, two claps, two snares, closed and open hats, bongos and percussion.
2. Program the pattern in the MIDI editor (said, [6:20](https://youtu.be/XlltkalLaU4?t=380)). He does the same in
   Logic (said).
3. What he says changes: he now writes extra low drum hits he never bothered to place as audio (said,
   [6:43](https://youtu.be/XlltkalLaU4?t=403)), and he layers sounds on the same hit (said).
4. Shown at [7:05](https://youtu.be/XlltkalLaU4?t=425), as roles only: a continuous 16th hat line, an open hat
   on the offbeats, a clap on the backbeat, two different kick samples sharing a syncopated kick pattern (this
   track is not four on the floor), and a few bongo hits. The clip's groove is set to a 16th swing (shown,
   6:30).
5. Before moving on, test the loop against the chords: same song, same dynamics? (said,
   [7:03](https://youtu.be/XlltkalLaU4?t=423)).

## In Rohil's setup
Ableton's Drum Rack is Logic's Drum Machine Designer: drag the Splice one-shots onto pads, one software
instrument track, one region. Swing for the whole kit is then one setting (the region's Quantize with a swing
value) instead of nudging clips. A pad can still get its own channel strip for processing. In a `song.py` the
equivalent is one `sample=` track per sound with the hits written out; that path renders audio, so the notes are
not editable in Logic afterwards (`skill/logic.md`). Choose the sounds by comparison first (`rick-rubin
audition`, PREFERENCES §3). Nothing is lost by not using Ableton here.

## How to check it
`rick-rubin hits <dir> drums.wav` on a bounce: hits where they were written, swung 16ths late by a constant
amount. `rick-rubin spectrum` with and without the extra low hits: energy under about 150 Hz between the main
kicks appears, without masking the bass (bounce drums and bass together and look for the bass notes still
standing out). The groove itself is for his ears.

## Why it works
One region for the whole kit makes a variation a copy and an edit, so more variations get tried; velocity, swing
and layering become properties of notes instead of chores per clip (inferred from what he says changed for him).
