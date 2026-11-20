---
title: A "dance piano" unit: bright piano layered with a tight supersaw, stabbing the chords in the melody's rhythm
topic: sound-design
genres: [progressive house]
source: RYOS — Making Beautiful Progressive House | Studio Time with Ryos EP. 50 (https://youtu.be/WnZ7GN1tpek?t=1539)
status: untested
---
## What it is
An energy layer for the drop made of two instruments treated as one: a bright EDM piano and a short supersaw,
both playing the chord voicings re-struck on every note of the melody's rhythm, through one chain.

## When to use it
The leads are done but the supporting synths in the drop lack energy (said,
[25:39](https://youtu.be/WnZ7GN1tpek?t=1539)). He heard the idea while doing drums and noted it for later.

## How
1. Piano: a classic dance or EDM piano preset (Nexus "EDM Piano", shown
   [26:44](https://youtu.be/WnZ7GN1tpek?t=1604)). Layer a tight supersaw on the same MIDI and send both to one
   mixer channel (said, [26:01](https://youtu.be/WnZ7GN1tpek?t=1561); shown [27:48](https://youtu.be/WnZ7GN1tpek?t=1668)).
2. MIDI: take the lead pattern, rebuild the chords under it, and strike the full chord on each melody onset
   (shown, [27:04](https://youtu.be/WnZ7GN1tpek?t=1624)). He raises the chords an octave while working.
3. He is unsure about doubling the melody in this unit and removes it; the unit plays chords only (said,
   [27:07](https://youtu.be/WnZ7GN1tpek?t=1627)).
4. Chain, shown at [29:54](https://youtu.be/WnZ7GN1tpek?t=1794): a guitar-style tone shaper (Waves Maserati GTi),
   a distortion used for a slight bit-crush colour (said, [28:43](https://youtu.be/WnZ7GN1tpek?t=1723)), an
   exciter, an EQ, then a delay because it felt dull without "vibes" (said,
   [29:39](https://youtu.be/WnZ7GN1tpek?t=1779); ValhallaDelay preset "Instant Vibe"), and Kickstart 2 last.
5. He notes that a soft grand that is right for chords is wrong for a fast melody; a piano that must play the
   hook needs a brighter, shorter sound (said, [33:31](https://youtu.be/WnZ7GN1tpek?t=2011)).

## In Rohil's setup
Piano: a bright piano from Logic's Library on a software-instrument track (`rick-rubin logic add-instrument`),
chosen by ear. Supersaw in Serum 2; this ran without error on this Mac (2026-11-20), envelope numbers ours:
`rick-rubin serum set init osc_a.unison=7 osc_a.detune=0.2 env_1.decay_ms=300 env_1.sustain_db=-12
env_1.release_ms=60 --save tight-supersaw --project <dir>`, then `rick-rubin logic add-serum
<dir>/serum/presets/tight-supersaw.SerumPreset --name "Piano saw"`. Measured on G2: decay 170 ms, sustain
-10.5 dB, 55 % side in the low band, so high-pass it under the piano. Chain on the shared bus: Logic's Bitcrusher
lightly, Exciter, Channel EQ, Stereo Delay, and `rick-rubin logic insert "Dance Piano" "Kickstart 2" Mix=0.6`.
The Maserati plug-in has no equivalent here; a Channel EQ presence lift stands in.

## How to check it
`rick-rubin hits` on a bounce of the unit against the lead: same onsets. `rick-rubin spectrum` with the lead
group and the unit overlaid: the unit should add energy below the lead's top line without raising the 200 to
500 Hz band much (see `ryos-clear-200-500hz-pocket-for-the-lead.md`). In `rick-rubin reference compare`, the
drop's transient contrast should rise with the unit in.

## Why it works
Piano attacks give each chord a percussive front that pads and strings lack; the supersaw gives the stab the
sustain and width the piano lacks. Tied to the melody's rhythm, the unit reinforces the hook without a new part.
