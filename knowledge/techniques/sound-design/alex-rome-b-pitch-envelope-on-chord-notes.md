---
title: A short pitch envelope on a plain chord sound, so each note falls or rises into pitch
topic: sound-design
genres: [any, progressive house, bass house]
source: Alex Rome — A Simple System For Making Songs in 2026 (https://youtu.be/XlltkalLaU4?t=297)
status: untested
---
## What it is
The one piece of "sauce" he allows on the chord sound of his trench: every note starts slightly off pitch and
slides to the right note. He tries it both ways, starting above and starting below.

## When to use it
The chords are a plain filtered saw (as his systems ask) and need a little character without becoming a busier
sound. Also on a pluck or a stab.

## How
1. Keep the chord sound simple. It is what glues the harmony together, and simple sounds are easier to work with
   (said, [4:36](https://youtu.be/XlltkalLaU4?t=276)).
2. Add a pitch movement at the start of each note; he heard it in a well-known recent track (said,
   [4:57](https://youtu.be/XlltkalLaU4?t=297)).
3. Version one: pitch starts high and comes down to the note. Version two: starts low and comes up (said,
   [5:17](https://youtu.be/XlltkalLaU4?t=317)). He plays both under the vocal and says the effect is a kind of
   laziness (said, [5:37](https://youtu.be/XlltkalLaU4?t=337)).
4. Shown at [5:10](https://youtu.be/XlltkalLaU4?t=310): Serum 2, ENV 2 selected and being edited while he does
   this. The destination and the amount are not visible in the frame, so the depth and time below are ours.

## In Rohil's setup
In Serum 2, route ENV 2 to the oscillator's coarse pitch with a short decay and no sustain (inferred values, to
be tuned by ear):
```
rick-rubin serum set saw-pad env_2.attack_ms=0.5 env_2.decay_ms=250 env_2.sustain_pct=0 \
    --mod env_2:osc_a.coarse:4 --save saw-pad-fall --project <dir>
```
A positive amount starts above the note and falls; a negative one starts below and rises. `saw-pad` is the patch
from `sound-design/alex-rome-filtered-saw-pad.md`; if ENV 2 already drives the cutoff, the same envelope will
move both. Compare the two directions and two or three depths with `rick-rubin serum ab`, then `rick-rubin serum
audition` for him to hear in context. On chords, a large amount smears the harmony: start small.

## How to check it
`rick-rubin notes` on a rendered note (or `rick-rubin serum describe ... --note C3`): the pitch begins some cents
or semitones away and reaches the written note within the decay time; after that it is steady and in tune. Sharp
or flat for the whole note means the sustain is not at zero.

## Why it works
A pitch slide at the onset is what a bent string or a tape start does, so a static synth note reads as played;
because it is over in a fraction of a beat, the chord itself stays clear.
