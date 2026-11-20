---
title: Vary the second pass of a drop: wobble the lead, let a one-shot follow the sub, change the drums
topic: arrangement
genres: [bass house, tech house]
source: RYOS — I Made A Bass House Banger! | Studio Time with Ryos EP. 36 (https://youtu.be/N_RgytoSM94?t=687)
status: untested
---
## What it is
The concrete changes he makes when the call and response come round "the second time". The rule behind it
is `arrangement/ryos-something-significant-every-eight-bars.md`; these are bass house ways to obey it without
writing a new riff.

## When to use it
Once the first eight bars of a drop are full. Each move changes one thing about a part that already exists.

## How
1. **Wobble the call.** The second time, an LFO is automated on the call lead so it wobbles (said,
   [11:27](https://youtu.be/N_RgytoSM94?t=687)). On screen: LFOTool with a triangle shape on its own mixer
   track, and automation clips for its rate and its mix (shown, [11:42](https://youtu.be/N_RgytoSM94?t=702)).
2. **Speed it up in one spot.** He hears a place where the wobble can go faster and automates the rate there
   (said, [11:48](https://youtu.be/N_RgytoSM94?t=708)).
3. **The sub comes in under it**, and the project also holds an "Alt Sub" track for the second pass (said;
   shown, [11:42](https://youtu.be/N_RgytoSM94?t=702)).
4. **A one-shot starts following the harmony.** The bass shot, on one pitch the first time, follows the
   sub's simple two-note line the second time (said, [12:29](https://youtu.be/N_RgytoSM94?t=749); the second
   note name is unclear in the captions).
5. **Different drums per half.** A tambourine comes in for the second half; the classic offbeat ride is
   tried everywhere and kept only under the response (said, [14:03](https://youtu.be/N_RgytoSM94?t=843)).
   A fill separates the passes; it is replaced once because its tonal content clashed (said,
   [13:38](https://youtu.be/N_RgytoSM94?t=818)).

## In Rohil's setup
- The wobble as a second patch: `rick-rubin serum set "<call>" lfo_2.rate=1/8 --mod
  lfo_2:filter_1.cutoff_hz:30 --save call-wobble --project <dir>`, compared first with `rick-rubin serum ab
  "<call>" --bpm 126 --try "lfo_2.rate=1/4" --try "lfo_2.rate=1/8" --try "lfo_2.rate=1/16"`. Then
  `rick-rubin logic add-serum call-wobble --name "Call 2"` and Rohil moves the second pass's region onto it.
  This avoids automation, which the bridge cannot write; the faster spot can be a third patch.
- The bass shot per pitch: `rick-rubin serum render "<bass>" --note E1 --secs 0.4 --out samples/raw/shot_e.wav`.
- In a `song.py`: a variant of the drop section with the changed tracks.

## How to check it
`rick-rubin reference compare <dir>`: the share of near-identical blocks between the first and second eight
bars falls. `rick-rubin serum describe call-wobble --note C#2 --secs 2 --bpm 126` against the plain patch:
the "movement" column rises. `rick-rubin notes` on the bass shot track: its pitches match the sub's.

## Why it works
The listener already knows the riff the second time, so small changes to its sound are heard clearly and
read as development, at almost no writing cost.
