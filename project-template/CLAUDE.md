# {title}

A song project for rick-rubin. {bpm} BPM, {key}.

@{prefs}

## How this project works

- Read `{repo}/SKILL.md` before doing anything: it is the manual (notation, commands, Live bridge, tools).
- `song.py` is the song — the only file you compose in. Every other command rebuilds from it.
- `project.md` is this song's memory: the brief, the exploration log, decisions, what is still weak.
  Read it first; add to it as you go, not only at the end.
- `samples/raw/` holds untouched downloads, `samples/` the imported/conformed files, and
  `samples/manifest.json` records every candidate (and, under `analysis`, each file's measured character — `{cli} samples .` lists and searches them) — the ones used *and* the ones rejected, with the reason.
- **After every change to `song.py`, run `{cli} check .`** — it lints and type-checks the Python (ruff, mypy; config in `pyproject.toml`), builds the song and runs the music lint. Fix what it reports before measuring or pushing.
- Run the tools from this folder: `{cli} score .`, `{cli} eval .`, `{cli} audition . samples/raw/*.wav`,
  `{cli} push .`, `{cli} capture . --bars 33-40`.
