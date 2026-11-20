# Mix and master: effects, returns, the master, and the comparison with released tracks

Parameter names below are Ableton Live's. In Logic the same `effects`, `sends`, returns and `master_effects` take Logic's plug-in and parameter names: see `skill/logic.md`.

## Does it sound like a record? `reference`

`check` and `eval` answer "is it correct?". A correct track can still sound flat. `reference` answers the other question by measuring your mix against released tracks in the genre, on the things a listener reacts to:

```
rick-rubin reference add ~/Music/some-released-track.wav ...   # once; any format; only measurements are kept, shared by all projects
rick-rubin reference list
rick-rubin reference compare <dir>                              # the Live capture (live.wav) against the shelf -> reference.md
```

It measures, on the loudest 30 seconds: loudness and crest (density), tonal balance per band and tilt, stereo side energy overall and per band, low-end pump (off-beat vs kick), transient contrast and top-end activity; and for development: how much the spectrum changes from one 2-bar block to the next, the share of near-identical blocks, texture changes per minute (2-bar blocks that differ clearly from the one before, in level or — with the level taken out — in which bands carry the energy, so a layer swapped for another at equal loudness counts) and loudness range. Each line is placed against the references' min–median–max, and whatever falls outside is listed.

Use it on a capture after the arrangement and balance are right, and treat every "outside the references" line as a question to answer — fix it, or write down why this track should differ. What it has shown so far on this library's own output, i.e. the ways an agent's track tends to come out flat:

- **Unmastered.** A balanced mix lands around −15 LUFS with 15 dB of crest; released tech house measures about −7.5 LUFS with 8.5 dB. Next to a record it is 7 dB quieter and far less dense, which reads as dull and weak however good the parts are. Finish with a master chain (`song.master_effects`) — gentle saturation, bus compression, then a Limiter doing real work — and iterate on captures until loudness and crest sit inside the references' range without clipped samples. Density on individual sounds (Saturator, compression on drums and bass) counts for more than limiter gain.
- **Mono top end.** References carry 4–29 % side energy above 4 kHz; a track built from centred one-shots has 2–3 %. Pan hats, percussion and tops apart, use stereo samples and loops for them, send them to a short reverb, widen with Utility `Stereo Width` — and keep everything below 150 Hz centred.
- **Too little change.** If movement sits at the bottom of the references' range or blocks repeat, the drop is a loop. Add and remove layers every 8 bars, vary fills, automate filters, change a Serum macro between sections (a second track with other `serum_params` works today), and make later drops measurably different from the first.
- **Velocity is steep.** At a high `Vol < Vel`, ghost notes disappear: at 80 % a velocity-23 hit is 30 dB under a velocity-116 one. Check the dB range your velocities produce (see "Levels mean the same everywhere") rather than assuming.

The offline preview cannot stand in for this: its stems are mono and it has no master chain. Compare captures.

## Effects and compressors

`rick-rubin devices <name> ...` loads a device in Live on a throwaway track and prints every parameter with its range, its menu choices and its default (remembered in `.cache/live-devices.json`, so it works without Live afterwards). Read it before writing an effect instead of guessing names.

A track's `effects` is an ordered list of Live audio effects placed after the instrument. Every parameter is set by the value Live displays, in Live's own names and units:

```json
{"op": "track", "name": "Bass", "set": {"effects": [
  {"device": "Compressor", "sidechain": "Kick", "sidechain_tap": "Post FX",
   "params": {"Threshold": -32, "Ratio": 6, "Attack": 0.1, "Release": 110, "Knee": 3,
              "Model": "Peak", "LookAhead": "1 ms", "Makeup": false, "S/C EQ On": false, "Dry/Wet": 100}}]}}
```

Numbers are dB, ms, Hz, % or the ratio's first figure (`"inf"` for a limiter); switches take true/false; menus take the option's name. Compressor parameters: Threshold, Ratio, Expansion Ratio, Attack, Release, Auto Release On/Off, Output, Makeup, Dry/Wet, Model (Peak | RMS | Expand), Env Mode (Lin | Log), Knee, LookAhead (0 ms | 1 ms | 10 ms), S/C Listen, S/C EQ On, S/C EQ Type, S/C EQ Freq, S/C EQ Q, S/C EQ Gain, S/C On, S/C Gain, S/C Mix. `sidechain` names the track that keys the device (a Compressor on the bass keyed from the kick is the house pump); `sidechain_tap` is Pre FX, Post FX or Post Mixer. The push report echoes what Live shows after setting each value and lists any name it did not find — an unknown parameter name is reported with the device's full parameter list, which is also how to discover the parameters of any other device (EQ Eight, Saturator, Reverb, Glue Compressor...). `sidechain: true` on a track remains the shorthand for a default kick-keyed Compressor (−28 dB, 4:1, 0.5 ms, 120 ms); `sidechain: "kickstart"` puts Kickstart 2 there instead (a tempo-locked volume shape, no routing; see the Logic section for its parameters — in Live, read them with `rick-rubin devices "Kickstart 2"` first: the VST3's names and values have only been checked in Logic). The offline preview only models the ducking, not the compressor's exact curve: tune compressors against `capture`.

## Returns, sends and the master

One shared reverb or delay on a return track instead of one per track — Ableton's A and B:

```python
song.add_return("A", [{"device": "Reverb", "params": {"Decay Time": 1800, "Predelay": 20, "Dry/Wet": 100}}])
song.add_return("B", [{"device": "Delay", "params": {"L 16th": 3, "R 16th": 4, "Feedback": 35, "Dry/Wet": 100}}])
clap = song.add_track("Clap", "clap", sample="samples/clap.wav", sends={"A": -14, "B": -22})     # dB; unlisted sends are off
song.master_effects = [{"device": "Limiter", "params": {"Ceiling": -0.3}}]
```

- Return chains are effect chains like a track's `effects` (keep them 100% wet). `push` makes the return hold exactly that chain, sets every track's send levels, and puts `master_effects` on the master. Live Intro/Lite have two returns (A, B).
- Offline, the preview approximates a Reverb or Delay that is first on a return (tail length from `Decay Time`, echoes from the 16ths/feedback), enough for `eval` and `width` to notice the space; its exact sound is Live's — check on a `capture`.
- Keep kick and bass out of the reverb; send what needs depth (claps, vocals, stabs, FX) and check the low end stays centred with `width`.
