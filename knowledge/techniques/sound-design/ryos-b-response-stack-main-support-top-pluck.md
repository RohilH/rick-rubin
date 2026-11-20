---
title: A bass house lead stack in four roles: harsh main, support, crisp top, plucky bass for attack
topic: sound-design
genres: [bass house, tech house]
source: RYOS — I Made A Bass House Banger! | Studio Time with Ryos EP. 36 (https://youtu.be/N_RgytoSM94?t=144)
status: untested
---
## What it is
How the "response" sound of his drop is built up from one harsh Serum lead into a stack that is thick, bright
and bouncy. The general rule is `sound-design/ryos-layer-by-contrast.md`; this is the bass house case.

## When to use it
A short-note riff sound that has the right character but sounds thin, dull on top, or has no punch.

## How
1. **Main.** Chain on screen: EQ, CamelCrusher, OTT, two more EQs ([4:17](https://youtu.be/N_RgytoSM94?t=257)).
   The first EQ cuts the sub; distortion and "a little bit of" OTT bring it to life (said,
   [2:24](https://youtu.be/N_RgytoSM94?t=144)). Because the sound is "wildly harsh" he then does heavy EQ: one
   band is a wide dip of about 3 dB near 3.85 kHz (shown, [4:17](https://youtu.be/N_RgytoSM94?t=257)). Another
   EQ cleans up the stereo image (said, [2:45](https://youtu.be/N_RgytoSM94?t=165); settings not shown).
2. **Support.** A second Serum patch under it ("LD Hooked", shown [2:51](https://youtu.be/N_RgytoSM94?t=171)).
3. **Top.** A "crispy, smooth" high layer; his first choice is swapped for a crisper preset (said,
   [4:33](https://youtu.be/N_RgytoSM94?t=273), [4:53](https://youtu.be/N_RgytoSM94?t=293)).
4. **Attack.** The stack still lacked bounce; a plucky bass layer was "the missing piece" (said,
   [5:14](https://youtu.be/N_RgytoSM94?t=314)).
5. **Group.** Pultec-style EQ, soothe2, Supercharger compressor, and Kickstart 2 last at 1/4, mix 100 %
   (shown, [4:51](https://youtu.be/N_RgytoSM94?t=291), [4:03](https://youtu.be/N_RgytoSM94?t=243)).
6. The mixer names the four tracks Main, Support, Top and Attack (shown,
   [11:42](https://youtu.be/N_RgytoSM94?t=702)).

## In Rohil's setup
- Four Serum 2 tracks in a summing stack. Pluck layer: see `bass/moonboy-tech-house-pluck-bass-in-serum.md`;
  the keys that matter are `env_1.decay_ms`, `env_1.sustain_db` and `filter_1.cutoff_hz`.
- Main: drive inside Serum with `--fx-add distortion fx.distortion.drive=40` (try several with `rick-rubin
  serum ab`), or Logic's Overdrive or Phat FX; then `rick-rubin logic insert "Resp Main" "OTT" Depth=30`; then
  Channel EQ with a low cut and a broad dip around 3 to 4 kHz, set from `rick-rubin spectrum`.
- Group: Vintage Tube EQ, Compressor, then `rick-rubin logic insert Response "Kickstart 2" Mix=1.0`. He has
  no soothe2; RESO is the nearest (loaded by hand), and what is lost is automatic tracking of the harshness.

## How to check it
`rick-rubin serum describe` on each layer: the pluck has the shortest attack and decay, the top layer the
highest spectral centre. `rick-rubin spectrum` of the four bounced layers: each is strongest in a different
band. `rick-rubin width <dir> response.wav`: low band mono, sides only above the low mids.

## Why it works
One patch rarely has body, air and a hard front edge at once. Giving each quality its own layer lets each be
turned up or down, and one group chain makes them move as one sound.
