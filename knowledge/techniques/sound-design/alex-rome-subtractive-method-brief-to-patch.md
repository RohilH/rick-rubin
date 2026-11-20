---
title: From a description of a sound to a patch, one oscillator at a time
topic: sound-design
genres: [any, progressive house, tech house, bass house]
source: Alex Rome — How To Make Any Sound From Scratch (https://youtu.be/p1-WmITJqBk?t=53)
status: untested
---
## What it is
His mental model for building any basic sound from init: answer four questions in signal order (what wave, how dark,
what shape over time, what moves), then add effects. Every sound in the video is one oscillator through one low-pass
filter; only the answers change.

## When to use it
When a brief can be said in plain words ("a wide soft pad", "a short dark pluck"). Also for learning: he says to get
full control of bass first, then widen out.

## How
1. Loop some chords, switch a reverb on, init the synth, one oscillator on the default saw (said,
   [1:22](https://youtu.be/p1-WmITJqBk?t=82), [8:31](https://youtu.be/p1-WmITJqBk?t=511)).
2. **Oscillator = timbre** (said, [2:25](https://youtu.be/p1-WmITJqBk?t=145)): sine is pure and warm, triangle a
   sine with corners, square dense and strong, saw thin and gritty and the best for unison. **Unison = width and
   size**, counted per note (said, [4:37](https://youtu.be/p1-WmITJqBk?t=277)).
3. **Filter = how dark.** Low-pass, the steep 24 dB type for a "tight" sound (said; MG Low 24 shown
   [2:12](https://youtu.be/p1-WmITJqBk?t=132)).
4. **ENV 1 = shape.** Sustain up is a pad; sustain off with short decay is a pluck; slow attack is a swell; release
   is the tail. Decay does nothing until sustain comes down (said, [7:06](https://youtu.be/p1-WmITJqBk?t=426) to
   [10:00](https://youtu.be/p1-WmITJqBk?t=600)).
5. **Modulation = movement and warmth.** An envelope turns a knob once per note, an LFO keeps turning it; drag
   either onto the cutoff (said, [17:22](https://youtu.be/p1-WmITJqBk?t=1042)). Leave the cutoff low and automate it
   later (said, [20:28](https://youtu.be/p1-WmITJqBk?t=1228)).
6. **Effects last**: distortion to add harmonics, delay and reverb for space (said,
   [15:20](https://youtu.be/p1-WmITJqBk?t=920) and [22:05](https://youtu.be/p1-WmITJqBk?t=1325)).
7. Go back to earlier modules after each step; that is how one patch becomes ten (said,
   [10:31](https://youtu.be/p1-WmITJqBk?t=631)).

## In Rohil's setup
| The brief says | Serum key | Measured on this Mac (`serum ab init`, C3) |
|---|---|---|
| pure, soft | `osc_a.wt_pos=45` (sine) | 1 harmonic |
| hollow, strong | `osc_a.wt_pos=128` (square) | 16 harmonics, odd-heavy |
| soft with some edge | `osc_a.wt_pos=72` (triangle) | 3 harmonics, odd-heavy |
| wide, big | `osc_a.unison=10` | side about 50 % in every band |
| dark, tight | `filter_1.on=on "filter_1.type=MG Low 24" filter_1.cutoff_hz=...` | harmonics fall |
| plucky | `env_1.decay_ms=275 env_1.sustain_db=-120` | word `plucky` |
| moving | `--mod lfo_1:filter_1.cutoff_hz:45` | word `moving`, a rate in beats |

`rick-rubin serum ab init --note C3 --try "..." --try "..."` compares answers in about a second each. The repo's
rule is to start from the closest preset; init suits these one-oscillator sounds and learning.

## How to check it
`rick-rubin serum describe` after each step: one word or number should change per decision, as in the table.

## Why it works
Each module answers one question, so a description can be translated a clause at a time (inferred).
