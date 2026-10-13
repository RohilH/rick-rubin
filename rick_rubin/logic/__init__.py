"""Logic Pro as a render target: the song goes in as a MIDI file Logic opens as a project; the mixer,
instruments, effects, sends and bounces are driven through accessibility, posted keystrokes and an
emulated Mackie Control. See bridge.py for the mechanisms, client.py for the push and stems.py for
Logic's Stem Splitter."""
from .bridge import LogicBridge, LogicError, logic_running
from .client import capture_logic, push_song
from .smf import export_logic_midi
from .stems import split_stems

__all__ = ["LogicBridge", "LogicError", "capture_logic", "export_logic_midi", "logic_running", "push_song", "split_stems"]
