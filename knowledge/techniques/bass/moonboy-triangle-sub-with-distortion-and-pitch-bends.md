---
title: A sub with its own rhythm: triangle wave, distortion, hard ducking and pitch bends on the offbeat
topic: bass
genres: [bass house]
source: MOONBOY — HOW TO BASS HOUSE (Knock2, Skrillex, Porter Robinson) (https://youtu.be/3-0JCDyiPaw?t=391)
status: untested
---
## What it is
His three rules for the sub (triangle, distortion, automate volume and pitch bend) and the trick that makes
it bounce: the sub holds long notes, the level is ducked hard on every kick, and the pitch jumps up and
falls back on every offbeat.

## When to use it
Under a mid bass or lead that has no real low end of its own, in bass house and anything trap-influenced.
For a tech house groove bass the sub usually lives inside the bass patch instead.

## How
1. Triangle wave: enough harmonics to be heard, still a sub (said, [6:38](https://youtu.be/3-0JCDyiPaw?t=398);
   shown: Basic Shapes, triangle frame).
2. Distortion: Serum's Tube type; he turns the drive up to 100 % while demonstrating (shown at
   [6:44](https://youtu.be/3-0JCDyiPaw?t=404)). The amount he keeps is not shown.
3. Pitch movement inside the patch: LFO 1 as a very steep falling curve, mode ENV, rate 1/4, routed in the
   matrix to master tune at about 22 (shown at [6:54](https://youtu.be/3-0JCDyiPaw?t=414)): each note starts
   high and drops into pitch.
4. In the track (shown at [7:01](https://youtu.be/3-0JCDyiPaw?t=421)): mono and legato on; the notes are held
   for a bar or more; LFO 1 is redrawn as a shape that swells up through each beat and falls at its end,
   free-running at 1/4, which reads as the volume duck (inferred: the amp envelope is flat); pitch-bend
   range +12.
5. A pitch-bend curve drawn in the clip spikes up on every offbeat 8th and decays back before the next beat
   (shown). He says: hard sidechain plus pitch bends on the offbeat gives a satisfying bounce
   ([6:51](https://youtu.be/3-0JCDyiPaw?t=411)).
6. Use headphones or monitors to judge it (on-screen note).

## In Rohil's setup
```
rick-rubin serum set init osc_a.on=off sub.on=on sub.shape=Triangle sub.level_db=0 \
  global.mono=on global.legato=on global.bend_up=12 fx.distortion.mode=Tube fx.distortion.drive=40 \
  lfo_1.rate=1/4 lfo_1.mode=Envelope lfo_1.shape="Basic/Saw Down Curved" \
  --fx-add distortion --mod lfo_1:sub.coarse:10 --save bounce-sub --project <dir>
```

- Drive and bend depth are ours. Ducking: `rick-rubin logic insert Sub "Kickstart 2" Mix=1.0` (full depth is
  his "hard" sidechain). Offbeat bends: draw pitch bend in Logic's piano roll automation lane, or write the
  sub's notes on the offbeats so the patch's own drop does it.

## How to check it
`rick-rubin serum ab <preset> --note F#0 --bpm 126 --try "mod_1.amount=0" --try "fx.distortion.drive=0"`. A
first run (2026-11-20, not heard): the word `pitch-drop` appears only with the mod; 99 % of the energy
below the bass band, no side energy; drive 40 % added 2.5 LU. On a bounce, `rick-rubin eval --bars A-B
--tracks Kick Sub`: sub level lowest on the kick's steps, highest on the offbeats.

## Why it works
A static sub is felt but not heard. Ducking gives it the kick's rhythm in negative, and a pitch blip on the
offbeat adds a second, audible accent exactly where the kick is not.
