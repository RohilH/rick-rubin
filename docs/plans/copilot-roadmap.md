# rick-rubin as a Logic Pro copilot: roadmap and status

Goal (Rohil, 2026-11-19): a copilot for his DAW that can do the tasks he asks for, help him create new sounds,
and carry knowledge from producers he follows so he improves as a producer.

Phases 0 to 3 were built on 2026-11-19/20. Phases 4 and 5 are next. "Checked live" below means run against
Logic Pro 11.2.2 on this Mac and read back or bounced; "tests" means the fake-bridge tests only.

## Phase 0. Consolidate — done

One branch (`logic-consolidated`, PR 1 on the fork) holds what was in three places: upstream `main`, the
stem-split work (two unpushed commits and the uncommitted 2026-10-27 work: `conform`, Flex Mode, macOS 15.6 file
panels), and the Serum design and matching work. Checked live with a push and a bounce.

## Phase 1. Make it Rohil's, make it load everywhere — done

| Item | State |
|---|---|
| `PREFERENCES.md`, `CLAUDE.md` are this fork's: Logic first, session rules, mashup rules, verdicts | done |
| `SKILL.md` is a 7 KB router; the manual is `skill/*.md`, read by job | done |
| The skill is linked into `~/.claude/skills/rick-rubin` | done |
| A song declares which genre checks apply (`song.meta["lint"]`) | done, tests. Which genres Rohil makes is still his to say |
| `serum index` (626 presets measured) | done |
| demucs installed for `isolate` | done: a bass part separated from a released mp3 and its notes read |
| Reference shelf | seeded with the four released tracks of the two mashup projects; Rohil should add 8 to 15 tracks he measures himself against |

## Phase 2. Session mode: inside the open project — done, with limits

`rick-rubin logic ...` (`rick_rubin/logic/session.py`, `skill/logic.md`, `docs/LOGIC.md`).

| Command | State |
|---|---|
| `inspect` (tempo, key, strips, inserts, sends, regions) | checked live, about 1 s, Logic stays in the background |
| `set` fader / pan / mute / solo, on tracks and Aux | checked live |
| `tweak` and `params` (plug-in parameters by displayed value) | checked live on Logic's Compressor, Limiter and Kickstart 2 |
| `insert` a plug-in on a track | checked live, in the background |
| `send` to a bus | checked live |
| `add-audio`, `add-midi`, `bounce` | checked live |
| `rename` | checked live (capitals, brackets) |
| `add-instrument` (an empty channel strip, then the instrument) | checked live with Serum 2 |
| `add-serum`, `serum` (a patch into a live Serum 2) | tests for the commands; the bridge call under them (`load_setting`) checked live inside `push --serum-live` |
| `sidechain`, `instrument` on an existing track, `instrument` parameters | tests; the bridge calls under them are the ones `push` has used live |
| `devices` (a plug-in's parameter names, read in a scratch project) | not yet run: the screen was locked when it was started. One command: `rick-rubin logic devices OTT ValhallaSupermassive LIMITER BASSROOM MIXROOM STEREOVAULT RESO FUSER ANIMATE` |
| `backup`, change log, selection and Mixer window put back | checked live |

Safety, in code: nothing opened, closed, saved or deleted; a pending alert stops the command; the saved state is
backed up before the first change; every change read back; one track selected and verified before strip edits;
Logic comes forward only for the steps that need it and only when the keyboard and mouse are still.

Found and fixed on the way (each would have hurt in a real project):

- With Logic in the background its Save commands are disabled and Aux / Stereo Out strips are not selected.
- A new Mixer window is 644 px high and clips the top of the strips; Logic stops naming clipped slots, so the top
  insert was dropped and instruments read `input`. The second of two sends was read as an insert.
- The MIDI file a push opens carried volume and pan controllers; Logic moved the faders to them on every
  playback (a track written at -14 dB played at -21 dB).
- Logic puts Transpose +12 on the region of a bass program when it opens a MIDI file, so a bass track given its own
  instrument played an octave up. The push now sets it back to 0 for those tracks.
- A bar-range bounce failed on Logic 11.2.2 (its position fields move ten bars at a time): it is now cut out of a
  full bounce. `isolate` could not read mp3 files and called demucs with a broken command line.
- `instrument="Serum 2"` loaded Serum 2 FX. A new instrument track took Logic's default patch and its two reverb
  busses. Typed text lost its capitals. A cold start of Logic was not seen for 150 s.

Not built: moving, cutting or deleting regions; editing notes inside an existing region; writing automation
without playing the bars; reading markers, region positions or automation (Logic does not expose them); an
incremental push for song projects.

## Phase 3. Sound creation — mostly done

| Item | State |
|---|---|
| Design, compare, fit, save a `.SerumPreset` (was already there) | renders checked |
| `serum install`: a designed preset in Serum's browser under User / rick-rubin | done, tests. **Rohil: open one in Serum's own window once** (the round trip is tested, a human has not looked) |
| `serum audition`: a wav, an mp3 and a picture for him to hear; `verdict` and `taste` | done, checked with real renders |
| A live Serum 2 in Logic carrying the patch (`push --serum-live`, `logic add-serum`) | checked live: the bass bounced from Logic matches the offline render in every band within 0.4 dB, level as the fader says |
| Sample tracks in Logic play the sample (rendered part), MIDI effects written into the notes, the project key | checked live in a push |
| Parameter or macro movement per section; custom wavetables from audio; Vital | not built |

## Phase 4. Knowledge from the producers Rohil follows — next

Waiting for the video links. Per video: captions (or a transcript of the audio), plus frames where a setting is
on screen. From those:

- `knowledge/sources/<creator>/<video>.md`: a short digest in our own words, with timestamps.
- `knowledge/techniques/<topic>/<name>.md`: one card per technique: what it is, when to use it, the settings,
  how rick-rubin does it (commands, keys), how to check it by measurement, the source.
- Each card is tried on this Mac (in Serum, or in a Logic bounce) and marked tested, with the numbers, or untested.
- `knowledge/INDEX.md`, one line per card, read through `SKILL.md`.
- Where a technique is measurable it also becomes a check or a command.

The library still holds no canned notes or patterns: a card says how and why, the agent writes the part.

## Phase 5. The level-up loop — started

- Verdicts (`rick-rubin verdict`, `~/.rick-rubin/taste.md`) exist; the habit of asking for one after every bounce
  is in `PREFERENCES.md` §5.
- To build: a review mode that takes a bounce of Rohil's own work and gives a measured critique against his
  references and the technique cards; before and after bounces left for him whenever a card is applied.

## Open questions for Rohil

1. The video links, and which genres he wants to make.
2. Whether to send any of this upstream. The session mode, preferences and skill layout are this fork's; the
   bug fixes (controllers in the MIDI file, the strip reader, the foreground handling) would help upstream too.
3. Scratch data to delete when he says so: `~/Documents/apps/rr-logic-scratch` (about 2 GB), `~/Documents/rr-stem-demo`.
