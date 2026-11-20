---
title: Progressive house drop drums, in the order he lays them: kick, rides, claps, 16th layer, fills, sparkle loop
topic: drums
genres: [progressive house]
source: RYOS — Making Beautiful Progressive House | Studio Time with Ryos EP. 50 (https://youtu.be/WnZ7GN1tpek?t=1270)
status: untested
---
## What it is
The drop's drum group built from samples in a fixed order, one job per element, with a fill that quotes the
melody's rhythm.

## When to use it
After the leads and bass exist: he says getting the drop drums down helps finalise chords and bass (said,
[21:00](https://youtu.be/WnZ7GN1tpek?t=1260)).

## How
1. Kick: a classic progressive house kick, four to the bar, with its tail trimmed shorter (said,
   [21:16](https://youtu.be/WnZ7GN1tpek?t=1276); sample FXP_kick_club_01 shown at 21:28). The break and build use
   a smaller, shortened kick, and he considers using the drop kick there instead (said,
   [30:41](https://youtu.be/WnZ7GN1tpek?t=1841)).
2. Noise rides (said, [21:30](https://youtu.be/WnZ7GN1tpek?t=1290); sample not readable), then a ride: his
   full "prog ride" was too splashy, so he cuts one slice and fades its tail (said, 21:45).
3. Claps: a clap loop he reuses across tracks (said, [22:33](https://youtu.be/WnZ7GN1tpek?t=1353)).
4. Something on 16ths: a shaker loop; he keeps one bouncy piece and repeats it, finds it too high and moves it
   down with a frequency shifter at -478 Hz (said and shown, [23:20](https://youtu.be/WnZ7GN1tpek?t=1400)).
5. Fills: a spray fill, and a big clap fill at the end of the phrase (said,
   [23:26](https://youtu.be/WnZ7GN1tpek?t=1406)).
6. Remove what masks the leads: a closed hat goes because it adds white noise on top of them; a small hat roll
   stays as an accent (said, [23:48](https://youtu.be/WnZ7GN1tpek?t=1428)).
7. Sparkle and dynamics: one percussion top loop, EQ'd, with a quarter-note volume duck. Shown at
   [24:38](https://youtu.be/WnZ7GN1tpek?t=1478): Kickstart 2, 1/4, mix 100 %, after he asks for it "a little heavier".
8. Last-bar fill: a snare playing the melody's rhythm, started by the closed-hat flam, with other drums and
   synths cut under it (said, [24:56](https://youtu.be/WnZ7GN1tpek?t=1496), [25:39](https://youtu.be/WnZ7GN1tpek?t=1539)).

## In Rohil's setup
Samples from Splice, several candidates per role compared with `rick-rubin audition` (PREFERENCES §3); the
kick card `ryos-kick-that-fits-the-genre.md` says what kind. Bring loops in with `rick-rubin logic add-audio
loop.wav --bar 25 --name "Perc loop"`, then `rick-rubin logic insert "Perc loop" "Kickstart 2" Mix=1.0`. Step 4:
Logic's Pitch Shifter moves a shaker down in semitones; a frequency shifter moves every partial by the same
number of Hz, which changes the tone more. Serum 2 has one (`--fx-add frequency_shifter`) for sounds made there;
for audio, try Logic's Ringshifter in its frequency-shift mode (read its names with `rick-rubin logic devices
Ringshifter` first). In `song.py`, the fill's onsets are the melody's (see `ryos-pg-two-rhythm-cells-melody.md`).

## How to check it
`rick-rubin spectrum` on the shaker before and after: the hump of energy should move down by a few hundred Hz.
`rick-rubin hits` on the fill bounce against the lead: same onsets. `rick-rubin reference compare`: top-end
activity and side energy above 4 kHz inside the references' range, and the drop's drums changing every 8 bars.

## Why it works
Each sample covers one band and one rhythmic level (beats, offbeats, 16ths), so nothing doubles. A fill that
copies the hook ties the drums to the song instead of sounding like a stock fill.
