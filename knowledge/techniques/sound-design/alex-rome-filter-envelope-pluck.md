---
title: Filter-envelope pluck, a closed low-pass opened by ENV 2 on every note
topic: sound-design
genres: [progressive house, tech house, bass house]
source: Alex Rome — How To Make Any Sound From Scratch (https://youtu.be/p1-WmITJqBk?t=1083)
status: untested
---
## What it is
The one modulated sound he says every producer should learn, usable as melody, chords or bass: a saw behind a closed
low-pass, with a second envelope snapping the cutoff open on each note. His "electro pluck".

## When to use it
Melodic plucks and arps, tech house stabs, a plucked bass: anywhere the note should start bright and end dark, which
the amp-envelope pluck cannot do.

## How
1. Init: one saw (said, [18:23](https://youtu.be/p1-WmITJqBk?t=1103)).
2. Filter 1 on with OSC A routed to it, MG Low 24, cutoff closed until there is no sound (said; shown
   [20:15](https://youtu.be/p1-WmITJqBk?t=1215): 8 Hz).
3. Drag ENV 2 onto the cutoff knob (said, [19:04](https://youtu.be/p1-WmITJqBk?t=1144)). Serum draws the range as a
   blue arc round the knob (said, [19:50](https://youtu.be/p1-WmITJqBk?t=1190)).
4. ENV 2 sustain off: attack 0.5 ms, hold 0, decay 1.51 s, release 15 ms (shown
   [19:55](https://youtu.be/p1-WmITJqBk?t=1195)).
5. Set how far it opens and from where. The frame at [20:55](https://youtu.be/p1-WmITJqBk?t=1255) reads cutoff 133
   Hz reaching 1667 Hz at the peak.
6. Leave it that dark on purpose and automate the cutoff upward through the arrangement (said,
   [20:28](https://youtu.be/p1-WmITJqBk?t=1228)). Reverb on while designing (said,
   [20:05](https://youtu.be/p1-WmITJqBk?t=1205)).
7. Variants from the same patch: square with unison 9 and decay 1.12 s, cutoff 20 Hz reaching 752 Hz (shown
   [21:35](https://youtu.be/p1-WmITJqBk?t=1295)).

## In Rohil's setup
```
rick-rubin serum set init filter_1.on=on "filter_1.type=MG Low 24" filter_1.cutoff_hz=133 env_2.attack_ms=0.5 \
    env_2.decay_ms=1510 env_2.sustain_pct=0 --mod env_2:filter_1.cutoff_hz:32 --save filter-pluck --project <dir>
```
The amount 32 is inferred: 133 Hz to 1667 Hz is about a third of Serum's cutoff range; he never states it. Tune
`env_2.decay_ms` (150 to 1500) and the amount with `rick-rubin serum ab`. For the automation: a `serum=` track holds
one cutoff, so use the section's `filter` automation or a second track with a higher `filter_1.cutoff_hz`; with a
live Serum in Logic (`rick-rubin logic add-serum`) Rohil draws the cutoff automation himself.

## How to check it
`rick-rubin serum describe ... --note C3 --secs 1.5`: one render here gave brightness falling from 299 to 262 Hz
over the note, decay 1150 ms, 2 harmonics within 30 dB (a very dark starting point, as he intends); at amount 45 it
read 401 to 262 Hz with the word `closes`. Raising cutoff or amount should raise the early brightness, not the late.

## Why it works
Brightness and loudness fall together, as they do in a plucked string, so it reads as a natural pluck. Because the
filter does the shaping, the tone is rounder than cutting the level alone (he says modulated sounds are warmer).
