# rick-rubin — project rules

@PREFERENCES.md

This is Rohil's fork of dadams22/rick-rubin. Upstream is an Ableton Live toolkit for writing house tracks as
code; this fork makes Logic Pro the main target and adds session mode (work inside the project that is
open), Serum sound design and the stem and conform tools. `docs/plans/copilot-roadmap.md` says where it is
going and what is done.

## No templates. The agent writes the music.

- Do not add pattern generators, arrangement templates, named groove presets, or any other "pick from
  canned musical content" API. Not as defaults, not as scaffolding.
- The authoring surface is a project's `song.py`: every note, rhythm, section and groove number is
  written out by the agent. Helpers must be neutral tools (note parsing, theory lookups, sample
  import), never sources of musical content.
- Reading and measuring tools (score, eval, view, width, transcribe, serum, capture, `logic inspect`) are
  welcome: they tell the agent what is there. Lint rules check correctness; they never write notes. A song
  may say which genre checks apply to it (`song.meta["lint"]`); that changes what is checked, not what is
  written.
- Knowledge about how producers work (techniques, settings, why they work) is welcome as text the agent
  reads and applies by hand. It never becomes a part the library hands out.

## Working notes

- New songs start with `rick-rubin init <dir> ...`, which copies `project-template/` (a scaffold with no
  musical content) and wires its `CLAUDE.md` to import `PREFERENCES.md`.
- `song.py` is the source of truth for a song made here; `song.json`, `score.md`, previews and the DAW project
  are build outputs. A project of Rohil's own is the other way round: Logic holds the truth, and session mode
  reads it.
- Tests: `.venv/bin/python -m pytest -q`. The generator in `tests/fixture_songs.py` is test data only. Logic
  itself is exercised by hand (see `docs/LOGIC.md`); `tests/fake_logic.py` stands in for the bridge.
- Logic has no scripting API. The bridge (`rick_rubin/logic/bridge.py`) drives it through accessibility,
  keystrokes posted to Logic's process, and an emulated Mackie Control. Before touching it, read the
  troubleshooting table in `docs/LOGIC.md`. The rules that have each cost a crash or a lost edit:
  one track selected before a strip edit; the control surface paused while a plug-in header pop-up is used;
  "Don't Close" when Logic asks about a project that is not ours; never treat a project the bridge did not
  open as its own; no keystrokes outside Logic's process.
- Serum 2 is hosted in-process (`rick_rubin/serum.py`, via pedalboard): a `.SerumPreset` is converted to
  plug-in state (same XferJson/zstd/CBOR container; header hash = MD5 of the zstd block).
- Do not write into `~/Library` or `/Library` from this project without Rohil's say-so. `serum install` and
  `serum set --install` do it because he asked for a designed preset to appear in Serum.
- The Ableton path (`rick_rubin/live/`, the remote script, Python 3.7 there) is kept working for upstream but
  is not installed on this Mac: its tests run against a fake Live.
- User state lives outside the repo, in `~/.rick-rubin/`: `taste.md` (verdicts), `backups/`, `sessions/`.
  The reference shelf, the Serum index and the plug-in maps are in the repo's `.cache/` (not committed).
