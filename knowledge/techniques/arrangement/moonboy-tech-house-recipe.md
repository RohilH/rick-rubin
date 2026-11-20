---
title: Tech house according to MOONBOY: tempo, the parts, what each does, and the order he builds them
topic: arrangement
genres: [tech house]
source: MOONBOY — HOW TO TECH HOUSE | Full Tutorial (Odd Mob, Chris Lake, Mau P) (https://youtu.be/JqKaSvHImB0?t=21)
status: untested
---
## What it is
A one-page genre sheet from his tutorial: what must be in a tech house loop for it to read as tech house,
and in which order to make it. It covers the loop only; he does not arrange it into a track.

## When to use it
As the checklist when starting a tech house sketch, and when a loop "does not sound like tech house": find
the row that is missing or doing the wrong job.

## How
Tempo: 120 to 130 BPM for house; 130 for an upbeat tech house track (said, [1:44](https://youtu.be/JqKaSvHImB0?t=104)).

| Part | What it is doing | His settings |
|---|---|---|
| Kick | every beat; owns the downbeats | from his house kit (said) |
| Clap | beats 2 and 4; thickened with a limiter | ceiling −3 dB (said), +11 dB in (shown) |
| Hat | every offbeat 8th | one closed hat (shown) |
| Crash | beat 1 of the phrase, impact | about −6 dB (shown) |
| Ghost snare and clap | weak 16ths around the downbeat and before the turnaround: the swing of the kit | −6 dB (said) |
| Drum group | one instrument: soft clip for loudness, band-pass switched on for fills | Glue soft clip; band-pass near 1 kHz (shown) |
| Groove bass | offbeat 8ths on the root, low, mono, plucky; sets the rhythm of the track | saw + sub, MG Low 12, LFO as envelope at 1/8 (shown); D#0/E0 (shown) |
| Character bass | acid, stutter or borrowed bass sound on top; the groove keeps playing | Serum 2 presets (shown) |
| Vocal | the hook people remember; treated as a synth | tune 100 %, vocoder 20 bands, OTT (shown) |

Order he builds in:
1. Tempo, then kick, clap, hat, crash; loop 2 bars, duplicate to 4 ([2:05](https://youtu.be/JqKaSvHImB0?t=125)).
2. Ghost hits for groove ([2:48](https://youtu.be/JqKaSvHImB0?t=168)).
3. Group, level, soft clip, clap limiter, filter fill ([3:37](https://youtu.be/JqKaSvHImB0?t=217)).
4. Bass sound in Serum 2 ([7:07](https://youtu.be/JqKaSvHImB0?t=427)), then the bassline ([11:57](https://youtu.be/JqKaSvHImB0?t=717)).
5. Vocal: find it, tune it, vocode it, compress it ([13:17](https://youtu.be/JqKaSvHImB0?t=797)).

What he says makes it tech house rather than house: it is "minimal and groovy"; three elements; the creative
effort goes into the bass sound and the vocal processing, and into how much rhythm a few parts can carry
([0:21](https://youtu.be/JqKaSvHImB0?t=21)).

Missing from the video, to take from other sources: swing amount, sidechain, arrangement (intro, build,
breakdown, drop lengths), risers and impacts, reverb and delay sends, the master chain.

## In Rohil's setup
`rick-rubin init <dir> --title "..." --bpm 130 --key "E minor"` for a new sketch; the default lint already
assumes club house at 118 to 130 BPM (`skill/genres.md`, which puts tech house at 124 to 128 and nearly
straight: his 130 is the fast end). Each row above has its own card: drums
(`drums/moonboy-house-beat-plus-ghost-hits`), drum group (`mixing/moonboy-drum-group-soft-clip`), bass sound
(`bass/moonboy-tech-house-pluck-bass-in-serum`), bassline (`bass/moonboy-offbeat-bassline-and-its-variations`),
vocal (`sound-design/moonboy-vocoder-vocal-chain`). The parts are still written by hand for each track.

## How to check it
`rick-rubin eval <dir>` with 0 errors, then a Logic bounce and `rick-rubin reference compare <dir>` against
released tech house: loudness, low-end pump and top-end activity inside the references' range. The loop is
not a track until an arrangement exists; this sheet does not get you there.

## Why it works
With so few parts, each one has a single job and none overlap: kick on the beat, bass between the beats,
ghost hits for swing, vocal for memory. Anything added has to earn a job the others do not have.
