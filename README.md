# rick-rubin

**A toolkit that lets coding agents (Claude Code, Codex, …) produce house tracks by conversation and render them straight into Ableton Live.** There is no custom agent harness: your coding agent is the harness. It reads `SKILL.md` and drives the `rick-rubin` CLI / Python API with its own shell and file tools.

Describe a track ("deep house, 121 BPM, dub chords, long DJ intro, big second drop"), the agent proposes a plan, builds the arrangement, checks its own work, and pushes a full Arrangement View into Live. That includes tracks, instruments, MIDI clips, section locators, filter automation and kick-keyed sidechain.

Inspired by [browser-use/video-use](https://github.com/browser-use/video-use) and borrows its core idea: **the LLM never listens to the music, it reads it.**

| video-use | rick-rubin |
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

## Setup

You need macOS or Windows with **Ableton Live 11 or later** (Live 12 recommended; any edition, though Intro's 16-track limit applies), **Python 3.10+**, and a coding agent with shell access (Claude Code, Codex, …). The fastest way is to paste the setup prompt from [`install.md`](install.md) into your agent. By hand:

**1. Clone and install**

```bash
git clone https://github.com/dadams22/rick-rubin.git
cd rick-rubin
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[all]"
rick-rubin --help
```

Optional extras, only if you want the feature:

| Extra | Adds | Install |
|---|---|---|
| `serum` | Hosting Serum 2 presets (macOS, needs Serum 2 installed) | `pip install -e ".[serum]"` |
| `transcribe` | Word-level timing of vocal samples | `pip install -e ".[transcribe]"` |
| `dev` | Tests and linters | `pip install -e ".[dev]"` |

`ffmpeg` is needed to tempo-match sample loops, read non-WAV reference tracks and write mp3s (`brew install ffmpeg`). Everything else works without it.

**2. Install the Live bridge**

```bash
rick-rubin install-bridge     # copies the RickRubin remote script into Live's User Library
```

Restart Live, open **Settings → Link, Tempo & MIDI**, and under **Control Surface** choose **RickRubin**. Live's status bar shows "rick-rubin bridge … listening on 127.0.0.1:9889".

**3. Check the connection**

```bash
rick-rubin status             # {"bridge": "0.7.1", "live_version": "12.x.y"}
```

If this fails, check that the control surface is selected and that Live is running. For recording from Live (`rick-rubin capture`), Live's audio engine must be on: pick an Output Device in **Settings → Audio**.

**4. Register the skill with your agent**

```bash
ln -sfn "$PWD" ~/.claude/skills/rick-rubin      # Claude Code
# ln -sfn "$PWD" ~/.codex/skills/rick-rubin     # Codex
```

**5. Start a song**

```bash
rick-rubin init ~/music/night-bus --title "Night Bus" --bpm 126 --key "A minor"
cd ~/music/night-bus && claude
```

Open an **empty Live set** before the agent pushes: a push builds the arrangement in whatever set is open.

Notes on Live versions: arrangement clips are created directly on Live 12; on Live 11 each clip is built in a session slot and copied to the arrangement. Inserting devices by name uses Live 12.3+ and the browser otherwise.

## Ableton Live: setup and troubleshooting

### How it connects

`rick-rubin install-bridge` copies a small MIDI Remote Script, `RickRubin`, into Live's User Library (`~/Music/Ableton/User Library/Remote Scripts` on macOS, `Documents\Ableton\User Library\Remote Scripts` on Windows). Once selected as a Control Surface, it listens on `127.0.0.1:9889` (this machine only) and the `rick-rubin` commands talk to it. Nothing is written into your Live set until you run `push`, `watch`, `capture` or `ab --live`.

Before the first push:

- Open an **empty set**. `push` adds tracks to the open set; `--replace` deletes tracks with the same names first, and `--clean` also removes the set's untouched empty tracks.
- In **Settings → Audio**, make sure an **Output Device** is chosen. Pushing works without one; recording from Live does not.
- While a `capture` or `ab --live` is running, leave Live's transport and mixer alone. A take that was disturbed is thrown away and redone.

### Troubleshooting

| What you see | Cause and fix |
|---|---|
| `RickRubin` is not in the Control Surface list | Live reads Remote Scripts at start-up: restart Live after `install-bridge`. If your User Library is somewhere else (Settings → Library shows where), run `rick-rubin install-bridge --dest "<User Library>/Remote Scripts"`. |
| `cannot reach the rick-rubin bridge at 127.0.0.1:9889` | Live is not running, or the control surface is not selected. Select it under Settings → Link, Tempo & MIDI. If it is selected, set it to None and back to RickRubin. |
| The bridge is selected but still unreachable | Another program holds port 9889, or the script failed to load. Search Live's `Log.txt` for "rick-rubin" (macOS: `~/Library/Preferences/Ableton/Live x.x.x/Log.txt`; Windows: `%APPDATA%\Ableton\Live x.x.x\Preferences\Log.txt`). |
| `rick-rubin status` shows an older bridge version than the repo | You updated the code but Live still runs the old script. Run `rick-rubin install-bridge`, then set the Control Surface to None and back to RickRubin (or restart Live). |
| `Live's audio engine is off` or `Live's transport is not moving` | Live has no audio output. This happens when the device it used goes away or the device list changes (headphones, a monitor, a call app). Choose an Output Device in Settings → Audio, then run the command again. |
| A push warns `no sidechain source 'Kick' among ['(none)']` | Same cause: with the audio engine off, tracks offer no routing, so sidechains are not connected. Fix the Output Device, then push again. |
| `Live set already has tracks [...]` | The set already holds tracks with those names. Push with `--replace`, or open an empty set. |
| Tracks are missing, or track creation fails part-way | Live Intro allows 16 tracks and Lite 8, and a new set's default tracks count. Push with `--replace --clean`, and keep the song within the limit. |
| `none of <instrument> found in the Live browser` | That instrument is not in your edition of Live or your library. Run `rick-rubin browse` to see what is there, and name one of those in `song.py`. |
| `gave up after 3 takes: each one was disturbed` | Something changed in Live during every recording (transport, tempo, solo, mute, volume or pan). Leave Live alone until the capture finishes. |
| `Live is in use by another rick-rubin run` | Two commands tried to drive Live at once (two agents, or a `watch` left running). Wait for the other to finish or stop it. |
| A capture sounds different from the offline preview | Expected. The preview is a sketch; what Live plays is the reference. Judge sound on `rick-rubin capture`. |

## Logic Pro

The same song renders into **Logic Pro 11** (macOS): `rick-rubin --daw logic push <dir>` builds the project —
tempo, markers, named tracks and regions, a Logic patch or named instrument per track, the mixer, effects chains
with their parameters, kick-keyed sidechain compressors, returns (busses with an Aux each) and sends, the master
chain — and saves it as `<project>/logic/<title>.logicx`. `--daw logic capture` is an offline bounce. Nothing is
installed into Logic: the song goes in as a MIDI file Logic opens as a project, and the mixer, plug-ins and
dialogs are driven through macOS accessibility plus a Mackie Control that Logic detects on its own.
`rick-rubin split <dir> refs/track.wav` uses Logic's own Stem Splitter to separate a recording into vocals, drums,
bass, guitar, piano and other stems. `pip install -e ".[logic]"`, grant your terminal Accessibility permission, and
read [`docs/LOGIC.md`](docs/LOGIC.md) for what is built, what differs from Live and troubleshooting.

## Use it

### With Claude Code (or any coding agent) — the intended way

Paste the setup prompt from [`install.md`](install.md) into your agent, or do it by hand:

```bash
ln -s "$PWD" ~/.claude/skills/rick-rubin
cd ~/music/new-track && claude
> make a deep house track, 121bpm, F dorian, dubby chords, DJ-friendly, then put it in Ableton
```

The agent follows `SKILL.md`: inventory → questions → plan → confirm → edit → eval → push → remember.

### CLI

```
rick-rubin init ~/music/night-bus --title "Night Bus" --bpm 126 --key "A minor"
# write the song in ~/music/night-bus/song.py (see "Writing a song" in SKILL.md), then:
rick-rubin score ~/music/night-bus            # the song as a compact text score
rick-rubin eval ~/music/night-bus             # lint + offline render + measurements
rick-rubin view ~/music/night-bus --bars 33-48
rick-rubin push ~/music/night-bus             # build it in Live
rick-rubin capture ~/music/night-bus          # record Live's output and measure that
```

### The song is Python

```python
from rick_rubin import Song

song = Song("Night Bus", bpm=126, key="A minor", swing=56)
kick = song.add_track("Kick", "kick", sample="samples/kick.wav")
bass = song.add_track("Bass", "bass", sample="samples/bass.wav", sample_root=36.0, sidechain=True)

four = song.pattern("four", kick, "x...x...x...x...")
line = song.pattern("line", bass, ["1.3 A0 0.35; 2.3 A0 0.35 v108; 3.3 A0 0.35; 4.4 G0 0.2",
                                   "1.3 F0 0.35; 2.3 F0 0.35 v108; 3.3 G0 0.35; 4.3 E0 0.3"])
line_busy = line.variant("line_busy", add={1: "2.2 A0 0.2 v80; 2.4 A1 0.2"}, mono=True)

drop = song.add_section("drop", 16, kind="drop", energy=9, parts={kick: four, bass: line})
drop2 = drop.variant("drop2", energy=10, add={bass: line_busy})
song.arrange(drop, drop2)
```

There are no templates, generators or presets: the agent writes every note. Patterns and sections are plain
Python variables that can be derived from (`variant`) and reused.

## Starting a song, and house rules

`rick-rubin init` copies `project-template/` — a scaffold with no musical content: a `CLAUDE.md` for the
song, an empty `song.py`, `project.md` (brief, exploration log, decisions) and a sample manifest. The
project's `CLAUDE.md` imports `PREFERENCES.md` from this repo, so standing preferences (no templates;
explore, don't one-shot; judge on Live's audio) are written once and apply to every song.

`rick-rubin check <dir>` lints and type-checks `song.py` (ruff, mypy), builds it and runs the music lint;
the scaffold ships the config. `rick-rubin audition <dir> <files...>` compares candidate samples by measurement,
`rick-rubin samples <dir> snappy dark` and `rick-rubin serum search bass subby mono` search samples and Serum
presets by how they sound, and
`rick-rubin browse "sounds/Bass"` lists Live's instruments and presets — the tools that make exploring cheap.

## Samples (Splice or your own)

```
rick-rubin sample my-track kick.wav  --name kick --oneshot              # drum one-shot -> Simpler (One-Shot mode)
rick-rubin sample my-track organ.wav --name bass --oneshot --melodic    # measures the pitch -> sample_root
rick-rubin sample my-track top.wav   --name top  --loop --src-bpm 128 --bars 8   # tempo-matched, cut to 8 bars
rick-rubin sample my-track riser.wav --name riser --loop --src-bpm 130 --bars 8 --align end
```

Each command prints the edit op that wires the sample into the song. One-shots play from a Simpler on a MIDI
track (melodic ones are tuned from their *measured* pitch — filenames lie about octaves); loops sit unwarped on
audio tracks because they are conformed to the song tempo on import (needs `ffmpeg`). The preview render and the
self-eval use the same files, so what you measure is what Live will play for those tracks. An agent with the
Splice MCP connected can search, download and import in one go — see "Using Splice / samples" in `SKILL.md`.

## Reading tools for vocals and width

```
rick-rubin transcribe my-track samples/vocal.wav    # which syllable falls on which 16th, and how many ms off
rick-rubin retime my-track samples/vocal.wav --name vocal_q   # slide each word onto the grid
rick-rubin notes my-track samples/vocal.wav         # the notes a sample sings: pitch with octave, cents, length
rick-rubin width my-track [file]                    # stereo image as numbers: correlation, side %, mono loss, per band
rick-rubin serum list --folder Pad                  # search installed Serum 2 presets
rick-rubin serum show "<preset>"                    # a preset as a text patch sheet
rick-rubin serum render "<preset>" --note F1 --out x.wav   # play a preset through the real plug-in, offline
```

`rick-rubin reference compare <dir>` measures a Live capture against released tracks you add with `reference add`
(loudness, density, balance, width, pump, movement) — the check for "correct but flat".

These exist so an agent can read what a producer would hear or see on a meter or a plug-in window. `transcribe` needs
`pip install "rick-rubin[transcribe]"` and `serum` needs `pip install "rick-rubin[serum]"`; its result is cached next to the sample and printed in `score.md`.

## What gets built in Live

* Tempo, 4/4, and one locator per section.
* One MIDI track per song track (an audio track for loop tracks), with name, colour, volume (dB-accurate) and pan.
* Sample tracks: a Simpler holding the one-shot, in One-Shot mode for drums or tuned Classic mode for melodic parts. Loop tracks: unwarped audio clips, one per pass of the loop.
* An instrument loaded by browser name, tried in order. For example, a drum track tries `909 Core Kit`, then `Kit-Core 909`, then `Drum Rack`. Set `instrument` per track to use your own presets or plug-ins.
* One arrangement clip per (section, track), named `section · pattern`. Notes include baked-in swing.
* Filter automation written as clip envelopes on an Auto Filter that the bridge inserts.
* Effects: each track's `effects` chain — any Live audio effect, every parameter set by its displayed value (dB, ms, Hz, %, option names), with sidechain routing. `sidechain: true` is shorthand for a Compressor keyed from the Kick.
* `rick-rubin capture` records what Live actually plays (through a temporary Resampling track) so the self-eval can measure Live's sound instead of the sketch render.

The push report lists anything that needs a human: an instrument not found, a sidechain that couldn't be routed, or a failed envelope.

## Layout

```
rick_rubin/
  model.py        Song / Track / Pattern / Section; flatten() -> arrangement clips
  theory.py       keys, scales, diatonic chords, voice leading, chord naming (C3 = 60)
  compose.py      the two notations (step strings, event lines) used to write patterns
  score.py        packed text score (primary reading view)
  edits.py        JSON edit ops for projects without a song.py
  analysis.py     lint rules + BS.1770 loudness + spectral checks -> eval.md
  views.py        on-demand piano-roll / waveform / spectrogram PNG
  render/midi.py  dependency-free SMF export
  render/preview.py  numpy sketch synth with sidechain + filter automation
  live/client.py  bridge client + push_song()
  live/remote_script/RickRubin/  Live remote script (TCP JSON bridge; handlers testable without Live)
  logic/smf.py    the song as a MIDI file Logic opens as a project (GM program per role, markers, names)
  logic/ax.py     Logic through macOS accessibility: Mixer strips, plug-in windows, menus, dialogs, file panels
  logic/mcu.py    a Mackie Control emulated on a virtual MIDI port (LCD, faders, clock) that Logic auto-detects
  logic/bridge.py the Logic bridge: open/save projects, strips, inserts, sends, parameters, side chains, bounce
  logic/client.py push_song / capture_logic for Logic (the counterpart of live/client.py)
  logic/stems.py  split_stems: a recording's stems through Logic's Stem Splitter
  serum.py        Serum 2: preset catalog, patch sheets, and the plug-in hosted in-process (load presets, render parts)
  transcribe.py   syllable-level alignment of vocals to the grid, and re-timing
  pitch.py        the notes inside a single-voice sample
  midifx.py       MIDI effects: real devices in Live, emulated offline where deterministic
  pictures.py     imager, spectrum analyzer, Serum patch panel, sample comparer
  reference.py    profile a mix and compare it with released reference tracks
  options.py      option(): named choices in song.py, switched by `ab` / `--set` for A/B runs
  samples.py      sample import: pitch detection, tempo-conforming loops, 24-bit WAV io
  project.py      project folder, history/undo, project.md memory
SKILL.md          agent instructions: principles, hard rules, process, house craft
install.md        setup prompt + steps for your coding agent
docs/HOUSE.md     research notes behind the defaults
```

## Limitations

* The preview synth is only a sketch for measuring rhythm, balance and arrangement. It is not a mixdown. Compare its sections against each other, not against commercial masters.
* Live's API cannot draw sound design. The agent chooses instruments by name and writes notes and automation; timbre is down to your presets.
* The bridge has been run against Live 12.4 (Intro) on macOS; the automated tests use a simulated Live Object Model. On other versions the first real push is the moment to watch for API differences. The push report and Live's `Log.txt` will show them.
* House is the first-class genre: the lint rules and the craft notes in SKILL.md are written for it. The model, notation and bridge are genre-agnostic.

## Tests

```bash
pip install -e ".[dev]" && pytest -q
```

The tests cover theory, JSON round-trips, flattening and swing, writing a song in Python, the edit ops, lint rules, MIDI round-trips, preview rendering and analysis. They also run a full `push_song` over a real socket against a fake Live Object Model.
