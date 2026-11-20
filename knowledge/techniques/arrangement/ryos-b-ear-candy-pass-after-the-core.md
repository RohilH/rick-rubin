---
title: The ear-candy pass: once the core of a bass house drop works, decorate its gaps one element at a time
topic: arrangement
genres: [bass house, tech house]
source: RYOS — I Made A Bass House Banger! | Studio Time with Ryos EP. 36 (https://youtu.be/N_RgytoSM94?t=406)
status: untested
---
## What it is
A separate stage of work. After the call, the response, the sub and a basic beat exist, he spends the second
half of the session adding small one-off sounds. He says this is where the genre is fun and where the drop
starts to sound much better.

## When to use it
A drop that is correct but plain. Do not start it before the core riff works on its own (see
`mindset/ryos-b-two-sounds-must-carry-the-feeling.md`).

## How
1. Core first: "the main meat and potatoes", then the candy: vocal cuts, percussion, stabs, synth cuts (said,
   [6:46](https://youtu.be/N_RgytoSM94?t=406)).
2. One element at a time, each tried in a gap of the riff (all said): a clap figure and a filler over the
   kick ([7:26](https://youtu.be/N_RgytoSM94?t=446)), a quiet background synth and synth stabs
   ([8:49](https://youtu.be/N_RgytoSM94?t=529)), bass stabs, a "bass shot" and reverse synths
   ([10:37](https://youtu.be/N_RgytoSM94?t=637)), a hip-hop siren, which he likes in harder drops
   ([14:44](https://youtu.be/N_RgytoSM94?t=884)).
3. Hype vocal: he searches Splice for "hype vocal", takes the first that fits and speeds it up. A clip
   unmuted by mistake also stays, because it sounds good (said, [9:30](https://youtu.be/N_RgytoSM94?t=570)).
4. Tonal candy follows the track: the bass shot is made to follow the sub's notes, and a fill is replaced
   because its tonal content did not fit (said, [12:29](https://youtu.be/N_RgytoSM94?t=749)).
5. Soften the cut into the fill: Endless Smile used as a reverb on the vocal chop so it does not stop dry
   (said, [11:48](https://youtu.be/N_RgytoSM94?t=708)).
6. Then make a quick filler build so the drop is heard in context (said,
   [14:44](https://youtu.be/N_RgytoSM94?t=884)).
A drop built entirely from such one-shots is `arrangement/moonboy-drop-from-one-shot-chops.md`.

## In Rohil's setup
- Candidates come from Splice and from the project's own parts. Compare several per slot (`rick-rubin
  samples`, `rick-rubin audition`), and check anything tonal with `rick-rubin notes <dir> <file>` before use.
- Own-sound shots: `rick-rubin serum render "<preset>" --note C#2 --secs 0.5 --out samples/raw/shot.wav`.
- Place one: `rick-rubin logic add-audio samples/hype.wav --bar N --name "Hype Vox"` (lands on the bar line;
  Rohil nudges it, and speeds it up with Flex or varispeed).
- Which sound goes in which gap is written for the song; this card gives the order of work, not a pattern.

## How to check it
`rick-rubin hits <dir> --bars <drop>`: candy lands on steps where the riff is silent, not on top of it.
`rick-rubin reference compare <dir>`: texture changes per minute rise towards the bass house references;
top-end balance stays in range (see `mixing/ryos-pg-top-end-noise-budget.md`). Then a bounce for his ears.

## Why it works
A simple riff leaves holes; filling each with a different short sound gives the ear something new every bar
while the riff stays easy to follow.
