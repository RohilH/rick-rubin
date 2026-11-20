---
title: Fit a chord-derived bassline to the track: copy the rhythm of the part above, leave gaps, thicken a thin saw with a sine
topic: bass
genres: [any, progressive house, tech house, bass house]
source: Alex Rome — My Insanely Simple System for Remixing Any Song (The 3-STEP FLIP) (https://youtu.be/bx8X7oiYhCg?t=443)
status: untested
---
## What it is
In all four of these videos the bass is the chord part with everything but its lowest notes deleted. That move
and the 40 to 80 Hz octave rule already have a card (`sound-design/alex-rome-c-bass-layer-from-the-chord-sound.md`).
This card is what he does next, which differs from video to video: which rhythm the bass takes, how long its
notes are, and how a thin sound is made heavy.

## When to use it
Straight after the chord-derived bass exists and sounds correct but slow, blurred or thin.

## How
1. Starting point, each time: chord notes copied to a bass track, upper notes deleted (said,
   [7:30](https://youtu.be/bx8X7oiYhCg?t=450), [3:30](https://youtu.be/ZkRds6iTfhQ?t=210),
   [9:57](https://youtu.be/XlltkalLaU4?t=597), [8:12](https://youtu.be/kSXHTJJ7D34?t=492)); octave chosen so the
   strongest peak is between 40 and 80 Hz (said, [8:06](https://youtu.be/bx8X7oiYhCg?t=486); shown
   [8:15](https://youtu.be/bx8X7oiYhCg?t=495): Channel EQ analyzer, fundamental near 45 Hz).
2. Rhythm, three cases:
   - under held pads, held bass notes are fine (the remix; shown [13:32](https://youtu.be/bx8X7oiYhCg?t=812): a
     track named for a sustained bass);
   - under chords that pulse, held notes sound slow, so he splits them to follow the chords' rhythm and keep the
     rhythms cohesive (said, [4:12](https://youtu.be/ZkRds6iTfhQ?t=252));
   - under a rhythmic pluck, he copies the pluck's notes themselves, so the bass matches it exactly: tighter and
     more bass-led (said, [8:12](https://youtu.be/kSXHTJJ7D34?t=492)).
3. Note length: shorten every note a little so neighbours do not touch. The rhythm becomes more obvious, and he
   says many house producers do it (said, [8:54](https://youtu.be/kSXHTJJ7D34?t=534); shown
   [9:05](https://youtu.be/kSXHTJJ7D34?t=545): small gaps between repeated notes).
4. Weight: a saw alone is a thin bass. He turns on the synth's sub oscillator as a sine (said,
   [8:27](https://youtu.be/bx8X7oiYhCg?t=507)). Alternatives he uses: a saw an octave down with unison 4, filtered
   to the sub (shown [10:40](https://youtu.be/XlltkalLaU4?t=640); unusual for him, he says), or an 808-style
   preset ([8:33](https://youtu.be/kSXHTJJ7D34?t=513)).
5. Test with the chords muted: bass, drums and melody alone (said,
   [11:07](https://youtu.be/XlltkalLaU4?t=667)).

## In Rohil's setup
40 to 80 Hz is E1 (41 Hz) up to D#2 (78 Hz); a root outside that range moves an octave (computed, not from the
video). Weight: `rick-rubin serum set "<bass preset>" sub.on=on --save bass-with-sub --project <dir>` (check the
sub's shape and level with `rick-rubin serum params --group sub`); see also
`sound-design/alex-rome-sine-sub-with-distortion.md`. Unison on a bass widens the lows: keep it mono below about
150 Hz. Kickstart 2 is on his bass at [10:40](https://youtu.be/XlltkalLaU4?t=640) (shown): `rick-rubin logic
insert Bass "Kickstart 2" Mix=0.6`. Write the three rhythm cases as alternatives and compare them on a bounce
(PREFERENCES §3). Ryos does the copied-rhythm version with slides instead of gaps:
`bass/ryos-pg-bass-copies-melody-rhythm-with-slides.md`.

## How to check it
`rick-rubin hits` on bounces of bass and the part above: onsets coincide where the rhythm was copied.
`rick-rubin notes <dir> bass.wav --fmin 30`: each note ends before the next starts. `rick-rubin spectrum <dir>
bass.wav`: strongest peak at 40 to 80 Hz on every note, with harmonics above it.

## Why it works
A bass that moves with the part above it reads as one instrument with that part; the gap before each note lets
its attack be heard, which is where a low note's rhythm lives.
