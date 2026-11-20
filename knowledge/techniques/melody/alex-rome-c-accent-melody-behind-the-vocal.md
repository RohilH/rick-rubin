---
title: Accent melody: sparse, short notes far back in reverb, behind the vocal and chords
topic: melody
genres: [tech house, progressive house, bass house, any]
source: Alex Rome — 5 Melody Styles Every Hit Song Uses (https://youtu.be/cjyEdyEWXbQ?t=544)
status: untested
---
## What it is
A background melody whose job is atmosphere. It is not the hook and nobody should be able to sing it. Because it is
not carrying the song, it has no rules: wandering pitches, uneven lengths, as much reverb as you like.

## When to use it
A section with a vocal and chords (or a bass groove and a vocal) that is complete on paper and plain to listen to. His
examples: behind the vocal in John Summit's "Where You Are"; a guitar that enters halfway through the verse of Chris
Lake's "Ease My Mind" ([12:45](https://youtu.be/cjyEdyEWXbQ?t=765)).

## How
1. Sound: a brief "poke" with a fast decay and no sustain (said, [10:02](https://youtu.be/cjyEdyEWXbQ?t=602)). Shown
   at [10:18](https://youtu.be/cjyEdyEWXbQ?t=618): a saw at unison 2 with a square an octave up, MG Low 12 with the
   cutoff fairly open, amp attack 0.5 ms, decay 145 ms, sustain −46.8 dB, release 15 ms.
2. Put an arpeggiator before it in chord-trigger mode, so every held note is re-struck at a steady rate (said). Shown
   at [10:42](https://youtu.be/cjyEdyEWXbQ?t=642): style Chord Trigger, rate 1/16, Hold on, gate 99 %.
3. Hold down notes that "venture off": scattered pitches from the key, held for uneven lengths, with gaps (said,
   [10:40](https://youtu.be/cjyEdyEWXbQ?t=640)). It is improvised, then kept if pretty.
4. Drown it: a shimmer reverb first (said). Shown at [11:42](https://youtu.be/cjyEdyEWXbQ?t=702), ValhallaShimmer: mix
   0.33, shift 12, feedback 0.211, diffusion 0.910, size 0.50, low cut 10, high cut 8000, colour bright.
5. Stack one or two more reverbs after it; for the extreme version go fully wet and cut the top off (said,
   [11:55](https://youtu.be/cjyEdyEWXbQ?t=715)).
6. It can enter partway through a section as the "something new" (inferred from the Chris Lake example).

## In Rohil's setup
```
rick-rubin serum set init osc_a.unison=2 osc_b.on=on osc_b.octave=1 osc_b.wt_pos=128 filter_1.on=on \
    "filter_1.type=MG Low 12" filter_1.cutoff_hz=3000 env_1.decay_ms=145 env_1.sustain_db=-46.8 \
    --save accent-poke --project <dir>
```
(cutoff 3000 is our reading of a knob; `osc_b.wt_pos=128` is the square of the default table.) He uses Ableton's
Arpeggiator. In Logic the nearest is the Arpeggiator MIDI effect's grid pattern with Chord switched on per step (not
verified here; Rohil sets MIDI effects by hand). The same result is the notes written as repeated sixteenths, which is
what a `song.py` part does anyway. Rohil has no shimmer reverb: Valhalla Supermassive at high feedback gives the wash
without the octave-up shimmer; ChromaVerb is the other option. What is lost is the rising octave in the tail.

## How to check it
One offline render of the patch here (C4): decay 145 ms, sustain −46 dB, 89 % of its energy in the mid band, nothing
in the lows. In the mix, `rick-rubin compare` with and without the layer: loudness nearly unchanged, a little more
high and side energy. If the vocal's band (1 to 4 kHz) rises audibly, turn it down or darken it.

## Why it works
Short notes leave the foreground alone, and the long reverb turns them into a moving texture, so the section gains
motion and depth without a second thing to follow (inferred; he says it "livens up the atmosphere").
