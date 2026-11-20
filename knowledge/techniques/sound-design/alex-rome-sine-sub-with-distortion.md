---
title: Make a pure sine sub audible with distortion
topic: sound-design
genres: [tech house, bass house, progressive house]
source: Alex Rome — How To Make Any Sound From Scratch (https://youtu.be/p1-WmITJqBk?t=888)
status: untested
---
## What it is
A sine wave played low is a "silent sub": felt on big speakers, absent on phones and laptops. Distortion adds
harmonics above it, so the same note is heard everywhere and gains character.

## When to use it
Whenever the bass is, or sits on, a sine: a sub layer, an 808-style line, a deep house bass. And whenever a bass
disappears on small speakers.

## How
1. Sine in OSC A, unison 1, filter open or off (shown [14:32](https://youtu.be/p1-WmITJqBk?t=872)).
2. Know the limit: a sine has no edges, so it makes one narrow band with nothing above it (said,
   [14:26](https://youtu.be/p1-WmITJqBk?t=866)).
3. Add distortion, in the synth's effects or in the DAW (said). Serum FX: Distortion, type Tube, filter set to post,
   freq 425, Q 1.9 (shown [15:45](https://youtu.be/p1-WmITJqBk?t=945); drive and mix are small unreadable knobs).
4. Go through every distortion type you have, overdrives and saturators included, and listen to what each does to
   the same sub (said, [16:05](https://youtu.be/p1-WmITJqBk?t=965)). He ends on a diode type (said,
   [16:41](https://youtu.be/p1-WmITJqBk?t=1001); settings not visible).
5. Watch the result on an analyzer: new peaks appear above the fundamental (shown
   [16:35](https://youtu.be/p1-WmITJqBk?t=995), Channel EQ analyzer).

## In Rohil's setup
```
rick-rubin serum set init osc_a.wt_pos=45 fx.distortion.mode=Diode1 fx.distortion.drive=40 --fx-add distortion \
    --save sine-sub-diode --project <dir>
```
Put the `KEY=VALUE` settings before `--fx-add`. `fx.distortion.mode=Tube` is his first type. Compare types with
`rick-rubin serum ab`, one `--try` per mode. Outside Serum: Logic's Overdrive, Distortion II or ChromaGlow after the
instrument; read their parameter names with `rick-rubin logic devices "ChromaGlow"` first.

## How to check it
`rick-rubin serum describe ... --note G0`. One render here: the bare sine has 1 harmonic and 99 % of its energy in
the sub band; Tube at drive 40 gave 2 harmonics; Diode1 at drive 40 gave 6, odd-heavy, with 7 % in the bass band and
2 % in the low-mid. More harmonics and more share above the sub band is the direction. Then the phone test: an
audition file Rohil plays on his laptop speakers.

## Why it works
Distortion bends the sine's shape, and any bend is new harmonics at multiples of the note. The ear rebuilds the
missing fundamental from those harmonics on speakers that cannot play it (the second sentence is inferred).
