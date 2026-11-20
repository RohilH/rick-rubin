---
title: A "power chord" bass: a sine sub and a saw lead on different chord notes, crushed through one distortion
topic: sound-design
genres: [bass house]
source: MOONBOY — HOW TO MELODIC HOUSE (Knock2, Kx5, John Summit) (https://youtu.be/woNtFzXYB5Y?t=855)
status: untested
---
## What it is

The bass of his second, heavier drop. Two very plain Serum patches (a sine two octaves down, a saw up an
octave) play different notes of the same chords, and both run through one shared effect chain that starts
with distortion, so they stop being two sounds. The note idea is already in
`harmony/moonboy-sub-a-third-below-the-lead`; this card is the sound and where the notes come from.

## When to use it

For a bass house drop that follows a melodic break and should keep its harmony: the drop reuses the break's
chords instead of dropping to one note.

## How

1. Sub: a sine, octave −2. Lead: a saw, octave up (said, [14:36](https://youtu.be/woNtFzXYB5Y?t=876)).
2. Group the two tracks and put the effects on the group, not on either synth (said).
3. Chain on the group (said; shown at [15:45](https://youtu.be/woNtFzXYB5Y?t=945)): distortion first (Tube,
   its filter off, drive raised) so the layers are "like one"; hyper (4 voices) and dimension after it for
   width; a compressor in multiband mode, gain 9.9 dB; then delay (wet low, filtered, short time) and reverb
   last "so they don't get crushed".
4. Rhythm inside each patch: an LFO on the oscillator level, level turned down, trigger mode on, drawn as a
   one-shot. Fast decay on the lead, slow decay on the sub (said,
   [15:59](https://youtu.be/woNtFzXYB5Y?t=959)); the lead blips while the sub rings under it.
5. Notes: the sub takes the roots of the song's chords (G, D, D#, F) and the lead takes their top notes
   (A#, F, G; the fourth is lost in the captions) in the same rhythm (said,
   [17:01](https://youtu.be/woNtFzXYB5Y?t=1021); two lanes under a "Bass House Drop" marker shown at
   [17:15](https://youtu.be/woNtFzXYB5Y?t=1035), pitches too small to read). So the lead sits a third plus
   octaves over the sub; on the F chord, whose top is C, it would be a fifth (inferred).
6. Then the notes get a drop rhythm and the lead a second oscillator (said,
   [17:22](https://youtu.be/woNtFzXYB5Y?t=1042)); the pattern is not readable.

## In Rohil's setup

```
rick-rubin serum set init osc_a.on=off sub.on=on sub.shape=Sine sub.octave=-2 sub.level_db=0 global.mono=on \
  env_1.decay_ms=900 env_1.sustain_db=-12 --save pc-sub --project <dir>
rick-rubin serum set init osc_a.octave=1 global.mono=on env_1.decay_ms=180 env_1.sustain_db=-24 \
  env_1.release_ms=60 --save pc-lead --project <dir>
```

Here the amp envelope does what his level LFO does; all four times and levels are ours (parsed 2026-11-20,
not heard: the sub measured 100 % sub band, the lead `plucky` with no low end). Both tracks into a summing
stack; on the stack Logic's Distortion II or Overdrive, then STEREOVAULT (width with the lows kept mono),
then `rick-rubin logic insert "PC Bass" OTT Depth=40`; delay and reverb as sends after the stack.

## How to check it

`rick-rubin spectrum <dir> --tracks "PC Sub" "PC Lead"` before the stack: no overlap. On a bounce of the
stack: harmonics between the two layers filled in, crest lower. `rick-rubin width`: nothing wide below 150 Hz.
`rick-rubin score`: same onsets on both tracks, sub on chord roots.

## Why it works

Distorting two notes together creates sum and difference tones between them, so the pair is heard as one
gritty chord, and that only happens if the distortion comes after the two are mixed.
