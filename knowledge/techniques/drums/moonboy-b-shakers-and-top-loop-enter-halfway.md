---
title: Loop the drop's drums for eight bars and bring the shaker and top loop in at bar five
topic: drums
genres: [tech house, bass house]
source: MOONBOY — HOW TO TECH HOUSE (John Summit, Dom Dolla, Chris Lake,) (https://youtu.be/_4qJSUFao50?t=85)
status: untested
---
## What it is

His 2023 tech house beat. The four-bar house pattern is duplicated to eight bars because the first section
of a drop is usually eight bars, then three "secret sauce" layers go on top: shakers, an accent percussion
loop for swing, and panned rides in 8ths. On screen the shaker and the percussion loop cover only the
second half of the eight.

## When to use it

Once kick, clap and offbeat hat loop. It is the quickest way to make bars 5 to 8 of a drop feel like a lift
over bars 1 to 4 without touching the kick or adding a fill.

## How

1. Tempo: tech house is around 123 to 128 BPM, he uses 128 (said,
   [0:42](https://youtu.be/_4qJSUFao50?t=42)). (His 2025 tutorial uses 130.)
2. Kick on every beat, clap on beats 2 and 4, a hat on every offbeat (said and captioned,
   [1:10](https://youtu.be/_4qJSUFao50?t=70)).
3. Rides in an 8th-note pattern across the whole loop (said; shown as a dense lane at
   [1:32](https://youtu.be/_4qJSUFao50?t=92)), panned left and right for width (said).
4. Duplicate to eight bars (said, [1:15](https://youtu.be/_4qJSUFao50?t=75)).
5. Add a shaker loop and a percussion top loop ("Astral Top Loop 01 – 128BPM" on screen). Both start at the
   midpoint of the loop and run to its end (shown at 1:32; he does not comment on the placement, so reading
   it as a deliberate lift at bar 5 is inferred).
6. Their job is swing and groove (said): they are the only parts of the kit that are not on the grid.
7. Levels are not shown here; his guide elsewhere keeps rides around 16 dB under the kick
   (`mixing/moonboy-auto-pan-rides-and-drum-level-guide`).

## In Rohil's setup

- Loops from Splice at the project tempo; shortlist a few and compare with `rick-rubin audition <dir>
  <files...>`. Check a loop's own swing before trusting it: `rick-rubin hits <dir> samples/top_loop.wav`
  shows which 16ths it accents.
- In Logic: `rick-rubin logic add-audio samples/shaker.wav --bar 5 --name Shaker`, the same for the top loop,
  then `rick-rubin logic set Shaker volume=-14` as a first pass (ours). High-pass both (Channel EQ low cut
  near 300 Hz) so they add no low end.
- In a `song.py`: the shaker and top-loop tracks appear only in the second half of the drop section, or in a
  variant section for bars 5 to 8.

## How to check it

`rick-rubin reference compare <dir>`: "top-end activity" rises between bars 1 to 4 and 5 to 8, and one more
texture change is counted per eight bars. `rick-rubin width <dir> --bars 5-8`: more side energy above 4 kHz
than bars 1 to 4, none below 150 Hz.

## Why it works

Eight bars of an unchanged loop is where attention drops. A layer that arrives halfway is heard as the
track stepping up, and loops played by a human hand loosen a grid that every other drum sits on exactly.
