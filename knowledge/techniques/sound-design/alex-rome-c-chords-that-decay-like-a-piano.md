---
title: Give held chords a shape: sustain down, long decay, so each chord swells and fades like a piano
topic: sound-design
genres: [progressive house, tech house, any]
source: Alex Rome — How To Get That 'Pro Sound' (as a beginner producer) (https://youtu.be/Uazkku5yuM8?t=283)
status: untested
---
## What it is
A pad that holds at one level for the whole chord is "stiff". Lowering the amp envelope's sustain and lengthening its
decay makes each chord hit and then fall away over several seconds, which leaves room for the melody and gives the
progression a pulse of its own.

## When to use it
Chords that are correct and sit like a block; a melody that does not stand out over its chords; any pad in a section
that needs motion without adding a part. His line: in professional tracks the sounds are always moving.

## How
1. Notice the problem: the chord sound "doesn't change, it doesn't move" (said,
   [4:43](https://youtu.be/Uazkku5yuM8?t=283)).
2. On the amp envelope, reduce sustain and increase decay until it behaves more like a piano (said,
   [5:03](https://youtu.be/Uazkku5yuM8?t=303)).
3. His settings, shown at [5:18](https://youtu.be/Uazkku5yuM8?t=318) on his preset "PD Basic Pad": two "MB Saw"
   oscillators, unison 10 each, filter MG Low 12 with the cutoff well open, ENV 1 attack 11 ms, hold 0, decay 6.46 s,
   sustain at minimum (−inf dB), release 39 ms.
4. With sustain at minimum the decay time sets how long the chord lasts. At 128 BPM a two-bar chord is 3.75 s; a
   render here of the 6.46 s decay was about 15 dB down after 3 s, so each chord has mostly faded by the next (ours).
5. Play melody and chords together again: the falling chords "push the melody out" (said,
   [5:44](https://youtu.be/Uazkku5yuM8?t=344)).
6. Do the voicing first (third up an octave, a held note on top): see
   `../harmony/alex-rome-ten-progressions-overview.md`.

## In Rohil's setup
```
rick-rubin serum set init "osc_a.wavetable=Analog/MB Saw.wav" osc_a.unison=10 osc_b.on=on \
    "osc_b.wavetable=Analog/MB Saw.wav" osc_b.unison=10 filter_1.on=on "filter_1.type=MG Low 12" \
    filter_1.cutoff_hz=2000 env_1.attack_ms=11 env_1.decay_ms=6460 env_1.sustain_db=-120 env_1.release_ms=39 \
    --save decay-pad --project <dir>
```
Cutoff 2000 is our reading of a knob. On an existing pad only the last four keys matter. Scale `env_1.decay_ms` to the
chord length and tempo; compare with `rick-rubin serum ab "<pad>" --note C3 --try "env_1.decay_ms=3000
env_1.sustain_db=-120" --try "env_1.decay_ms=6460 env_1.sustain_db=-120"`. A sidechain pump adds movement at the beat
level; this adds it at the chord level, and the two combine.

## How to check it
One offline render here (C3 held 3 s): level falls 14.6 dB over the note (`sustain` column), measured decay about 1.7
s, wide (about 50 % side energy), words `punchy moving`. A static pad reads 0 dB of fall. In the track, `rick-rubin
reference compare`: the movement row should rise. Not yet heard by Rohil.

## Why it works
A sound that is loudest at its start and then recedes makes space in the bars where the melody plays, and the repeated
swell marks every chord change, so the harmony has rhythm (inferred).
