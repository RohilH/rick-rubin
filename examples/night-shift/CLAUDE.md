# Night Shift

The example song of the Logic Pro render target: 126 BPM, F minor, a simple house track with a tech house
bassline. Pushed with `rick-rubin --daw logic push examples/night-shift` from the repo root.

@../../PREFERENCES.md

## How this project works

- Read `../../SKILL.md` before doing anything: it is the manual (notation, commands, the DAW bridges, tools).
- `song.py` is the song — the only file you compose in. Every other command rebuilds from it.
- `project.md` is this song's memory: the brief, the exploration log, decisions, what is still weak.
- **After every change to `song.py`, run `rick-rubin check .`** — it lints and type-checks the Python (ruff, mypy;
  config in `pyproject.toml`), builds the song and runs the music lint.
- Build outputs (`song.json`, `score.md`, `eval.md`, `preview.wav`, `logic/`) are not committed.
