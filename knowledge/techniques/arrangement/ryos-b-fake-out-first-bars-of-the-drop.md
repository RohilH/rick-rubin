---
title: A fake-out drop: the lead alone with no pump for two bars, washed into reverb, then the real drop
topic: arrangement
genres: [bass house, tech house, progressive house]
source: RYOS — I Made A Bass House Banger! | Studio Time with Ryos EP. 36 (https://youtu.be/N_RgytoSM94?t=341)
status: untested
---
## What it is
What he calls the classic fake-out. The drop seems to start, but only the call lead plays, dry of drums and
sidechain; over those bars it is drowned in an effect like a mini build, and then the kick, the drums and
the pump arrive together.

## When to use it
The first bars of a drop, mostly in bass house and tech house. It makes a simple drop land twice.

## How
1. The first two bars of the drop hold the call lead and no drums; hats and claps start on the third bar
   (shown, [6:20](https://youtu.be/N_RgytoSM94?t=380); bar numbers on the ruler are small).
2. With no kick there should be no pumping. He automates the sidechain: Kickstart 2's mix sits at the bottom
   for the fake-out and steps up where the drums enter (said, [5:41](https://youtu.be/N_RgytoSM94?t=341);
   shown, [5:58](https://youtu.be/N_RgytoSM94?t=358)).
3. Make the fake-out move. Endless Smile on the call lead, its intensity automated upward across the two
   bars, "drowning" the sound in reverb: "almost like a mini build" (said,
   [6:03](https://youtu.be/N_RgytoSM94?t=363); ramp shown, [6:20](https://youtu.be/N_RgytoSM94?t=380)).
4. He also tried a volume LFO (LFOTool) for a wilder transition and took it out: too crazy (said,
   [6:24](https://youtu.be/N_RgytoSM94?t=384)). Trying and discarding is part of the method.
5. The playlist shows two lanes for the call, one for the fake-out and one labelled with "SC" for the rest
   (shown, [6:20](https://youtu.be/N_RgytoSM94?t=380)).
The general case of step 2 is `mixing/ryos-pg-pump-depth-by-section.md`.

## In Rohil's setup
The bridge cannot write automation, so copy his two-lane layout:
- Track "Call fake": the lead for the first two bars, no Kickstart. For the wash, Rohil draws a ramp on
  ChromaVerb's mix and on an AutoFilter high-pass; he has no Endless Smile, and what is lost is doing it
  with one knob. Supermassive with its mix ramped is the other option.
- Track "Call": the same patch from bar three on, with `rick-rubin logic insert Call "Kickstart 2" Mix=1.0`.
- In a `song.py`: a two-bar section with only the call track and its automation, then the full drop section.

## How to check it
Bounce the drop's first four bars. `rick-rubin hits <dir> --bars A-B`: no kick-band energy and no beat-rate
dips in bars 1 and 2; both present from bar 3. The level of bars 3 and 4 should be clearly above bars 1 and
2 (`rick-rubin eval <dir> --bars`), and the top band should rise through the fake-out as the wash builds.

## Why it works
The listener expects the full drop on the downbeat; holding the drums back for two bars resets that
expectation, so their entry is a second impact. Pumping without a kick would give the trick away.
