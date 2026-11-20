---
title: OTT before the reverb keeps the space natural; after it, the tail is pulled up into the sound
topic: mixing
genres: [any, progressive house, tech house]
source: Alex Rome — Give me 19 mins, and I'll Improve your mixing skills by 126% (https://youtu.be/XrGZPWuiJ7o?t=525)
status: untested
---
## What it is
OTT compresses whatever reaches it. Placed before delay and reverb it shapes only the dry sound. Placed after, it
raises the quiet tails toward the level of the notes, so the space becomes part of the sound.

## When to use it
After: a sparse melody whose gaps feel empty, a pluck that should sound continuous, a part you want thick and "glued".
Before: a part whose reverb should stay behind it, and anything where a loud tail would crowd the mix.

## How
1. Know the default chain he shows on an arp: synth, OTT, reverb (shown [9:10](https://youtu.be/XrGZPWuiJ7o?t=550):
   Serum, OTT, ValhallaVintageVerb). Here Depth can go high without touching the reverb (said,
   [9:06](https://youtu.be/XrGZPWuiJ7o?t=546)).
2. Drag OTT to after the reverb and compare the two orders at the same Depth (said,
   [9:26](https://youtu.be/XrGZPWuiJ7o?t=566)). After the reverb, the tail is crushed and stuck to the note.
3. Use the after position in some places, not everywhere (said, [9:47](https://youtu.be/XrGZPWuiJ7o?t=587)).
4. His worked case, from "How To Get That 'Pro Sound'": a pluck lead with Serum's own 1/4 delay and hall reverb, then
   OTT at Depth 64 % as an insert after the synth, used to lift the echoes in the gaps between notes (said and shown,
   [1:53](https://youtu.be/Uazkku5yuM8?t=113), [2:08](https://youtu.be/Uazkku5yuM8?t=128)).
5. Effects inside the synth count as "before" any insert that follows the synth (inferred from step 4).

## In Rohil's setup
With reverb on a send (the usual Logic layout) OTT on the track never sees the tail. To get the "after" sound, put the
reverb as an insert before OTT (`rick-rubin logic insert Lead "ValhallaSupermassive" Mix=0.25`, then `rick-rubin logic
insert Lead "OTT" Depth=50`), or use Serum's own reverb: `--fx-add reverb` with `fx.reverb.wet`, then OTT on the
strip. Insert order is the order shown by `rick-rubin logic inspect`. Serum can also do both inside the patch:
`--fx-add reverb --fx-add compressor` with `fx.compressor.multiband=1`.

## How to check it
Bounce the part alone both ways. `rick-rubin compare <dir> ott_before.wav ott_after.wav`: with OTT after, crest should
be lower and the level in the gaps between notes higher (the decay figure in `rick-rubin serum describe <file>` gets
longer). If width or low-mid share jumps, the tail is now too loud: lower Depth or the reverb mix.

## Why it works
Upward compression raises anything below its threshold. A reverb tail is exactly that, so after the reverb OTT acts
like turning the tail up only when the note is not playing (inferred).
