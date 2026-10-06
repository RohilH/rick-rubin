"""Built-in agent loop (Anthropic API). Optional — ableton-use is designed to be
driven equally well by a coding agent (Claude Code, Codex...) reading SKILL.md.

    from ableton_use import Agent
    Agent("~/music/sunrise", task="deep house, 122bpm, warm Rhodes, long DJ intro").run()

Pipeline (mirrors video-use):  read score -> propose plan -> confirm -> edit ops ->
render preview -> self-eval (max 3 passes) -> push to Live -> persist memory.
"""
from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Callable

from .project import Project

DEFAULT_MODEL = os.environ.get("ABLETON_USE_MODEL", "claude-opus-5-5")

SYSTEM = """You are a house-music producer working through the ableton-use library.
You never hear audio. You READ the song: score.md (arrangement map, energy curve,
every pattern as step strings / note events) is your primary view; eval.md gives
measured loudness and spectral balance per section; `view` gives a piano-roll +
spectrogram PNG for a bar range — use it only at decision points (a transition,
the drop, a muddy bar).

Workflow — follow it in order:
1. read_project. If project.md has history, summarise the last session in one line.
2. propose_plan: 4-8 sentences — subgenre, tempo/key, arrangement shape with bar
   counts, groove, harmony, sound palette, what makes the drop land. Wait for approval.
3. edit (batch JSON ops) to realise the plan. Prefer `generate` ops for
   idiomatic parts, then hand-edit notes/steps where taste matters.
4. render_and_eval. Fix every error and every warning you agree with. Re-run.
   At most 3 eval passes; if issues remain, report them rather than looping.
5. If the user wants it in Ableton: push_to_live (only after eval passes).
6. remember: strategy, decisions, reasoning, outstanding.

Hard rules (production correctness, not taste):
- Section lengths are multiples of 8 bars (4 at most for pickups); big change every 16.
- DJ-friendly: >=16-bar drums-led intro and outro; no bass/chords in the first/last 8 bars.
- One tempo for the whole track, 118-130 BPM.
- Melodic notes stay in key unless a chromatic note is a deliberate, noted choice.
- Bass is monophonic, roughly C0-G2, mostly avoids kick hits, and is sidechained.
- Nothing but bass/kick below C2 (MIDI 48): voice chords/pads above it.
- A drop must be preceded by tension (build or breakdown) and start with the kick on bar 1.
- song.json is the source of truth; Live is a render target. Never 'fix' things in Live.
Everything else — sound, groove, harmony, arrangement details — is your taste call.
"""

TOOLS = [
    {"name": "read_project", "description": "Return score.md, the last eval.md (if any) and project.md memory.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "propose_plan", "description": "Present the plain-English plan to the user and wait for approval. Returns the user's reply.",
     "input_schema": {"type": "object", "properties": {"plan": {"type": "string"}}, "required": ["plan"]}},
    {"name": "edit", "description": "Apply a batch of edit ops (see ableton_use.edits docstring) to song.json. Returns a change log and the new score.",
     "input_schema": {"type": "object", "properties": {"ops": {"type": "array", "items": {"type": "object"}}}, "required": ["ops"]}},
    {"name": "undo", "description": "Revert the last edit batch.", "input_schema": {"type": "object", "properties": {}}},
    {"name": "render_and_eval", "description": "Render the audio preview and return eval.md (lint + per-section audio measurements).",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "view", "description": "Piano roll + waveform + spectrogram PNG for a bar range (1-based inclusive). Use sparingly.",
     "input_schema": {"type": "object", "properties": {"start_bar": {"type": "integer"}, "end_bar": {"type": "integer"},
                                                        "tracks": {"type": "array", "items": {"type": "string"}}},
                      "required": ["start_bar", "end_bar"]}},
    {"name": "export_midi", "description": "Write song.mid and per-track .mid files.", "input_schema": {"type": "object", "properties": {}}},
    {"name": "push_to_live", "description": "Render the song into Ableton Live's arrangement via the bridge.",
     "input_schema": {"type": "object", "properties": {"replace": {"type": "boolean"}}}},
    {"name": "remember", "description": "Append this session to project.md.",
     "input_schema": {"type": "object", "properties": {k: {"type": "string"} for k in ("strategy", "decisions", "reasoning", "outstanding")}}},
]

EDIT_OPS_DOC = (Path(__file__).parent / "edits.py").read_text().split('"""')[1]


class Agent:
    def __init__(self, project: str | Path | Project, task: str, model: str = DEFAULT_MODEL,
                 confirm: Callable[[str], str] | None = None, max_turns: int = 40, client=None,
                 on_event: Callable[[str, str], None] | None = None, create_kwargs: dict | None = None):
        self.project = project if isinstance(project, Project) else Project(project)
        if not self.project.exists():
            Project.create(self.project.root, **(create_kwargs or {}))
        self.task = task
        self.model = model
        self.confirm = confirm or (lambda plan: "approved")
        self.max_turns = max_turns
        self.on_event = on_event or (lambda kind, text: print(f"[{kind}] {text}"))
        if client is None:
            import anthropic
            client = anthropic.Anthropic()
        self.client = client
        self.evals = 0

    # ---------------------------------------------------------------- tools
    def _tool(self, name: str, args: dict):
        p = self.project
        if name == "read_project":
            ev = p.eval_path.read_text() if p.eval_path.exists() else "(no eval yet)"
            return f"{p.score()}\n\n---\n# eval.md\n{ev}\n\n---\n# project.md\n{p.memory() or '(new project)'}"
        if name == "propose_plan":
            self.on_event("plan", args["plan"])
            return self.confirm(args["plan"])
        if name == "edit":
            log = p.edit(args["ops"])
            return "\n".join(log) + "\n\n" + p.score()
        if name == "undo":
            return f"restored {p.undo()}\n\n" + p.score()
        if name == "render_and_eval":
            self.evals += 1
            r = p.evaluate()
            note = "" if self.evals < 3 else "\n(3rd eval pass — report remaining issues instead of looping further.)"
            return r.text + note
        if name == "view":
            path = p.view((int(args["start_bar"]), int(args["end_bar"])), args.get("tracks"))
            data = base64.b64encode(path.read_bytes()).decode()
            return [{"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": data}},
                    {"type": "text", "text": f"saved {path}"}]
        if name == "export_midi":
            return "\n".join(str(x) for x in p.midi())
        if name == "push_to_live":
            return p.push(replace=bool(args.get("replace", False)), progress=lambda m: self.on_event("live", m)).text()
        if name == "remember":
            p.remember(**{k: args.get(k, "") for k in ("strategy", "decisions", "reasoning", "outstanding")})
            return "saved to project.md"
        raise ValueError(f"unknown tool {name}")

    # ---------------------------------------------------------------- loop
    def run(self) -> str:
        system = SYSTEM + "\n\nEdit op reference:\n" + EDIT_OPS_DOC
        msgs = [{"role": "user", "content": f"Project folder: {self.project.root}\n\nTask: {self.task}"}]
        final = ""
        for _ in range(self.max_turns):
            resp = self.client.messages.create(model=self.model, max_tokens=8000, system=system, tools=TOOLS, messages=msgs)
            msgs.append({"role": "assistant", "content": resp.content})
            results = []
            for block in resp.content:
                if block.type == "text" and block.text.strip():
                    final = block.text
                    self.on_event("agent", block.text)
                elif block.type == "tool_use":
                    self.on_event("tool", f"{block.name} {json.dumps(block.input)[:200]}")
                    try:
                        out = self._tool(block.name, block.input)
                        results.append({"type": "tool_result", "tool_use_id": block.id, "content": out})
                    except Exception as e:  # noqa: BLE001 — errors go back to the model to fix
                        results.append({"type": "tool_result", "tool_use_id": block.id, "content": f"ERROR: {e}", "is_error": True})
            if resp.stop_reason != "tool_use":
                break
            msgs.append({"role": "user", "content": results})
        return final
