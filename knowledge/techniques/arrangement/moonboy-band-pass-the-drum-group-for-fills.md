---
title: Switch a band-pass filter on over the whole drum group for one beat as a fill
topic: arrangement
genres: [tech house, bass house]
source: MOONBOY — HOW TO TECH HOUSE | Full Tutorial (Odd Mob, Chris Lake, Mau P) (https://youtu.be/JqKaSvHImB0?t=320)
status: untested
---
## What it is
A band-pass filter sits on the drum group, bypassed. Automating it on for a beat or a bar makes the whole
kit sound like a small radio, and the full kit coming back is the impact. It is the only transition device
in the video.

## When to use it
Last beat or last bar before a new 8-bar phrase, in intros and breakdowns where the kit should be present
but thin, and for small fills inside a drop when adding another drum would be too much.

## How
1. Put a filter on the drum group and set it to band-pass (said, [5:20](https://youtu.be/JqKaSvHImB0?t=320)).
2. Settings on screen: 24 dB slope, centre around 1 kHz (993 Hz, later 1.21 kHz), resonance 31 to 45 %,
   no drive, 100 % wet (shown at [5:35](https://youtu.be/JqKaSvHImB0?t=335)).
3. Drag the frequency while it plays to find where the kit sounds best thinned (said).
4. Automate the device's on/off, not its mix: off for the phrase, on for the last beat before bar 3 in his
   example, off again on the downbeat (said and shown at [5:52](https://youtu.be/JqKaSvHImB0?t=352)).

## In Rohil's setup
- Logic's AutoFilter on the drum Track Stack: `rick-rubin logic insert Drums AutoFilter`, read its names
  with `rick-rubin logic params Drums AutoFilter`, choose the band-pass mode and a cutoff near 1 kHz.
- Session mode has no automation command today, so the bypass automation is drawn by hand in Logic (press A,
  choose the plug-in's Bypass parameter on the stack). Say so to Rohil rather than leaving the filter on.
- In a `song.py`, a section's `automation={drums: {"filter": [...]}}` is a low-pass only; for a band-pass
  write a short variant section with the effect on the track.

## How to check it
Bounce the two bars around the fill: `rick-rubin logic bounce bounces/fill.wav --bars 8-9`. The filtered
beat should lose nearly all energy below 300 Hz and above 4 kHz, and the bar after should be back to the
level of the bar before it. `reference compare` should count one more texture change per phrase.

## Why it works
Removing the kick's low end for a moment creates the contrast a drop needs without a single new sound, and
switching (rather than sweeping) keeps it rhythmic.
