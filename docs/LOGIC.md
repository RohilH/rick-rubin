# Logic Pro as a render target

`rick-rubin --daw logic push <dir>` builds the song as a Logic Pro project; `--daw logic capture` bounces it
offline. Everything else (writing the song, `score`, `eval`, `view`, samples) is unchanged. Set
`RICK_RUBIN_DAW=logic` to make it the default.

Checked against Logic Pro 11.2.2 on macOS 15. Nothing is installed into Logic: no remote script, no
plug-in, no control-surface setup by hand.

## Setup

```bash
pip install -e ".[logic]"          # mido, python-rtmidi, pyobjc (Cocoa, Quartz, ApplicationServices)
rick-rubin --daw logic status      # {"logic_version": "11.2.2", "mcu": true, "projects": [...]}
```

The process that runs `rick-rubin` (your terminal, or the agent's) needs two macOS permissions, both under
System Settings > Privacy & Security:

- **Accessibility** — to read and press Logic's Mixer, plug-in windows, menus and dialogs.
- **Screen Recording** is *not* needed for a push; it is only needed if you want screenshots of Logic.

Logic finds the emulated Mackie Control by itself the moment the port appears (it shows its Control
Surface Setup window the first time; the bridge closes it). If a push says Logic has not connected to the
port, open Logic Pro > Control Surfaces > Setup and check that a Mackie Control is listed with the
`rick-rubin MCU` input and output ports; if not, New > Install… > Mackie Designs > Mackie Control and pick
those ports.

## How a push works

Logic has no scripting API for its arrangement, so a push uses three ways in, each where it is reliable:

1. **A MIDI file Logic opens as a project** (`logic/smf.py`). Logic reads a Type 1 SMF as a *new project*:
   tempo, 4/4, one marker per section, one software-instrument track per MIDI track, one region per track
   with the notes, and an instrument picked from each track's General MIDI program number (drums on
   channel 10 get a kit). The song's roles map to programs that give sensible Logic patches: bass → a synth
   bass, chords/stab → a poly synth, pad → a pad, keys → an electric piano, drums → a kit. The region keeps
   the MIDI track's name; Logic names the *track* after the patch, so the bridge runs Tracks area >
   Functions > "Name Track by Region/Cell Name" and the tracks carry the song's names again.
2. **The accessibility API** (`logic/ax.py`). Logic's Mixer exposes every strip: fader (with its dB
   readout), pan, mute, solo, insert slots, sends, output. Plug-in windows expose their header (side chain,
   bypass) and whatever parameters their view offers. The menu bar and every dialog (bounce, save, alerts)
   are reachable the same way. None of this takes the keyboard or mouse away from the person using the
   Mac; the few keystrokes needed are posted to Logic's process only (`logic/keys.py`).
3. **An emulated Mackie Control** (`logic/mcu.py`) on a virtual MIDI port. Logic detects it on its own and
   mirrors to it what a real unit shows: the two-line LCD, fader positions, the bar/beat clock, button
   LEDs. The bridge uses it for what the accessibility tree does not offer: selecting strips, inserting
   plug-ins and instruments (the plug-in list scrolls under a V-Pot, the preselected name reads back on the
   LCD), sends (Logic creates the Aux for a new bus by itself), plug-in parameters by their displayed value
   (the Plug-in Edit view shows names and values; a detent steps a parameter and the bridge converges on the
   value you wrote), transport and the clock, and automation modes.

`logic/bridge.py` is the one class that knows these mechanisms; `logic/client.py` turns a `Song` into
calls on it, mirroring `live/client.py`.

## What ends up in Logic

| Song | Logic |
|---|---|
| tempo, 4/4, sections | project tempo and signature, one marker per section |
| track | software-instrument track with the song's name; strip volume (dB) and pan |
| role | a Logic patch from the General MIDI program for the role (the report says which) |
| `instrument="Retro Synth"` / `"Alchemy"` / `"Serum 2"` | that instrument in the instrument slot (Logic's own and Audio Units) |
| `instrument="Deep House Kit"` (not an instrument name) | the first Library patch the search finds |
| `instrument_params` | the instrument's parameters by displayed value, set in the surface's Instrument Edit view (e.g. Drum Synth: `{"Sound Category": "Kicks", "Sound Model": "Punch Kick", "Decay": 42}`) |
| pattern / section parts | one region per track per section with the notes (swing and groove baked in, as for Live) |
| drum track on a single-voice instrument (Drum Synth, Quick Sampler, `sample=`) | every hit sent on C3, like Live's Simpler one-shots (those instruments pitch by note) |
| `effects` | Logic plug-ins by name in the insert slots, in order, after the patch's own inserts; `params` set by displayed value |
| `sidechain: true` | a Compressor keyed from the Kick (side chain input = the Kick's channel strip) |
| `returns` A, B … and `sends` | Bus 1, 2 … with an Aux each, the return's plug-ins on the Aux, sends in dB |
| `master_effects` | plug-ins on Stereo Out |
| section automation `volume`, `filter` | written as track automation in real time with `--automation` (the automated bars are played once per parameter): the fader for volume, the Cutoff of an AutoFilter the push inserts for filter |
| | the project is saved as `<project>/logic/<title>.logicx` |

Parameter names are Logic's: what the plug-in window shows ("Threshold", "Ratio", "Attack", "Release",
"Make Up", "Knee"), or the abbreviation the Mackie Control LCD uses ("Thrs", "Rel", "AutRel"). Units are
the displayed ones (dB, ms, Hz, %, `4:1` ratios as 4). Options are given by name ("RMS", "On").

Logic's Compressor adds make-up gain of its own ("Auto Gain", -12 dB by default), which Live's does not: a track
ducked with `sidechain: true` comes out *louder* on average than it went in. Set the fader with that in mind, or
put `"Auto Gain": "Off"` in an explicit Compressor's params.

Logic patches come with their own inserts (a Channel EQ, a compressor, a limiter…). They stay — they are
part of the sound Logic's patch designers made — and the report lists them as `patch fx`, so the agent
knows what is on the strip before its own `effects`.

## Capture = offline bounce

`rick-rubin --daw logic capture <dir> [--bars 33-40] [--tracks Kick Bass]` is File > Bounce > Project or
Section, offline, 24-bit WAV, the bar range you give (tracks soloed when asked), written to `live.wav`
(or `zoom/live_bars_…wav`) and measured like a Live capture. A 5-minute track bounces in about ten seconds.

## Stem splitting

`rick-rubin split <dir> refs/track.wav [--stems vocals,bass] [--from 60 --to 90] [--submix] [--close]` separates a
recording with Logic's own **Stem Splitter** (Logic Pro 11 on Apple silicon; 11.2 has six stems: vocals, drums, bass,
guitar, piano, other) and writes `stems/track/<stem>.wav` in the project — 24-bit, at the recording's sample rate,
as long as the recording. It does not need `--daw logic`, a song or the Mackie Control. What it does:

1. The recording (WAV, AIFF, MP3, M4A — anything but WAV goes through macOS's `afconvert`; `--from/--to` cut it
   first) is copied to `stems/track/logic/` and a project is made for it: a one-track MIDI file Logic opens as a
   project, saved as `stems/track/logic/track stems.logicx` (named after the output folder), an audio track, File > Import. A sample-rate question
   is answered "Change Project", so nothing is resampled.
2. The region is selected (focusing it through accessibility) and Stem Splitter… is chosen from its right-click
   menu (Logic opens the context menu on AXShowMenu; the Tracks area's Functions menu has the same command and is
   the fallback), with the stems' check boxes set and the Submix (the unticked stems summed; Logic calls it "Instrumental" when
   only the vocals are ticked) on with `--submix`, written as `submix.wav`.
3. Logic writes the stems into the project's Audio Files folder as `<name>_<Stem>.wav` under a progress window,
   whose progress the command prints; then it adds a summing stack with one audio track per stem and mutes the
   original region. The command waits for the files to stop growing, copies them out and measures them.

Measured on an M4 Pro: 30 s of a vocal house track split into six stems in 10 s, a 2'43" song in 34 s. The six
stems add up to the original within 36 dB (the residual is 36 dB below the mix). A stem the recording does not
have comes out near silent (piano at -110 dB RMS in a house track) and the report says so.

The project is saved and left open, so the split can be auditioned in Logic (`--close` closes it). Running the
command again into the same folder replaces its project and stems. Other open projects are left alone; one with the
same name in another folder stops the command (the bridge finds project windows by name), rather than being closed. The
recording's copy next to the project is the project's source file — keep it with the project.

## What differs from Live, and what is missing

- Every push is a full push: the project is rebuilt from the MIDI file. `--update` and `watch` are Live
  only. `ab --live` pushes and bounces each candidate.
- A re-push closes the project it saved earlier (same title) without saving; any other open project is
  left alone and Logic keeps both open. If Logic asks about an unsaved project that is not ours, the bridge
  answers "Don't Close".
- Audio-loop tracks (`audio=True`) get an audio track after the MIDI tracks with each loop segment imported at
  its bar (File > Import > Audio File, driven through the panel's column browser). Sample one-shot tracks
  (`sample=`) are not built yet: their tracks exist and play the role's patch. Serum stems are not placed;
  use `instrument="Serum 2"` to play the part live.
- MIDI effects are not built; notes are sent as written.
- Automation needs `--automation` because it plays the automated bars: a 16-bar volume ride at 126 BPM takes
  30 seconds. Filter automation rides the Cutoff of an AutoFilter the push inserts on the track.
- A push takes one to four minutes, most of it scrolling Logic's plug-in list on the control surface
  (ChromaVerb is item 115 of 127) and converging parameters at a few detents per second.

## Troubleshooting

| What you see | Cause and fix |
|---|---|
| `Logic Pro is not running` / `did not start` | The bridge launches Logic when needed; a fresh launch shows its project chooser, which the push dismisses by opening the MIDI file. Wait and run again. |
| `Logic has not answered the Mackie Control port` | Logic Pro > Control Surfaces > Setup: a Mackie Control with the `rick-rubin MCU` ports. Rebuild Defaults re-scans. |
| `the surface is not in the Plug-in Channel view` | Something else changed the control surface state (a hand on Logic's Mixer, a plug-in window). Run the push again. |
| `no plug-in called X in Logic's list` | Spell it as Logic's plug-in menu does ("Channel EQ", "AutoFilter", "ChromaVerb", "Tape Delay"); Audio Units appear by their own names. |
| `X was preselected but Logic did not insert it` | The strip's first free insert slot was not where the bridge thought (slots beyond 8 are not reached). Check the strip in the Mixer. |
| `no parameter X in <plug-in>` | Use the name the plug-in window shows or the LCD abbreviation; the message lists the ones seen. |
| The push stops with `no project window` | Logic quit. Logic Pro 11.2 crashed for us when a plug-in header pop-up (side chain) was used while the Mackie Control was linked to that window; the bridge now disconnects the surface for that step. Check `~/Library/Logs/DiagnosticReports`. |
| Faders or plug-ins changed on *every* track | Several tracks were selected in Logic: it applies strip edits to all selected strips. The bridge selects one track before each edit; do not select tracks by hand during a push. |
| `Stem Splitter is not available` | The Stem Splitter needs Logic Pro 11 and a Mac with Apple silicon. On Logic 11.0/11.1 only four stems exist (vocals, drums, bass, other): ask for those. |
| `the Stem Splitter did not finish in … s` | Logic was still working (a long recording on a busy Mac) or asked something; the message says what is pending. The project stays open: wait for its progress window, then run again. |
| A file dialog does not find the folder | File panels are navigated by column; hidden folders (`/private/tmp`, dot folders) cannot be reached. Keep projects somewhere visible, e.g. under `~/Documents`. |

## Logic's instrument choices per role (for reference)

Measured on Logic Pro 11.2 with the General MIDI programs in `logic/smf.py`: drums (channel 10, program 0)
→ SoCal kit (Drum Kit Designer, a full acoustic kit — the default, because it answers every drum note); program
16 → a single "Kick 1" pad of the Tough Kit, 24/25 → a single "Sub Kick" Drum Synth (every note plays that one
voice, so hats and claps would all be sub kicks — name `instrument="Drum Synth"` per track with `instrument_params`
for electronic drums instead, as `examples/night-shift` does);
38 → Pulse Bass, 39 → Taureg Moon Bass, 33 → Simple Foundation; 81 → The Final Lead, 80 → Reverse
Engineering, 87 → Soft Square Lead; 89 → Classic Pad, 88 → Glistening Pad, 90 → Epic Cloud Formation;
4 → Classic Electric Piano, 16 → Tonewheel Organ. Name a patch or an instrument when the role's default is
not the sound you want.
