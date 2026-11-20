---
title: A rhythmic bass needs a sound with a shape: filter-envelope pluck with a long decay
topic: bass
genres: [tech house, progressive house, bass house]
source: Alex Rome — This Producer's Bass Was Weak. Here's the Fix. (https://youtu.be/HLCi1uYq8r0?t=551)
status: untested
---
## What it is
A flat sub played in a dotted-eighth rhythm sounds like one long note: there is nothing to mark where each note
starts. Giving the same saw a filter envelope makes each note open bright and close, so the rhythm is heard. The decay
is long enough that each note runs into the next.

## When to use it
A bassline with a rhythm of its own (dotted eighths, syncopation, the lead's rhythm) in melodic or deep house. Not
needed for one held root per chord.

## How
1. Notes: chord roots in the rhythm of the busiest melody. His is dotted eighths that restart every half bar: an
   eighth plus half its length again (said, [9:32](https://youtu.be/HLCi1uYq8r0?t=572)). First note shown at
   [9:48](https://youtu.be/HLCi1uYq8r0?t=588): G#0 in Logic's naming (about 52 Hz), three sixteenths long.
2. Hear the problem first: on the plain sub the rhythm is inaudible (said,
   [10:14](https://youtu.be/HLCi1uYq8r0?t=614)).
3. New patch: Serum init saw, filter MG Low 24 with the cutoff closed, ENV 2 assigned to the cutoff (shown
   [10:42](https://youtu.be/HLCi1uYq8r0?t=642)), ENV 2 sustain to zero (said).
4. "Warm it up" and lengthen it (said, [10:57](https://youtu.be/HLCi1uYq8r0?t=657)). Shown at
   [11:08](https://youtu.be/HLCi1uYq8r0?t=668): ENV 2 attack 0.5 ms, decay 2.70 s, sustain 0 %, release 15 ms.
5. Let the notes "crash into" the next one: he says it fills the headphones more (said, 10:57).
6. The SUB oscillator is on in both frames and looks routed into the filter at 11:08; he does not mention it (shown).
7. Sidechain as for any bass (said, [11:10](https://youtu.be/HLCi1uYq8r0?t=670)).
8. Cutoff and envelope amount are not readable.

## In Rohil's setup
```
rick-rubin serum set init filter_1.on=on "filter_1.type=MG Low 24" filter_1.cutoff_hz=60 env_2.decay_ms=2700 \
    env_2.sustain_pct=0 osc_a.rand_phase=0 global.mono=on --mod env_2:filter_1.cutoff_hz:40 \
    --save pluck-bass-long --project <dir>
```
Cutoff 60 and amount 40 are ours; tune them with `rick-rubin serum ab ... --try`. For his sub layer add `sub.on=on` (a
sine by default; `rick-rubin serum params --group sub`). Mono and fixed phase are ours, for a consistent low end. Note
length and other ways to add weight: `alex-rome-b-bassline-from-the-chords-bottom-notes.md`.

## How to check it
One offline render here (G#0, 1 s) against the plain saw sub at cutoff 120: brightness now falls from 102 to 59 Hz
across the note (the sub: flat at 56 Hz), 8 harmonics instead of 3, energy 81 % sub and 18 % bass (the sub: 92 and 8),
described as `closes`. In the track, `rick-rubin hits` on a bass-only bounce should show a level step at every note
start. Not yet heard by Rohil.

## Why it works
The ear finds note starts from sudden changes in brightness and level. A closed low-pass leaves almost only the
fundamental, which has neither; the envelope adds a burst of harmonics at each onset (inferred).
