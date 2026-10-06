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
# what `sidechain: true` on a track means: a pumping house compressor keyed from the kick
DEFAULT_SIDECHAIN = {"device": "Compressor", "params": {"Threshold": -28, "Ratio": 4, "Attack": 0.5, "Release": 120}}
# where instrument names are looked up, in order: Live's own, then the user's saved presets, then VST/AU plug-ins
INSTRUMENT_CATEGORIES = ["drums", "instruments", "sounds", "user_library", "plugins"]
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
            if info.get("instrument_params"):
                L.append(f"      instrument: {info['instrument_params']}")
            L += [f"      fx: {e}" for e in info.get("effects", [])]
        L += [f"  ! {w}" for w in self.warnings]
        return "\n".join(L)


def push_song(song: Song, bridge: LiveBridge, replace: bool = False, load_instruments: bool = True,
              sidechain: bool = True, clip_batch: int = 8, progress=None, clean: bool = False) -> PushReport:
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

    if clean:
        # drop the untouched tracks of a new set (no devices, no clips) — they count against Live Intro/Lite track limits
        empty = []
        for t in bridge.call("get_state")["tracks"]:
            if t["devices"] or t["arrangement_clips"] or t["name"] in {x.name for x in song.tracks}:
                continue
            slots = bridge.call("lom", path=f"song.tracks[{t['index']}].clip_slots")
            if not any(bridge.call("lom", path=f"song.tracks[{t['index']}].clip_slots[{j}].has_clip") for j in range(len(slots))):
                empty.append(t["index"])
        if empty:
            say(f"removing {len(empty)} empty tracks")
            bridge.call("delete_tracks", indices=empty)

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
            r = bridge.call("load_instrument", track=i, queries=t.instrument, categories=INSTRUMENT_CATEGORIES)
            info["instrument"] = r.get("loaded")
            if not r.get("loaded"):
                rep.warnings.append(f"{t.name}: none of {t.instrument} found in the Live browser — load an instrument manually")
        if t.instrument_params and not t.audio:
            dev = "Simpler" if t.sample else (info.get("instrument") or "")
            try:
                r = bridge.call("device", track=i, device=dev, params=t.instrument_params)
                info["instrument_params"] = ", ".join(f"{k} {v}" for k, v in r.get("set", {}).items())
                rep.warnings += [f"{t.name}: {dev}: {m}" for m in r.get("errors", [])]
            except BridgeError as err:
                rep.warnings.append(f"{t.name}: instrument parameters not set ({err})")
        bridge.call("set_track", index=i, volume_db=t.volume_db, pan=t.pan, mute=t.mute)
        rep.tracks[t.name] = info
    # tracks are appended at the end, so the indices returned above stay valid

    cmds = []
    for c in clips:
        trk = song.track(c.track)
        if c.audio:
            # Live drops envelopes when an audio clip is copied to the arrangement, so filter and volume moves
            # on loops are rendered into the audio itself (the same curves the preview uses)
            baked = {k: v for k, v in c.envelopes.items() if k in ("filter", "cutoff", "volume")}
            for k in set(c.envelopes) - set(baked):
                rep.warnings.append(f"clip {c.name}: automation of {k!r} is not supported on audio tracks")
            for s0, ln, off in c.segments:
                env = {k: _slice_env(pts, s0, s0 + ln) for k, pts in baked.items()}
                path = str(_segment_file(song, c.audio, off, ln, env))
                cmds.append(("create_audio_clip", {"track": index[c.track], "path": path, "start": c.start + s0, "name": c.name}))
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
    # effects after the clips, so they sit behind any Auto Filter the envelopes added
    kick = next((t.name for t in song.tracks if t.role == "kick"), None)
    for t in song.tracks:
        chain = [dict(e) for e in t.effects]
        if sidechain and t.sidechain and kick and not any(e.get("sidechain") for e in chain):
            chain.append(dict(DEFAULT_SIDECHAIN, sidechain=kick))        # `sidechain: true` shorthand
        seen: dict[str, int] = {}
        for e in chain:
            dev = e["device"]
            nth = seen.get(dev, 0)
            seen[dev] = nth + 1
            try:
                r = bridge.call("device", track=index[t.name], device=dev, params=e.get("params") or {},
                                sidechain=e.get("sidechain"), sidechain_tap=e.get("sidechain_tap"), nth=nth)
            except BridgeError as err:
                rep.warnings.append(f"{t.name}: {dev} failed ({err})")
                continue
            shown = ", ".join(f"{k} {v}" for k, v in r.get("set", {}).items())
            rep.tracks[t.name].setdefault("effects", []).append(
                dev + (f" <- {r['sidechain']}" if r.get("sidechain") else "") + (f" ({shown})" if shown else ""))
            if e.get("sidechain"):
                rep.tracks[t.name]["sidechain"] = "keyed from " + e["sidechain"] if r.get("sidechain") else "not routed"
            rep.warnings += [f"{t.name}: {dev}: {m}" for m in r.get("errors", [])]

    for m in markers:
        for _ in range(5):
            bridge.call("transport", action="seek", beat=m.start)
            if bridge.call("add_locator", name=m.name, beat=m.start).get("created"):
                break
        else:
            rep.warnings.append(f"locator {m.name!r} at beat {m.start:g} was not created")
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


def _segment_file(song: Song, rel: str, off: float, ln: float, env: dict | None = None) -> Path:
    """The file to place for `ln` beats of `rel` starting `off` beats in: the file
    itself when that is all of it and nothing is automated, otherwise a cut written
    next to it (samples/cuts/) with any filter/volume envelope rendered in."""
    import hashlib
    from ..render.preview import _apply_lowpass
    from ..samples import read_audio, write_wav24
    src = song.resolve(rel)
    sr, x = read_audio(src)
    spb = 60.0 / song.bpm
    a, n = int(round(off * spb * sr)), int(round(ln * spb * sr))
    env = {k: v for k, v in (env or {}).items() if v}
    if a == 0 and abs(len(x) - n) <= 2 and not env:
        return src
    tag = ("." + hashlib.sha1(json.dumps(env, sort_keys=True).encode()).hexdigest()[:8]) if env else ""
    out = src.parent / "cuts" / f"{src.stem}.{off:g}+{ln:g}{tag}.wav"
    if not out.exists() or out.stat().st_mtime < src.stat().st_mtime:
        seg = x[a:a + n].copy()
        if len(seg) < n:
            seg = np.concatenate([seg, np.zeros((n - len(seg), x.shape[1]), np.float32)])
        t = np.arange(len(seg)) / sr / spb                       # beats from the segment start
        for prm, pts in env.items():
            ctrl = np.interp(t, [q[0] for q in pts], [q[1] for q in pts])
            if prm == "volume":
                seg = seg * ctrl[:, None].astype(np.float32)
            else:
                cutoff = 60.0 * (18000.0 / 60.0) ** ctrl
                seg = np.stack([_apply_lowpass(seg[:, ch], cutoff, sr) for ch in range(seg.shape[1])], axis=1).astype(np.float32)
        f = min(len(seg) // 2, max(1, int(0.002 * sr)))
        ramp = np.linspace(0, 1, f, dtype=np.float32)[:, None]
        seg[:f] *= ramp
        seg[-f:] *= ramp[::-1]
        out.parent.mkdir(parents=True, exist_ok=True)
        write_wav24(out, sr, seg)
    return out


# ============================================================================ capture
CAPTURE_TRACK = "ableton-use capture"


def capture_live(song: Song, bridge: LiveBridge, out_path: str | Path, bars: tuple[int, int] | None = None,
                 tracks: list[str] | None = None, tail_beats: float = 2.0, progress=None) -> dict:
    """Record what Live itself plays — the pushed arrangement through Live's
    instruments, effects, sidechains and master — into a WAV, in real time.

    An audio track set to "Resampling" is armed, the arrangement is recorded from
    the first bar of `bars` (1-based, inclusive; default: the whole song) and the
    take is copied to `out_path`, trimmed so its first sample is that bar's
    downbeat. `tracks` solos those tracks for the take. Everything touched (solo,
    metronome, loop, the capture track) is put back afterwards."""
    import time
    from ..model import BEATS_PER_BAR
    from ..samples import read_audio, write_wav24
    say = progress or (lambda *_: None)
    lom = lambda path, **kw: bridge.call("lom", path=path, **kw)  # noqa: E731
    b0, b1 = bars or (1, song.total_bars)
    start, end = (b0 - 1) * BEATS_PER_BAR, b1 * BEATS_PER_BAR
    names = [t["name"] for t in bridge.call("get_state")["tracks"]]
    missing = [t for t in (tracks or []) if t not in names]
    if missing:
        raise BridgeError(f"cannot solo {missing}: not in the Live set (push first)")
    if lom("song.is_playing"):
        bridge.call("transport", action="stop")
        time.sleep(0.2)
    if CAPTURE_TRACK in names:
        bridge.call("delete_tracks", names=[CAPTURE_TRACK])
        names = [t["name"] for t in bridge.call("get_state")["tracks"]]
    restore: list[tuple[str, Any]] = []

    def setv(path, value):
        old = lom(path)
        if old != value:
            lom(path, op="set", value=value)
            restore.append((path, old))

    ci = bridge.call("create_audio_track", name=CAPTURE_TRACK)
    tp = f"song.tracks[{ci}]"
    try:
        lom(tp + ".input_routing_type", op="set", value="Resampling", choose=tp + ".available_input_routing_types")
        for i, n in enumerate(names):
            if lom(f"song.tracks[{i}].arm"):
                setv(f"song.tracks[{i}].arm", False)
            setv(f"song.tracks[{i}].solo", bool(tracks) and n in tracks)
        lom(tp + ".arm", op="set", value=True)
        setv("song.metronome", False)
        setv("song.loop", False)
        # Move the playhead while stopped (that also moves Live's start marker); "seek" only sets the
        # position — a second stop would send Live back to 1.1.1.
        for _ in range(10):
            bridge.call("transport", action="seek", beat=start)
            time.sleep(0.15)
            if not lom("song.is_playing") and abs(lom("song.current_song_time") - start) < 1e-3:
                break
        else:
            raise BridgeError(f"could not place Live's playhead at beat {start:g} (is someone using the transport?)")
        lom("song.record_mode", op="set", value=True)       # arrangement record: Live starts playing from the playhead
        for _ in range(20):
            if lom("song.is_playing"):
                break
            time.sleep(0.1)
        else:
            lom("song.continue_playing", op="call")
        secs = (end - start + tail_beats) * 60.0 / song.bpm
        say(f"recording bars {b0}-{b1} from Live ({secs:.0f} s, real time)")
        t_end = time.time() + secs + 20
        while lom("song.current_song_time") < end + tail_beats:
            if time.time() > t_end or not lom("song.is_playing"):
                raise BridgeError("Live stopped or stalled during the capture")
            time.sleep(0.25)
        bridge.call("transport", action="stop")
        lom("song.record_mode", op="set", value=False)
        time.sleep(0.5)
        clips = bridge.call("get_state")["tracks"][ci]["arrangement_clips"]
        if not clips:
            raise BridgeError("Live recorded nothing — is the capture track armed and set to Resampling?")
        k = max(range(len(clips)), key=lambda j: clips[j]["length"])
        src = lom(f"{tp}.arrangement_clips[{k}].file_path")
        clip_start = clips[k]["start"]
    finally:
        try:
            if lom("song.is_playing"):
                bridge.call("transport", action="stop")
            lom("song.record_mode", op="set", value=False)
        except BridgeError:
            pass
        for path, old in reversed(restore):
            try:
                lom(path, op="set", value=old)
            except BridgeError:
                pass
        try:
            bridge.call("delete_tracks", names=[CAPTURE_TRACK])
            bridge.call("transport", action="stop", beat=start)
        except BridgeError:
            pass
    for _ in range(20):                      # Live finishes writing the file just after stopping
        if Path(src).exists() and Path(src).stat().st_size > 1000:
            break
        time.sleep(0.25)
    sr, x = read_audio(src)
    spb = 60.0 / song.bpm
    shift = int(round((start - clip_start) * spb * sr))     # samples to drop (+) or pad (-) so the file starts on the downbeat
    x = x[shift:] if shift >= 0 else np.concatenate([np.zeros((-shift, x.shape[1]), np.float32), x])
    x = x[: int(round((end - start + tail_beats) * spb * sr))]
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_wav24(out_path, sr, x)
    return {"path": out_path, "source": src, "bars": (b0, b1), "tracks": tracks, "seconds": len(x) / sr,
            "peak_db": float(20 * np.log10(np.abs(x).max() + 1e-12))}


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
