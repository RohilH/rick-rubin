---
title: Pick the kick for the genre: a soft, clicky "basketball" kick for progressive house
topic: drums
genres: [progressive house, bass house, tech house]
source: RYOS — Giving Feedback On YOUR Tracks! (https://youtu.be/3I7jJyVczPQ?t=1742)
status: untested
---
## What it is
Ryos hears the kick as a genre marker. A progressive house kick should sound like a basketball bouncing on a
court: soft body, a click on top. A big knocking club or bass house kick in a progressive house track is the
wrong sample, however good it is.

## When to use it
When choosing or replacing a kick, and when a kick is "drowning", "thin" or "poppy". Four of the twelve tracks
had a kick he would change.

## How
1. Match the kick to the genre first. Progressive house: the basketball kick. Bass house and club tracks: the
   knocking kick. He told two progressive house producers their kick was too clubby (said,
   [29:02](https://youtu.be/3I7jJyVczPQ?t=1742), [2:05:45](https://youtu.be/3I7jJyVczPQ?t=7545)).
2. Solo the kick. It must not sound thin: it needs length and sub weight behind the attack (said,
   [3:07:20](https://youtu.be/3I7jJyVczPQ?t=11240)).
3. Listen to the transient. Too much mid range reads as a "pop"; he wants a click instead, so he takes some mids
   out and favours the top (said, direction only, [2:49:10](https://youtu.be/3I7jJyVczPQ?t=10150)).
4. If a progressive house kick is buried, check the sidechain on everything, the bass above all, then try a bell
   boost at about 3 kHz, where he says the snap of these kicks lives (said,
   [1:16:30](https://youtu.be/3I7jJyVczPQ?t=4590)).
5. Keep the kick's fader at 0 dB and mix the rest to it (see the clipper card).

## In Rohil's setup
Shortlist several kicks from Splice for the genre, then compare them by measurement with `rick-rubin audition
<dir> <files...>` (level, attack, decay, spectrum) and in context on a bounce, as PREFERENCES section 3 asks.
For tech house and bass house the knocking kick is the right one, so this card mostly matters when he moves to
progressive house.
The 3 kHz bell: Logic's Channel EQ on the kick track (`rick-rubin logic insert Kick "Channel EQ"`, then read
the band names with `rick-rubin logic params Kick "Channel EQ"`). Sidechain depth: `rick-rubin logic params Bass
Compressor`, or Kickstart 2's Mix.

## How to check it
`rick-rubin audition` rows for the candidates: the progressive house choice has a softer, shorter mid-range
transient and a clear high click, with a fundamental that still holds. In the mix, `rick-rubin reference
compare` against progressive house references: low-end pump and transient contrast inside their range. Then a
bounce for Rohil.

## Why it works
The kick sets the listener's expectation of the genre within one beat, and its length and spectrum decide how
much room is left for a long, melodic bass.
