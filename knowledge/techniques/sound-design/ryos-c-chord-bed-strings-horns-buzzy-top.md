---
title: A supporting chord bed in layers: strings, a horn-like atmosphere patch, and a clean buzzy layer for the top
topic: sound-design
genres: [progressive house]
source: RYOS — Making Progressive House MAGIC | Studio Time with Ryos EP. 51 (https://youtu.be/srkGlUWW3pg?t=258)
status: untested
---
## What it is
The chords behind the lead are their own small stack. Each layer covers one register and the low mids are
cut, because the bass already lives there. All layers sit on one chord group so they can be filtered together.

## When to use it
After the melody and a first bass exist and the chords are still "plain" on a piano; when a drop has lead and
bass but no body or top between them.

## How
1. Strings first: a string-pad preset with its attack made much faster, so chord changes speak on time
   (Spire "PD Virus Strings", shown [5:00](https://youtu.be/srkGlUWW3pg?t=300); said 4:38).
2. Finalise the voicing on this sound, not on the piano. He decides which note sits on top of each chord so
   the tops form a slow line of their own (said, [5:21](https://youtu.be/srkGlUWW3pg?t=321)).
3. Cut the low mids of the pad and of the bass, since both are heavy there; the pad can lose its lows too
   (said, [5:44](https://youtu.be/srkGlUWW3pg?t=344); an EQ on the strings, shown 6:12; amounts not readable).
4. Second layer: a horn-like atmosphere preset playing the same chords (Analog Lab V "Ambi Horns", shown
   [8:40](https://youtu.be/srkGlUWW3pg?t=520)). With it in, an atmosphere bed became redundant and was muted.
5. Third layer, added with the drop in mind: the group needs more high end, and the mood is not very
   electronic, so he looks for something "buzzy but clean" (said,
   [11:35](https://youtu.be/srkGlUWW3pg?t=695)). A Serum chord preset, low cut near 155 Hz at 12 dB/oct
   (shown, [12:28](https://youtu.be/srkGlUWW3pg?t=748)).
6. For the break he later adds one more chord sound an octave down ([23:41](https://youtu.be/srkGlUWW3pg?t=1421)).

## In Rohil's setup
Serum 2 for all three. Both commands ran on this Mac (2026-11-20); the values are our starting guesses:
- Strings: `rick-rubin serum set init osc_a.unison=5 osc_a.detune=0.15 filter_1.on=on filter_1.cutoff_hz=3000
  env_1.attack_ms=40 env_1.release_ms=400 --save chord-strings --project <dir>`, or a string preset
  (`rick-rubin serum search strings`) with `env_1.attack_ms` lowered.
- Buzzy top (settings before options): `rick-rubin serum set init osc_a.unison=7 osc_a.detune=0.12
  env_1.attack_ms=2 fx.utility.hpf=155 --fx-add utility --save chord-buzz --project <dir>`. Measured against
  init: brightness +120 %, bass share -56 points, flagged very-wide.
- Horn layer: no Analog Lab; a brass pad from `rick-rubin serum search horn`, or a Logic Library patch.
Low-mid cut with Channel EQ on each layer; the chord bus is made by hand in Logic.

## How to check it
`rick-rubin spectrum <dir> strings.wav horns.wav buzz.wav bass.wav` on bounced layers: each chord layer peaks
in a different band, the buzzy one has nothing under about 150 Hz, and 200 to 500 Hz on the chord group sits
below the bass. `rick-rubin width <dir> chords.wav`: wide above 1 kHz, low band centred.

## Why it works
Three plain sounds in three registers read as one large, clear chord, where one thick pad would fill the low
mids and mask bass and lead.
