---
title: A progressive house lead stack built one role at a time, every layer playing chords with the melody on top
topic: sound-design
genres: [progressive house]
source: RYOS — Making Beautiful Progressive House | Studio Time with Ryos EP. 50 (https://youtu.be/WnZ7GN1tpek?t=612)
status: untested
---
## What it is
The drop lead as six presets, each chosen for one job, all playing the same MIDI: the four chord voicings with
the melody as the top line. Layers that repeat a quality already present are deleted on the spot.

## When to use it
Building the drop lead of a progressive house track once the melody exists. It is "the classic approach" in his
words (said, [10:12](https://youtu.be/WnZ7GN1tpek?t=612)).

## How
1. MIDI: chords in the octave of the piano part plus the melody above them, in one pattern for every layer
   (shown, [10:37](https://youtu.be/WnZ7GN1tpek?t=637)).
2. Base: a big string-like progressive lead (Nexus "Progressive Strings", said). Test the melody on it first.
3. Character: a guitar sound. Remove its harshness straight away: low cut, and a narrow dip at 3.1 kHz, Q about
   7.5 (shown, [11:14](https://youtu.be/WnZ7GN1tpek?t=674)).
4. Colour: an 80s-style synth lead. Shown at [12:32](https://youtu.be/WnZ7GN1tpek?t=752): two oscillators on the
   same analog saw-like table, fine-tuned -13 and +13 cents, a 12 dB low-pass, bright white noise mixed in.
5. Transient: a xylophone-like pluck, dropped an octave, kept quiet for extra attack and texture (said,
   [12:53](https://youtu.be/WnZ7GN1tpek?t=773)).
6. A plain "standard" synth layer to balance the unusual ones (said, [11:40](https://youtu.be/WnZ7GN1tpek?t=700)),
   and last a warm layer (said, [13:38](https://youtu.be/WnZ7GN1tpek?t=818)).
7. Reject by redundancy: a vocal-like preset goes because two layers already have that quality (said,
   [12:01](https://youtu.be/WnZ7GN1tpek?t=721)); a lead that sounds "goofy" on second listen is replaced (14:48).
8. Route all layers to one group (see `ryos-pg-lead-group-chain-without-squashing.md`).

## In Rohil's setup
Serum 2 for the synth layers: find candidates by role with `rick-rubin serum list --search strings` (then
`lead`, `pluck`, `warm`), widen with `rick-rubin serum search --like "<preset>"`, and compare three per role
with `rick-rubin serum describe "<preset>" --note D4`. The detuned
pair of step 4 from init: `rick-rubin serum set init osc_a.wavetable="Analog/Basic Mini" osc_a.fine_cents=-13
osc_b.on=on osc_b.wavetable="Analog/Basic Mini" osc_b.fine_cents=13 filter_1.on=on filter_1.type="MG Low 12"
noise.on=on --save eighties-lead --project <dir>` (table, cents and filter type as shown; everything else is
ours to set). Guitar and xylophone layers: Logic's Library or a Splice one-shot in Sampler. Put each on its own
track with `rick-rubin logic add-serum "<preset>" --name "Lead strings"` and so on.

## How to check it
Per layer, `rick-rubin serum describe`: the layers should differ in the rows that define their role (attack
time for the transient layer, brightness and tilt for the bright one, low-mid share for the warm one). On a
bounce of the group, `rick-rubin spectrum` should show no hole between about 200 Hz and 8 kHz, and muting any
one layer should change a visible band; if it changes nothing, the layer is redundant.

## Why it works
One preset rarely has body, bite, attack and width at once. Layers with different jobs add up to a full
spectrum, while layers with the same job only add level and mud.
