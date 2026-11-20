---
title: Four chords in one open shape, with the second and fourth pushed an eighth early
topic: harmony
genres: [progressive house]
source: RYOS — Making Beautiful Progressive House | Studio Time with Ryos EP. 50 (https://youtu.be/WnZ7GN1tpek?t=362)
status: untested
---
## What it is
A four-bar progression where every chord uses the same four-note open voicing (root, fifth, octave, then the
third above that), one chord is left without its third, and two of the four changes arrive half a beat before
the bar line.

## When to use it
The harmonic bed of an emotional progressive house break and drop, written before anything else.

## How
1. Tempo 128 BPM (shown, [3:26](https://youtu.be/WnZ7GN1tpek?t=206)). Key D major / B minor; the progression is
   G, B, D, A, which is IV, vi, I, V (shown; he names the bass roots at [5:10](https://youtu.be/WnZ7GN1tpek?t=310)).
2. Voice each chord root, fifth, octave, tenth. Shown at [6:02](https://youtu.be/WnZ7GN1tpek?t=362), in Logic's
   note names (FL shows them two octaves higher): G1 D2 G2 B2; B1 F#2 B2 E3; D2 A2 D3 F#3; A1 E2 A2 C#3.
3. The B chord has E on top where a B minor would have D: a sus4, no third (shown). It keeps the bar open and
   lets the melody supply the colour (inferred).
4. Timing: chords 1 and 3 start on the bar line; chords 2 and 4 start one eighth note before bars 2 and 4, so
   chords 1 and 3 last 3.5 beats and chords 2 and 4 last 4.5 (shown, 6:02).
5. The lead stack, the pad and the dance piano all reuse these same four voicings; only the octave and the
   rhythm change (shown, [10:37](https://youtu.be/WnZ7GN1tpek?t=637), [27:04](https://youtu.be/WnZ7GN1tpek?t=1624)).
6. The break bass plays one root per bar under them (said, [4:58](https://youtu.be/WnZ7GN1tpek?t=298)).

## In Rohil's setup
In a `song.py` the notation is the same as Logic's (C3 = 60): write the four voicings as bracketed chords and
start chords 2 and 4 at `4.3` of the bar before (beat 4, third 16th). These are his chords for his track: use
the shape and the push on a progression written for the song at hand, and compare it with an unpushed version
(PREFERENCES §3). In an open Logic project, `rick-rubin logic add-midi chords.mid --bar 1` brings a written
part in on a new track.

## How to check it
`rick-rubin score <dir>` should show chord starts at 1.1, then 4.3 of bar 1, 1.1 of bar 3, 4.3 of bar 3. On a
bounce, `rick-rubin notes` on the chord stem should list only D major scale notes. The push is for the ear: bounce
the pushed and the straight version for Rohil.

## Why it works
Root-fifth-octave at the bottom is stable and clear on a big system; the third alone on top is the note the ear
follows, so the top voices (B, E, F#, C#) make a second melody. The early changes add forward motion without
any extra notes.
