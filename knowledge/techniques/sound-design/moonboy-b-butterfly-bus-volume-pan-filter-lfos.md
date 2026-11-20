---
title: The "butterfly effect": send synths and vocal to one bus and flutter its volume, pan and filter with three LFOs
topic: sound-design
genres: [progressive house, bass house]
source: MOONBOY — HOW TO MELODIC HOUSE (Knock2, Kx5, John Summit) (https://youtu.be/woNtFzXYB5Y?t=478)
status: untested
---
## What it is

One shared effect bus for the chord synths and the vocal hook. On it, a free-running LFO flutters the
volume, a second moves the pan, a third slowly opens and closes a low-pass, and the flutter's speed is
automated across the section. Because both sources pass through the same movement, they fuse into one
shimmering sound. He shows it again in his vocal video ([13:32](https://youtu.be/7wcJShg8tn4?t=812)).

## When to use it

On the big chord-and-vocal moment of a melodic break or drop. Not on drums or bass, and not on a dry
rhythmic tech house vocal.

## How

1. Group the synths and set the group's output to a bus instead of the master; later route the vocal to the
   same bus (said, [8:18](https://youtu.be/woNtFzXYB5Y?t=498), [11:33](https://youtu.be/woNtFzXYB5Y?t=693)).
2. On the bus: SerumFX with the noise oscillator set to the audio input and Note Latch on, so the incoming
   audio is treated as an oscillator (said and shown at [9:30](https://youtu.be/woNtFzXYB5Y?t=570)).
3. Volume: LFO 1 onto that level, level turned down and the depth turned up (said). Sync off for a free
   feel: 5.1 Hz, plain triangle, on screen (shown at 9:30). Add LFO smoothing (said).
4. Automate the LFO rate across the section: one point where it starts, one where it ends (said,
   [9:47](https://youtu.be/woNtFzXYB5Y?t=587)); values not readable.
5. Pan: LFO 2 onto the pan, a smaller amount (said, [10:07](https://youtu.be/woNtFzXYB5Y?t=607)).
6. Filter: MG Low 12 on the bus with LFO 3 on its cutoff, very slow; the cutoff knob reads 11 kHz with the
   modulated value at 6.9 kHz (shown at [10:40](https://youtu.be/woNtFzXYB5Y?t=640)), so the top end breathes
   rather than closes.
7. Variations by redrawing LFO 1: a choppy saw for a stutter, a rising ramp for a reversed feel (said,
   [11:54](https://youtu.be/woNtFzXYB5Y?t=714)).

## In Rohil's setup

- Bus: set the output of the chord stack and the vocal track to the same Bus in Logic (by hand: session mode
  has no output command); the Aux that appears is the "butterfly bus".
- On the Aux: `rick-rubin logic insert "<Aux>" Tremolo` twice and `rick-rubin logic insert "<Aux>" AutoFilter`
  (Aux strips need Logic in front). First Tremolo: phase 0°, free rate near 5 Hz, depth high: the flutter.
  Second: phase 180° (that is auto-pan), low depth. AutoFilter: low-pass near 11 kHz, its LFO slow.
  Read names first: `rick-rubin logic devices Tremolo AutoFilter`.
- Draw the first Tremolo's Rate automation by hand. Serum 2 FX is installed here and could do it in one
  device, but it loads as a MIDI-controlled effect and has not been tried.

## How to check it

Bounce the bus: `rick-rubin width`: correlation never negative, mid-band side % moving over time. `rick-rubin
eval` on the bars: the level wobbling at about the LFO rate, faster at the end than the start. `rick-rubin
transcribe` on the vocal through the bus still finds the hook's words.

## Why it works

Sounds that share the same amplitude and pan movement are heard as one source, so a vocal and a supersaw
moving together become a single instrument; an unsynced rate keeps it from sounding like a sidechain.
