"""Drive the built-in Agent loop with a scripted fake Anthropic client."""
from types import SimpleNamespace as NS

from ableton_use.agent import Agent


def _tool(i, name, inp):
    return NS(type="tool_use", id=f"t{i}", name=name, input=inp)


class FakeClient:
    def __init__(self, script):
        self.script = list(script)
        self.calls = []
        self.messages = self

    def create(self, **kw):
        self.calls.append({**kw, "messages": list(kw["messages"])})  # snapshot
        content, stop = self.script.pop(0)
        return NS(content=content, stop_reason=stop)


def test_agent_loop(tmp_path):
    script = [
        ([_tool(1, "read_project", {})], "tool_use"),
        ([_tool(2, "propose_plan", {"plan": "Tech house at 126, rolling bass."})], "tool_use"),
        ([_tool(3, "edit", {"ops": [{"op": "set", "field": "bpm", "value": 126}]}),
          _tool(4, "edit", {"ops": [{"op": "part", "section": "drop", "track": "Nope", "pattern": "x"}]})], "tool_use"),
        ([_tool(5, "render_and_eval", {}), _tool(6, "view", {"start_bar": 33, "end_bar": 48})], "tool_use"),
        ([_tool(7, "remember", {"strategy": "rolling tech house"})], "tool_use"),
        ([NS(type="text", text="Done: 126 BPM tech house, eval passes.")], "end_turn"),
    ]
    client = FakeClient(script)
    plans = []
    agent = Agent(tmp_path / "p", "tech house please", client=client, confirm=lambda p: plans.append(p) or "approved",
                  on_event=lambda *a: None, create_kwargs={"subgenre": "tech", "template": "radio", "seed": 1})
    out = agent.run()
    assert out.startswith("Done")
    assert plans == ["Tech house at 126, rolling bass."]
    assert agent.project.load().bpm == 126
    # the bad edit came back to the model as an error, not an exception
    results = client.calls[3]["messages"][-1]["content"]
    assert results[1]["is_error"] and "ERROR" in results[1]["content"]
    # view returned an image block
    img = client.calls[4]["messages"][-1]["content"][1]["content"][0]
    assert img["type"] == "image" and img["source"]["media_type"] == "image/png"
    assert "Session 1" in agent.project.memory()
