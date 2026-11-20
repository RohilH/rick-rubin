---
title: Bass house according to MOONBOY: tempo, the parts, what each does, and the order he builds them
topic: arrangement
genres: [bass house]
source: MOONBOY — HOW TO BASS HOUSE (Knock2, Skrillex, Porter Robinson) (https://youtu.be/3-0JCDyiPaw?t=65)
status: untested
---
## What it is
A one-page genre sheet from his tutorial: the parts of a festival-style bass house track, the job of each,
and his build order. His version leans on trance for the breakdown and on complextro for the drop.

## When to use it
As the checklist for a bass house sketch, and to see what separates it from tech house: a separate sub, a
mid bass that is also the lead, real melody and pads in the breakdown, and a drop in two alternating halves.

## How
Tempo: 126 to 128 BPM; he uses 126 (said, [1:10](https://youtu.be/3-0JCDyiPaw?t=70)). Key: F# minor (said).

| Part | What it is doing | His settings |
|---|---|---|
| Kick, clap, offbeat hat | the house frame; clap a few ms ahead of the kick | kick 0 dB, clap 0 dB (shown) |
| Crash, rides | impact on beat 1; a quiet wide top layer | −12 dB and −16 dB; rides auto-panned (shown) |
| Accent snares, reverse kick | swing around beat 3; pull into the next phrase | last beat of bar 4 (shown) |
| Pluck lead | breakdown melody in cells of three 16ths | unison saws, low-pass plucked per note, delay and reverb (shown) |
| Pad | long root notes under the melody (D, E, F#) | saw, 15 voices, detuned, low-pass, phaser, reverb (shown) |
| Rave lead | the melody's notes held long in the build | preset, 16-voice oscillators (shown) |
| Mid bass ("space laser") | the drop's hook: two 16ths and an 8th per beat, rising by step | two saws (2 and 16 voices), high-pass swept per note, big chain (shown) |
| Sub | the low end with its own bounce, a third under the lead | triangle, tube distortion, ducked, offbeat pitch bends (said and shown) |
| Vocal | the human element; clean copy plus a pad made from it | width, delay, reverb, compressor; parallel wash (shown) |
| Chops | drop B: one-shots from bass, vocal and synths taking turns | in key, bus-compressed, sidechained (shown) |

Order he builds in:
1. Drums ([1:05](https://youtu.be/3-0JCDyiPaw?t=65)), then their extras and levels.
2. "The vibe": pluck lead and trance melody ([2:39](https://youtu.be/3-0JCDyiPaw?t=159)), pad
   ([3:36](https://youtu.be/3-0JCDyiPaw?t=216)), rave lead ([4:30](https://youtu.be/3-0JCDyiPaw?t=270)).
3. Basses: mid bass ([4:55](https://youtu.be/3-0JCDyiPaw?t=295)), then sub ([6:13](https://youtu.be/3-0JCDyiPaw?t=373)).
4. Vocal and its two racks ([7:19](https://youtu.be/3-0JCDyiPaw?t=439)).
5. The drop: chops ([10:07](https://youtu.be/3-0JCDyiPaw?t=607)), sub against lead
   ([10:50](https://youtu.be/3-0JCDyiPaw?t=650)), A and B halves of two bars each from bar 89
   ([11:35](https://youtu.be/3-0JCDyiPaw?t=695)).

Shape of his track, from the markers: a melody section around bar 65, a build at bar 81, the drop at bar 89
(shown). Synths, basses, chops and FX all pass through one "Sidechain" bus; drums and vocals do not (shown;
what is on the bus is not).

Missing from the video: how the build is made, risers and impacts, the intro and outro, any mix or master.

## In Rohil's setup
`rick-rubin init <dir> --title "..." --bpm 126 --key "F# minor"`. One card per row: drums
(`drums/moonboy-bass-house-drum-layers`, `drums/moonboy-clap-slightly-before-the-kick`), melody
(`melody/moonboy-trance-melody-in-three-sixteenth-cells`), sounds (`sound-design/moonboy-pluck-lead-with-filter-envelope`,
`sound-design/moonboy-detuned-saw-pad`, `sound-design/moonboy-space-laser-bass`), sub
(`bass/moonboy-triangle-sub-with-distortion-and-pitch-bends`), drop (`arrangement/moonboy-a-b-drop-sections`,
`arrangement/moonboy-drop-from-one-shot-chops`, `harmony/moonboy-sub-a-third-below-the-lead`). All Serum
sounds here translate to Serum 2 directly; the parts are written by hand for each track.

## How to check it
`rick-rubin eval <dir>`: breakdown at least 3 LU under the drop. After a Logic bounce, `rick-rubin reference
compare <dir>` against released bass house: loudness, low-end pump, side energy above 4 kHz and texture
changes per minute inside the references' range. Nothing wide below 150 Hz (`rick-rubin width`).

## Why it works
The contrast is the genre: a wide, melodic, kickless breakdown makes the mono, percussive drop hit harder,
and inside the drop the A and B halves repeat that contrast every two bars.
