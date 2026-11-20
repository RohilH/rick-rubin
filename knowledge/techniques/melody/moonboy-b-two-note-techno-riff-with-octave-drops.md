---
title: A dark techno riff from two notes: one pitch, its octave below, and a few short stabs at the bar's end
topic: melody
genres: [tech house, bass house]
source: MOONBOY — HOW TO TECH HOUSE (John Summit, Dom Dolla, Chris Lake,) (https://youtu.be/_4qJSUFao50?t=243)
status: untested
---
## What it is

His "vibe" synth line, which he says is inspired by "Satisfaction" and old-school techno: almost everything
is one note and the same note an octave lower, and the interest is the rhythm. He says two notes are enough
to make an album, and that octave changes alone add a lot.

## When to use it

For the hook of a tech house intro or break when there is no vocal yet, or as the answer to a vocal phrase.
It suits a remix: a riff this simple never fights a rap vocal's own rhythm.

## How

1. Pick the note. His is D, with the piano roll's scale set to G minor (shown at
   [4:10](https://youtu.be/_4qJSUFao50?t=250)); D is also his bass root, so riff and bass agree.
2. Bar 1 (shown, same frame): D2 for the whole first beat; D1, an octave down, on beat 2; beats 3 and 4 are
   very short stabs stepping down F2, D#2, D2.
3. Bar 2: the same D2 then D1 opening, then nothing until two short notes (D2, D#2) right at the end of the
   bar. Bars 3 and 4 repeat bars 1 and 2 with the stabs slightly moved (shown; the exact lengths of the
   shortest notes are not readable).
4. So each bar is: long note, octave drop, then either a run of stabs or silence. The silence in bar 2 is
   part of the riff.
5. The extra pitches are neighbours only: a semitone and a minor third above the main note (D#, F) (shown).
6. Octave changes are the main variation tool (said, [4:20](https://youtu.be/_4qJSUFao50?t=260)).
7. Layout: the riff alone opens the track for eight bars, the next eight are the riser, then the drop; he
   sections everything in eights (said, [4:55](https://youtu.be/_4qJSUFao50?t=295)).

The pitches and stab positions are his example; the rule is one note, its octave, rests, neighbours.

## In Rohil's setup

Sound: `sound-design/moonboy-b-compressed-saw-techno-lead`. Write two or three rhythm variants in `song.py`
and compare (`rick-rubin ab`). Against a vocal, read `rick-rubin transcribe` first and put the stabs where
the vocal rests.

## How to check it

`rick-rubin score <dir> --bars 1-4 --tracks Lead`: at most four pitch classes, the main note and its octave
taking most of the time; bar 2 emptier than bar 1. `rick-rubin check`: no out-of-key notes.

## Why it works

With pitch almost fixed, the ear follows note length and register instead, which is what a dance floor
reads anyway; the octave drop on beat 2 gives the riff a low "answer" without a second instrument.
