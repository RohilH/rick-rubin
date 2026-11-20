---
title: Flatten a thin clap or snare with a limiter so its body comes up
topic: mixing
genres: [tech house, bass house, any]
source: MOONBOY — HOW TO TECH HOUSE | Full Tutorial (Odd Mob, Chris Lake, Mau P) (https://youtu.be/JqKaSvHImB0?t=279)
status: untested
---
## What it is
A limiter used as a tone tool on one drum hit: the spike is cut off and the noisy tail is pushed up to the
same level, so a thin clap sounds wide and full.

## When to use it
When the clap or snare on 2 and 4 disappears once bass and vocal are in, or sounds like a click with no
body. Not for a clap that is already dense; it will only get harsher.

## How
1. Solo the clap and put a limiter on it (said, [4:39](https://youtu.be/JqKaSvHImB0?t=279)).
2. Ceiling to −3 dB (said).
3. Raise the input gain until the hit is clearly flattened: 11 dB in his case (shown at
   [5:18](https://youtu.be/JqKaSvHImB0?t=318); the meter reads about 3.7 dB of reduction at that moment).
4. Shorten the release as far as it goes: 0.02 ms shown, with look-ahead 3 ms and the standard mode.
5. Unsolo and adjust the gain by ear against the kick (said: "adjust to your liking").

## In Rohil's setup
- Logic's Limiter does the same job: `rick-rubin logic insert Clap Limiter`, read the names with
  `rick-rubin logic params Clap Limiter`, then raise its gain, set its output level to −3 dB and its release
  to the minimum. Mastering The Mix LIMITER also works but is built for the master.
- The ceiling makes the track quieter by 3 dB at its peak: put the fader back where the clap sat.

## How to check it
Bounce the clap alone before and after and run `rick-rubin audition <dir> before.wav after.wav`: the decay
should read longer and the level higher at a lower peak (crest down by several dB). `rick-rubin spectrum
<dir> before.wav after.wav`: more energy from 200 Hz to 2 kHz relative to the top. In the mix, the clap's
steps in `rick-rubin hits` should stand out by the same amount with the fader lower.

## Why it works
A clap is a burst of noise with one loud spike at the front. With an instant release the limiter only holds
the spike down, so the gain you added lifts everything after it: the same trick as clipping, on one sound.
