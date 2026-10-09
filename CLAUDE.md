# rick-rubin — project rules

@PREFERENCES.md

## No templates. The agent writes the music.

This library exists so an agent can write a song — notes and all — as Python code, with full
creative freedom, and render it into Ableton Live.

- Do not add pattern generators, arrangement templates, subgenre profiles, named groove presets,
  or any other "pick from canned musical content" API. Not as defaults, not as scaffolding.
- The authoring surface is a project's `song.py`: every note, rhythm, section and groove number is
  written out by the agent. Helpers must be neutral tools (note parsing, theory lookups, sample
  import), never sources of musical content.
- Reading and measuring tools (score, eval, view, width, transcribe, serum, capture) are welcome:
  they tell the agent what it made. Lint rules check correctness; they never write notes.
- When making a track with this library, compose every part by hand. Never fall back to stock
  patterns to save time.

## Working notes

- New songs start with `rick-rubin init <dir> ...`, which copies `project-template/` (a scaffold with no musical content) and wires its `CLAUDE.md` to import `PREFERENCES.md`.

- `song.py` is the source of truth; `song.json`, `score.md`, previews and the Live set are build outputs.
- The Live bridge listens on 127.0.0.1:9889. After changing `handlers.py`, run
  `rick-rubin install-bridge` and send the bridge a `reload` command; only `bridge.py` changes need
  the Control Surface re-selected.
- Remote-script code must stay Python 3.7 compatible.
- Tests: `.venv/bin/pytest -q`. The generator in `tests/fixture_songs.py` is test data only.
- Serum 2 is hosted in-process (`rick_rubin/serum.py`, via pedalboard): a `.SerumPreset` is converted to plug-in state (same XferJson/zstd/CBOR container; header hash = MD5 of the zstd block). Do not write files into `~/Library` from this project without David's say-so.
- **Ableton is the one source of truth for sound** (David, 2026-10-06: "are we building two sources of truth? i would rather lean on ableton where our own implementation might differ"). Do not add offline imitations of Live devices or of Live's mixer to the preview. When judging sound is slow, make the Live path faster (incremental push, short captures) instead.
