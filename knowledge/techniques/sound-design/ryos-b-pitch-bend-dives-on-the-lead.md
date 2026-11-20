---
title: Pitch-bend dips on the lead stack (and the bass group) at phrase ends
topic: sound-design
genres: [progressive house, bass house]
source: RYOS — Can I Fix My Subscribers Music? (https://youtu.be/23NY1XxOlbA?t=171)
status: untested
---
## What it is
The last touch on a lead stack before moving on: an automation curve on the synth's pitch-bend wheel that
makes the lead dip and snap back at chosen moments. It gives a static supersaw-type stack a hand-played,
"alive" quality.

## When to use it
On a finished lead stack in a drop, at the end of a phrase or just before a chord change. Sparingly: a few
moments per eight bars.

## How
1. Build the stack first. His three layers for this drop: a main Spire lead, a "buzzy, gritty" layer (Spire
   preset "AS_LD - Digital Punk", shown [2:32](https://youtu.be/23NY1XxOlbA?t=152)), and a warm layer with a
   processing chain reused from an older project (said, [2:30](https://youtu.be/23NY1XxOlbA?t=150)).
2. Then add pitch automation, which he calls the last thing to do with the leads (said,
   [2:51](https://youtu.be/23NY1XxOlbA?t=171)).
3. What it looks like: an automation clip on the Spire's bend wheel. It rests at centre, has one small
   wiggle mid-phrase, and near the end of the phrase dives down quickly and returns to centre right at the
   boundary (shown, [3:10](https://youtu.be/23NY1XxOlbA?t=190)). Depth in semitones is not readable.
4. Later the project holds clips named "LD Pitch" and "BASS GRP - Pitch", so the leads and the bass group
   bend together (shown, [9:00](https://youtu.be/23NY1XxOlbA?t=540)).
5. All layers must bend by the same amount, or the stack goes out of tune with itself (inferred).

## In Rohil's setup
- Serum 2: set the same bend range on every layer, for example `rick-rubin serum set "<lead>"
  global.bend_down=-12 global.bend_up=12 --save lead-bend --project <dir>`, and the same on the bass patch.
- In a `song.py` the bend curve is automation the agent writes for the section. In his open Logic project the
  bridge cannot write automation or MIDI controller data: say the bar and the beat, and he draws pitch bend
  in the piano roll's automation lane, or the agent delivers the part as a MIDI file containing the bend with
  `rick-rubin logic add-midi`.
- If layers are different synths (Serum and Vital), check each one's bend range by hand.

## How to check it
`rick-rubin notes` reads single-voice audio, so bounce a part that plays one note at a time (the bass, or one
lead layer on a single-line passage) over the phrase: the reading at the phrase end should sit flat by the
intended amount and be back at 0 cents on the next downbeat. Layers bounced separately must agree. Whether it
sounds expressive or seasick is Rohil's call on a before and after bounce.

## Why it works
A fall in pitch just before a boundary creates a small tension that the next downbeat resolves, and it is
the kind of movement a player makes, which programmed stacks otherwise lack.
