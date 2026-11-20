# Logic Pro

Two ways in. `rick-rubin logic ...` (**session mode**) works inside the project that is open: it reads it and
makes one change at a time. `rick-rubin --daw logic push <dir>` builds a song written as code into a **new**
project, and `--daw logic capture` bounces it offline. Set `RICK_RUBIN_DAW=logic` to make Logic the default for
`push` and `capture`. How to use both is in `skill/logic.md`; this file is how they work, what is built, and what
to do when something goes wrong.

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

## Session mode: inside the open project

`rick_rubin/logic/session.py`. A `Session` wraps a connected bridge that points at an open project (the front
one, or `--project`), and keeps these rules in code:

- **Nothing is opened, closed or saved**, and no alert is answered: when Logic is asking something as a command
  starts, the command stops and says what Logic asks.
- **Backup first.** Before the first change, every alternative's `ProjectData` and plists (the saved state, not
  the audio: a few MB) are copied to `~/.rick-rubin/backups/<project>/<time>/`, once per saved state. A project
  that was never saved has nothing to copy, and the command says so. To restore: close the project, copy the
  backup's `Alternatives` folder over the one inside the `.logicx` package, reopen.
- **Every change is read back** from Logic and logged with the value before and after in
  `~/.rick-rubin/sessions/<project>.jsonl`. A readback that differs from what was asked is reported
  (`NOT AS ASKED`, exit code 1), not smoothed over.
- **One track selected** before a channel-strip edit, verified, because Logic applies strip edits to every
  selected strip. If the track cannot be selected on its own, nothing is changed. The selection the person had
  comes back when the command ends.
- **A Mixer window the session opened is closed again**; one that was already open and had to be made taller
  gets its old frame back.

What it can read: tempo, key and time signature (the control bar), the playhead, and per strip the name, fader,
pan, mute, solo, instrument, inserts in order, sends, output, automation mode and region names. Plug-in and
instrument parameters are read off the control surface's edit view, eight per page, as the names and values the
surface shows. What it cannot read: markers, region positions and lengths, automation curves, notes inside
regions. Those are not in Logic's accessibility tree.

### Front or background

With Logic in the background (another app in front), two things do not work on Logic 11.2.2 / macOS 15.6: the
File > Save commands are disabled, and Aux and Stereo Out strips are not selected by the control surface (a
plug-in meant for the master landed on the selected track). Tracks, their plug-ins, parameters and sends do work
there. So the bridge takes a `front` argument:

- `front=True` (session mode): Logic is brought forward only by the steps that need it (`need_front`: menus
  that open sheets and file panels, Aux / output strips, renaming), after the keyboard and mouse have been still
  for 1.5 s, and the app that was in front gets the front back when the bridge closes. If nobody stops typing
  for 30 s the step fails with a message instead.
- `front="start"` (push, capture, split, conform): forward for the whole run.
- `RICK_RUBIN_LOGIC_BACKGROUND=1` or `logic --background`: never.

`RICK_RUBIN_FRONT_WAIT=<seconds>` changes how long a step waits for a pause (default 30).

Two of Logic's own pop-ups are not in the accessibility tree and are needed (the New Tracks sheet's Instrument
menu, a plug-in window's Settings menu). They are driven the same way (`_own_popup_pick`): a press
opens the pop-up, the entry is found by typing the start of its name, return takes it, and what Logic shows
afterwards is checked. This is done with the control surface paused.

No keystroke is ever posted to anything but Logic's process, and text is only typed after checking that a text
field has the focus (outside one, Logic reads letters as key commands).

### Two things the strip reader depends on

- **A tall Mixer window.** Logic stops naming plug-in slots that are clipped off the top of the Mixer: the top
  insert reads `audio plug-in` and the instrument reads `input`. A new Mixer window opens 644 px high, which
  clips them. The bridge opens a Mixer window of its own (not the pane) and makes it 900 px high. A slot whose
  name is still hidden is listed as `?` so that slot numbers stay right.
- **A wide Mixer window.** Strips beyond the window's right edge are not named either. With more strips than fit
  (a 38-strip project needs about 2,700 px) the window is widened to hold them all, hanging off the left of the
  screen: a window may be wider than the screen once its left edge is off it. When macOS puts it back at x = 0
  and it hangs off the right instead, Logic names the strip controls by identifier (`volumeFader`, `midiPlugIn`,
  `sendKnob`); the reader takes both spellings. The old frame is restored when the bridge closes.
- **Track names.** A muted track's header reads `Track 5 “Audio 30”, mute`; an output track shown at the bottom
  of the Tracks area (`Stereo Out`) is not a track strip. Collapsed stacks hide their inner tracks from both the
  track list and the Mixer, so `#n` counts the tracks that are visible.
- **Slots are told apart by what they hold**: a plug-in slot has `bypass`, `open`, `list`; a send has `bypass`,
  `list`, and all send knobs follow all sends (so the second of two sends is not followed by its knob).

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
| drum track on a single-voice instrument (Drum Synth, Quick Sampler) | every hit sent on C3, like Live's Simpler one-shots (those instruments pitch by note) |
| `sample="samples/kick.wav"` | the part played from the sample offline (`render/stems.py`: whole file per hit for drum roles, repitched from `sample_root` for melodic ones, Simpler's velocity law, `Ve Attack`), imported at bar 1 onto an audio track named after the track |
| `midi_effects` | Chord, Pitch, Note Length and Velocity are written into the region's notes; Arpeggiator, Random, Scale are named in the report and not applied |
| `key` | the project's key signature (a mode shows as its relative major) |
| `effects` | Logic plug-ins by name in the insert slots, in order, after the patch's own inserts; `params` set by displayed value |
| `serum="<preset>"` | the part rendered through Serum 2 offline (at the song's tempo, section filter/volume baked in), imported at bar 1 onto an audio track named after the track; its effects, sends and mixer as for any track |
| `serum="<preset>"` with `push --serum-live` | a MIDI track: the role patch's inserts taken off one by one (each slot's V-Pot turned back to the list's empty entry and pressed), Serum 2 in the instrument slot, the patch loaded from `<project>/logic/presets/<track>.aupreset` through the plug-in window's Settings > Load… (`serum.write_aupreset`: the Audio Unit wraps the VST3's processor and controller state, and renders the same audio, r = 1.000) |
| `sidechain: true` | a Compressor keyed from the Kick (side chain input = the Kick's channel strip) |
| `sidechain: "kickstart"` | Kickstart 2 on the track (no routing: a tempo-locked volume shape), its Loop Length from the kick pattern: 0.00 every beat, 0.33 every 2 beats, 1.00 every bar (measured on bounces at 126 BPM), Mix 1.0 (≈ 47 dB deep) |
| `effects=[{"device": "Trackspacer 2.5", "sidechain": "Vocal", ...}]` | Trackspacer on the track, its side chain input = the named track's strip; it carves that track's spectrum out of this one |
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

`rick-rubin split <dir> refs/track.wav [--stems vocals,bass] [--from 60 --to 90] [--bpm 128] [--transpose -2] [--submix] [--close]` separates a
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

`--bpm 128` conforms the recording to a tempo first, with Logic's own tools: the project is made at that tempo, Smart
Tempo analyses the recording (Edit > Open Smart Tempo Editor > Analyze; `--source-bpm` corrects a half or double
detection with its x2 and /2 buttons), and the region is set to Flex & Follow: On in the Region Inspector, so it plays at
the project's tempo. `--transpose N` moves it by semitones with the region's Transpose. The stems the Stem Splitter
then makes inherit both, and each is bounced from Logic on its own (soloed, offline) and cut to the conformed length,
so the files are Logic's stretch and pitch shift. Checked: a 126 BPM song conformed to 128 came out 230.6 s long (234.3
× 126/128) and kept its grid to within 11 ms over four minutes.

Measured on an M4 Pro: 30 s of a vocal house track split into six stems in 10 s, a 2'43" song in 34 s. The six
stems add up to the original within 36 dB (the residual is 36 dB below the mix). A stem the recording does not
have comes out near silent (piano at -110 dB RMS in a house track) and the report says so.

The project is saved and left open, so the split can be auditioned in Logic (`--close` closes it). Running the
command again into the same folder replaces its project and stems. Other open projects are left alone; one with the
same name in another folder stops the command (the bridge finds project windows by name), rather than being closed. The
recording's copy next to the project is the project's source file — keep it with the project.

A bar range (`--bars 33-40`) is dialled into the bounce dialog. On Logic 11.2.2 its position fields do not take
typed numbers and their increment and decrement actions move ten units, but giving a segment a value below (or
above) its own moves it by exactly one, so each field is walked one unit at a time (end first when the range
grows). This works with a cycle or a region selection in place, which otherwise narrow what the dialog offers
(a project with seven regions selected offered bars 25-43). If a field ever refuses to move, the bounce is made
over the range the dialog holds and the bars are cut out of the file afterwards. A bounce without `--tracks`
keeps whatever solos the project has and says so.

## What differs from Live, and what is missing

- Every push is a full push: the project is rebuilt from the MIDI file. `--update` and `watch` are Live
  only. `ab --live` pushes and bounces each candidate.
- A re-push closes the project it saved earlier (same title) without saving; any other open project is
  left alone and Logic keeps both open. If Logic asks about an unsaved project that is not ours, the bridge
  answers "Don't Close".
- Audio-loop tracks (`audio=True`) and Serum tracks (`serum=`) get audio tracks after the MIDI tracks: each loop
  segment imported at its bar, the Serum stem at bar 1 (File > Import > Audio File, driven through the panel's
  column browser). The MIDI file has an empty placeholder track for each of them (so the import keeps the song's
  order); the push deletes those (Track > Delete Track). Sample tracks (`sample=`) take the same road: their part
  is rendered from the sample and imported as audio, so their notes are not editable in Logic.
  `instrument="Serum 2"` instead puts a live Serum on its init patch.
- MIDI effects are not Logic MIDI plug-ins: the deterministic ones are written into the notes, the others are
  reported and skipped.
- Logic sets the region's Transpose to +12 for a bass General MIDI program when it opens the file: its own bass
  patches are built to be played that way. When the push puts another instrument on the track (`instrument=` naming a
  Logic instrument or Audio Unit, or a live Serum), it sets the region's Transpose back to 0 and says so in the
  report; otherwise the part would play an octave above the written notes (measured: F1 written, F2 bounced).
  A track that keeps the role's own patch keeps Logic's +12.
- The MIDI file carries no volume or pan controllers. It used to (CC7 and CC10 as a first guess at the mixer), and
  Logic moved each fader to them whenever playback started: a track written at -14 dB played at -21 dB.
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
| A push stalls after an audio import, every strip edit failing | Logic was asking a question the bridge did not expect. Known ones are answered: the file's tempo ("Don't Import"), its sample rate ("Convert File", keeping the project's rate: stems are 44.1 kHz, new projects may be 48 kHz), "Delete Track and Regions?" ("Delete", for the placeholder tracks). Anything else is reported by name; answer it in Logic and push again. |
| `no plug-in called X` for a third-party plug-in that is installed | The surface shows only the end of a long name (7 to 14 characters by column: `rackspacer 2.5`, `start 2`); the bridge matches those tails. If it still fails, check the name in Logic's own plug-in menu. |
| `Logic Pro has to be in front for this step, and the keyboard or mouse was in use for the last 30 s` | The step needs Logic in front (see "Front or background") and never found a pause. Stop typing for a moment, or click on Logic, and run it again. |
| `track #n could not be selected on its own, so nothing was changed` | The track list did not take the selection (Logic in the background and no control surface, or several tracks held selected). Click on Logic's window and run it again. |
| `Logic is asking '...'. Answer it in Logic first` | An alert or sheet is up in Logic. A session never answers one it did not cause. |
| An insert is listed as `?`, or an instrument as `input` | That slot is clipped off the top of the Mixer and Logic does not name it. The bridge makes its Mixer window 900 px high; on a small screen, or with many inserts, close the Mixer pane and run it again. |
| `'X' was preselected but Logic did not load it` for an instrument | The surface's list held a longer name that begins the same way (`Serum 2 FX` before `Serum 2`). Names ending in `FX` are skipped now; for another clash, give the full name as Logic's instrument menu shows it. |
| `New Tracks: could not choose an empty channel strip` | The sheet's Instrument pop-up did not take the choice; the sheet is cancelled and no track is added. Run it again with Logic in front. |
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
