---
title: A 16th-note tremolo on a chord stack whose depth is automated up to the section's peak
topic: sound-design
genres: [progressive house, any]
source: RYOS — Can I Fix My Subscribers Music? (https://youtu.be/23NY1XxOlbA?t=682)
status: untested
---
## What it is
A volume LFO on held chords that starts almost unnoticeable and is automated deeper, so the chords begin
smooth and end up fluttering at the point of highest energy. The subscriber's track had the idea; Ryos
rebuilds it on his own chord stack.

## When to use it
Big sustained chords in a build-like or "hands up" section that need to gain energy without new notes. The
static version of this is `sound-design/ryos-pg-gated-pad-movement-after-the-synth.md`.

## How
1. The chord stack is replaced with a larger, more "angelic" one from an earlier project, with its MIDI cut
   to the section's rhythm (said, [10:57](https://youtu.be/23NY1XxOlbA?t=657)).
2. LFOTool goes last on the chord group, after a multiband compressor, a Pultec-style EQ, an EQ and
   Kickstart 2 (shown, [11:34](https://youtu.be/23NY1XxOlbA?t=694)).
3. Shape: a plain triangle. The rate reads as 1/16 (shown, same frame; small text).
4. Reduce its amount at the start, let it rise, and reach "full blast" at the chosen spot (said,
   [11:30](https://youtu.be/23NY1XxOlbA?t=690)). The project then holds an automation clip for LFOTool's mix
   level (shown, [12:18](https://youtu.be/23NY1XxOlbA?t=738)).
5. Start and end values are not readable.

## In Rohil's setup
- Logic's Tremolo on the chord stack: `rick-rubin logic insert Chords Tremolo`, rate 1/16, a symmetrical
  (triangle-like) shape; read names with `rick-rubin logic params Chords Tremolo`. Put it after Kickstart 2.
- The rise is automation of Tremolo's depth. The bridge cannot write automation: tell Rohil the bars (depth
  near 0 at the start, full at the peak) and he draws the ramp. Two tracks, one without and one with full
  tremolo, give a two-step version with no automation.
- In Serum 2 the same can live in the patch: an LFO with a triangle from `rick-rubin serum shapes`, `lfo_2.rate=1/16`,
  routed to level with `--mod`, its amount scaled by a macro (`macro_1.value`) that is automated in Logic.
- In a `song.py` this is section automation the agent writes.

## How to check it
Bounce the chords alone over the section and run `rick-rubin hits <dir> --tracks Chords --bars A-B`: early
bars show nearly equal level on every 16th; by the peak, alternate 16ths differ strongly. Overall loudness of
the stem should not fall as depth rises; if it does, raise the stem.

## Why it works
A tremolo adds rhythm and a sense of speed to held notes, and making it grow turns a static pad into a build
of its own.
