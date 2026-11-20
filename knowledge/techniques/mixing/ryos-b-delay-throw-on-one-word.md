---
title: A delay throw on one word of the vocal, thinned and made strange, and not repeated on the next line
topic: mixing
genres: [progressive house, bass house, tech house, any]
source: RYOS — Can I Fix My Subscribers Music? (https://youtu.be/23NY1XxOlbA?t=509)
status: untested
---
## What it is
Ear candy for a vocal break: the last word of one line is sent into a delay so it echoes through the gap
that follows. The echoes are filtered and modulated so they sound different from the dry vocal.

## When to use it
A vocal line that ends before a gap of a beat or more. One or two per section.

## How
1. Choose the word: the end of a line with space after it. His is the word "lost" (said,
   [8:29](https://youtu.be/23NY1XxOlbA?t=509)).
2. Send only that word to a delay. He uses Waves H-Delay at a quarter note on its own mixer track, fed by an
   automated send from the vocal (shown, [9:00](https://youtu.be/23NY1XxOlbA?t=540): the automation clip reads
   "Vocal - To Insert 4").
3. Raise the delay's high-pass so the echoes are thin, and turn ping-pong off so they stay in one place (said,
   [8:50](https://youtu.be/23NY1XxOlbA?t=530)).
4. Make the echoes "funky": an ensemble (chorus) after the delay, and perhaps a reverb after that (said,
   [8:55](https://youtu.be/23NY1XxOlbA?t=535)).
5. Do not use the same trick on the next line. Where she sings the next key word he answers with a synth
   sound instead of another throw (said, [9:12](https://youtu.be/23NY1XxOlbA?t=552)).
6. Feedback and mix values are not readable.

## In Rohil's setup
The bridge cannot write send automation, so use a second track instead of an automated send:
- Rohil copies the one word to a new audio track, "Vocal Throw" (region editing is his). The dry word stays
  on the main vocal track.
- Inserts on "Vocal Throw", in order: `rick-rubin logic insert "Vocal Throw" "Tape Delay"` (or Stereo Delay)
  at 1/4, fully wet, its low cut raised to about 500 Hz or higher; then `Ensemble`; then `ChromaVerb` at a low
  mix. Read each one's parameter names with `rick-rubin logic params "Vocal Throw" "Tape Delay"`.
- Level of the throw: `rick-rubin logic set "Vocal Throw" volume=-8`, then by ear.
- In a `song.py`, a separate track holding that one word with the delay on it does the same.

## How to check it
Bounce the two bars after the word with `--tracks "Vocal Throw"`: level starts right after the word and
decays through the gap, ending before the next line. `rick-rubin spectrum`: little below the high-pass.
`rick-rubin transcribe` on the vocal gives the word's position, so the throw can be placed to the 16th.

## Why it works
The gap after a line is free space; an echo of the last word fills it with material the listener already
knows. Filtering keeps the echo behind the next line, and using it once keeps it a surprise.
