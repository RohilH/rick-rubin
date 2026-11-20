---
title: A rolling melodic-house bass: short dark pluck, held roots, an arpeggiator at eight notes a bar
topic: bass
genres: [progressive house, tech house]
source: Alex Rome — How To Get That 'Pro Sound' (as a beginner producer) (https://youtu.be/Uazkku5yuM8?t=427)
status: untested
---
## What it is
The trance-leaning bass of melodic house (his reference is John Summit): one root per chord, played by a short, dark
filter pluck that an arpeggiator re-strikes on every eighth note. One held note in the piano roll becomes a steady
pulse of eight per bar.

## When to use it
Melodic and progressive house drops and builds where the bass should drive without having a tune of its own. Not for
tech house grooves that need syncopation (see `../melody/alex-rome-c-bass-melody-root-rhythm-then-resolve.md`).

## How
1. Notes: the bottom note of each chord, held for the chord's length, in the 40 to 80 Hz octave (said,
   [6:04](https://youtu.be/Uazkku5yuM8?t=364); `alex-rome-c-bass-octave-by-the-analyzer-40-80hz.md`).
2. Sound: Serum init saw, filter on, MG Low 24, cutoff closed, ENV 2 on the cutoff: the same pluck he uses for leads
   (said; shown [7:22](https://youtu.be/Uazkku5yuM8?t=442)).
3. "Shorten it up, warm it up": a shorter envelope decay and a lower cutoff than the lead version (said,
   [7:27](https://youtu.be/Uazkku5yuM8?t=447); no figures readable).
4. Add an arpeggiator as a MIDI effect at a rate of eight triggers per bar (said). Shown at
   [7:44](https://youtu.be/Uazkku5yuM8?t=464): Logic's Arpeggiator, Rate 1/8, direction up.
5. With one note held, the arpeggiator simply repeats it (inferred from the single-note regions at
   [8:28](https://youtu.be/Uazkku5yuM8?t=508)).
6. Then add passing notes where the melody rests (`alex-rome-c-bass-passing-notes-in-the-melody-gaps.md`).
7. No sidechain is shown in this video; with a kick on every beat, every other bass note lands on a kick, so it needs
   ducking (inferred).

## In Rohil's setup
```
rick-rubin serum set init filter_1.on=on "filter_1.type=MG Low 24" filter_1.cutoff_hz=300 env_2.decay_ms=400 \
    env_2.sustain_pct=0 osc_a.rand_phase=0 global.mono=on --mod env_2:filter_1.cutoff_hz:35 \
    --save pluck-bass-8ths --project <dir>
```
Cutoff, decay and amount are ours. The arpeggiator: in Logic it is the Arpeggiator in the track's MIDI FX slot, set by
Rohil by hand (the bridge inserts audio effects). In `song.py` write the eighth notes out: rick-rubin does not emulate
an Arpeggiator offline, so written notes are what the score, lint and eval can see. Then `rick-rubin logic insert Bass
"Kickstart 2" Mix=0.8`.

## How to check it
One offline render of the patch here (G#0, 0.5 s): decay 130 ms, brightness falling from 111 to 74 Hz, energy 71 %
sub, 25 % bass, 4 % low-mid, side energy 0. `rick-rubin hits` on a bass bounce: eight even steps per bar, the on-beat
ones lower after ducking. `reference compare` against PH-prefixed references for low-end share and pump.

## Why it works
Constant eighths under long chords give forward motion that the harmony alone lacks, and a short pluck leaves silence
between notes, so the low end stays clean at speed (inferred).
