"""Client for the ableton-use bridge + the `push_song` renderer (Song -> Live arrangement)."""
from __future__ import annotations

import itertools
import json
import os
import platform
import shutil
import socket
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from ..model import Song

DEFAULT_PORT = 9889
REMOTE_SCRIPT_DIR = Path(__file__).parent / "remote_script" / "AbletonUse"


class BridgeError(RuntimeError):
    pass


class LiveBridge:
    """Newline-delimited JSON over TCP to the AbletonUse remote script."""

    def __init__(self, host: str = "127.0.0.1", port: int = DEFAULT_PORT, timeout: float = 120.0):
        self.host, self.port, self.timeout = host, port, timeout
        self._sock: socket.socket | None = None
        self._buf = b""
        self._ids = itertools.count(1)

    def connect(self) -> "LiveBridge":
        try:
            self._sock = socket.create_connection((self.host, self.port), timeout=5)
        except OSError as e:
            raise BridgeError(
                f"cannot reach the ableton-use bridge at {self.host}:{self.port} ({e}). Is Live running with the "
                "'AbletonUse' control surface selected? Run `ableton-use install-bridge` first.") from e
        self._sock.settimeout(self.timeout)
        return self

    def close(self) -> None:
        if self._sock:
            self._sock.close()
            self._sock = None

    def __enter__(self):
        return self.connect() if self._sock is None else self

    def __exit__(self, *a):
        self.close()

    def _roundtrip(self, req: dict) -> dict:
        if self._sock is None:
            self.connect()
        assert self._sock
        self._sock.sendall((json.dumps(req) + "\n").encode())
        while b"\n" not in self._buf:
            chunk = self._sock.recv(1 << 16)
            if not chunk:
                raise BridgeError("bridge closed the connection")
            self._buf += chunk
        line, self._buf = self._buf.split(b"\n", 1)
        return json.loads(line)

    def call(self, cmd: str, **args: Any) -> Any:
        resp = self._roundtrip({"id": next(self._ids), "cmd": cmd, "args": args, "timeout": self.timeout})
        if not resp.get("ok"):
            raise BridgeError(f"{cmd}: {resp.get('error')}")
        return resp.get("result")

    def batch(self, commands: list[tuple[str, dict]]) -> list[dict]:
        resp = self._roundtrip({"id": next(self._ids), "cmd": "batch", "timeout": self.timeout,
                                "args": {"commands": [{"cmd": c, "args": a} for c, a in commands]}})
        if not resp.get("ok"):
            raise BridgeError(f"batch: {resp.get('error')}")
        return resp["result"]


@dataclass
class PushReport:
    live_version: str | None = None
    tracks: dict[str, dict] = field(default_factory=dict)
    clips: int = 0
    notes: int = 0
    warnings: list[str] = field(default_factory=list)

    def text(self) -> str:
        L = [f"Pushed to Live {self.live_version or '?'}: {len(self.tracks)} tracks, {self.clips} clips, {self.notes} notes"]
        for name, info in self.tracks.items():
            L.append(f"  - {name}: instrument={info.get('instrument')!s}" + (f", sidechain={info['sidechain']}" if info.get("sidechain") else ""))
        L += [f"  ! {w}" for w in self.warnings]
        return "\n".join(L)


def push_song(song: Song, bridge: LiveBridge, replace: bool = False, load_instruments: bool = True,
              sidechain: bool = True, clip_batch: int = 8, progress=None) -> PushReport:
    """Render a Song into Live's Arrangement View.

    One MIDI track per Song track, one arrangement clip per (section, track),
    section locators, tempo, instruments loaded from the browser by name,
    mixer volume/pan, filter automation as clip envelopes, and kick-keyed
    sidechain compressors. Re-pushing with replace=True deletes tracks with the
    same names first (the Song is the source of truth; Live is a render target).
    """
    say = progress or (lambda *_: None)
    rep = PushReport()
    rep.live_version = bridge.call("ping").get("live_version")
    state = bridge.call("get_state")
    existing = {t["name"] for t in state["tracks"]}
    clash = existing & {t.name for t in song.tracks}
    if clash:
        if not replace:
            raise BridgeError(f"Live set already has tracks {sorted(clash)}; re-run with replace=True to overwrite them")
        say(f"deleting {len(clash)} existing tracks")
        bridge.call("delete_tracks", names=sorted(clash))

    clips, markers = song.flatten()
    bridge.call("set_tempo", bpm=song.bpm)
    bridge.call("set_signature", numerator=4, denominator=4)

    index: dict[str, int] = {}
    for t in song.tracks:
        say(f"track {t.name}")
        i = bridge.call("create_audio_track" if t.audio else "create_midi_track", name=t.name, color_index=t.color)
        index[t.name] = i
        info: dict[str, Any] = {"index": i}
        if t.audio:
            info["instrument"] = "audio track"
        elif t.sample:
            path = song.resolve(t.sample)
            if not path.exists():
                rep.warnings.append(f"{t.name}: sample {path} not found")
            else:
                voices = 1 if t.role in ("bass", "sub") else 8 if t.role in ("chords", "stab", "keys", "pad", "organ") else 4
                r = bridge.call("load_sample", track=i, path=str(path), mode="oneshot" if t.is_drum else "classic",
                                root=t.sample_root, voices=None if t.is_drum else voices)
                info["instrument"] = f"Simpler <- {Path(t.sample).name}"
                if r.get("warning") or r.get("mode_error") or r.get("param_errors"):
                    rep.warnings.append(f"{t.name}: Simpler {r.get('warning') or r.get('mode_error') or r.get('param_errors')}")
        elif load_instruments and t.instrument:
            r = bridge.call("load_instrument", track=i, queries=t.instrument)
            info["instrument"] = r.get("loaded")
            if not r.get("loaded"):
                rep.warnings.append(f"{t.name}: none of {t.instrument} found in the Live browser — load an instrument manually")
        bridge.call("set_track", index=i, volume_db=t.volume_db, pan=t.pan, mute=t.mute)
        rep.tracks[t.name] = info
    # tracks are appended at the end, so the indices returned above stay valid

    cmds = []
    for c in clips:
        trk = song.track(c.track)
        if c.audio:
            for s0, ln, off in c.segments:
                # a segment that is not the whole file gets its own pre-cut file, so clips stay unwarped and exact
                path = str(_segment_file(song, c.audio, off, ln))
                env = {k: _slice_env(pts, s0, s0 + ln) for k, pts in c.envelopes.items()}
                cmds.append(("create_audio_clip", {"track": index[c.track], "path": path, "start": c.start + s0,
                                                   "name": c.name, "envelopes": env}))
            continue
        # Simpler one-shot drums: Simpler plays its sample at C3, so send every hit there
        notes = [[60 if (trk.sample and trk.is_drum) else n.pitch, round(n.start, 5), round(n.dur, 5), n.vel] for n in c.notes]
        cmds.append(("create_clip", {
            "track": index[c.track], "start": c.start, "length": c.length, "name": c.name,
            "notes": notes,
            "envelopes": {k: [[round(b, 5), v] for b, v in pts] for k, pts in c.envelopes.items()},
        }))
        rep.notes += len(c.notes)
    for k in range(0, len(cmds), clip_batch):
        say(f"clips {k + 1}-{min(k + clip_batch, len(cmds))} of {len(cmds)}")
        for res, (_, args) in zip(bridge.batch(cmds[k:k + clip_batch]), cmds[k:k + clip_batch]):
            if not res.get("ok"):
                rep.warnings.append(f"clip {args['name']}: {res.get('error')}")
                continue
            rep.clips += 1
            for prm, v in (res["result"].get("envelopes") or {}).items():
                if str(v).startswith("error"):
                    rep.warnings.append(f"clip {args['name']}: automation {prm} {v}")
    # sidechain after the clips so the compressor sits after any Auto Filter the envelopes added
    if sidechain and any(t.role == "kick" for t in song.tracks):
        kick = next(t.name for t in song.tracks if t.role == "kick")
        for t in song.tracks:
            if t.sidechain:
                try:
                    r = bridge.call("sidechain", track=index[t.name], source_track_name=kick)
                    rep.tracks[t.name]["sidechain"] = "keyed from " + kick if r.get("routed") else "compressor added, route its sidechain to Kick manually"
                    if not r.get("routed"):
                        rep.warnings.append(f"{t.name}: could not route compressor sidechain to {kick}")
                except BridgeError as e:
                    rep.warnings.append(f"{t.name}: sidechain failed ({e})")

    bridge.call("add_locators", markers=[[m.name, m.start] for m in markers])
    bridge.call("transport", action="stop", beat=0)
    bridge.call("show_message", text=f"ableton-use: pushed '{song.title}' ({rep.clips} clips)")
    return rep


def _slice_env(pts, a: float, b: float) -> list[list[float]]:
    """Envelope points [(beat, v)] restricted to [a, b] and re-based to a, with
    values interpolated at both edges."""
    pts = sorted(pts)

    def at(t):
        if t <= pts[0][0]:
            return pts[0][1]
        for (t0, v0), (t1, v1) in zip(pts, pts[1:]):
            if t0 <= t <= t1:
                return v0 if t1 == t0 else v0 + (v1 - v0) * (t - t0) / (t1 - t0)
        return pts[-1][1]
    out = [[0.0, at(a)]] + [[round(t - a, 5), v] for t, v in pts if a < t < b] + [[round(b - a, 5), at(b)]]
    return out


def _segment_file(song: Song, rel: str, off: float, ln: float) -> Path:
    """The file to place for `ln` beats of `rel` starting `off` beats in: the file
    itself when that is all of it, otherwise a cut written next to it (samples/cuts/)."""
    from ..samples import read_audio, write_wav24
    src = song.resolve(rel)
    sr, x = read_audio(src)
    spb = 60.0 / song.bpm
    a, n = int(round(off * spb * sr)), int(round(ln * spb * sr))
    if a == 0 and abs(len(x) - n) <= 2:
        return src
    out = src.parent / "cuts" / f"{src.stem}.{off:g}+{ln:g}.wav"
    if not out.exists() or out.stat().st_mtime < src.stat().st_mtime:
        seg = x[a:a + n].copy()
        if len(seg) < n:
            seg = np.concatenate([seg, np.zeros((n - len(seg), x.shape[1]), np.float32)])
        f = min(len(seg) // 2, max(1, int(0.002 * sr)))
        ramp = np.linspace(0, 1, f, dtype=np.float32)[:, None]
        seg[:f] *= ramp
        seg[-f:] *= ramp[::-1]
        out.parent.mkdir(parents=True, exist_ok=True)
        write_wav24(out, sr, seg)
    return out


# ============================================================================ install
def user_library_candidates() -> list[Path]:
    home = Path.home()
    if platform.system() == "Darwin":
        return [home / "Music" / "Ableton" / "User Library" / "Remote Scripts"]
    if platform.system() == "Windows":
        docs = Path(os.environ.get("USERPROFILE", home)) / "Documents"
        return [docs / "Ableton" / "User Library" / "Remote Scripts"]
    return [home / "Music" / "Ableton" / "User Library" / "Remote Scripts"]


def install_bridge(dest: str | Path | None = None) -> Path:
    """Copy the AbletonUse remote script into Live's User Library."""
    target_root = Path(dest) if dest else user_library_candidates()[0]
    target_root.mkdir(parents=True, exist_ok=True)
    target = target_root / "AbletonUse"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(REMOTE_SCRIPT_DIR, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return target
