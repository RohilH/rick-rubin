---
title: A hidden drone: a few high notes through echo and a fully wet reverb, bounced and trimmed
topic: sound-design
genres: [progressive house, any]
source: Alex Rome — 7 Useful Layering Techniques and Why They Work (https://youtu.be/u8ozR9cnCTU?t=695)
status: untested
---
## What it is
A bed of pitched wash made in two minutes: play one to four notes high up, smear them with an echo and a reverb at 100
% wet, bounce the result to audio, and keep whichever stretch of it sounds best. He calls it "the Armin", after seeing
Armin van Buuren hide layers like this.

## When to use it
A sparse section that already has its important parts (his example is a vocal and one instrument) and sounds empty,
with no room for another real part. Intros, breaks, verses.

## How
1. Load any synth sound (said, [12:30](https://youtu.be/u8ozR9cnCTU?t=750); his comes from Sylenth1).
2. High on the keyboard, play between one and four notes; he plays two (said,
   [12:38](https://youtu.be/u8ozR9cnCTU?t=758)). Use notes of the section's key (inferred; he does not say which).
3. Add an echo, then any reverb: decay turned up, wet at 100 % (said, [12:55](https://youtu.be/u8ozR9cnCTU?t=775)).
   The result should be a blur with no clear attack.
4. Bounce the track in place to audio (said, [13:15](https://youtu.be/u8ozR9cnCTU?t=795)).
5. Cut any piece out of the audio and try it under the section; a different piece gives a different drone, so it is
   trial and error (said, [13:37](https://youtu.be/u8ozR9cnCTU?t=817)).
6. Loop the chosen piece from the first bar of the section (said, [14:39](https://youtu.be/u8ozR9cnCTU?t=879)).
7. Level: low enough that nobody attends to it (said). No figure is given, and Ryos argues the opposite: a drone
   nobody can hear is wasted (`../arrangement/ryos-fill-the-mid-range-and-atmosphere-bed.md`). Try both.

## In Rohil's setup
Serum for the notes, Logic's Tape Delay or Stereo Delay, then Valhalla Supermassive with Mix at 100 % and a long decay
(`rick-rubin logic insert Drone "ValhallaSupermassive" Mix=1.0`; its other names are in `rick-rubin logic devices
"ValhallaSupermassive"`). Bounce: Logic's Bounce in Place (Ctrl-B), or `rick-rubin logic bounce bounces/drone.wav
--tracks Drone --bars 1-8`, then `rick-rubin logic add-audio bounces/drone.wav --bar 1 --name Drone`. Before using it,
`rick-rubin notes <dir> bounces/drone.wav` to confirm the pitches fit the key. Low-cut it (the reverb card:
`../mixing/alex-rome-eq-the-reverb.md`).

## How to check it
`rick-rubin compare <dir> section_without.wav section_with.wav`: a small rise in mid and high share and in side
energy, almost no change in loudness or crest. If loudness moves by more than about 1 dB it is no longer hidden.
`rick-rubin width`: the low band stays mono.

## Why it works
A sustained, attack-free sound in the section's key fills the silence between phrases, so the foreground parts no
longer start and stop against nothing (inferred).
