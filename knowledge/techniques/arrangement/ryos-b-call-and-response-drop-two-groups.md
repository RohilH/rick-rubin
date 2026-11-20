---
title: A bass house drop as call and response: a long-note lead answered by a short-note stack, each its own group
topic: arrangement
genres: [bass house, tech house]
source: RYOS — I Made A Bass House Banger! | Studio Time with Ryos EP. 36 (https://youtu.be/N_RgytoSM94?t=83)
status: untested
---
## What it is
The skeleton of his drop at 126 BPM. A nasty lead holds a few long notes (the call); a second, different
sound answers with short rhythmic hits (the response). The notes are kept very simple on purpose; the effort
goes into the sounds and the arrangement around them.

## When to use it
Starting a bass house or tech house drop from nothing. It is the phrase-level cousin of
`arrangement/moonboy-a-b-drop-sections.md` (two drop versions taking turns).

## How
1. Sounds before notes. Hunt for one "disgusting" lead preset to base the drop on; he changes its LFO timing
   and opens it up (said, [1:03](https://youtu.be/N_RgytoSM94?t=63); a Serum patch with two complex
   wavetables and an LFO-shaped filter, shown [1:24](https://youtu.be/N_RgytoSM94?t=84)).
2. His rule for the genre: a simple melody, then go "absolutely nuts" with production and arrangement (said,
   [1:23](https://youtu.be/N_RgytoSM94?t=83)).
3. Call: long notes. His is three notes over two bars, one of a full bar and two of half a bar, a semitone
   up and then a minor third down (shown, [2:00](https://youtu.be/N_RgytoSM94?t=120); pitch names read by
   counting piano-roll rows: D sharp, E, C sharp).
4. Response: the next two bars, a second lead playing short syncopated hits on the first note's pitch with a
   jump up an octave at the end (said, [2:04](https://youtu.be/N_RgytoSM94?t=124); shown,
   [2:16](https://youtu.be/N_RgytoSM94?t=136), while still being written).
5. Add a sub line, then a very simple loop (a "knocking" kick, clap, hat) straight away so the groove can be
   judged (said, [3:10](https://youtu.be/N_RgytoSM94?t=190)).
6. Two groups in the mixer: the call lead with a white-noise layer under it (said,
   [6:24](https://youtu.be/N_RgytoSM94?t=384)), and a response group of four layers (see
   `sound-design/ryos-b-response-stack-main-support-top-pluck.md`). Later the offbeat ride plays under the
   response only (said, [14:24](https://youtu.be/N_RgytoSM94?t=864)).

## In Rohil's setup
- Call sound: `rick-rubin serum search`, shortlist three, then his "change the timing" step by measurement:
  `rick-rubin serum ab "<preset>" --note C#2 --bpm 126 --try "lfo_1.rate=1/4" --try "lfo_1.rate=1/8" --try
  "lfo_1.rate=1/16"`, and `rick-rubin serum audition` so he hears the candidates.
- White noise inside the call patch: `noise.on=on noise.type=White noise.level_db=-20`.
- In Logic: two summing stacks, "Call" and "Response". The notes are written for the song in `song.py`.

## How to check it
`rick-rubin reference compare <dir>`: fewer near-identical two-bar blocks and more texture changes per
minute than a one-riff drop. `rick-rubin eval <dir> --bars <drop>`: call bars and response bars within about
1 LU, so the trade is a change of colour, not of level.

## Why it works
Long notes show off a complex sound; short notes carry rhythm. Alternating them gives contrast every two
bars from very little melodic material.
