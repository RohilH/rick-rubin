---
title: A bright, dirty pluck doubling the melody: lo-fi colour first, reverb and delay outside the synth, short release
topic: sound-design
genres: [progressive house, any]
source: RYOS — Making Progressive House MAGIC | Studio Time with Ryos EP. 51 (https://youtu.be/srkGlUWW3pg?t=1283)
status: untested
---
## What it is
A pluck preset that plays the melody in the break, made "brighter and dirtier" with a lo-fi unit and given
space by insert effects instead of the synth's own. It then stays in the drop as the layer with character.

## When to use it
A break that needs the melody stated quietly before the lead stack arrives; a drop bed that sounds clean but
anonymous.

## How
1. Load a pluck in Serum on the melody ([21:23](https://youtu.be/srkGlUWW3pg?t=1283)).
2. Colour: Cymatics Origin, a vintage/lo-fi unit, on its "Bitcrush" preset; its large dial sets a resample
   frequency, with small saturation, movement and chorus amounts (shown,
   [22:15](https://youtu.be/srkGlUWW3pg?t=1335); knob values not readable).
3. Space: ValhallaVintageVerb, then ValhallaDelay, as inserts after the colour (shown,
   [23:00](https://youtu.be/srkGlUWW3pg?t=1380)).
4. Turn off the reverb and delay inside the synth preset and shorten the amp release, so the notes are tight
   and all the space comes from the inserts (said, [23:01](https://youtu.be/srkGlUWW3pg?t=1381)).
5. Pump last, with its mix automated per section (a "Kickstart 2 (Pluck) mix level" clip, shown 25:05).
6. Try it in the drop before deciding it is a break sound. He keeps it there
   ([24:02](https://youtu.be/srkGlUWW3pg?t=1442)).

## In Rohil's setup
Serum 2 can do the pluck and the dirt in one patch (our values; settings go before the options):
`rick-rubin serum set init env_1.decay_ms=250 env_1.sustain_db=-120 env_1.release_ms=80 filter_1.on=on
filter_1.cutoff_hz=2500 fx.distortion.mode=Downsample fx.distortion.drive=60 fx.distortion.wet=100
--fx-add distortion --save dirty-pluck --project <dir>`. Or start from a preset (`rick-rubin serum search
pluck`) and take out its own space with `--fx-remove fx.reverb --fx-remove fx.delay`. Outside the synth,
Logic's Bitcrusher is the nearest thing to Origin's resample dial (lost: its tape wobble and chorus in one
box). Space: `rick-rubin logic insert Pluck "Valhalla Supermassive"` or ChromaVerb, then Stereo Delay (read
names with `rick-rubin logic devices` first). Pump: `rick-rubin logic insert Pluck "Kickstart 2" Mix=0.5`.

## How to check it
`rick-rubin serum ab <preset> --note C4 --try "fx.distortion.wet=0"`: the dirty version should be brighter
and richer with the same decay. Run here on 2026-11-20 with the patch above: 830 to 1056 Hz centroid (+27 %),
harmonics 9 to 32, decay unchanged, flagged noisy; at drive 30 and wet 50 nothing moved, so the unit has to be
pushed. The aliasing also shifted the pitch reading, so check tuning on a bounce (`rick-rubin notes`). Then an
audition file for Rohil, clean against dirty: nothing here has been judged by ear.

## Why it works
Sample-rate reduction adds harsh upper partials that cut through pads at low level, and dry short notes into
a shared reverb and delay keep the rhythm of a fast melody readable.
