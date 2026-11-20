---
title: A big synth brass from two saws: one plain voice for the body, eight unison voices for width, a resonant low-pass
topic: sound-design
genres: [tech house, bass house, progressive house]
source: MOONBOY — HOW TO TECH HOUSE (John Summit, Dom Dolla, Chris Lake,) (https://youtu.be/_4qJSUFao50?t=304)
status: untested
---
## What it is

His "Big Brass" preset, explained in three sentences: one saw is the deep mid layer, a second oscillator
adds tone and width, and a low-pass filter with a high resonant peak makes it sound like brass. The preset
on screen fills in the rest: a slow attack, mono with glide, and a long envelope closing the filter.

## When to use it

For a held, swelling stab or a slow melody in a drop or build (the horn-like sound of big-room tech house).
It is mono and legato: lines, not chords.

## How

1. Oscillator A: saw, octave +1, one voice. Oscillator B: saw, octave 0, 8 unison voices (shown at
   [5:30](https://youtu.be/_4qJSUFao50?t=330); he says one saw for the deep mid layer and a second for tone
   and width).
2. Sub oscillator on, octave 0, a triangle-like shape, sent direct out past the filter (shown).
3. Filter: MG Low 12 with A and B through it and a clear resonance peak; cutoff and resonance each carry a
   modulation (shown; no numbers). The peak is "the brass tonality" (said,
   [5:35](https://youtu.be/_4qJSUFao50?t=335)).
4. Amp envelope: attack 280 ms, decay 1.00 s, sustain 0 dB, release 15 ms (shown). The slow attack is the
   breath of a horn (inferred).
5. LFO 1 in Envelope mode at 2 bars: starts at the top, sinks slowly, then falls away at the end; three
   targets (shown). So the brightness fades across a long note.
6. Mono and legato on, portamento set to Always, bend range +1 / −5 (shown).
7. Four macros: Tone, Distort, Higher, Width; one knob moves it between deeper and higher (said and shown).

## In Rohil's setup

```
rick-rubin serum set init osc_a.octave=1 osc_b.on=on osc_b.unison=8 sub.on=on sub.shape=Triangle \
  filter_1.on=on filter_1.type="MG Low 12" filter_1.cutoff_hz=600 filter_1.res=60 env_1.attack_ms=280 \
  lfo_1.rate="2 bar" lfo_1.mode=Envelope lfo_1.shape=0:1,0.6:0.85,1:0 \
  global.mono=on global.legato=on global.glide_ms=60 global.glide_always=on global.bend_up=1 global.bend_down=-5 \
  --mod lfo_1:filter_1.cutoff_hz:30 --save big-brass --project <dir>
```

Cutoff, resonance, glide time and depth are ours. Parsed on 2026-11-20 (not heard): attack +210 ms against
init, `slow-attack`, `wide`, and `wide-low-end`: so cut the track below 150 Hz or lower `osc_b.width`. Tune
with `rick-rubin serum ab big-brass --try "filter_1.res=40" --try "filter_1.cutoff_hz=900"`.

## How to check it

`rick-rubin serum describe big-brass --note D2 --bpm 128 --secs 4`: slow attack (200 ms or more), brightness
falling from early to late, a peak in the spectrum near the cutoff. `rick-rubin width`: side energy in the
mids and highs only.

## Why it works

A real brass note opens up as it gets louder and has a strong formant; a resonant low-pass on a saw copies
both. One clean voice keeps the pitch firm while the eight detuned ones supply the size.
