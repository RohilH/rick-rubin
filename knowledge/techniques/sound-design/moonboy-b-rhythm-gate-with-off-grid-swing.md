---
title: Give a pad or vocal a groove: gate its volume with a swung, off-grid pattern instead of an even one
topic: sound-design
genres: [bass house, progressive house, tech house]
source: MOONBOY — 13 Insane Ways to Make Any Vocal Sound MAGICAL (https://youtu.be/7wcJShg8tn4?t=245)
status: untested
---
## What it is

Two of his effect presets for sustained material. "Hover" is a slow, lopsided tremolo for pads. "Swing Cut"
is a volume gate whose openings are deliberately off the grid, so whatever goes through it picks up a
swung rhythm. He links the idea to Fred again.. combining a percussion loop with a vocal or synth in a
morphing plug-in: borrow the rhythm of one sound and stamp it on another.

## When to use it

On a vocal pad, a held chord or a long vocal note that should move with the drums. In tech house this is how
a background vocal wash gets the groove of the percussion without adding another percussion part.

## How

1. Hover (shown at [4:25](https://youtu.be/7wcJShg8tn4?t=265), preset "SFX – HOVER" in SerumFX): audio into
   the noise slot, Note Latch on; LFO 1 at 1/4, synced, drawn as a peak about a third of the way through the
   cycle that falls away to nothing before the end; macros for speed (57 %), tightness and stereo. Used on a
   reverb pad made from a vocal.
2. Swing Cut (shown at [5:20](https://youtu.be/7wcJShg8tn4?t=320), preset "FX – Swing Cut 1"): LFO 1 on the
   volume, rate 1/4 with the dotted switch on, smoothing 33.8, drawn as four spikes of different heights
   that are not evenly spaced. The peaks are "off grid, in a swing format" (said,
   [4:52](https://youtu.be/7wcJShg8tn4?t=292)).
3. After the gate in the same rack: EQ, hall reverb, a 1/4 ping-pong delay filtered around 1.3 kHz, a
   compressor; macros Smooth, Wet (36 %), Space, LP FX (shown at 5:20).
4. The concept he borrows (said, [4:31](https://youtu.be/7wcJShg8tn4?t=271)): a "morph" plug-in that combines
   a rhythmic percussion loop with a vocal or synth.
5. He made many rhythm presets this way; the exact spike positions are his and not readable to the step.

## In Rohil's setup

- The most direct Logic version of step 4: a Noise Gate on the pad keyed from a percussion loop, so the pad
  only sounds when the loop hits: `rick-rubin logic insert "Vox pad" "Noise Gate" --sidechain "Top loop"`, then
  set threshold and release from `rick-rubin logic params "Vox pad" "Noise Gate"`. The swing is then the
  loop's own.
- Drawn pattern: Logic's Step FX has a step sequencer that can gate the level; read what it offers with
  `rick-rubin logic devices "Step FX"` before promising it. Tremolo cannot draw shapes.
- Hover: Tremolo at 1/4 with its symmetry pushed to one side and smoothing up, phase a few degrees.
- Follow the gate with a send to a delay and a reverb, as his rack does (`rick-rubin logic send "Vox pad" 1 -12`).

## How to check it

`rick-rubin hits <dir> bounces/pad_gated.wav` beside `rick-rubin hits <dir> samples/top_loop.wav`: the pad's
loud steps are the loop's loud steps, including the late ones. Without the gate the pad reads flat.
`reference compare`: more movement in the mid band at the same loudness.

## Why it works

Swing lives in timing the grid does not have. A sustained sound carries no timing of its own, so cutting it
with a swung pattern transfers the groove to it, and the kit and the pad then lean the same way.
