# Logic Pro

Logic has no scripting API. Everything here goes through macOS accessibility, keystrokes posted to Logic's own
process, and an emulated Mackie Control that Logic detects by itself. Setup, how it works and the troubleshooting
table: `docs/LOGIC.md`.

There are two ways in, for two different jobs. **Session mode** works inside the project that is open. **Push**
builds a new project from a `song.py`. Never use push to change a project of Rohil's.

## Session mode: the project that is open

```
rick-rubin logic inspect                         # read first, always
rick-rubin logic params Bass Compressor          # what a plug-in is set to
rick-rubin logic set Bass volume=-8 pan=0 mute=off
rick-rubin logic insert Pad "Kickstart 2" Mix=0.6
rick-rubin logic insert Pad "Trackspacer 2.5" Ratio=60 --sidechain Vocal
rick-rubin logic tweak Bass Compressor Threshold=-24 Ratio=4
rick-rubin logic send Vocal 1 -14                # Bus 1; Logic makes its Aux when the bus is new
rick-rubin logic add-audio ~/Music/take.wav --bar 17 --name "Vocal take"
rick-rubin logic add-midi line.mid --bar 9
rick-rubin logic bounce bounces/drop.wav --bars 33-48 --tracks Bass Kick
```

`--project "<title>"` names the project when more than one is open (any case, without `.logicx`, or a unique part
of the title); the default is the front one. A strip is named by its name (any case, a unique beginning will do)
or as `#3`, the third track. Aux strips, `Stereo Out` and `Master` go by name.

**Read first.** `logic inspect` prints tempo, key, time signature, playhead, and one row per strip: fader, pan,
mute/solo, instrument, inserts in order, sends, output, region names. It takes about a second and does not bring
Logic forward. `--json` gives the same as data. It does not show markers, region positions or automation: those
are not readable from outside Logic.

**One change at a time, read back.** Every change prints `[ok] <what> <strip>: <before> -> <after>`, or
`[NOT AS ASKED]` when what Logic shows afterwards is not what was asked (the command then exits 1). Report those
lines to Rohil as they are.

**What a session never does.** It does not open, close or save a project (he saves when he is happy), does not
delete tracks or regions, and does not answer a question Logic is asking: if an alert is up, the command stops and
says what Logic asks. Before the first change, the project's saved state (every alternative's ProjectData, not
the audio) is copied to `~/.rick-rubin/backups/<project>/<time>/`, and every change is appended to
`~/.rick-rubin/sessions/<project>.jsonl`. To go back: Logic's own Undo, File > Revert to, or close the project and
copy a backup's `Alternatives` folder over the one in the `.logicx` package.

**Front or background.** Fader, pan, mute, solo, inserting a plug-in on a track, its parameters, reading
parameters and sends on tracks all work with Logic in the background (checked with another app in front). Logic
comes to the front only for what needs it: new tracks, audio and MIDI import, bounce, renaming, and anything on an
Aux or Stereo Out strip. It waits for the keyboard and mouse to be still for a moment first, gives up after 30 s if
they never are, and returns the front to the app that had it. `--background` forbids it altogether.

**Plug-in parameters** are set and read by the value Logic displays, through the control surface. Names are what
the plug-in window shows ("Threshold", "Ratio") or the surface's short form ("Thrs", "AutRel"); `logic params`
prints the short forms with their values, eight to a page (`--pages N` reads further: a synth can have hundreds).
For a plug-in you have not used before, `rick-rubin logic devices "OTT"` reads its parameters in a scratch project
(closed without saving) and remembers them. Numbers take the displayed unit (dB, ms, Hz, %); switches take
on/off; menus take the option's name.

**Timing.** A fader is instant. A parameter is 5 to 10 s. Inserting a plug-in is 10 to 140 s, most of it scrolling
Logic's plug-in list on the surface (the order is remembered, so the second time is quicker). A bounce of a few
bars is about 15 s.

**Limits today.** `bounce --bars` can only shorten what Logic's bounce dialog offers (the cycle or selection when
there is one, else the project): for an exact range with a selection active, clear the selection in Logic first.
Imported audio lands on the bar line. There is no command to move, cut or delete regions, to write automation, or
to edit notes inside an existing region: say so and describe the manual steps instead of approximating.

## A song.py into a new Logic project: `push` and `capture`

`rick-rubin --daw logic push <dir>` (or `RICK_RUBIN_DAW=logic`) renders the same `song.py` into Logic Pro, and
`--daw logic capture` bounces it offline (a 5-minute track in about ten seconds) into `live.wav` for the same
measurements. What changes for you:

- Instruments: without `instrument=`, Logic picks a patch from the track's role (the push report says which,
  e.g. `Pulse Bass`, `SoCal`). `instrument="Retro Synth"` / `"Alchemy"` / `"Serum 2"` loads that instrument;
  any other string is a Library search and the first patch found is loaded (`"Deep House Kit"`). A Logic patch
  brings its own inserts (`patch fx` in the report) — your `effects` come after them. `instrument_params` sets
  the instrument's parameters by displayed value (Drum Synth: `{"Sound Category": "Kicks", "Sound Model":
  "Punch Kick", "Decay": 42}` — one Drum Synth per drum track is how electronic drums are done in Logic here;
  the role's default kit is Logic's acoustic Drum Kit Designer).
- Effects and parameters use Logic's names: `{"device": "Compressor", "params": {"Threshold": -28, "Ratio": 4,
  "Attack": 0.5, "Release": 120}}`, `"Channel EQ"`, `"AutoFilter"`, `"Limiter"`, `"ChromaVerb"`, `"Tape Delay"`.
  Units are the displayed ones. `sidechain: true` is a Compressor keyed from the Kick, as in Live.
- Serum tracks (`serum=`) arrive as their rendered stem on an audio track named after the track, from bar 1, with
  their effects, sends and mixer settings (checked: a Logic bounce of the track matches the offline stem, r = 0.985).
- Pumping without routing: `sidechain="kickstart"` puts Kickstart 2 on the track, its shape repeating as often as
  the kick lands on the beat (every beat, every 2 beats, every bar). Explicitly: `{"device": "Kickstart 2",
  "params": {"Loop Length": 0.0, "Used Wave": 0.2, "Mix": 0.8}}` — Loop Length is a switch: 0.00 every beat, 0.33
  every 2 beats, 1.00 every bar; Used Wave picks one of 16 curves (steps of 1/15); Mix is the depth (1.0 ≈ 47 dB
  duck). Prefer it for pads and chords that should breathe with the kick; keep a kick-keyed compressor on the bass,
  which should duck only when the kick actually hits (fills, gaps, half-time bars).
- Spectral ducking: `{"device": "Trackspacer 2.5", "sidechain": "Vocal", "params": {"Ratio": 60, "Attack": 5,
  "Release": 120, "Low-cut": 200, "High-cut": 8000}}` carves the keying track's spectrum out of this one (Ratio is the
  amount, 0-100). Measured: a pad under a lead lost 12 dB in the lead's band (300-1200 Hz) while the lead played, and
  nothing between its phrases. Uses: pads/chords under a vocal or lead, a bass under the kick instead of a
  compressor. Check it with `--daw logic capture --tracks <the ducked track>` before/after; the side chain still
  feeds while the keying track is muted by the solo.
- Returns become Bus 1, 2… with an Aux each; sends are in dB; `master_effects` go on Stereo Out.
- Every push is a full push (no `--update`, no `watch`); it takes one to four minutes. Section `volume` and
  `filter` automation is written only with `--automation` (it plays the automated bars in real time).
- Sample tracks (`sample=`) arrive the way Serum tracks do: the part played from the sample offline (the whole
  file per hit for drum roles, repitched from `sample_root` for melodic ones, the same velocity law and attack as
  the preview) on an audio track from bar 1. What you measured offline is what Logic plays; the notes are not
  editable MIDI there. Audio loops are imported onto an audio track.
- MIDI effects: Chord, Pitch, Note Length and Velocity are written into the notes of the region (Logic's own MIDI
  plug-ins are not set from here). Arpeggiator, Random and Scale are not: the report names them, and that part
  plays as written.
- The project's key signature is the song's (a mode shows as its relative major: F dorian as E♭ major).
- Mixer levels are the bridge's alone: the MIDI file carries no volume or pan controllers (it used to, and Logic
  moved the faders to them whenever playback started).
- A push brings Logic to the front for its whole run (saving and the Aux / Stereo Out strips need it there) and
  gives the front back when it ends. Do not click in Logic during a push: it applies strip edits to every
  selected track, and the control surface state must not change. Keep projects in a visible folder (file panels
  cannot reach hidden ones).

## Stems, tempo and key with Logic's own tools

- `rick-rubin split <dir> refs/track.wav` runs Logic's Stem Splitter on a recording (Logic Pro 11 on Apple silicon,
  no `--daw` needed): vocals, drums, bass, guitar, piano and other as `stems/track/<stem>.wav`, at the recording's
  rate, with each stem's level; one near silent means the recording has none of it. Use it to read a reference's
  parts on their own — `notes` on its bass stem, `transcribe` on its vocal, `width` and `reference` on its drums —
  instead of guessing them from the full mix. A 3-minute song takes about 40 s. `--bpm 128 [--transpose N]` brings a
  second song to this one's tempo and key with Logic's Smart Tempo and Transpose (for a mashup): its stems come out
  conformed.
- `rick-rubin conform <dir> file.wav --bpm 128 [--transpose N] [--flex-mode "Flex Time - Speed (FX)"]` conforms a recording to a tempo
  (and key) with Smart Tempo and Flex & Follow and bounces it, without splitting. `Speed (FX)` is a varispeed: pitch follows
  the tempo. Measure the result's pitch against the bed before trusting it (`skill/mashups.md`).
