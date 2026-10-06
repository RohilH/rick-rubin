"""ableton-use — agentic house-music production that renders to Ableton Live.

The LLM never listens to the track. It reads it: a compact text score, a
self-eval report with measured loudness and spectral balance per section, and
on-demand piano-roll/spectrogram pictures. song.json is the source of truth;
MIDI files, an audio preview and a full Ableton Live arrangement are render targets.
"""
from .model import Song, Track, Pattern, Section, Part, Fill, Note
from .theory import Key
from .house import generate
from .project import Project

__version__ = "0.1.0"
__all__ = ["Song", "Track", "Pattern", "Section", "Part", "Fill", "Note", "Key", "generate", "Project", "Agent"]


def __getattr__(name):
    if name == "Agent":
        from .agent import Agent
        return Agent
    raise AttributeError(name)
