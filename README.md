# ableton-use

**A toolkit that lets coding agents (Claude Code, Codex, …) produce house tracks by conversation and render them straight into Ableton Live.** There is no custom agent harness: your coding agent is the harness. It reads `SKILL.md` and drives the `ableton-use` CLI / Python API with its own shell and file tools.

Describe a track ("deep house, 121 BPM, dub chords, long DJ intro, big second drop"), the agent proposes a plan, builds the arrangement, checks its own work, and pushes a full Arrangement View into Live. That includes tracks, instruments, MIDI clips, section locators, filter automation and kick-keyed sidechain.

Inspired by [browser-use/video-use](https://github.com/browser-use/video-use) and borrows its core idea: **the LLM never listens to the music, it reads it.**

| video-use | ableton-use |
|---|---|
| Word-level transcript packed into `takes_packed.md` | Packed score in `score.md`: arrangement map, energy curve, every pattern as step strings or note events (~6 KB per track) |
| `timeline_view` filmstrip + waveform, on demand | `view`: piano roll + waveform + spectrogram for a bar range, on demand |
| `edl.json` is the edit decision list | `song.json` holds tracks, a pattern library, and sections saying who plays what |
| ffmpeg render, then self-eval at every cut | Preview render, then lint plus per-section loudness and spectral checks (max 3 passes) |
| `final.mp4` | Ableton Live arrangement via the bridge, plus `.mid` files |
| `project.md` memory | `project.md` memory |
| 12 hard rules, artistic freedom elsewhere | 12 house production rules, artistic freedom elsewhere |

## Why this design

Sending raw audio to an LLM is token-expensive and gives poor feedback. MIDI dumps are precise but unreadable. The packed score sits in between. A 5-minute house track fits in about 6 KB of markdown that a model can reason about bar by bar. Two kinds of checks then confirm the result:

* **Symbolic lint** catches correctness problems:
  * phrase lengths
  * DJ-friendly intro and outro
  * key
  * bass range and monophony
  * kick/bass collisions
  * mud below C2
  * drops without tension
* **Measurement** of an offline numpy preview render, per section:
  * integrated LUFS (BS.1770)
  * crest factor
  * six-band spectral balance
  * whether loudness follows the intended energy curve
  * breakdown-vs-drop contrast

## Install

```bash
pip install -e ".[all]"        # numpy, scipy, matplotlib (for views)
ableton-use install-bridge     # copies the AbletonUse remote script into Live's User Library
```

To connect Live, restart it, then open **Settings → Link, Tempo & MIDI → Control Surface** and choose **AbletonUse**. Live shows "ableton-use bridge … listening on 127.0.0.1:9889". To check the connection:

```bash
ableton-use status
```

Requirements: Live 11+. Live 12 is recommended. Arrangement clips are created directly with `Track.create_midi_clip`. On older versions the bridge falls back to building each clip in a session slot and copying it to the arrangement. Inserting devices by name uses `Track.insert_device` on Live 12.3+ and the browser otherwise.

## Use it

### With Claude Code (or any coding agent) — the intended way

Paste the setup prompt from [`install.md`](install.md) into your agent, or do it by hand:

```bash
ln -s "$PWD" ~/.claude/skills/ableton-use
cd ~/music/new-track && claude
> make a deep house track, 121bpm, F dorian, dubby chords, DJ-friendly, then put it in Ableton
```

The agent follows `SKILL.md`: inventory → questions → plan → confirm → edit → eval → push → remember.

### CLI

```bash
ableton-use new ~/music/sunrise --subgenre deep --template club --seed 4 --title "Sunrise Dub"
ableton-use edit ~/music/sunrise ops.json      # JSON edit ops (see SKILL.md)
ableton-use eval ~/music/sunrise               # lint + preview.wav + measurements -> eval.md
ableton-use view ~/music/sunrise --bars 61-80  # PNG of the build into the drop
ableton-use push ~/music/sunrise               # build it in Live (--replace to re-push)
```

### Python

```python
from ableton_use import Project

p = Project.create("~/music/sunrise", subgenre="deep", template="club", key="F dorian", seed=4)
p.edit([
    {"op": "generate", "what": "bass", "name": "bass_roll", "options": {"style": "rolling"}},
    {"op": "part", "section": "drop2", "track": "Bass", "pattern": "bass_roll"},
    {"op": "automation", "section": "build", "track": "Pad", "param": "filter", "points": [0.3, 1.0]},
])
print(p.evaluate().text)
p.push(replace=True)
```

## Samples (Splice or your own)

```
ableton-use sample my-track kick.wav  --name kick --oneshot              # drum one-shot -> Simpler (One-Shot mode)
ableton-use sample my-track organ.wav --name bass --oneshot --melodic    # measures the pitch -> sample_root
ableton-use sample my-track top.wav   --name top  --loop --src-bpm 128 --bars 8   # tempo-matched, cut to 8 bars
ableton-use sample my-track riser.wav --name riser --loop --src-bpm 130 --bars 8 --align end
```

Each command prints the edit op that wires the sample into the song. One-shots play from a Simpler on a MIDI
track (melodic ones are tuned from their *measured* pitch — filenames lie about octaves); loops sit unwarped on
audio tracks because they are conformed to the song tempo on import (needs `ffmpeg`). The preview render and the
self-eval use the same files, so what you measure is what Live will play for those tracks. An agent with the
Splice MCP connected can search, download and import in one go — see "Using Splice / samples" in `SKILL.md`.

## What gets built in Live

* Tempo, 4/4, and one locator per section.
* One MIDI track per song track (an audio track for loop tracks), with name, colour, volume (dB-accurate) and pan.
* Sample tracks: a Simpler holding the one-shot, in One-Shot mode for drums or tuned Classic mode for melodic parts. Loop tracks: unwarped audio clips, one per pass of the loop.
* An instrument loaded by browser name, tried in order. For example, a drum track tries `909 Core Kit`, then `Kit-Core 909`, then `Drum Rack`. Set `instrument` per track to use your own presets or plug-ins.
* One arrangement clip per (section, track), named `section · pattern`. Notes include baked-in swing.
* Filter automation written as clip envelopes on an Auto Filter that the bridge inserts.
* Sidechain: a Compressor on each `sidechain: true` track, with its sidechain input routed to the Kick track.

The push report lists anything that needs a human: an instrument not found, a sidechain that couldn't be routed, or a failed envelope.

## Layout

```
ableton_use/
  model.py        Song / Track / Pattern / Section; flatten() -> arrangement clips
  theory.py       keys, scales, diatonic chords, voice leading, chord naming (C3 = 60)
  house.py        subgenre profiles (classic/deep/tech), pattern generators, arrangement templates
  score.py        packed text score (primary reading view)
  edits.py        JSON edit ops (the agent's write interface)
  analysis.py     lint rules + BS.1770 loudness + spectral checks -> eval.md
  views.py        on-demand piano-roll / waveform / spectrogram PNG
  render/midi.py  dependency-free SMF export
  render/preview.py  numpy sketch synth with sidechain + filter automation
  live/client.py  bridge client + push_song()
  live/remote_script/AbletonUse/  Live remote script (TCP JSON bridge; handlers testable without Live)
  samples.py      sample import: pitch detection, tempo-conforming loops, 24-bit WAV io
  project.py      project folder, history/undo, project.md memory
SKILL.md          agent instructions: principles, hard rules, process, house craft
install.md        setup prompt + steps for your coding agent
docs/HOUSE.md     research notes behind the defaults
```

## Limitations

* The preview synth is only a sketch for measuring rhythm, balance and arrangement. It is not a mixdown. Compare its sections against each other, not against commercial masters.
* Live's API cannot draw sound design. The agent chooses instruments by name and writes notes and automation; timbre is down to your presets.
* The bridge is tested against a simulated Live Object Model, not a real Live install. The first real push is the moment to watch for API differences between Live versions. The push report and Live's `Log.txt` will show them.
* House is the first-class genre. The model, edits and bridge are genre-agnostic, so adding profiles and templates for techno, garage or DnB is mostly data.

## Tests

```bash
pip install -e ".[dev]" && pytest -q
```

The tests cover theory, JSON round-trips, flattening and swing, the edit ops, lint rules, MIDI round-trips, preview rendering and analysis. They also run a full `push_song` over a real socket against a fake Live Object Model.
