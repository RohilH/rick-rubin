# Installing ableton-use for a coding agent

ableton-use has no agent harness of its own. Your coding agent (Claude Code, Codex, or any agent with shell access) is the harness. It reads `SKILL.md` and drives the `ableton-use` CLI and Python API.

## Setup prompt

Paste this into your agent:

```
Set up https://github.com/<you>/ableton-use for me.

Read install.md first: install the package, register the skill with whichever
agent you're running under, and install the Ableton bridge. Then read SKILL.md
for daily usage. After install, don't generate anything on your own. Tell me
it's ready, remind me to select the AbletonUse control surface in Live, and wait
for a brief.
```

## Steps (what the agent does)

1. **Clone and install** (Python 3.10+):
   ```bash
   git clone <repo> ~/Developer/ableton-use
   cd ~/Developer/ableton-use && pip install -e ".[all]"     # or: uv pip install -e ".[all]"
   ableton-use templates                                     # smoke test
   ```

2. **Register the skill:**
   ```bash
   ln -sfn ~/Developer/ableton-use ~/.claude/skills/ableton-use     # Claude Code
   # ln -sfn ~/Developer/ableton-use ~/.codex/skills/ableton-use    # Codex
   ```

3. **Install the Live bridge** (a MIDI Remote Script):
   ```bash
   ableton-use install-bridge          # copies AbletonUse/ into User Library/Remote Scripts
   ```
   The user then restarts Live and opens **Settings → Link, Tempo & MIDI**. Under **Control Surface**, they choose **AbletonUse**. Live's status bar shows "ableton-use bridge … listening on 127.0.0.1:9877".

4. **Verify:**
   ```bash
   ableton-use status                  # {"bridge": "0.2.0", "live_version": "12.x.y"}
   ```
   If this fails, check that the control surface is selected, then check Live's `Log.txt` for "ableton-use".

## Requirements

- Ableton Live 11 or later. Live 12 is recommended.
  - Arrangement clips are created natively on Live 12. On Live 11, each clip is built in a session slot and copied to the arrangement.
  - Device insertion by name uses Live 12.3+. On older versions it goes through the browser.
- `ffmpeg` is needed to tempo-match sample loops whose tempo differs from the song's (`brew install ffmpeg`), and to turn `preview.wav` into an mp3 for sharing. Everything else works without it.

## Day to day

Open your agent in any folder and give it a brief, for example: "deep house at 121, F dorian, dubby chords, long DJ intro, then push it to Ableton." The agent creates a project folder there and follows SKILL.md: plan → confirm → edit → eval → push → remember.
