---
title: Make a pad out of a vocal: reverb fully wet with the decay maxed, then bounce it to audio
topic: sound-design
genres: [progressive house, bass house, any]
source: MOONBOY — 13 Insane Ways to Make Any Vocal Sound MAGICAL (https://youtu.be/7wcJShg8tn4?t=165)
status: untested
---
## What it is

A pad made from the track's own vocal: one short sample through any reverb with decay and wetness all the
way up, recorded to a new audio file. The file is then an ordinary sound to cut, filter, reverse or leave
quietly behind the track. `sound-design/moonboy-vocal-space-rack-and-pad-layer` does a live version of this
in parallel with the vocal; here the pad becomes audio, which is cheaper and easier to edit.

## When to use it

When a section sounds empty behind the drums and vocal, and a synth pad would add harmony the track does not
want. In a remix it is a way to fill the background with the original song's voice, already in key.

## How

1. Pick any reverb and a vocal sample; a single word is enough (said,
   [2:50](https://youtu.be/7wcJShg8tn4?t=170); a one-beat clip on screen at
   [3:15](https://youtu.be/7wcJShg8tn4?t=195)).
2. Turn the reverb's decay and its wet amount all the way up (said). Ableton's Reverb is on screen with a
   decay of tens of seconds and the mix near 90 %; the small text is not fully readable (shown at 3:15).
3. Record or export the result: freeze the track or bounce it, depending on the DAW (said).
4. Use the file two ways (said, [3:30](https://youtu.be/7wcJShg8tn4?t=210)): process it further (his
   "hover" volume wobble, see `sound-design/moonboy-b-rhythm-gate-with-off-grid-swing`), or put it low in the
   background for a lush feel.
5. For the longer "choir" version he also cuts the reverb's low end and adds a delay before recording
   (said and shown at [6:30](https://youtu.be/7wcJShg8tn4?t=390): decay 12.9 s, size 100, wet 52 %, the input
   filter centred at 1.66 kHz).

## In Rohil's setup

- Put the word on its own track: `rick-rubin logic add-audio samples/vox_word.wav --bar 1 --name "Vox pad src"`,
  then `rick-rubin logic insert "Vox pad src" ValhallaSupermassive Mix=1.0` (raise its feedback and choose a
  long mode by hand, or read the names with `rick-rubin logic params "Vox pad src" ValhallaSupermassive`), or
  ChromaVerb with its decay at maximum and dry at 0.
- Record it: `rick-rubin logic bounce bounces/vox_pad.wav --bars 1-8 --tracks "Vox pad src"` (leave bars for
  the tail), then `rick-rubin logic add-audio bounces/vox_pad.wav --bar 17 --name "Vox pad"`.
- On the pad track: Channel EQ low cut near 200 Hz, `rick-rubin logic set "Vox pad" volume=-18` as a first
  level (ours), and `rick-rubin logic insert "Vox pad" "Kickstart 2" Mix=0.5` so it breathes with the kick.

## How to check it

`rick-rubin notes <dir> bounces/vox_pad.wav`: pitch classes inside the track's key (if not, tune the word
before the reverb). `rick-rubin audition`: no clear onsets after the first. In the mix, `rick-rubin
spectrum --mix` before and after: the pad should fill 300 Hz to 3 kHz in the gaps without raising the peaks.

## Why it works

A reverb with a very long decay averages a sound into its sustained pitches and vowel colour. Starting from
the track's vocal, that average is automatically in key and in character.
