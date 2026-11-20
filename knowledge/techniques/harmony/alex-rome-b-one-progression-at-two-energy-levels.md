---
title: Write one progression twice: held two-note pads for low energy, a rhythmic pluck with passing notes for high energy
topic: harmony
genres: [progressive house, tech house, any]
source: Alex Rome — The Simplest Strategy for Building House Songs (it's like cheating) (https://youtu.be/kSXHTJJ7D34?t=21)
status: untested
---
## What it is
The first step of his house-song strategy: the same chord notes exist in a relaxed form and an energetic form.
He names the two levers that turn one into the other: sound choice and rhythm. Nothing about the harmony changes.

## When to use it
A progression works in the breakdown but the drop needs more drive, or the reverse. It is also the cheapest way
to get two sections that plainly belong to one track.

## How
Low energy:
1. A relaxed, deep sound: one saw through a low-pass, his "deep electro pad" (said,
   [0:30](https://youtu.be/kSXHTJJ7D34?t=30); shown [0:45](https://youtu.be/kSXHTJJ7D34?t=45): Serum, MG Low 24).
2. Hold one note in the middle of the keyboard across the loop, find bass notes that sound good under it, then
   move the top note of each chord to a third above its bass note, major or minor (said,
   [0:55](https://youtu.be/kSXHTJJ7D34?t=55) to [2:13](https://youtu.be/kSXHTJJ7D34?t=133)). Five chords in his
   loop, the first three two bars each (shown [2:20](https://youtu.be/kSXHTJJ7D34?t=140)).
3. Stop there: two notes per chord. Strictly these are intervals, not chords, and that is why they sound mellow
   (said, [2:36](https://youtu.be/kSXHTJJ7D34?t=156)).

High energy, same notes:
4. Sound: turn the pad into a pluck by dragging ENV 2 onto the cutoff and pulling its sustain down (said,
   [3:17](https://youtu.be/kSXHTJJ7D34?t=197); shown [3:25](https://youtu.be/kSXHTJJ7D34?t=205) and
   [3:45](https://youtu.be/kSXHTJJ7D34?t=225): amount 60 to 68, decay 1.00 s, sustain 0). Reverb on, then RC-20
   to rough it up and widen it; not too bright (said, [3:39](https://youtu.be/kSXHTJJ7D34?t=219)).
5. Rhythm: break the held notes into a dotted or a straight eighth pattern. He takes the rhythm of a track he
   likes as the model (said, [3:39](https://youtu.be/kSXHTJJ7D34?t=219)). Shown at
   [4:15](https://youtu.be/kSXHTJJ7D34?t=255): both notes of each chord re-struck in short repeated notes for the
   whole chord.
6. On a dotted-eighth rhythm, add passing notes between the chord tones (said,
   [4:02](https://youtu.be/kSXHTJJ7D34?t=242)).
7. Each form then gets its own 16 bars (see `arrangement/alex-rome-b-two-energy-sections-house-song.md`).

## In Rohil's setup
Pad: `sound-design/alex-rome-filtered-saw-pad.md`. Pluck: `sound-design/alex-rome-filter-envelope-pluck.md`, which
has the Serum command (`--mod env_2:filter_1.cutoff_hz:<amount>`). RC-20 he does not own: Logic's Ensemble or
Chorus for width with a little ChromaGlow for dirt, or STEREOVAULT after the synth; what is lost is RC-20's tape
wobble and noise in one box. The rhythm is written for the song; borrowing another track's rhythm as he does is a
reference, not a part to paste (`CLAUDE.md`). In a `song.py`: two tracks, the same pitches, compared on a bounce.

## How to check it
Bounce both forms. `rick-rubin hits`: the pluck has several onsets per chord, the pad one. `rick-rubin spectrum`:
the pluck is brighter at each onset and dies away; the pad is steady and dark. `rick-rubin notes` on both: the
same pitch classes. Whether the energy step is big enough is his verdict, heard back to back.

## Why it works
Energy in a chord part comes mostly from how often and how sharply it is struck and how bright it is, not from
which notes it holds; so the notes can stay and carry the identity of the track across sections.
