---
title: When a kick, a sub boom and a bass land together, delete one and sidechain what is left
topic: mixing
genres: [progressive house, bass house, any]
source: RYOS — Can I Fix My Subscribers Music? (https://youtu.be/23NY1XxOlbA?t=615)
status: untested
---
## What it is
A low-end rule from his fix of a big half-time "hands up" section: three things with sub energy on the same
beat is a clash. The cure is an arrangement decision first, then a sidechain, and only then EQ.

## When to use it
Any downbeat where an impact or sub drop, the bass and the kick coincide: first beats of drops, half-time
sections, big chord hits.

## How
1. Line things up first. The section's heavy kicks sounded slightly off; he moves them so each kick lands
   with a chord hit (said, [9:55](https://youtu.be/23NY1XxOlbA?t=595)).
2. Name what is fighting: a big sub boom, the bass and the kick, all at once (said,
   [10:15](https://youtu.be/23NY1XxOlbA?t=615)).
3. Remove one. His first thought is to delete the boom; he then keeps it because it sounds good, and takes
   the bass out at that point instead (said, [10:35](https://youtu.be/23NY1XxOlbA?t=635)).
4. Sidechain the survivor to the kick so the two do not overlap in time (said,
   [10:45](https://youtu.be/23NY1XxOlbA?t=645)).
5. Where a bass does play in the section, swap in a less muddy one that cuts through, to give the section
   breathing room (said, [11:42](https://youtu.be/23NY1XxOlbA?t=702)).
6. Same thinking elsewhere in the session: cinematic drums under a big reese are EQ'd to be less boomy
   (said, [9:35](https://youtu.be/23NY1XxOlbA?t=575)).

## In Rohil's setup
- See the clash: bounce each low part over the bars (`rick-rubin logic bounce boom.wav --bars A-B --tracks
  "Sub Boom"`, same for kick and bass) and overlay them with `rick-rubin spectrum <dir> kick.wav boom.wav
  bass.wav`. BASSROOM on the master shows the same thing.
- Audition the choice without deleting anything: `rick-rubin logic set Bass mute=on`, bounce, then the other
  way round. Removing the bass only on that beat is a region edit for Rohil.
- Sidechain the survivor: `rick-rubin logic insert "Sub Boom" Compressor --sidechain Kick`, or `rick-rubin
  logic insert "Sub Boom" "Kickstart 2" Mix=1.0` if the kicks are on every beat.

## How to check it
`rick-rubin compare <dir> before.wav after.wav` on the section: energy below about 100 Hz falls and crest
rises (the kick's peak is no longer buried). `rick-rubin reference compare <dir>`: low-end balance and punch
move towards the references. The master should clip or limit less on those downbeats.

## Why it works
The sub range has room for one sustained source at a time. Two or three add up to level without definition,
and the limiter then turns everything else down on the track's biggest moments.
