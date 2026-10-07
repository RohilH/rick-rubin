"""Client for the ableton-use bridge + the `push_song` renderer (Song -> Live arrangement)."""
from __future__ import annotations

import itertools
import json
import os
import platform
import shutil
import socket
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from ..model import Song, simpler_velocity_db

DEFAULT_PORT = 9889
# what `sidechain: true` on a track means: a pumping house compressor keyed from the kick
DEFAULT_SIDECHAIN = {"device": "Compressor", "params": {"Threshold": -28, "Ratio": 4, "Attack": 0.5, "Release": 120}}
# where instrument names are looked up, in order: Live's own, then the user's saved presets, then VST/AU plug-ins
INSTRUMENT_CATEGORIES = ["drums", "instruments", "sounds", "user_library", "plugins"]
REMOTE_SCRIPT_DIR = Path(__file__).parent / "remote_script" / "AbletonUse"


def sample_unity_offset(track) -> float:
    """dB by which Simpler would play a velocity-100 note above the file's level at this track's sensitivity."""
    sens = float(track.instrument_params.get("Vol < Vel", 35.0)) if track.instrument_params else 35.0
    return simpler_velocity_db(100, sens)


class BridgeError(RuntimeError):
    pass


def lock_path(port: int = DEFAULT_PORT) -> Path:
    import tempfile
    return Path(tempfile.gettempdir()) / ("ableton-use-live.lock" if port == DEFAULT_PORT else f"ableton-use-live-{port}.lock")


@contextmanager
def live_lock(what: str = "", wait_s: float = 1800.0, progress=None, port: int = DEFAULT_PORT):
    """One push/capture at a time: Live has a single arrangement and a single transport, so two agents
    (or two terminals) using it at once would record each other's audio. Waits for whoever holds it
    (a holder whose process is gone is ignored); nested use within one process is free."""
    import os
    import time
    path = lock_path(port)
    me = os.getpid()

    def holder():
        try:
            pid, _, label = path.read_text().partition(" ")
            try:
                os.kill(int(pid), 0)
            except PermissionError:                         # alive, just not ours to signal
                pass
            return int(pid), label.strip()
        except (OSError, ValueError):
            return None

    h = holder()
    if h and h[0] == me:
        yield
        return
    t_end = time.time() + wait_s
    told = False
    while True:
        h = holder()
        if h is None:
            try:
                path.unlink(missing_ok=True)
                fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, f"{me} {what}".encode())
                os.close(fd)
                break
            except FileExistsError:
                continue
        if time.time() > t_end:
            raise BridgeError(f"Live is in use by another ableton-use run ({h[1] or 'pid ' + str(h[0])}) and did not free up in {wait_s / 60:.0f} min")
        if progress and not told:
            progress(f"waiting: Live is in use by {h[1] or 'pid ' + str(h[0])}")
            told = True
        time.sleep(2.0)
    try:
        yield
    finally:
        path.unlink(missing_ok=True)


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
    mode: str = ""

    def text(self) -> str:
        n_tracks = sum(1 for k in self.tracks if k != "master" and not k.startswith("return "))
        L = [f"Pushed to Live {self.live_version or '?'}: {n_tracks} tracks, {self.clips} clips, {self.notes} notes"
             + (f"  [{self.mode}]" if self.mode else "")]
        for name, info in self.tracks.items():
            L.append(f"  - {name}: instrument={info.get('instrument')!s}" + (f", sidechain={info['sidechain']}" if info.get("sidechain") else ""))
            L += [f"      midi fx: {e}" for e in info.get("midi_effects", [])]
            if info.get("instrument_params"):
                L.append(f"      instrument: {info['instrument_params']}")
            L += [f"      fx: {e}" for e in info.get("effects", [])]
            if info.get("sends"):
                L.append("      sends: " + ", ".join(info["sends"]))
        L += [f"  ! {w}" for w in self.warnings]
        return "\n".join(L)


def push_song(song: Song, bridge: LiveBridge, replace: bool = False, load_instruments: bool = True,
              sidechain: bool = True, clip_batch: int = 8, progress=None, clean: bool = False,
              only: set[str] | None = None, fx_only: set[str] | None = None, mix_only: set[str] | None = None,
              chains: bool = True, locators: bool = True) -> PushReport:
    """Render a Song into Live's Arrangement View.

    One MIDI track per Song track, one arrangement clip per (section, track),
    section locators, tempo, instruments loaded from the browser by name,
    mixer volume/pan, filter automation as clip envelopes, and kick-keyed
    sidechain compressors. Re-pushing with replace=True deletes tracks with the
    same names first (the Song is the source of truth; Live is a render target).

    `only` rebuilds just those tracks and leaves the rest of the set alone (see `update_song`): `fx_only`
    are further tracks whose device parameters are set again, `mix_only` ones whose fader/pan/sends are,
    `chains` / `locators` say whether returns + master and the section locators are redone.
    """
    part = only is not None
    touch_fx = (only or set()) | (fx_only or set())
    touch_mix = (only or set()) | (mix_only or set())
    say = progress or (lambda *_: None)
    rep = PushReport()
    rep.live_version = bridge.call("ping").get("live_version")
    state = bridge.call("get_state")
    existing = {t["name"] for t in state["tracks"]}
    clash = existing & {t.name for t in song.tracks}
    if part:
        clash &= only or set()
        replace, clean = True, False
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
    sounding, _ = song.flatten(sounding=True)             # for parts rendered offline (Serum): what the MIDI effects make of them
    bridge.call("set_tempo", bpm=song.bpm)
    bridge.call("set_signature", numerator=4, denominator=4)

    index: dict[str, int] = {}
    for t in song.tracks:
        if part and t.name not in (only or ()):
            continue
        say(f"track {t.name}")
        i = bridge.call("create_audio_track" if (t.audio or t.serum) else "create_midi_track", name=t.name, color_index=t.color)
        index[t.name] = i
        info: dict[str, Any] = {"index": i}
        if t.audio:
            info["instrument"] = "audio track"
        elif t.serum:
            info["instrument"] = f"Serum 2 '{t.serum}' (rendered to audio)"
        elif t.sample:
            path = song.resolve(t.sample)
            if not path.exists():
                rep.warnings.append(f"{t.name}: sample {path} not found")
            else:
                voices = 1 if t.role in ("bass", "sub") else 8 if t.role in ("chords", "stab", "keys", "pad", "organ") else 4
                # Simpler boosts by velocity (see model.simpler_velocity_db); cancel it at velocity 100 so that
                # a velocity-100 hit plays the file at its own level, like an audio clip and like the preview
                r = bridge.call("load_sample", track=i, path=str(path), mode="oneshot" if t.is_drum else "classic",
                                root=t.sample_root, voices=None if t.is_drum else voices,
                                volume_db=round(-sample_unity_offset(t), 2))
                info["instrument"] = f"Simpler <- {Path(t.sample).name}"
                if r.get("warning") or r.get("mode_error") or r.get("param_errors"):
                    rep.warnings.append(f"{t.name}: Simpler {r.get('warning') or r.get('mode_error') or r.get('param_errors')}")
        elif load_instruments and t.instrument:
            r = bridge.call("load_instrument", track=i, queries=t.instrument, categories=INSTRUMENT_CATEGORIES)
            info["instrument"] = r.get("loaded")
            if not r.get("loaded"):
                rep.warnings.append(f"{t.name}: none of {t.instrument} found in the Live browser — load an instrument manually")
        for k, e in enumerate([] if (t.audio or t.serum) else t.midi_effects):
            try:                                            # in front of the instrument, in chain order
                r = bridge.call("device", track=i, device=e["device"], params=e.get("params") or {}, at=k,
                                nth=sum(1 for x in t.midi_effects[:k] if x["device"] == e["device"]))
                shown = ", ".join(f"{a} {b}" for a, b in r.get("set", {}).items())
                info.setdefault("midi_effects", []).append(e["device"] + (f" ({shown})" if shown else ""))
                rep.warnings += [f"{t.name}: {e['device']}: {m}" for m in r.get("errors", [])]
            except BridgeError as err:
                rep.warnings.append(f"{t.name}: MIDI effect {e['device']} failed ({err})")
        if t.serum and t.midi_effects:
            info["midi_effects"] = [e["device"] + " (rendered into the audio)" for e in t.midi_effects]
        if t.instrument_params and not t.audio and not t.serum:
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
    if clean:
        mine = {t.name for t in song.tracks}
        st = bridge.call("get_state")["tracks"]
        left = [t["index"] for t in st if t["name"] not in mine and not t["devices"] and not t["arrangement_clips"]
                and not any(bridge.call("lom", path=f"song.tracks[{t['index']}].clip_slots[{j}].has_clip")
                            for j in range(len(bridge.call("lom", path=f"song.tracks[{t['index']}].clip_slots"))))]
        if left:                                           # e.g. the placeholder Live needed while the old tracks went
            bridge.call("delete_tracks", indices=left)
            index = {t["name"]: t["index"] for t in bridge.call("get_state")["tracks"] if t["name"] in mine}
            for name, i in index.items():
                rep.tracks[name]["index"] = i

    if part:
        index = {t["name"]: t["index"] for t in bridge.call("get_state")["tracks"] if t["name"] in {x.name for x in song.tracks}}
        for t in song.tracks:
            if t.name in (mix_only or ()) and t.name in index:
                bridge.call("set_track", index=index[t.name], volume_db=t.volume_db, pan=t.pan, mute=t.mute)
    cmds = []
    for t in song.tracks:
        mine = [c for c in clips if c.track == t.name]
        if part and t.name not in (only or ()):
            continue
        if t.serum and mine:
            # one unwarped clip for the whole song: the part as Serum plays it, with any filter/volume moves rendered in
            from ..serum import track_stem
            stem = track_stem(song, t, sounding)
            regions = [(c.start, {k: v for k, v in c.envelopes.items() if k in ("filter", "cutoff", "volume")}) for c in mine]
            path = _baked_stem(song, stem, [(st, env) for st, env in regions if env])
            cmds.append(("create_audio_clip", {"track": index[t.name], "path": str(path), "start": 0.0, "name": f"Serum · {t.serum}"}))
            rep.notes += sum(len(c.notes) for c in mine)
    for c in clips:
        trk = song.track(c.track)
        if trk.serum or (part and c.track not in (only or ())):
            continue
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
        if part and t.name not in touch_fx:
            continue
        rep.tracks.setdefault(t.name, {"index": index.get(t.name)})
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

    # returns, sends and the master chain
    letters = sorted(song.returns) if chains else []
    if letters:
        need = max("ABCDEFGHIJKL".index(x) for x in letters) + 1
        try:
            bridge.call("ensure_returns", count=need)
        except BridgeError as err:
            rep.warnings.append(f"returns: could not create return tracks ({err})")
    for where, label, chain in ([(f"return:{'ABCDEFGHIJKL'.index(x)}", f"return {x}", song.returns[x]) for x in letters]
                                + ([("master", "master", song.master_effects)] if song.master_effects and chains else [])):
        try:
            bridge.call("set_chain", track=where, devices=[e["device"] for e in chain],
                        name=chain[0]["device"] if chain and where != "master" else None)
            seen: dict[str, int] = {}
            shown_all = []
            for e in chain:
                nth = seen.get(e["device"], 0)
                seen[e["device"]] = nth + 1
                r = bridge.call("device", track=where, device=e["device"], params=e.get("params") or {}, nth=nth)
                shown = ", ".join(f"{k} {v}" for k, v in r.get("set", {}).items())
                shown_all.append(e["device"] + (f" ({shown})" if shown else ""))
                rep.warnings += [f"{label}: {e['device']}: {m}" for m in r.get("errors", [])]
            rep.tracks[label] = {"instrument": "—", "effects": shown_all}
        except BridgeError as err:
            rep.warnings.append(f"{label}: {err}")
    if song.returns or any(t.sends for t in song.tracks):
        n_returns = len(bridge.call("lom", path="song.return_tracks"))
        for t in song.tracks:
            if part and t.name not in touch_mix:
                continue
            rep.tracks.setdefault(t.name, {"index": index.get(t.name)})
            for k in range(n_returns):
                letter = "ABCDEFGHIJKL"[k]
                try:
                    v = bridge.call("set_send", track=index[t.name], index=k, db=t.sends.get(letter))
                    if letter in t.sends:
                        rep.tracks[t.name].setdefault("sends", []).append(f"{letter} {v}")
                except BridgeError as err:
                    rep.warnings.append(f"{t.name}: send {letter} failed ({err})")

    for m in (markers if locators else []):
        for _ in range(5):
            bridge.call("transport", action="seek", beat=m.start)
            if bridge.call("add_locator", name=m.name, beat=m.start).get("created"):
                break
        else:
            rep.warnings.append(f"locator {m.name!r} at beat {m.start:g} was not created")
    if part and bridge.call("lom", path="song.is_playing"):
        bridge.call("show_message", text=f"ableton-use: updated '{song.title}'")    # hot reload: leave the transport running
        return rep
    bridge.call("transport", action="stop", beat=0)
    bridge.call("show_message", text=f"ableton-use: pushed '{song.title}' ({rep.clips} clips)")
    return rep


# ============================================================================ pushing only what changed
def _fingerprints(song: Song) -> dict:
    """What decides each part of the Live set, so a later push can tell what it has to redo."""
    import hashlib
    clips, markers = song.flatten()
    sounding, _ = song.flatten(sounding=True)
    kick = next((t.name for t in song.tracks if t.role == "kick"), None)

    def h(obj) -> str:
        return hashlib.sha1(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:12]

    def mtime(rel):
        try:
            return song.resolve(rel).stat().st_mtime
        except OSError:
            return None

    tracks = {}
    for t in song.tracks:
        d = t.to_json()
        mix = {k: d.pop(k, None) for k in ("volume_db", "pan", "mute", "sends")}
        chain = [dict(e) for e in d.pop("effects", [])]
        if t.sidechain and kick and not any(e.get("sidechain") for e in chain):
            chain.append(dict(DEFAULT_SIDECHAIN, sidechain=kick))
        src = sounding if t.serum else clips
        mine = [[c.name, c.start, c.length, [n.to_json() for n in c.notes], c.envelopes, c.audio, c.segments, mtime(c.audio) if c.audio else None]
                for c in src if c.track == t.name]
        tracks[t.name] = {
            "content": h([d, mine, mtime(t.sample) if t.sample else None, song.bpm, song.total_bars if t.serum else None]),
            "shape": h([[e["device"], e.get("sidechain"), e.get("sidechain_tap"), sorted(e.get("params") or {})] for e in chain]),
            "params": h(chain), "mix": h(mix), "keys": sorted({e["sidechain"] for e in chain if e.get("sidechain")}),
        }
    return {"title": song.title, "order": [t.name for t in song.tracks], "tracks": tracks,
            "chains": h([song.returns, song.master_effects]), "markers": h([[m.name, m.start] for m in markers]), "bpm": song.bpm}


def push_record(song: Song) -> Path | None:
    return Path(song.base_dir) / ".live-push.json" if song.base_dir is not None else None


def update_song(song: Song, bridge: LiveBridge, progress=None, **kw) -> PushReport:
    """Bring the Live set in line with `song`, redoing only what changed since the last push from this
    project: a changed part or instrument rebuilds that one track, a changed device parameter is set in
    place, a fader, pan or send is moved, returns and master are redone only when they differ. Falls back
    to a full replace when there is no record of the last push or the set no longer matches it (tracks
    renamed, removed or added by hand). The report says which it was."""
    say = progress or (lambda *_: None)
    rec_path = push_record(song)
    new = _fingerprints(song)
    old = None
    if rec_path and rec_path.exists():
        try:
            old = json.loads(rec_path.read_text())
        except ValueError:
            old = None
    why = None
    if old is None:
        why = "no record of an earlier push"
    else:
        live = [t["name"] for t in bridge.call("get_state")["tracks"]]
        if sorted(n for n in live if n in old["tracks"]) != sorted(old["tracks"]) or old.get("title") != new["title"]:
            why = "the Live set does not hold the last push any more"
        elif old.get("bpm") != new["bpm"] or set(old["tracks"]) - set(new["tracks"]):
            why = "tempo or track list changed"
    if why:
        say(f"full push ({why})")
        rep = push_song(song, bridge, replace=True, clean=True, progress=progress, **kw)
        rep.mode = f"full push — {why}"
    else:
        assert old is not None
        o, n = old["tracks"], new["tracks"]
        only = {k for k in n if k not in o or o[k]["content"] != n[k]["content"] or o[k]["shape"] != n[k]["shape"]}
        fx = {k for k in n if k not in only and (o[k]["params"] != n[k]["params"] or set(n[k]["keys"]) & only)}
        mix = {k for k in n if k not in only and o[k]["mix"] != n[k]["mix"]}
        chains = old["chains"] != new["chains"]
        marks = old["markers"] != new["markers"]
        if not (only or fx or mix or chains or marks):
            rep = PushReport(live_version=bridge.call("ping").get("live_version"))
            rep.mode = "nothing changed since the last push"
        else:
            say("update: " + "; ".join(x for x in (f"rebuild {sorted(only)}" if only else "", f"devices {sorted(fx)}" if fx else "",
                                                   f"mixer {sorted(mix)}" if mix else "", "returns/master" if chains else "",
                                                   "locators" if marks else "") if x))
            rep = push_song(song, bridge, replace=True, progress=progress, only=only, fx_only=fx, mix_only=mix, chains=chains,
                            locators=marks, **kw)
            rep.mode = "update — " + ", ".join(x for x in (
                f"rebuilt {', '.join(sorted(only))}" if only else "", f"device parameters on {', '.join(sorted(fx))}" if fx else "",
                f"mixer on {', '.join(sorted(mix))}" if mix else "", "returns/master" if chains else "", "locators" if marks else "") if x)
    if rec_path:
        rec_path.write_text(json.dumps(new, indent=1) + "\n")
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


def _baked_stem(song: Song, stem: Path, regions: list[tuple[float, dict]]) -> Path:
    """`stem` with section automation rendered in. regions: (start beat, {param: [(beat in clip, value 0..1), ...]})."""
    if not regions:
        return stem
    import hashlib
    from ..render.preview import _apply_lowpass
    from ..samples import read_audio, write_wav24
    out = stem.with_name(stem.stem + "." + hashlib.sha1(json.dumps(regions, sort_keys=True).encode()).hexdigest()[:8] + ".baked.wav")
    if out.exists() and out.stat().st_mtime >= stem.stat().st_mtime:
        return out
    sr, x = read_audio(stem)
    x = x.copy()
    spb = 60.0 / song.bpm
    for start, env in regions:
        for prm, pts in env.items():
            pts = sorted(pts)
            a, b = int((start + pts[0][0]) * spb * sr), min(len(x), int((start + pts[-1][0]) * spb * sr))
            if b - a < 16:
                continue
            t = np.arange(b - a) / sr / spb + pts[0][0]
            ctrl = np.interp(t, [q[0] for q in pts], [q[1] for q in pts])
            if prm == "volume":
                x[a:b] *= ctrl[:, None].astype(np.float32)
            else:
                cutoff = 60.0 * (18000.0 / 60.0) ** ctrl
                x[a:b] = np.stack([_apply_lowpass(x[a:b, ch], cutoff, sr) for ch in range(x.shape[1])], axis=1)
    write_wav24(out, sr, x)
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
        # Arrangement record starts from Live's start marker, not from the playhead
        setv("song.start_time", float(start))
        time.sleep(0.15)
        # Live starts playing and recording from the start marker. Right after a push it can still be busy
        # loading samples and devices and ignore the first request, so the start is tried a few times.
        for attempt in range(4):
            lom("song.record_mode", op="set", value=True)
            for _ in range(20):
                if lom("song.is_playing"):
                    break
                time.sleep(0.1)
            else:
                lom("song.continue_playing", op="call")
            time.sleep(1.2)
            if lom("song.current_song_time") - start >= 0.05:
                break
            say("Live's transport has not started yet — trying again")
            bridge.call("transport", action="stop")
            lom("song.record_mode", op="set", value=False)
            time.sleep(1.5 * (attempt + 1))
            lom("song.start_time", op="set", value=float(start))
            time.sleep(0.2)
        else:
            raise BridgeError("Live's transport is not moving, so nothing can be recorded. That is what Live does when it has no "
                              "audio output device: choose one in Live > Settings > Audio (Output Device), then run capture again.")
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


# ============================================================================ what a Live device offers
PROBE_TRACK = "ableton-use probe"


def devices_cache() -> Path:
    return Path(__file__).resolve().parent.parent.parent / ".cache" / "live-devices.json"


def describe_device(bridge: LiveBridge, name: str) -> dict:
    """Every parameter of a Live device with its range, as Live displays it: {"device", "parameters":
    [{"name", "value", "min", "max", "choices"}]}. The device is loaded on a temporary track that is removed
    again, so nothing in the set changes. Results are remembered in .cache/live-devices.json."""
    state = bridge.call("get_state")
    if any(t["name"] == PROBE_TRACK for t in state["tracks"]):
        bridge.call("delete_tracks", names=[PROBE_TRACK])
    err: Exception | None = None
    for make in ("create_midi_track", "create_audio_track"):     # MIDI effects and instruments need a MIDI track
        ti = bridge.call(make, name=PROBE_TRACK)
        try:
            bridge.call("insert_device", track=ti, name=name)
            base = f"song.tracks[{ti}].devices"
            devs = bridge.call("lom", path=base)
            if not devs:
                raise BridgeError(f"{name} did not load")
            dp = f"{base}[{len(devs) - 1}]"
            names = bridge.call("lom", path=dp + ".parameters")
            cmds: list[tuple[str, dict]] = []
            for i in range(len(names)):
                pp = f"{dp}.parameters[{i}]"
                cmds += [("lom", {"path": pp + "." + a}) for a in ("min", "max", "value", "is_quantized")]
            got = [r.get("result") for r in bridge.batch(cmds)]
            cmds = []
            for i in range(len(names)):
                pp = f"{dp}.parameters[{i}]"
                lo, hi, val, quant = got[4 * i: 4 * i + 4]
                cmds += [("lom", {"path": pp + ".str_for_value", "op": "call", "args": [v]}) for v in (lo, hi, val)]
                cmds.append(("lom", {"path": pp + ".value_items"}) if quant else ("ping", {}))
            shown = [r.get("result") for r in bridge.batch(cmds)]
            params = []
            for i, n in enumerate(names):
                lo, hi, val, items = shown[4 * i: 4 * i + 4]
                quant = got[4 * i + 3]
                params.append({"name": n, "value": val, "min": lo, "max": hi, "choices": list(items) if quant and isinstance(items, list) else None})
            out = {"device": bridge.call("lom", path=dp + ".name"), "class": bridge.call("lom", path=dp + ".class_display_name"), "parameters": params}
            cache = json.loads(devices_cache().read_text()) if devices_cache().exists() else {}
            cache[out["device"]] = out
            devices_cache().parent.mkdir(parents=True, exist_ok=True)
            devices_cache().write_text(json.dumps(cache, indent=1) + "\n")
            return out
        except BridgeError as e:
            err = e
        finally:
            bridge.call("delete_tracks", names=[PROBE_TRACK])
    raise BridgeError(f"could not load {name!r} in Live: {err}")


def device_text(d: dict) -> str:
    L = [f"{d['device']} — parameters as Live shows them (use these names and values in effects / master_effects / returns / midi_effects)"]
    for p in d["parameters"]:
        rng = " | ".join(p["choices"]) if p.get("choices") else f"{p['min']} .. {p['max']}"
        L.append(f"  {p['name']:<22} now {p['value']:<14} {rng}")
    return "\n".join(L)


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
