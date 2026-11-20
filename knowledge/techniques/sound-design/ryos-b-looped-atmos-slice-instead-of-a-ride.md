---
title: Fill the top of a drop with a looped slice of an atmosphere sample, turned down and sidechained
topic: sound-design
genres: [bass house, tech house, any]
source: RYOS — I Made A Bass House Banger! | Studio Time with Ryos EP. 36 (https://youtu.be/N_RgytoSM94?t=487)
status: untested
---
## What it is
Where a ride or noise layer would normally fill the space above the kick, he uses a short piece cut from a
tonal atmosphere sample, looped, quiet and pumping. He calls it "more interesting" than a cymbal.

## When to use it
A drop that needs constant energy in the upper mids and highs but already has hats, or where a ride makes it
sound generic.

## How
1. Notice the gap: he wants a filler above the kick. A ride fits, but he holds it back to try synth material
   first (said, [7:46](https://youtu.be/N_RgytoSM94?t=466), [8:07](https://youtu.be/N_RgytoSM94?t=487)).
2. Take a tonal atmosphere sample in the track's key. On screen it is an "atmos shot" from his own pack,
   labelled C sharp minor (shown, [8:37](https://youtu.be/N_RgytoSM94?t=517)).
3. Scrub through it for a spot that sounds good and loop a short slice of that spot (said,
   [8:28](https://youtu.be/N_RgytoSM94?t=508)). The slice length is not readable.
4. Lower it and sidechain it "so it sounds halfway decent": Kickstart 2 at 1/4, mix 100 %, with the fader
   pulled well down (said; shown, [8:37](https://youtu.be/N_RgytoSM94?t=517)).
5. He then adds one more quiet synth texture the same way (said, [8:49](https://youtu.be/N_RgytoSM94?t=529)).
6. The ride is not thrown away: later a rattle ride and the ride are layered for part of the drop (said,
   [10:13](https://youtu.be/N_RgytoSM94?t=613)).

## In Rohil's setup
- Find the sample (Splice: atmosphere, drone or texture in the song's key) and confirm the key with
  `rick-rubin notes <dir> samples/atmos.wav`.
- Cutting and looping the slice is region work in Logic (or Quick Sampler with a loop), so Rohil does it; or
  the agent cuts the slice to a file and places it: `rick-rubin logic add-audio samples/atmos_slice.wav --bar N
  --name "Atmos Loop"`.
- `rick-rubin logic insert "Atmos Loop" "Kickstart 2" Mix=1.0` and `rick-rubin logic set "Atmos Loop"
  volume=-14` as a first level, then by ear. A low cut with Channel EQ keeps it out of the bass.
- In a `song.py`: a sample track with the slice on every bar and `sidechain="kickstart"`.

## How to check it
Bounce the drop with and without the loop: `rick-rubin compare <dir> without.wav with.wav` shows a little
more energy above about 2 kHz and no change below 200 Hz. The loop alone dips on every beat. If `rick-rubin
reference compare` shows the top end above the references, lower it or drop a hat.

## Why it works
A tonal texture adds brightness that is in key and unique to the track, where a ride adds only noise; ducked
hard and kept low it reads as air around the beat.
