---
title: Any synth sound in three decisions: wavetable, filter, movement
topic: sound-design
genres: [any]
source: MOONBOY — HOW TO TECH HOUSE | Full Tutorial (Odd Mob, Chris Lake, Mau P) (https://youtu.be/JqKaSvHImB0?t=427)
status: untested
---
## What it is
His working model of a synth patch. Pick the raw wave (character), set a filter (how deep or bright), then
make the filter move with an LFO whose shape, rate and trigger mode decide whether you get a wobble, an
offbeat stab or a one-shot pluck. He builds every bass in the video from these three moves.

## When to use it
When starting a sound from Serum's init patch, and as the order in which to read someone else's preset:
which wave, which filter, what moves the filter.

## How
1. **Wavetable.** Saw is fuzzy, square is more powerful, sine and triangle are soft (said,
   [7:27](https://youtu.be/JqKaSvHImB0?t=447)). He stays on the saw: Default Shapes, position 1 (shown).
2. **Filter.** Low-pass for a deep sound, high-pass for a thin one with no bass; resonance for a nasal edge
   (said, [7:49](https://youtu.be/JqKaSvHImB0?t=469)). MG Low 18 while demonstrating, MG Low 12 in the
   finished bass (shown).
3. **Movement.** Drag LFO 1 onto the cutoff, lower the cutoff, and set the depth on the small ring next to
   the knob (said, [8:09](https://youtu.be/JqKaSvHImB0?t=489)). With the default triangle at 1/4 this is a
   wobble (shown at [8:25](https://youtu.be/JqKaSvHImB0?t=505)).
4. **Shape the LFO.** Redrawn as a curve that starts at the top and falls, it becomes a stab on every LFO
   cycle (shown at [9:16](https://youtu.be/JqKaSvHImB0?t=556)); a faster rate gives more stabs per bar.
5. **Envelope mode.** Switched to Envelope, the LFO plays once per note and stops, so the rhythm comes from
   the notes you write, not from the LFO (said and shown at [9:38](https://youtu.be/JqKaSvHImB0?t=578)).

## In Rohil's setup
Serum 2 is the synth he uses, so this maps one to one:

```
rick-rubin serum ab init --note E1 --bpm 130 \
  --try "osc_a.wt_pos=64" --try "filter_1.on=on filter_1.type='MG Low 12' filter_1.cutoff_hz=150" \
  --try "filter_1.on=on filter_1.type='High 12' filter_1.cutoff_hz=400"
rick-rubin serum set init filter_1.on=on filter_1.cutoff_hz=150 lfo_1.shape="Basic/Saw Down Curved" \
  lfo_1.rate=1/8 lfo_1.mode=Envelope --mod lfo_1:filter_1.cutoff_hz:40 --save stab --project <dir>
```

`rick-rubin serum shapes` lists drawn LFO shapes; a shape can also be written as points (`lfo_1.shape=0:1,1:0`).

## How to check it
`rick-rubin serum describe <preset> --note E1 --bpm 130`: with the LFO on the cutoff, "bright early→late"
must fall across the note and the word `closes` (or `plucky`) appear; in a free-running LFO, "movement"
reports a rate in beats that should equal the LFO rate. Without the mod, early and late are equal.

## Why it works
A static filtered wave is a tone; the ear hears "a bass sound" in how the brightness changes over each
note. One modulator on the cutoff gives that change, and its shape and trigger mode set the rhythm of it.
