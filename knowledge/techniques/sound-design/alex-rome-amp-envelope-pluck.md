---
title: Amp-envelope pluck, and the same idea as a sine arp
topic: sound-design
genres: [progressive house, tech house, any]
source: Alex Rome — How To Make Any Sound From Scratch (https://youtu.be/p1-WmITJqBk?t=322)
status: untested
---
## What it is
A pluck made with nothing but ENV 1: sustain all the way down, so the length of every note is the decay time. On a
ten-voice saw it is a bright stab; on a single sine with an arpeggiator it is a soft melodic pattern.

## When to use it
Rhythmic chords, arps and top-line plucks where the brightness should stay constant through the note. For a pluck
that gets darker as it fades, use the filter-envelope pluck card instead.

## How
1. Start from the filtered saw pad: saw, MG Low 24, unison 10 (shown [6:24](https://youtu.be/p1-WmITJqBk?t=384)).
2. OSC A up one octave (shown [6:24](https://youtu.be/p1-WmITJqBk?t=384): OCT +1).
3. ENV 1: attack 1 ms, hold 0, decay 275 ms, sustain −inf, release 15 ms (shown
   [6:24](https://youtu.be/p1-WmITJqBk?t=384)).
4. Length is now the decay knob: sustain off and decay 5.35 s is a long fade (shown
   [10:15](https://youtu.be/p1-WmITJqBk?t=615)).
5. Punch with body: short decay to a middle sustain (shown [9:35](https://youtu.be/p1-WmITJqBk?t=575): attack 29 ms,
   decay 1.1 s, sustain −11.8 dB, release 111 ms).
6. Go back to the oscillator with the envelope set: sine up an octave is "spooky", square is hollow (said,
   [10:31](https://youtu.be/p1-WmITJqBk?t=631)).
7. Sine arp: sine, sustain off, short decay, unison 1, an arpeggiator MIDI effect in front (said
   [11:17](https://youtu.be/p1-WmITJqBk?t=677); shown [11:45](https://youtu.be/p1-WmITJqBk?t=705): Logic's
   Arpeggiator, rate 1/8 in the frame, note order up).

## In Rohil's setup
```
rick-rubin serum set init osc_a.unison=10 osc_a.octave=1 env_1.attack_ms=1 env_1.decay_ms=275 \
    env_1.sustain_db=-120 env_1.release_ms=15 --save amp-pluck --project <dir>
```
Sine arp: `osc_a.wt_pos=45 osc_a.unison=1 osc_a.octave=1` with the same envelope. Logic's Arpeggiator is not set
from rick-rubin: in a `song.py` the arpeggio is written out note by note; in his own project he adds the MIDI effect
by hand.

## How to check it
`rick-rubin serum describe`: one render here on C3 gave decay 260 ms, sustain −90 dB, the word `plucky`, and
brightness unchanged from start to end of the note (1580 to 1583 Hz), which is what separates it from a filter
pluck. Audition file and verdict still to do.

## Why it works
With sustain at zero the envelope is a fixed-length fade that restarts on every note, so rhythm comes from the notes
and tone stays put (inferred).
