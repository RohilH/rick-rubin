---
title: Swells and repeating movement from the same filter patch, ENV 2 attack or an LFO on the cutoff
topic: sound-design
genres: [progressive house, tech house, any]
source: Alex Rome — How To Make Any Sound From Scratch (https://youtu.be/p1-WmITJqBk?t=1325)
status: untested
---
## What it is
Two changes to the filter-envelope pluck that turn it into other sounds. Give ENV 2 an attack and some sustain and
the filter swells open and stays: a soft pad or lead. Swap ENV 2 for an LFO and the filter keeps opening and closing
in time: a pulsing, moving part.

## When to use it
The swell for breakdown chords and long notes; the LFO version for rhythmic motion on held chords or a bass without
writing more notes, as in the one-chord sections of tech house.

## How
1. Swell, starting from the filter-envelope pluck: lengthen ENV 2's attack and raise its sustain (said "soft
   attack", [22:33](https://youtu.be/p1-WmITJqBk?t=1353); shown [22:38](https://youtu.be/p1-WmITJqBk?t=1358) with
   attack about 235 ms, decay 1.12 s, sustain 59 %, unison 6; shown [23:10](https://youtu.be/p1-WmITJqBk?t=1390)
   with attack 41 ms, same decay and sustain).
2. Add an echo: a 1/4-note delay after the synth (shown [22:38](https://youtu.be/p1-WmITJqBk?t=1358): Baby Audio
   Comeback Kid, time 1/4).
3. Movement: remove ENV 2 from the cutoff and drag LFO 1 onto it instead; same job, but it never stops (said,
   [22:45](https://youtu.be/p1-WmITJqBk?t=1365)).
4. LFO rate 1/8, synced; he reshapes the LFO by hand, a raised triangle then a ramp (shown
   [23:10](https://youtu.be/p1-WmITJqBk?t=1390), [23:25](https://youtu.be/p1-WmITJqBk?t=1405); the points are not
   readable), and tries a triangle wave in OSC A while it moves (shown
   [23:25](https://youtu.be/p1-WmITJqBk?t=1405)).
5. His first demonstration of the idea: LFO 1 dragged onto OSC A level, so the volume knob turns itself (said
   [17:42](https://youtu.be/p1-WmITJqBk?t=1062); the LFO is at rate 1/4 in the frame at
   [17:52](https://youtu.be/p1-WmITJqBk?t=1072)).

## In Rohil's setup
Swell:
```
rick-rubin serum set init osc_a.unison=6 filter_1.on=on "filter_1.type=MG Low 24" filter_1.cutoff_hz=133 \
    env_2.attack_ms=235 env_2.decay_ms=1120 env_2.sustain_pct=59 --mod env_2:filter_1.cutoff_hz:32 \
    --save swell --project <dir>
```
Movement: replace the ENV 2 settings and `--mod` with `lfo_1.rate=1/8 lfo_1.shape=Basic/Triangle --mod
lfo_1:filter_1.cutoff_hz:45`, rendered with `--bpm` at the song's tempo. Echo: no Comeback Kid here; use Serum's
delay (`fx.delay.wet=25 fx.delay.feedback=35 --fx-add delay`) or Logic's Tape Delay at 1/4; its tone controls are
what is lost. Amounts are inferred, as on the pluck card.

## How to check it
`rick-rubin serum describe ... --secs 2 --bpm 123`. One render each here: the swell measured attack 230 ms, sustain
−5.2 dB, words `slow-attack sustained`; the LFO version measured movement at 4.10 Hz, 0.50 beats at 123 BPM, word
`moving`. The movement rate in beats should equal the LFO division.

## Why it works
The filter is the same; only the shape of what turns the cutoff changes. An envelope runs once per note, an LFO
loops, so one patch covers plucks, swells and pulses (said in substance,
[22:50](https://youtu.be/p1-WmITJqBk?t=1370)).
