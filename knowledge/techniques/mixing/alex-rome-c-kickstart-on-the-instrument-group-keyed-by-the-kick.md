---
title: Duck the bass and the instrument group with Kickstart 2, sized to the kick
topic: mixing
genres: [tech house, bass house, progressive house]
source: Alex Rome — Give me 19 mins, and I'll Improve your mixing skills by 126% (https://youtu.be/XrGZPWuiJ7o?t=670)
status: untested
---
## What it is
A volume-shaping plug-in instead of a compressor for sidechain, used at two depths of thinking: the necessary part
(the bass must get out of the kick's way) and the optional part (everything pumps, as a genre effect).

## When to use it
Every four-on-the-floor track. Always on the bass and sub; on chords, leads and pads to taste and by genre.

## How
1. Prefer a dedicated ducking plug-in to the DAW's compressor: cleaner and more controllable (said,
   [11:30](https://youtu.be/XrGZPWuiJ7o?t=690); [7:29](https://youtu.be/HLCi1uYq8r0?t=449)).
2. If the instruments are already grouped, one instance on the group does the job (said,
   [12:10](https://youtu.be/XrGZPWuiJ7o?t=730)).
3. Trigger it from the kick's audio so it ducks only when the kick plays: AUDIO mode with the kick as sidechain input
   (said). Shown at [11:56](https://youtu.be/XrGZPWuiJ7o?t=716): 1/4, AUDIO, Mix 100 %, first curve.
4. In that mode the kick's waveform is drawn behind the curve. Drag the curve's recovery so the level comes back where
   the kick's body ends (said, [13:16](https://youtu.be/XrGZPWuiJ7o?t=796); shown at 11:56).
5. Simpler alternative on a bass that plays only with the kick: SYNC mode, 1/4, second curve, Mix 100 %, then eased to
   88 % (shown [7:38](https://youtu.be/HLCi1uYq8r0?t=458), [8:25](https://youtu.be/HLCi1uYq8r0?t=505)), last in the
   strip after Serum and Channel EQ.
6. Try a long recovery (big pump) and a short one (quick duck) and keep what the track wants (said,
   [8:12](https://youtu.be/HLCi1uYq8r0?t=492)).
7. If the pump does not suit the genre, still spend time on kick and bass separation (said,
   [13:36](https://youtu.be/XrGZPWuiJ7o?t=816)).

## In Rohil's setup
He owns Kickstart 2. `rick-rubin logic insert Bass "Kickstart 2" Mix=0.88` (SYNC is the default). Curve and rate go
through `logic tweak`: `Used Wave` picks one of 16 curves in steps of 1/15, `Loop Length` 0.00 is every beat. AUDIO
mode needs the kick chosen in the plug-in window's Side Chain menu; whether `logic insert ... --sidechain Kick` sets
it for Kickstart is not verified. This repo's standing advice (`skill/logic.md`): shaper on pads and chords, a
kick-keyed compressor or AUDIO mode on the bass, so fills and gaps do not pump.

## How to check it
`rick-rubin logic bounce bounces/kb.wav --bars 33-36 --tracks Kick Bass`, then `rick-rubin reference compare`: the
pump measure should rise into the references' range and the sub band should show less overlap on the beat (`rick-rubin
hits <dir> bounces/kb.wav` shows each 16th's level: the on-beat steps should be the kick alone).

## Why it works
Kick and bass share the sub band, and two sources there at once sum into mud; removing the bass for the length of the
kick gives each its own time (said, [12:55](https://youtu.be/XrGZPWuiJ7o?t=775)).
