---
title: Two basses with two jobs: a groove bass that never stops and a character bass on top
topic: bass
genres: [tech house, bass house]
source: MOONBOY — HOW TO TECH HOUSE | Full Tutorial (Odd Mob, Chris Lake, Mau P) (https://youtu.be/JqKaSvHImB0?t=366)
status: untested
---
## What it is
He splits "the bass" of a tech house drop into roles. The groove bass is plain, low and rhythmic and plays
all the time, usually under the vocal. A second, louder-in-character sound is layered over it for the
moments that need attention, and the groove simply carries on underneath.

## When to use it
When a drop built on one bass feels either boring (only the groove) or tiring and thin in the low end (only
the crazy sound). Also the way to borrow a dubstep or bass house sound without losing the house feel.

## How
1. **The groove** sets the rhythm of the track and sits under a vocal or a wilder sound (said,
   [6:27](https://youtu.be/JqKaSvHImB0?t=387)). Its part is the offbeat line with small variations (shown
   at [6:26](https://youtu.be/JqKaSvHImB0?t=386)).
2. **A character bass** goes on top. His three examples ([6:38](https://youtu.be/JqKaSvHImB0?t=398) to
   [7:07](https://youtu.be/JqKaSvHImB0?t=427)):
   - "Sci-Fi Acid": his Serum 2 preset shows one saw with 6 unison voices, an MG Low 12 with a resonant
     peak, LFO 1 in Envelope mode at 2 bars with a slowly falling curve, mono with legato (shown). So: a
     resonant filter that closes over two bars while the notes slide into each other.
   - "Robo-Stutter": a robotic, stuttering rhythmic sound (said; nothing shown).
   - "BASS x House": a sound from dubstep or bass house thrown over the groove (said; nothing shown).
3. Keep the groove playing while the character sound plays (said, [7:07](https://youtu.be/JqKaSvHImB0?t=427)).
4. Inferred, not said: the groove keeps the sub, so the character layer should be high-passed or simply not
   reach below about 100 Hz, or the two will fight.

## In Rohil's setup
- Two Serum tracks. The groove: the pluck bass card. The acid layer, as a starting point:
  `rick-rubin serum set init osc_a.unison=6 filter_1.on=on filter_1.type="MG Low 12" filter_1.res=55
  filter_1.cutoff_hz=400 lfo_1.rate="2 bar" lfo_1.mode=Envelope lfo_1.shape="Basic/Saw Down Curved"
  global.mono=on global.legato=on global.glide_ms=60 --mod lfo_1:filter_1.cutoff_hz:45 --save acid-top
  --project <dir>` (resonance, cutoff, glide and depth are ours; unison, mode and rate are shown).
- Or search what is installed first: `rick-rubin serum search acid bass`, `rick-rubin serum search --like
  "<a preset he likes>"`.
- If the layers mask each other, Trackspacer on the character bass keyed from the groove:
  `rick-rubin logic insert "Acid" "Trackspacer 2.5" Ratio=60 --sidechain Bass`.

## How to check it
`rick-rubin spectrum <dir> --tracks Bass Acid --bars 17-24`: the curves should cross near 100 to 150 Hz, the
groove above the character layer below that and under it above. `rick-rubin width`: nothing wide below
150 Hz even if the top layer has unison.

## Why it works
Low-end weight and midrange interest ask for opposite things (mono, simple and steady against wide, moving
and loud). Giving each to its own sound lets both be extreme.
