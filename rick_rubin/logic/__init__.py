"""Logic Pro as a render target: the song goes in as a MIDI file Logic opens as a project; the mixer,
instruments, effects, sends and bounces are driven through accessibility, posted keystrokes and an
emulated Mackie Control. See bridge.py for the mechanisms and client.py for the push."""
from .bridge import LogicBridge, LogicError, logic_running
from .client import capture_logic, push_song
from .smf import export_logic_midi

__all__ = ["LogicBridge", "LogicError", "logic_running", "capture_logic", "push_song", "export_logic_midi"]
