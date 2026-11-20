---
title: Set each low cut while the bass is playing, not in solo
topic: mixing
genres: [any, tech house, bass house, progressive house]
source: Alex Rome — Give me 19 mins, and I'll Improve your mixing skills by 126% (https://youtu.be/XrGZPWuiJ7o?t=125)
status: untested
---
## What it is
A way to find where a heavy instrument's low cut belongs: play it together with the sub and sweep the cut until both
sound full. The existing low-cut card says what to cut; this says how far.

## When to use it
On anything with real low-mid weight that shares bars with the bass: piano chords, pads, plucks, a mid-bass layer.
High parts (hats, arps) can simply be cut high; the search matters for the heavy ones.

## How
1. Start from about 150 Hz (said, [1:04](https://youtu.be/XrGZPWuiJ7o?t=64)).
2. Solo the instrument and the sub together, or play the whole track, never the instrument alone (said,
   [2:05](https://youtu.be/XrGZPWuiJ7o?t=125)).
3. Sweep the cut up and down. Too high: the bass is clear but the instrument loses its body. Too low: the sub
   "struggles to get through" (said, [3:06](https://youtu.be/XrGZPWuiJ7o?t=186)). Stop between the two.
4. His results on a piano house drop: piano chords at 278 Hz, Q 0.69, gentle slope (shown
   [3:32](https://youtu.be/XrGZPWuiJ7o?t=212)); arps at 400 Hz (shown [9:10](https://youtu.be/XrGZPWuiJ7o?t=550)); the
   bass layer that sits over the sub at 352 Hz with a 48 dB/oct slope (shown
   [5:18](https://youtu.be/XrGZPWuiJ7o?t=318)).
5. Spend longest on the lowest instruments, the bass layer above all (said,
   [5:11](https://youtu.be/XrGZPWuiJ7o?t=311)).
6. Cut parts with no audible low end too; the analyzer shows energy there and it costs headroom (said,
   [3:47](https://youtu.be/XrGZPWuiJ7o?t=227)).
7. The setting can be revisited later (said, [3:26](https://youtu.be/XrGZPWuiJ7o?t=206)).

## In Rohil's setup
Logic's Channel EQ does what EQ Eight does here: band 1 as a low cut, slope 12 dB/oct for chords and 48 dB/oct for a
bass layer. `rick-rubin logic insert Piano "Channel EQ"`, then read the band's parameter names with `rick-rubin logic
params Piano "Channel EQ"` before `logic tweak`. To hear the pair as he does: `rick-rubin logic bounce
bounces/piano_sub.wav --bars 33-40 --tracks Piano Sub`.

## How to check it
Bounce sub plus instrument before and after and overlay: `rick-rubin spectrum <dir> before.wav after.wav`. Below the
cut the curve should fall to the sub's own level; above about twice the cut frequency it should not move. On the full
drop, `reference compare` low-mid share should come down toward the references. Then Rohil listens: does the piano
still sound whole?

## Why it works
In solo any cut sounds like a loss, so cuts end up too timid; against the bass the ear judges the trade that matters
(inferred from his warning about solo).
