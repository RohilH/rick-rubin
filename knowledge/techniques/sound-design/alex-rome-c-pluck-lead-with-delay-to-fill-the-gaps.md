---
title: A sparse melody on a pluck: quarter-note delay and hall reverb fill the gaps, layers add character
topic: sound-design
genres: [progressive house, tech house, any]
source: Alex Rome — How To Get That 'Pro Sound' (as a beginner producer) (https://youtu.be/Uazkku5yuM8?t=46)
status: untested
---
## What it is
A melody with long rests is moved from a held supersaw to a filter-envelope pluck, and the rests are filled with the
pluck's own echoes and reverb so the energy never drops to zero. Two more layers on the same notes make the common
sound less generic.

## When to use it
A lead that sounds "powerless" or dated; a melody whose notes are fine but which leaves holes. He considers a supersaw
hard to use well and a pluck easier and more current.

## How
1. Keep the notes. Replace the sound with the pluck: Serum init, saw (shown [1:08](https://youtu.be/Uazkku5yuM8?t=68):
   "MB Saw"), MG Low 24, ENV 2 on the cutoff (see `alex-rome-filter-envelope-pluck.md` for values).
2. Delay inside the synth "to fill in the long gaps between notes" (said, [1:28](https://youtu.be/Uazkku5yuM8?t=88)).
   Shown at [1:52](https://youtu.be/Uazkku5yuM8?t=112): tempo-synced, 1/4 left and right, normal mode (not ping-pong),
   delay filter centred on 849 Hz with Q 6.8.
3. Reverb after the delay "to create a space" (said). Shown: Hall. Size, decay and mix are unlabelled knobs.
4. OTT after the synth to raise the echoes and tail in the gaps (said, [1:53](https://youtu.be/Uazkku5yuM8?t=113);
   Depth 64 % shown). See `../mixing/alex-rome-c-ott-before-or-after-reverb.md`.
5. Compare with the original sound: the test is "more consistent energy" (said,
   [2:13](https://youtu.be/Uazkku5yuM8?t=133)).
6. Layer for uniqueness: the same notes on a different-sounding preset, his with a guitar-like attack that speaks in
   the gaps (said, [2:54](https://youtu.be/Uazkku5yuM8?t=174)); and the original supersaw kept as a third layer (said,
   [3:05](https://youtu.be/Uazkku5yuM8?t=185)).
7. Delay feedback and mix are not readable; start low (ours).

## In Rohil's setup
```
rick-rubin serum set init filter_1.on=on "filter_1.type=MG Low 24" filter_1.cutoff_hz=133 env_2.decay_ms=1000 \
    env_2.sustain_pct=0 fx.delay.wet=30 fx.delay.feedback=40 fx.delay.freq=849 fx.reverb.type=Hall \
    fx.reverb.wet=25 --mod env_2:filter_1.cutoff_hz:45 --fx-add delay --fx-add reverb --save pluck-lead \
    --project <dir>
```
Wet, feedback, cutoff and amount are ours. Set the delay to 1/4 in Serum's window (`fx.delay.time_l`,
`fx.delay.time_r`; check the unit with `rick-rubin serum params --group fx`). Then `rick-rubin logic insert Lead "OTT"
Depth=60`. Nexus is not his: pick the contrasting layer with `rick-rubin serum search` (a guitar or keys pluck) and
`ryos-layer-by-contrast.md`.

## How to check it
One offline render here (C3, 2 s, 128 BPM): the dry pluck decays in 925 ms with a 25 ms release; with delay and
reverb, decay 1610 ms, release 1510 ms, level movement 10.5 dB (the echoes). In the track, bounce the lead alone: the
level between phrases should no longer fall to silence (`rick-rubin hits` shows the steps between notes).

## Why it works
Echoes at a note value repeat the melody's own pitches in time with the track, so the gaps are filled with material
that already belongs; a held sound fills them too but hides the rhythm (inferred).
