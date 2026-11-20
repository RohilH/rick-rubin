---
title: Five additions that turn the basic house beat into a bass house drop beat
topic: drums
genres: [bass house]
source: MOONBOY — HOW TO BASS HOUSE (Knock2, Skrillex, Porter Robinson) (https://youtu.be/3-0JCDyiPaw?t=98)
status: untested
---
## What it is
On top of kick, clap and offbeat hat he adds: a crash for the drop's first beat, a panned ride layer,
accent snares on weak 16ths, a busier last beat, and a reversed kick that pulls into the next phrase.

## When to use it
For the drop's 4-bar drum phrase in bass house (126 to 128 BPM), after the basic beat exists. The extras are
what make the drop sound bigger than the build without touching the kick.

## How
1. **Crash on beat 1** of the drop, ringing across the phrase (said and shown,
   [1:42](https://youtu.be/3-0JCDyiPaw?t=102)).
2. **Rides** as a steady layer for the whole phrase, auto-panned left and right for width (said: a 1/8
   pattern; shown at [1:47](https://youtu.be/3-0JCDyiPaw?t=107): one ride clip on every beat). Very quiet:
   −16 dB in his guide.
3. **Accent snares** on a separate lane: the 16th before and the 16th after beat 3 in bar 1, one after beat 3
   in bar 3 (shown at [1:52](https://youtu.be/3-0JCDyiPaw?t=112); he says "accent percussion for swing and
   groove").
4. **Turnaround**: in the last beat of bar 4 a snare on the beat and another on the last 16th (shown).
5. **Reverse kick** on that same last beat, ending exactly on the next downbeat (said and shown).
6. One extra short hat on the second 16th of bar 1 (shown, small clip under the snare lane).
7. Keep cymbals and hats well under kick and clap (said, [1:58](https://youtu.be/3-0JCDyiPaw?t=118)).

The positions are his example; the roles are what to keep: impact on 1, a wide quiet top layer, ghost hits
around a strong beat, and something that leads into the next phrase.

## In Rohil's setup
- Reverse kick: bounce or copy the kick to an audio region and tick Reverse in Logic's Region inspector;
  place it so it ends on the bar line. In a `song.py` it is a reversed sample on its own track.
- Rides and crash from Splice; compare candidates with `rick-rubin audition <dir> <files...>`.
- Levels: `rick-rubin logic set Rides volume=-16`, `rick-rubin logic set Crash volume=-12`.

## How to check it
`rick-rubin hits <dir> --tracks Snares --bars 1-4`: accents on the steps next to beat 3, none on kick steps
other than the turnaround. `rick-rubin width <dir> --bars 1-4`: side energy above 4 kHz up (the rides), none
below 150 Hz. `reference compare`: "top-end activity" inside the references' range.

## Why it works
The kick and clap cannot change without the drop losing its drive, so size has to come from layers that
start on the first beat (crash), fill the top (rides) and announce the phrase ends (snare pair, reverse).
