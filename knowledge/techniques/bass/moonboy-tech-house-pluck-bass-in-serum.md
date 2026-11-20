---
title: A plucky tech house bass from Serum's init patch: saw, sub, low-pass, one-shot LFO on the cutoff
topic: bass
genres: [tech house]
source: MOONBOY — HOW TO TECH HOUSE | Full Tutorial (Odd Mob, Chris Lake, Mau P) (https://youtu.be/JqKaSvHImB0?t=614)
status: untested
---
## What it is
The groove bass of the video, built in Serum 2 in about ten moves: one saw plus the sub oscillator, a
resonant 12 dB low-pass that a one-shot LFO opens at the start of each note, a decaying amp envelope, mono,
a fixed start phase and some filter drive.

## When to use it
For the offbeat groove bass that runs through a tech house track. It is short and dark on purpose: it
leaves the mids to the vocal and to a character bass on top.

## How
1. Init patch; oscillator A on the saw, one voice (shown, [7:22](https://youtu.be/JqKaSvHImB0?t=442)).
2. Filter 1 on, MG Low 12, cutoff low (he lowers it twice "so it's deeper"; no number shown: about 100 to
   200 Hz read off the filter graph, inferred), some resonance (shown, [11:40](https://youtu.be/JqKaSvHImB0?t=700)).
3. LFO 1 on the cutoff, drawn as a falling curve, rate 1/8, mode Envelope (shown). Depth not readable.
4. Amp envelope: attack 1 ms, sustain −18.9 dB, release 520 ms; decay stays at 1.00 s but its curve is pulled
   steep, so the level falls fast then holds low (shown at 11:40; he says release up, sustain down, decay
   tighter).
5. Mono on, so notes cannot overlap and smear (said, [10:50](https://youtu.be/JqKaSvHImB0?t=650)).
6. Sub oscillator on, sine, octave 0 (said "add some sub"; shown).
7. Oscillator random phase to 0, then turn the phase until the attack sounds right: 248° (said and shown,
   [11:16](https://youtu.be/JqKaSvHImB0?t=676)). Every note now starts identically.
8. Filter drive up to 32 % for weight (shown at [11:44](https://youtu.be/JqKaSvHImB0?t=704)).

## In Rohil's setup
```
rick-rubin serum set init osc_a.rand_phase=0 osc_a.phase=248 sub.on=on sub.shape=Sine \
  filter_1.on=on filter_1.type="MG Low 12" filter_1.cutoff_hz=150 filter_1.res=30 filter_1.drive=32 \
  env_1.attack_ms=1 env_1.decay_ms=1000 env_1.decay_curve=85 env_1.sustain_db=-18.9 env_1.release_ms=520 \
  lfo_1.rate=1/8 lfo_1.mode=Envelope lfo_1.shape="Basic/Saw Down Curved" global.mono=on \
  --mod lfo_1:filter_1.cutoff_hz:35 --save th-pluck-bass --project <dir>
```

Cutoff, resonance, decay curve and mod depth are our starting points; tune them with `rick-rubin serum ab`
(`--try "mod_1.amount=60"`, `--try "filter_1.cutoff_hz=220"`), then `rick-rubin serum audition` for him to
hear, and `rick-rubin logic add-serum <dir>/serum/presets/th-pluck-bass.SerumPreset --name Bass`.

## How to check it
`rick-rubin serum describe ... --note E1 --bpm 130`: `mono`, no side energy, "bright early→late" falling,
sustain 15 to 19 dB under the peak, pitch steady. A first run of the command above (2026-11-20, not heard)
gave bright 103→90 Hz, decay 485 ms and sustain −17.2 dB; with `lfo_1.shape="Basic/Saw Down"` the front is
brighter (150→90 Hz) and the word `closes` appears. Render the same note twice: with random phase at 0 the two files should be identical.

## Why it works
The low-pass keeps the bass under the vocal, the LFO gives each note a bright front that reads as a pluck on
small speakers, the sub gives the club its weight, and the fixed phase makes every offbeat hit the same.
