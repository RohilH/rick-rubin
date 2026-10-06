"""End-to-end example: generate -> edit -> self-eval -> MIDI -> (optionally) push to Live.

    python examples/quickstart.py ~/music/demo [--push]
"""
import sys

from ableton_use import Project

out = sys.argv[1] if len(sys.argv) > 1 else "demo-track"
p = Project(out) if Project(out).exists() else Project.create(
    out, subgenre="deep", template="club", key="F dorian", seed=4, title="Sunrise Dub")

# A few producer moves, expressed as edit ops
p.edit([
    # rolling bass for the second drop so it lifts
    {"op": "generate", "what": "bass", "name": "bass_roll", "options": {"style": "rolling"}},
    {"op": "part", "section": "drop2", "track": "Bass", "pattern": "bass_roll"},
    # a call-and-response perc line that only appears in the drops
    {"op": "pattern", "name": "perc_drop", "track": "Perc", "pitch": "D2", "steps": "...x..x...x..x.x|...x..x....x.ox."},
    {"op": "part", "section": "drop", "track": "Perc", "pattern": "perc_drop"},
    {"op": "part", "section": "drop2", "track": "Perc", "pattern": "perc_drop"},
    # breathe the chords through the breakdown
    {"op": "automation", "section": "breakdown", "track": "Chords", "param": "filter", "points": [[0, 0.3], [0.5, 0.65], [1, 0.45]]},
])

result = p.evaluate()
print(result.text)
print("score:", p.score_path, "\npreview:", p.preview_path)
print("view:", p.view((57, 80)))
print("midi:", *p.midi()[:1], "...")

if "--push" in sys.argv:
    print(p.push(replace=True, progress=print).text())
p.remember(strategy="deep house sketch from examples/quickstart.py",
           decisions="rolling bass in drop2; drop-only perc; chord filter breathing in breakdown")
