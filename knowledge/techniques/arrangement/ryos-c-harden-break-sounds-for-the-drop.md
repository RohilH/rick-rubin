---
title: Copy the break into the drop, add the kick, then harden whatever now sounds too soft
topic: arrangement
genres: [progressive house, bass house, any]
source: RYOS — Making Progressive House MAGIC | Studio Time with Ryos EP. 51 (https://youtu.be/srkGlUWW3pg?t=755)
status: untested
---
## What it is
His way from a finished break to a first drop: duplicate the parts, put a kick and sidechain under them, and
listen for what the kick exposes. Sounds that suit a dreamy "hands up" section are usually too soft for a drop,
so each group gets a drop version while the break keeps the original.

## When to use it
The break sounds good and the drop is empty. Also when a drop sounds like "the break with drums".

## How
1. Copy every break part to the drop region ([12:35](https://youtu.be/srkGlUWW3pg?t=755)).
2. Kick first, and sidechain on everything at once ([13:15](https://youtu.be/srkGlUWW3pg?t=795)).
3. Listen and say what is wrong. His verdict: still good sounds, but too soft for a drop (said,
   [14:00](https://youtu.be/srkGlUWW3pg?t=840)).
4. Drums before synths: fills, a tight ride, claps, a shaker loop, then an exciter (Fresh Air) because the
   drums still lack sparkle ([14:21](https://youtu.be/srkGlUWW3pg?t=861) to 16:31).
5. Bass: compress and distort the mid bass hard and blend in a metallic, tinny effect at a lowered mix; give
   the fuzzy layer more distortion until it growls (said, [16:51](https://youtu.be/srkGlUWW3pg?t=1011);
   Decapitator after CamelCrusher, shown 17:42). A third, very distorted high-mid bass only if that is not enough.
6. Chords: take the piano out, it suits a break ([17:58](https://youtu.be/srkGlUWW3pg?t=1078)); the chord
   group needs more top, which he planned earlier by adding a clean, buzzy chord layer
   ([11:35](https://youtu.be/srkGlUWW3pg?t=695)); then more squeeze on the chord group (18:19).
7. The break keeps its soft versions: he changes the sounds "for the drop" and leaves the break as it is (said).
8. Test break-only sounds in the drop before discarding them: the pluck made for the break stays in the drop
   because it gives the bed character ([24:02](https://youtu.be/srkGlUWW3pg?t=1442)).

## In Rohil's setup
In Logic a "drop version" is a second track: `rick-rubin logic add-serum "<preset>" --name "Bass mid drop"`
with the changed values, or the same preset plus inserts on the copy. Drive: Logic 11's ChromaGlow or Overdrive
in place of Decapitator and CamelCrusher (lost: their exact colour), or inside Serum
`rick-rubin serum set "<preset>" fx.distortion.drive=60 --fx-add distortion --save bass-mid-drop --project
<dir>` (leave out `--fx-add` if the preset already has the unit). Squeeze: OTT,
which he owns (`rick-rubin logic insert "Chords drop" OTT`). Sparkle: Logic's Exciter or ANIMATE on the drum
bus. Pump: `rick-rubin logic insert "Chords drop" "Kickstart 2" Mix=0.6`.

## How to check it
Bounce both (`rick-rubin logic bounce bounces/break.wav --bars A-B`, same for the drop) and run
`rick-rubin compare <dir> bounces/break.wav bounces/drop.wav`: the drop should be louder, with a lower crest
and more energy in the high-mid and top bands. `rick-rubin spectrum <dir> bass_break.wav bass_drop.wav` on
bounced bass groups: the drop version carries more harmonics above 1 kHz. Then both bounces to Rohil.

## Why it works
A kick and a sidechain take away level and low-mid space, so sustained soft sounds shrink exactly where energy
is expected. Distortion and compression add harmonics and density that survive the pump.
