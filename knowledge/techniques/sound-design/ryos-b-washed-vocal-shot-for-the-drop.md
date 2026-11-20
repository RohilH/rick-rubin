---
title: A washed-out vocal shot for the drop, made from the track's own vocal
topic: sound-design
genres: [progressive house, bass house, any]
source: RYOS — Can I Fix My Subscribers Music? (https://youtu.be/23NY1XxOlbA?t=382)
status: untested
---
## What it is
One short phrase of the song's vocal, drowned in reverb, printed to audio, then shaped into a thin, airy,
moving texture that answers the lead in the drop. He calls putting a piece of a good vocal in the drop a
"no-brainer".

## When to use it
Any track with a vocal whose drop is instrumental. It ties the drop to the song and fills gaps in the lead.

## How
1. Pick one word or short phrase from the vocal (said, [6:22](https://youtu.be/23NY1XxOlbA?t=382)).
2. Wash it out with Valhalla Supermassive on the insert (said, [6:30](https://youtu.be/23NY1XxOlbA?t=390)).
   His preset menu shows his own entries, among them "Vocal Wash"; which one he loads is not readable
   ([6:38](https://youtu.be/23NY1XxOlbA?t=398)).
3. Record the result to audio before anything else (said, [6:44](https://youtu.be/23NY1XxOlbA?t=404)), so the
   wash is part of the clip.
4. Shape it like a telephone: a band-pass EQ (Pro-Q 3 preset "Phone", shown
   [6:58](https://youtu.be/23NY1XxOlbA?t=418)), then open the high cut again because he wants it airy (said).
5. Auto-pan so it moves side to side (Soundtoys PanMan; said, [7:06](https://youtu.be/23NY1XxOlbA?t=426)).
6. Sidechain it so it bounces with the drop, then OTT at full depth (said; OTT shown at depth 100 %, time
   100 %, output about -6.9 dB, [7:27](https://youtu.be/23NY1XxOlbA?t=447)).
7. Copy the lead group's delay onto it so it shares the lead's space (said,
   [7:26](https://youtu.be/23NY1XxOlbA?t=446)).

## In Rohil's setup
- Check the phrase against the key: `rick-rubin notes <dir> samples/phrase.wav`.
- Wash: `rick-rubin logic insert Vocal "ValhallaSupermassive" Mix=0.6 Fb=0.7` on a copy of the vocal track
  (values are a starting point; his are unknown), then print it: `rick-rubin logic bounce shot_wet.wav --bars
  A-B --tracks "Vocal copy"` and `rick-rubin logic add-audio shot_wet.wav --bar N --name "Vocal Shot"`.
- On "Vocal Shot": Channel EQ (low cut near 400 Hz, a mid lift, highs left open), Tremolo set to pan (see
  `mixing/moonboy-auto-pan-rides-and-drum-level-guide.md`), `rick-rubin logic insert "Vocal Shot" "Kickstart 2"
  Mix=1.0`, then `rick-rubin logic insert "Vocal Shot" "OTT" Depth=100 OutGai=-7`.
- Cutting the bounced file into several hits across the drop is region editing: his hands.

## How to check it
`rick-rubin spectrum <dir> shot_wet.wav`: almost nothing under the low cut, energy up to the top. `rick-rubin
width`: side share high. Bounce "Vocal Shot" over two drop bars: level dips on each beat. Then
`rick-rubin spectrum` of lead and shot together: the shot should not out-weigh the lead at 1 to 4 kHz.

## Why it works
Printing the reverb turns voice and tail into one sound that can be filtered, panned and ducked as a whole;
thinned out, it reads as a texture and stays out of the lead's way.
