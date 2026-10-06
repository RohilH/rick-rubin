"""Standard MIDI File export (no dependencies).

Writes a type-1 file with a conductor track (tempo, 4/4, section markers) plus one
track per Song track, plus one single-track file per instrument. The per-track
files are the reliable manual path: drag each onto its Live track at bar 1.
Live does not adopt the file's tempo on import, so set the tempo in Live
yourself (the bridge does this for you).
"""
from __future__ import annotations

import struct
from pathlib import Path

from ..model import ArrangementClip, Marker, Song

PPQ = 480


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
    """events: (abs_tick, order, raw_bytes_without_delta). order breaks ties (offs before ons)."""
    events.sort(key=lambda e: (e[0], e[1]))
    out, last = bytearray(), 0
    for tick, _, raw in events:
        out += _vlq(tick - last) + raw
        last = tick
    out += _vlq(0) + _meta(0x2F, b"")
    return b"MTrk" + struct.pack(">I", len(out)) + bytes(out)


def _conductor(song: Song, markers: list[Marker]) -> bytes:
    mpqn = int(round(60_000_000 / song.bpm))
    ev = [(0, 0, _meta(0x03, song.title.encode()[:120])),
          (0, 1, _meta(0x51, mpqn.to_bytes(3, "big"))),
          (0, 2, _meta(0x58, bytes([4, 2, 24, 8])))]
    for m in markers:
        ev.append((int(round(m.start * PPQ)), 3, _meta(0x06, m.name.encode())))
    return _chunk(ev)


def _track_chunk(name: str, clips: list[ArrangementClip], channel: int = 0) -> bytes:
    ev: list[tuple[int, int, bytes]] = [(0, 0, _meta(0x03, name.encode()))]
    ch = channel & 0x0F
    for c in clips:
        for n in c.notes:
            on = int(round((c.start + n.start) * PPQ))
            off = max(on + 1, int(round((c.start + n.start + n.dur) * PPQ)))
            ev.append((on, 2, bytes([0x90 | ch, n.pitch & 0x7F, max(1, min(127, n.vel))])))
            ev.append((off, 1, bytes([0x80 | ch, n.pitch & 0x7F, 0])))
    return _chunk(ev)


def _file(chunks: list[bytes]) -> bytes:
    return b"MThd" + struct.pack(">IHHH", 6, 1, len(chunks), PPQ) + b"".join(chunks)


def export_midi(song: Song, out_dir: str | Path, per_track: bool = True) -> list[Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    clips, markers = song.flatten()
    by_track: dict[str, list[ArrangementClip]] = {t.name: [] for t in song.tracks}
    for c in clips:
        by_track[c.track].append(c)
    paths = []
    full = out_dir / "song.mid"
    chunks = [_conductor(song, markers)]
    for i, t in enumerate(song.tracks):
        chunks.append(_track_chunk(t.name, by_track[t.name]))
    full.write_bytes(_file(chunks))
    paths.append(full)
    if per_track:
        for t in song.tracks:
            p = out_dir / f"{_safe(t.name)}.mid"
            p.write_bytes(_file([_conductor(song, markers), _track_chunk(t.name, by_track[t.name])]))
            paths.append(p)
    return paths


def _safe(s: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in s)


def read_midi_notes(path: str | Path) -> list[tuple[int, float, float, int, int]]:
    """Minimal SMF reader for tests/round-trips: returns (track_idx, start_beats, dur_beats, pitch, vel)."""
    data = Path(path).read_bytes()
    assert data[:4] == b"MThd"
    _, ntrk, ppq = struct.unpack(">HHH", data[8:14])
    pos, out = 14, []
    for ti in range(ntrk):
        assert data[pos:pos + 4] == b"MTrk"
        ln = struct.unpack(">I", data[pos + 4:pos + 8])[0]
        p, end, tick, status, open_ = pos + 8, pos + 8 + ln, 0, 0, {}
        while p < end:
            d = 0
            while True:
                b = data[p]; p += 1
                d = (d << 7) | (b & 0x7F)
                if not b & 0x80:
                    break
            tick += d
            b = data[p]
            if b == 0xFF:
                ln2 = 0; p += 2
                while True:
                    c = data[p]; p += 1
                    ln2 = (ln2 << 7) | (c & 0x7F)
                    if not c & 0x80:
                        break
                p += ln2
                continue
            if b & 0x80:
                status = b; p += 1
            kind = status & 0xF0
            a, v = data[p], data[p + 1]; p += 2
            if kind == 0x90 and v > 0:
                open_[a] = (tick, v)
            elif kind in (0x80, 0x90) and a in open_:
                st, vel = open_.pop(a)
                out.append((ti, st / ppq, (tick - st) / ppq, a, vel))
        pos = end
    return out
