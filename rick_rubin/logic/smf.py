"""The song as a Standard MIDI File that Logic Pro opens as a complete project.

Logic has no scripting API for its arrangement, but it does read a Type 1 SMF as a *project*:
tempo, 4/4, markers (our sections), one software-instrument track per MIDI track with the track's
name, one region per track holding the notes, and an instrument chosen from the General MIDI program
number of the track (channel 10 gets a drum kit). That is the deterministic core of a Logic push:
the content goes in through this file, and the mixer, instruments, effects and automation are then
set through the Logic bridge (see bridge.py).

Differences from render/midi.py (the plain export): GM program changes so Logic picks a usable
instrument per role, a MIDI channel per track (drums on 10), CC7/CC10 initial values so the faders
start where the song says, and one MTrk per track even when the track is silent (Logic skips tracks
without events, so an empty track gets a muted placeholder note to keep the track order).
"""
from __future__ import annotations

import struct
from pathlib import Path

from ..model import DRUM_MAP, Song, Track

PPQ = 480

# General MIDI programs (0-based) Logic maps to its own patches when a MIDI file is opened. These are
# only the *default* sound of a role; `instrument=` on a track names a Logic patch loaded afterwards.
GM_PROGRAM_BY_ROLE = {
    "bass": 38, "sub": 38,            # Synth Bass 1 -> a synth bass patch
    "chords": 81, "stab": 81,         # Lead 1 (square) -> a poly synth
    "keys": 4, "organ": 16,           # Electric Piano 1 / Drawbar Organ
    "pad": 89, "vocal": 52,           # Pad 2 (warm) / Choir Aahs
    "lead": 80, "arp": 80, "pluck": 80,   # Lead 1 (square)
}
DRUM_CHANNEL = 9                      # MIDI channel 10 (0-based 9): Logic loads a drum kit
# CC7 as Logic reads it on import: 90 -> 0 dB, 127 -> +6 dB (checked on Logic 11.2)
CC7_UNITY = 90


def _vlq(n: int) -> bytes:
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.append((n & 0x7F) | 0x80)
        n >>= 7
    return bytes(reversed(out))


def _meta(t: int, data: bytes) -> bytes:
    return b"\xff" + bytes([t]) + _vlq(len(data)) + data


def _chunk(events: list[tuple[int, int, bytes]]) -> bytes:
    events.sort(key=lambda e: (e[0], e[1]))
    out, last = bytearray(), 0
    for tick, _, raw in events:
        out += _vlq(tick - last) + raw
        last = tick
    out += _vlq(0) + _meta(0x2F, b"")
    return b"MTrk" + struct.pack(">I", len(out)) + bytes(out)


def cc7_for_db(db: float) -> int:
    """The CC7 value that puts Logic's fader near `db` on import (a first guess; the bridge sets the
    exact value afterwards). Logic's fader law above 0 dB is ~ +6 dB over 37 steps, below it falls faster."""
    if db >= 0:
        return int(round(min(127, CC7_UNITY + db / 6.0 * 37)))
    return int(round(max(0, CC7_UNITY + db * 4.5)))


DRUM_PROGRAM = 25                     # on channel 10 Logic 11.2 answers this with its Drum Synth kit (0 is an acoustic SoCal kit)


def program_for(track: Track) -> int | None:
    if track.is_drum:
        return DRUM_PROGRAM
    return GM_PROGRAM_BY_ROLE.get(track.role, 80)


def channel_for(track: Track, i: int) -> int:
    """Drum roles on channel 10, everything else spread over the other 15 channels."""
    if track.is_drum:
        return DRUM_CHANNEL
    others = [c for c in range(16) if c != DRUM_CHANNEL]
    return others[i % len(others)]


def drum_pitch(track: Track) -> int:
    return DRUM_MAP.get(track.role, 60)


def export_logic_midi(song: Song, path: str | Path) -> dict:
    """Write `song` as the SMF Logic opens as a project. Returns {"path", "tracks": [{name, channel, program,
    notes}], "markers": n}. Audio-loop tracks and Serum tracks get an (empty) MIDI track too, so that Logic's
    track order equals the song's; their audio is placed by the bridge afterwards."""
    clips, markers = song.flatten()
    out_tracks = []
    mpqn = int(round(60_000_000 / song.bpm))
    cond: list[tuple[int, int, bytes]] = [
        (0, 0, _meta(0x03, song.title.encode("utf-8")[:120])),
        (0, 1, _meta(0x51, mpqn.to_bytes(3, "big"))),
        (0, 2, _meta(0x58, bytes([4, 2, 24, 8]))),
    ]
    for m in markers:
        cond.append((int(round(m.start * PPQ)), 3, _meta(0x06, m.name.encode("utf-8"))))
    chunks = [_chunk(cond)]                               # no channel events: Logic makes no track for it
    non_drum = 0
    for t in song.tracks:
        ch = channel_for(t, non_drum)
        if not t.is_drum:
            non_drum += 1
        prog = program_for(t)
        ev: list[tuple[int, int, bytes]] = [(0, 0, _meta(0x03, t.name.encode("utf-8")))]
        if prog is not None and not (t.audio or t.serum):
            ev.append((0, 1, bytes([0xC0 | ch, prog & 0x7F])))
        ev.append((0, 1, bytes([0xB0 | ch, 7, cc7_for_db(t.volume_db)])))
        ev.append((0, 1, bytes([0xB0 | ch, 10, max(0, min(127, int(round(64 + t.pan * 63))))])))
        n_notes = 0
        if not (t.audio or t.serum):
            for c in clips:
                if c.track != t.name:
                    continue
                for n in c.notes:
                    pitch = drum_pitch(t) if (t.sample and t.is_drum) else n.pitch
                    on = int(round((c.start + n.start) * PPQ))
                    off = max(on + 1, int(round((c.start + n.start + n.dur) * PPQ)))
                    ev.append((on, 3, bytes([0x90 | ch, pitch & 0x7F, max(1, min(127, int(n.vel)))])))
                    ev.append((off, 2, bytes([0x80 | ch, pitch & 0x7F, 0])))
                    n_notes += 1
        if n_notes == 0:
            # Logic drops an MTrk without note events; a velocity-1 note before the first downbeat keeps the
            # track (and the track order), and the bridge mutes nothing because it is inaudible at velocity 1
            ev.append((0, 3, bytes([0x90 | ch, 0, 1])))
            ev.append((1, 2, bytes([0x80 | ch, 0, 0])))
        chunks.append(_chunk(ev))
        out_tracks.append({"name": t.name, "channel": ch + 1, "program": prog, "notes": n_notes})
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"MThd" + struct.pack(">IHHH", 6, 1, len(chunks), PPQ) + b"".join(chunks))
    return {"path": path, "tracks": out_tracks, "markers": len(markers), "bars": song.total_bars}
