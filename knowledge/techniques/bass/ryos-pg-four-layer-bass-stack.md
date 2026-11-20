---
title: A four-layer drop bass: clean sine sub, aggressive mid, thin vocal-like mid, wide reese
topic: bass
genres: [progressive house]
source: RYOS — Making Beautiful Progressive House | Studio Time with Ryos EP. 50 (https://youtu.be/WnZ7GN1tpek?t=955)
status: untested
---
## What it is
The drop bass as four tracks with separate jobs, all playing the same rhythm, summed on a bass group: the
concrete stack behind his general advice in `ryos-bass-in-layers-sub-harmonics-mid.md`.

## When to use it
A drop bass that has to be heavy on a club system and still audible on small speakers.

## How
1. Aggressive mid bass first: it carries the rhythm and the pitch slides. He auditions one, then swaps it for
   another style and keeps the option of going back (said, [19:38](https://youtu.be/WnZ7GN1tpek?t=1178)).
2. A very thin layer that lives only in the mids, with a talking, robotic quality (see
   `ryos-pg-thin-robot-mid-bass.md`).
3. Sub: keep it clean, "nothing crazy" (said, [18:50](https://youtu.be/WnZ7GN1tpek?t=1130)). The first patch,
   shown at [19:10](https://youtu.be/WnZ7GN1tpek?t=1150), is one sine oscillator at octave -2 with a punchy
   attack; he then decides a cleaner sub with no attack suits it better (said,
   [19:17](https://youtu.be/WnZ7GN1tpek?t=1157)).
4. Reese to round the stack off, taken from an older track and moved up an octave (said,
   [20:00](https://youtu.be/WnZ7GN1tpek?t=1200)). Shown at [20:26](https://youtu.be/WnZ7GN1tpek?t=1226): one saw
   oscillator at octave -1 with 7 unison voices, an 18 dB ladder low-pass, mono with legato, amp attack 0.5 ms,
   release 40 ms, bend range 12.
5. Reese chain, shown at [20:52](https://youtu.be/WnZ7GN1tpek?t=1252): saturation, a second distortion, two EQs,
   a filter, then a volume-shaper for the pump last.
6. Route all four to a bass group (shown, [24:38](https://youtu.be/WnZ7GN1tpek?t=1478)). He keeps the sub simple
   partly to leave room for a bass guitar later (said, 18:50).

## In Rohil's setup
Serum 2 for every layer. Both of these ran without error on this Mac (2026-11-20); the cutoff is our guess:
- Sub: `rick-rubin serum set init osc_a.on=off sub.on=on sub.shape=Sine sub.level_db=0 env_1.attack_ms=5
  env_1.release_ms=40 global.mono=on --save clean-sub --project <dir>`. Measured on G0: one harmonic, 100 % of
  the energy in the sub band, 0 % side.
- Reese: `rick-rubin serum set init osc_a.octave=-1 osc_a.unison=7 filter_1.on=on filter_1.type="MG Low 18"
  filter_1.cutoff_hz=600 global.mono=on global.legato=on env_1.attack_ms=0.5 env_1.release_ms=40
  global.bend_up=12 global.bend_down=-12 --save reese-layer --project <dir>`. Measured on G2 (sounds G1): 57 %
  side energy in the low band, flagged `wide-low-end`.
So the reese needs its lows removed (`--fx-add utility` with `fx.utility.hpf`, or a Channel EQ low cut) and the
sub must be the only layer below about 100 Hz. Pump: `rick-rubin logic insert "Bass Bus" "Kickstart 2" Mix=0.8`.

## How to check it
`rick-rubin width` on a bounce of the bass group: the low band must read near 0 % side. `rick-rubin spectrum
<dir> sub.wav mid.wav reese.wav`: one layer per band, no two layers fighting below 100 Hz, harmonics running
without a gap into the mids. BASSROOM against a reference for the overall low-end level.

## Why it works
A sine sub gives weight without phase trouble; the wide and distorted layers give size and audibility above
it. Keeping width and dirt out of the sub band keeps the low end mono and the kick clear.
