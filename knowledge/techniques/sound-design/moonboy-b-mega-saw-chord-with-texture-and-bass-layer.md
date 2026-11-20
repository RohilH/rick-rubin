---
title: A "mega saw" chord: octave-doubled notes, a texture layer inside the synth, lows handed to a root-note bass
topic: sound-design
genres: [progressive house, bass house]
source: MOONBOY — HOW TO MELODIC HOUSE (Knock2, Kx5, John Summit) (https://youtu.be/woNtFzXYB5Y?t=311)
status: untested
---
## What it is

How he makes the big chord sound that the break rises into. Four moves on top of an ordinary supersaw: play
every chord in two octaves at once, soften the envelope, put a pad or vocal texture in the synth's noise slot
so it follows the keys, and cut the lows so a separate bass layer on the root notes can own them.

## When to use it

For the chord entry after an eight-bar pluck section, and for a melodic drop. The supersaw itself is in
`sound-design/moonboy-detuned-saw-pad`; this card is what makes it "mega".

## How

1. Two saw oscillators, both with unison: up to 16 voices on the first; the second an octave higher and
   mixed a little lower (said, [5:11](https://youtu.be/woNtFzXYB5Y?t=311)).
2. Double the MIDI: select all chord notes, copy them and move the copy down an octave, so every chord is
   stacked in two octaves (said, [5:51](https://youtu.be/woNtFzXYB5Y?t=351)).
3. Amp envelope: a little attack so it is smooth, some release; add a filter (said; no numbers).
4. Texture: load a pad or vocal noise into Serum's noise oscillator, switch its keyboard tracking on, turn
   it up, and raise the polyphony because of all the voices (said,
   [6:13](https://youtu.be/woNtFzXYB5Y?t=373)). The samples are from his own pack.
5. Before adding bass, high-pass the chord with an EQ (said, [6:55](https://youtu.be/woNtFzXYB5Y?t=415)).
6. Bass layer: a new Serum from init playing only the progression's root notes, an octave or two down, with
   a low-pass filter and a second oscillator for some mids (said,
   [7:15](https://youtu.be/woNtFzXYB5Y?t=435)).

Nothing in this section is readable off the screen; all of it is said.

## In Rohil's setup

```
rick-rubin serum set init osc_a.unison=16 osc_a.detune=0.2 osc_b.on=on osc_b.octave=1 osc_b.unison=8 \
  osc_b.detune=0.2 env_1.attack_ms=30 env_1.release_ms=400 filter_1.on=on filter_1.type="MG Low 12" \
  filter_1.cutoff_hz=6000 noise.on=on noise.pitch_track=on global.voices=32 --save mega-saw --project <dir>
```

Voice count on B, detune, envelope times and cutoff are ours. Parsed on 2026-11-20 (not heard): `very-wide`
and `wide-low-end`, attack +290 ms. Choosing the noise sample is done in Serum's window. Then
`rick-rubin logic insert Chords "Channel EQ"` with a low cut near 150 to 200 Hz, and the bass layer on its
own track (see `bass/ryos-bass-in-layers-sub-harmonics-mid`).

## How to check it

`rick-rubin width <dir> --bars A-B`: side energy high in mids and highs, nothing wide below 150 Hz after the
low cut. `rick-rubin spectrum <dir> --tracks Chords "Chord Bass"`: the curves cross near the low-cut point.
`rick-rubin score`: each chord's notes appear in two octaves.

## Why it works

Doubling in octaves fills the spectrum the way more instruments would; a keytracked texture adds movement
that plain saws lack; and taking the lows out of sixteen detuned voices stops them smearing the bass.
