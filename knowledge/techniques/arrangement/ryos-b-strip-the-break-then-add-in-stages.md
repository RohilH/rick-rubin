---
title: Strip the start of a break to vocal plus one or two synths, then bring parts back in stages
topic: arrangement
genres: [progressive house, any]
source: RYOS — Can I Fix My Subscribers Music? (https://youtu.be/23NY1XxOlbA?t=467)
status: untested
---
## What it is
His edit of a subscriber's break, which he already liked. Almost nothing is added: parts are muted at the
start and returned later, so the break grows instead of starting full.

## When to use it
A break or verse that sounds good but flat from first bar to last, or one where everything enters together.

## How
1. Mute what nobody would miss: a very soft pluck layer goes (said, [7:47](https://youtu.be/23NY1XxOlbA?t=467)).
2. No bass at the start. The reese waits for the second half of the verse (said,
   [7:58](https://youtu.be/23NY1XxOlbA?t=478)).
3. Mute the bright ambience at the opening: too bright that early. Open with only the vocal and one or two
   good synths (said, [8:08](https://youtu.be/23NY1XxOlbA?t=488)).
4. Return the muted parts as stages. When the reese and the drums come in, the ambient layer comes back to
   add energy (said, [8:29](https://youtu.be/23NY1XxOlbA?t=509)).
5. Fill the vocal's gaps with small ear candy: a delay throw on one word, a synth answer on another (see
   `mixing/ryos-b-delay-throw-on-one-word.md`).
6. For more rhythm in the second break, bring in finger snaps and keep the cinematic drums, EQ'd less boomy
   because the reese now owns the low end (said, [9:35](https://youtu.be/23NY1XxOlbA?t=575)).
7. A sweep leads out of the break into the bigger chord section (said,
   [9:55](https://youtu.be/23NY1XxOlbA?t=595)).

## In Rohil's setup
- `rick-rubin logic inspect` lists what plays in the break. Propose, per track, the bar where it should
  enter. Whole-track mutes can be tried with `rick-rubin logic set Ambience mute=on`; making a part start
  later means trimming regions, which only Rohil does in his project.
- In a `song.py` this is the section's track list: `break_a` with vocal and chords, `break_b` adding reese,
  drums and ambience, written out by the agent.
- The EQ on the cinematic drums: `rick-rubin logic insert "Cine Drums" "Channel EQ"` with a low cut or low
  shelf, set after looking at `rick-rubin spectrum` of drums against reese.

## How to check it
`rick-rubin eval <dir> --bars <break>` or a bounce of each half: loudness and the high band should step up
from the first half to the second, not sit level. `rick-rubin reference compare <dir>`: more texture changes
per minute. The low band should be nearly empty in the first half.

## Why it works
A section can only build if it starts with less than it ends with. Holding back the bass and the brightest
layer saves the two biggest sources of energy for the moment the drums arrive.
