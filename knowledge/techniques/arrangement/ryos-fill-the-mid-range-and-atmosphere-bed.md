---
title: Fill the gap between bass and lead with a mid-range driver, an atmosphere bed and a little sparkle
topic: arrangement
genres: [progressive house, any]
source: RYOS — Giving Feedback On YOUR Tracks! (https://youtu.be/3I7jJyVczPQ?t=8341)
status: untested
---
## What it is
A fat bass and a pretty lead with nothing between them sounds unfinished. Ryos adds three kinds of layer: a
melodic mid-range part that drives the section, an atmosphere under everything, and a quiet high-end pad.

## When to use it
Test: a section sounds epic while the vocal plays and smaller the moment it stops. That means the arrangement is
too thin (said, [2:01:10](https://youtu.be/3I7jJyVczPQ?t=7270)). Five tracks got this note.

## How
1. Mid-range driver, option A: a big chord stack (plain saw, a second saw, something odd such as a distorted
   organ); chords make a section uplifting (said, [2:20:01](https://youtu.be/3I7jJyVczPQ?t=8401)).
2. Option B, for darker tracks where chords would sound too happy: a ravey detuned saw playing a bassline-like
   rhythm but with no bass frequencies in it. The point is its crunchy, sizzling top, which he says gives a
   mainstage, modern energy (said, [2:21:01](https://youtu.be/3I7jJyVczPQ?t=8461)).
3. Option C: a big arp carrying the section. It wants a faster tempo (said,
   [2:19:50](https://youtu.be/3I7jJyVczPQ?t=8390)).
4. Atmosphere bed: every break needs one, and it should be audible. A special drone hidden at low level is
   wasted; turn it up, because an unfamiliar sound is what makes a listener curious (said,
   [1:22:04](https://youtu.be/3I7jJyVczPQ?t=4924), [1:42:45](https://youtu.be/3I7jJyVczPQ?t=6165)).
5. Sparkle: when a break and build have high mids (a choir) but no real top, add a string or a smooth analog pad
   high up, quiet enough to be "ear candy" only (said, [1:23:15](https://youtu.be/3I7jJyVczPQ?t=4995)).
6. A reese and a lead stack alone are "not going to cut it" in a euphoric section: add chords or aggressive saw
   basses according to mood, then the atmosphere (said, [2:51:01](https://youtu.be/3I7jJyVczPQ?t=10261)).
7. If a characterful sound from the break exists (keys, a reese), bring it back in the big section instead of
   inventing a new one (said, [2:02:20](https://youtu.be/3I7jJyVczPQ?t=7340)).

## In Rohil's setup
Option B in Serum 2: start from a detuned saw (`rick-rubin serum set init osc_a.unison=7 osc_a.detune=0.2 --save
rave-mid --project <dir>`), then high-pass it in Logic's Channel EQ so nothing remains under roughly 150 to
200 Hz (inferred; he only says "no bass frequencies"), and add drive (`fx.distortion.drive`). Atmospheres: Splice
(search "atmosphere", "drone", "texture" in the track's key) into Valhalla Supermassive. The agent writes the
notes of any new part; this card only says which role is missing.

## How to check it
`rick-rubin spectrum <dir> --mix --bars A-B` on the section: no dip between the bass harmonics and the lead
(roughly 300 Hz to 2 kHz), and energy present above 8 kHz in the break. `rick-rubin reference compare`: tonal
balance per band inside the references' range. Bounce the section with and without the vocal for Rohil: it
should not shrink.

## Why it works
A vocal fills the mid range; when it stops, whatever is left is exposed. A dedicated mid layer keeps the
spectrum full, and an atmosphere glues separate one-shots and synths into one space.
