---
title: A moving progressive house pad from a plain saw pad and a half-depth trance gate after the synth
topic: sound-design
genres: [progressive house]
source: RYOS — Making Beautiful Progressive House | Studio Time with Ryos EP. 50 (https://youtu.be/WnZ7GN1tpek?t=439)
status: untested
---
## What it is
The "moving synth" of a progressive house break made the simple way: a classic saw pad holds the chords and a
step gate placed after the synth chops its volume in 16ths, mixed in at about half so the pad pulses without
turning choppy.

## When to use it
A break or build that has chords and melody but no motion. He normally builds the movement inside the synth
and chose post-processing this time (said, [7:19](https://youtu.be/WnZ7GN1tpek?t=439)).

## How
1. Pad: a simple saw chord patch in Serum. Shown at [8:10](https://youtu.be/WnZ7GN1tpek?t=490): oscillator A a
   saw with 2 unison voices, filter type Low 24 part closed, amp attack 4.5 ms, decay 1 s.
2. After it, a trance gate: 16 steps, every other step on, resolution shown as 1/32, so the volume pulses once
   per 16th note (shown, 8:10).
3. Fully wet it is too choppy (said, [7:59](https://youtu.be/WnZ7GN1tpek?t=479)); the mix ends at 53 % (shown).
4. Play the chord voicings, no melody, and raise the part an octave (said, [8:10](https://youtu.be/WnZ7GN1tpek?t=490)).
5. Later, when it crowds the drop: take out lows and low mids and lift the high mids (said,
   [28:14](https://youtu.be/WnZ7GN1tpek?t=1694)).

## In Rohil's setup
He does not own the Kilohearts gate. Two ways:
- Inside Serum 2, so the pulse is part of the patch: `rick-rubin serum set init osc_a.unison=2 filter_1.on=on
  filter_1.type="Low 24" filter_1.cutoff_hz=2000 env_1.attack_ms=4.5 lfo_1.shape="Basic/Square" lfo_1.rate="1/16"
  --mod lfo_1:osc_a.level_db:-40 --save gated-pad --project <dir>` (the cutoff and the mod depth are our starting
  guesses; a negative depth because the level starts at the top). Lower the depth for the half-wet feel.
- In Logic: the stock Tremolo after Serum, synced to 1/16 with a square-like shape and its depth near half
  (read its names with `rick-rubin logic devices Tremolo` first). What is lost: his gate has a per-step pattern
  and an envelope per step.
For step 5, a Channel EQ low cut on the pad, or `fx.utility.hpf` inside the patch.

## How to check it
`rick-rubin serum describe gated-pad --note C3 --secs 2 --bpm 128`: the "movement while held" rate should read
about 0.25 beats (8.5 Hz at 128 BPM) and the word `moving` should appear. A dry run of the command above on
2026-11-20 saved without error and read 6.7 dB of movement at 0.20 beats, `+moving`, and a much darker tone
(open the cutoff if it is too dull); nobody has heard it. Compare depths with `rick-rubin serum ab`, then
`rick-rubin serum audition` so Rohil hears full depth against half depth.

## Why it works
A held pad has no rhythm; gating it borrows the 16th grid of the drums. Mixing the gate at half keeps the
sustained body, so the pad still fills the harmony while it flickers.
