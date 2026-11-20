---
title: A house beat in four lanes, then a few hits on weak 16ths to make it groove
topic: drums
genres: [tech house, bass house]
source: MOONBOY — HOW TO TECH HOUSE | Full Tutorial (Odd Mob, Chris Lake, Mau P) (https://youtu.be/JqKaSvHImB0?t=125)
status: untested
---
## What it is
The beat every house track starts from (kick, clap, offbeat hat, crash), and the step that turns it from a
metronome into a groove: a snare and a short clap placed on 16ths next to the strong beats, never on them.

## When to use it
The first eight bars of any tech house or bass house sketch, before bass or vocal exist.

## How
1. Kick on every beat, clap on beats 2 and 4, closed hat on every offbeat 8th, a crash on beat 1 of the
   phrase (said; shown at [2:40](https://youtu.be/JqKaSvHImB0?t=160)). Loop two bars, duplicate to four.
2. On a separate lane add a snare on the last 16th of bar 1 and another on the second 16th of bar 2, so the
   pair straddles the downbeat (shown at [3:12](https://youtu.be/JqKaSvHImB0?t=192), positions 1.4.4 and
   2.1.2; he only says "percussive grooves").
3. Add a short, snappy clap on the and of beat 4 in bar 2 (shown, 2.4.3). In the fourth bar add one more on
   the last 16th, so the turnaround is busier than the middle of the phrase (shown at
   [3:23](https://youtu.be/JqKaSvHImB0?t=203), 4.4.4).
4. Pull that lane down to about −6 dB against the kick and clap at 0, and the crash too (snare −6 said;
   cymbal −6.0 shown at [4:22](https://youtu.be/JqKaSvHImB0?t=262)).
5. Use a different clap sample for the ghost hits than for the backbeat ("Clap (Thick)" on 2 and 4, "Clap
   (Snappy)" for the extras: shown in the browser).

These positions are his example. The idea to keep is: ghost hits on weak 16ths that lead into a downbeat or
into the next clap, quieter than the backbeat, and more of them at the end of the phrase.

## In Rohil's setup
In a `song.py`, write the snare lane as its own track with its own velocities and compare two or three
placements (`rick-rubin ab <dir> ... --hits`). In a Logic project of his, the lanes are audio or Drum Machine
Designer tracks; set the lane level with `rick-rubin logic set Snare volume=-6`.

## How to check it
`rick-rubin hits <dir> --tracks Snare --bars 1-4`: the ghost steps should read about 6 dB under the clap's
steps, and no ghost should share a step with the kick. In `reference compare`, "top-end activity" should rise
without "transient contrast" falling.

## Why it works
The four grid parts are the same in every house record, so they carry no information. The ear takes the
groove from the quiet hits around the strong beats, and from the fact that bar 4 differs from bar 2.
