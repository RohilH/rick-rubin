---
title: A/B the mix against a released track at matched loudness, then by band
topic: mixing
genres: [any, tech house, bass house, progressive house]
source: Alex Rome — 10 Mixing Tips That Changed My Life (https://youtu.be/cU0tHoyJYjo?t=187)
status: untested
---
## What it is
A reference plug-in on the master that holds a released track and switches between it and the mix at equal loudness,
so differences in balance are heard instead of differences in level.

## When to use it
Once the arrangement is in place and before any master chain decisions. Again after every round of balance changes.

## How
1. Put the reference plug-in last on the Stereo Out (shown [3:20](https://youtu.be/cU0tHoyJYjo?t=200): REFERENCE 2
   by Mastering The Mix).
2. Load a released song with similar dynamics and density to yours (said) and pick its loudest section (shown: a
   loop region set on the reference waveform).
3. Turn on level matching (said; shown [4:00](https://youtu.be/cU0tHoyJYjo?t=240): Level Match lit, his mix at −17.8
   LUFS, the reference at −14.8).
4. Flip between Original and Reference and name what differs. His findings: bass too loud against the lead, hats far
   too quiet (said, [4:10](https://youtu.be/cU0tHoyJYjo?t=250)).
5. Fix one thing in the mix, flip again (said: lead up first, then the hat).
6. Solo one frequency band of both to compare a single element, here the highs for the hats (said,
   [4:55](https://youtu.be/cU0tHoyJYjo?t=295)), then raise and brighten the hat until the top band matches.
7. The plug-in's tonal curve shows the same thing as a picture (shown [4:00](https://youtu.be/cU0tHoyJYjo?t=240):
   reference brighter above 2 kHz).

## In Rohil's setup
He owns REFERENCE; it goes on the Stereo Out by hand (loading the track into its window is manual). rick-rubin does
the same comparison in numbers: `rick-rubin reference add <released tracks>` once, then `rick-rubin reference
compare <dir> bounces/drop.wav` after `rick-rubin logic bounce bounces/drop.wav --bars 33-48`. For one element,
split the reference (`rick-rubin split <dir> refs/track.wav`) and compare its drum stem with his drum bounce:
`rick-rubin reference stems`.

## How to check it
`reference compare` prints each measure against the references' min, median and max. After the fixes the lines he
would have flagged (tonal balance in the top bands, low-end share) should move inside the range.

## Why it works
Louder sounds better to the ear, so an unmatched comparison only says the master is louder. Matched, the ear is free
to notice balance (said in substance).
