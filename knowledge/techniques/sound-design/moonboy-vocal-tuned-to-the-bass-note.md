---
title: Hard-tune the vocal, then force it onto the note the bass is playing
topic: sound-design
genres: [tech house]
source: MOONBOY — HOW TO TECH HOUSE | Full Tutorial (Odd Mob, Chris Lake, Mau P) (https://youtu.be/JqKaSvHImB0?t=817)
status: untested
---
## What it is
Three pitch treatments that turn a spoken or sung phrase into a tech house hook: snap it to the key with no
glide, "play" its pitch from a keyboard (he holds the bassline's note, so the voice becomes a monotone
locked to the bass), and shift its formants to make the voice deeper or smaller.

## When to use it
On a short vocal phrase that should work as a riff rather than as singing: rap or spoken acapellas, a
one-line hook over the groove bass.

## How
1. **Hard tune.** A pitch quantizer set to the track's root and scale, strength 100 %, smoothing 0 ms, fully
   wet (shown at [13:48](https://youtu.be/JqKaSvHImB0?t=828): Ableton Auto Shift, Quantizer page). That is
   the robotic stepped sound.
2. **MIDI tune.** Arm an empty MIDI track, switch the tuner's MIDI input on and point it at that track;
   whatever key is held is the pitch the vocal is forced to (said, [14:00](https://youtu.be/JqKaSvHImB0?t=840)).
   He holds the same note the bassline plays (shown as a caption at
   [14:18](https://youtu.be/JqKaSvHImB0?t=858); smoothing 11 ms, mono, there).
3. **Formant shift.** Down for a deeper, bigger voice, up for a smaller one: −6 % and +24 % are on screen
   (shown at 14:18 and [14:46](https://youtu.be/JqKaSvHImB0?t=886)); small moves, not chipmunk settings.
4. His sample is a wet acapella at 130 BPM in A minor (shown): tempo and key were matched before any of this.

## In Rohil's setup
- Read the vocal first: `rick-rubin transcribe <dir> samples/vocal.wav` and `rick-rubin notes <dir>
  samples/vocal.wav` (which syllable lands where, which pitches, key fit).
- Hard tune: Logic's Pitch Correction on the vocal (`rick-rubin logic insert Vocal "Pitch Correction"`, then
  `rick-rubin logic params Vocal "Pitch Correction"` for the names): fastest response, root and scale of the
  track.
- One-note tune: Pitch Correction takes no MIDI. Nearest: in its keyboard leave only the bass's note
  enabled, or in Flex Pitch select all notes, drag them to that pitch and flatten drift and vibrato. What is
  lost: playing the pitch live; a changing melody means editing notes in Flex Pitch.
- Formant: Logic's Vocal Transformer (`rick-rubin logic insert Vocal "Vocal Transformer"`, Formant knob), or
  Formant Shift per note in Flex Pitch.

## How to check it
Bounce the vocal and run `rick-rubin notes <dir> bounces/vocal_tuned.wav`: every note within a few cents of
a scale tone after step 1; one pitch only, equal to the bass's pitch class, after step 2. Then listen: a
bounce for Rohil, before and after.

## Why it works
A voice pinned to the bass note cannot clash with the bassline, and a pitch that moves in steps reads as a
synth riff, which is what a minimal track needs from its only melodic element.
