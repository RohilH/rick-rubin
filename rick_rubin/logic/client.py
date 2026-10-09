"""Song -> Logic Pro project: the Logic counterpart of live/client.py's push_song and capture_live.

A push writes the song as a MIDI file Logic opens as a new project (smf.py), then shapes that project
through the bridge (bridge.py): track names, instruments or Library patches, the mixer, effects chains with
their parameters and side chains, returns (busses with an Aux each) and sends, the master chain, and the
project is saved next to the song as <project>/logic/<title>.logicx. A capture is an offline bounce.

Differences from Live that a reader of the push report should know:
  * Logic chooses a patch per track from the song's role (General MIDI program) unless `instrument` names a
    Logic instrument ("Retro Synth", "Alchemy", "Serum 2"...) or a Library patch to search for.
  * Logic patches come with their own effects (Channel EQ, Compressor...); those stay and are listed as
    "patch fx" so the agent knows what is already on the strip. The song's `effects` go after them.
  * `returns` A, B, ... become Bus 1, 2, ... each with its Aux; `sends` are set in dB on those busses.
  * Section automation ("filter", "volume") is written in real time through the control surface and is
    done by `write_automation` only when asked for (it plays the automated bars once per track).
  * `--update` is not incremental: every push rebuilds the project from the MIDI file.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from ..live.client import DEFAULT_SIDECHAIN, PushReport
from ..model import Song
from .bridge import LOGIC_INSTRUMENTS, LogicBridge, LogicError
from .smf import export_logic_midi

# Logic's names for the shorthand `sidechain: true` compressor (Live: Threshold/Ratio/Attack/Release)
# Logic's Compressor adds make-up gain by itself ("Auto Gain" -12 dB) — Live's does not, so it is switched off here
LOGIC_SIDECHAIN = {"device": "Compressor", "params": {"Threshold": DEFAULT_SIDECHAIN["params"]["Threshold"], "Ratio": DEFAULT_SIDECHAIN["params"]["Ratio"],
                                                       "Attack": DEFAULT_SIDECHAIN["params"]["Attack"], "Release": DEFAULT_SIDECHAIN["params"]["Release"],
                                                       "Auto Gain": "Off"}}
BUS_LETTERS = "ABCDEFGHIJKL"


def logic_dir(song: Song) -> Path:
    base = Path(song.base_dir) if song.base_dir is not None else Path.cwd()
    d = base / "logic"
    d.mkdir(parents=True, exist_ok=True)
    return d


def safe_name(s: str) -> str:
    return "".join(ch if ch.isalnum() or ch in " -_()" else "_" for ch in s).strip() or "song"


def push_record(song: Song) -> Path:
    return logic_dir(song) / ".logic-push.json"


def is_logic_instrument(name: str) -> bool:
    low = name.lower()
    return any(low == x.lower() or low.startswith(x.lower() + " ") for x in LOGIC_INSTRUMENTS) or low in ("serum 2", "serum", "vital", "kickstart 2")


def push_song(song: Song, bridge: LogicBridge, replace: bool = False, load_instruments: bool = True, sidechain: bool = True,
              progress=None, save: bool = True, automation: bool = False, strict: bool = False) -> PushReport:
    """Render `song` as a Logic project. A project of ours (saved under the song's title) that is open is
    closed first; anyone else's open project is left alone (Logic keeps both open)."""
    say = progress or (lambda *_: None)
    rep = PushReport()
    rep.live_version = f"Logic Pro {bridge.ping().get('logic_version') or '?'}"
    title = safe_name(song.title)
    out_dir = logic_dir(song)
    smf = export_logic_midi(song, out_dir / f"{title}.mid")
    say(f"wrote {smf['path'].name}: {len(smf['tracks'])} tracks, {smf['markers']} markers")

    ours = {title, f"{title}.logicx"} | our_projects()
    rec = _load_record(song)
    if rec:
        ours |= set(rec.get("projects", []))
    open_titles = [bridge.app.project_title(w) for w in bridge.app.project_windows()]
    for t in open_titles:
        if t in ours or (replace and t and t.startswith("Untitled")):
            say(f"closing our earlier project {t!r}")
            bridge.close_project(t)
    left = [bridge.app.project_title(w) for w in bridge.app.project_windows()]
    if left:
        say(f"leaving {left} open (not rick-rubin's); Logic will hold both projects")
    say("opening the MIDI file in Logic")
    proj = bridge.open_midi_project(smf["path"], expect_tracks=len(song.tracks), ours=tuple(ours))
    say(f"Logic project {proj!r}")
    midi_tracks = [t for t in song.tracks if not t.audio]
    try:
        names = bridge.name_tracks_by_regions()
    except LogicError as e:
        rep.warnings.append(f"track names: {e}")
        names = bridge.tracks()
    if names[: len(midi_tracks)] != [t.name for t in midi_tracks]:
        rep.warnings.append(f"Logic shows the tracks as {names[:len(midi_tracks)]}, not {[t.name for t in midi_tracks]}; strips are addressed by order")

    # the Mixer strips follow the track order; name -> index (by name when Logic shows ours, else by order)
    index: dict[str, int] = {}
    for i, t in enumerate(midi_tracks):
        index[t.name] = names.index(t.name) if t.name in names else i

    def strip_of(name: str) -> int:
        bridge.select_track(index[name])                     # only this strip selected, so edits land on it alone
        return index[name]

    # instruments
    for t in midi_tracks:
        info: dict[str, Any] = {"index": index[t.name]}
        strip = strip_of(t.name)
        before = bridge.strip_info(strip)
        info["instrument"] = f"{before.instrument} (Logic patch for role {t.role!r})" if before.instrument else "?"
        if before.inserts:
            info["patch_fx"] = list(before.inserts)
        loaded = None
        if load_instruments and t.instrument and not t.sample and not t.serum:
            for q in t.instrument:
                try:
                    if is_logic_instrument(q):
                        got = bridge.load_instrument(strip, q)
                        loaded = f"{got} (instrument)"
                    else:
                        r = bridge.load_patch(index[t.name], q)
                        if r["loaded"]:
                            loaded = f"patch '{q}' -> {r['instrument']}"
                            after = bridge.strip_info(index[t.name])
                            info["patch_fx"] = list(after.inserts)
                    if loaded:
                        break
                except LogicError as e:
                    rep.warnings.append(f"{t.name}: {q}: {e}")
            if loaded:
                info["instrument"] = loaded
            else:
                rep.warnings.append(f"{t.name}: none of {t.instrument} was found in Logic — the role's patch stays")
        if t.instrument_params and not t.sample and not t.serum:
            try:
                pr = bridge.set_instrument_params(index[t.name], t.instrument_params, (loaded or "").split(" (")[0] if load_instruments else "")
                info["instrument_params"] = ", ".join(f"{k} {v}" for k, v in pr.set.items())
                rep.warnings += [f"{t.name}: instrument: {m}" for m in pr.errors]
            except LogicError as err:
                rep.warnings.append(f"{t.name}: instrument parameters not set ({err})")
        if t.sample:
            rep.warnings.append(f"{t.name}: sample tracks (Simpler one-shots) are not yet built in Logic; the role's patch plays the notes")
        if t.serum:
            rep.warnings.append(f"{t.name}: Serum stems are not yet placed in Logic; use instrument=\"Serum 2\" to play the part live")
        if t.midi_effects:
            rep.warnings.append(f"{t.name}: MIDI effects are not built in Logic (notes are sent as written)")
        rep.tracks[t.name] = info
    # audio-loop tracks: an audio track appended after the MIDI tracks, each loop segment imported at its bar
    audio_tracks = [t for t in song.tracks if t.audio]
    for t in audio_tracks:
        try:
            ti = bridge.add_audio_track()
            index[t.name] = ti
            placed = 0
            for c in clips_for(song, t.name):
                for s0, ln, off in c.segments:
                    from ..live.client import _segment_file
                    path = _segment_file(song, c.audio, off, ln, {k: v for k, v in c.envelopes.items() if k in ("filter", "cutoff", "volume")})
                    beat = c.start + s0
                    bridge.import_audio(ti, path, int(beat // 4) + 1, int(beat % 4) + 1)
                    placed += 1
            rep.tracks[t.name] = {"index": ti, "instrument": f"audio track ({placed} regions)"}
            rep.warnings += [f"{t.name}: Logic shows the track as {bridge.tracks()[ti]!r}"] if bridge.tracks()[ti] != t.name else []
        except LogicError as err:
            rep.warnings.append(f"{t.name}: audio loops not placed ({err})")

    # mixer
    for t in [x for x in song.tracks if x.name in index]:
        strip = strip_of(t.name)
        try:
            v = bridge.set_volume(strip, t.volume_db)
            p = bridge.set_pan(strip, t.pan)
            if t.mute:
                bridge.set_mute(strip, True)
            rep.tracks[t.name]["mix"] = f"{v}, pan {p}"
        except Exception as e:  # noqa: BLE001
            rep.warnings.append(f"{t.name}: mixer: {e}")

    # effects: the written chain after the patch's own inserts; `sidechain: true` adds a compressor keyed from the kick
    kick = next((t.name for t in song.tracks if t.role == "kick"), None)
    clips_all, _ = song.flatten()
    filtered = {c.track for c in clips_all if any(k in ("filter", "cutoff") for k in c.envelopes)}
    for t in midi_tracks:
        chain = [dict(e) for e in t.effects]
        if sidechain and t.sidechain and kick and not any(e.get("sidechain") for e in chain):
            chain.append(dict(LOGIC_SIDECHAIN, sidechain=kick))
        if t.name in filtered and not any(e["device"].lower() == "autofilter" for e in chain):
            chain.append({"device": "AutoFilter", "params": {}})          # the device the filter automation rides on
        if not chain:
            continue
        say(f"effects on {t.name}")
        strip = strip_of(t.name)
        existing = len(bridge.strip_info(strip).inserts)
        for e in chain:
            dev = e["device"]
            try:
                strip = strip_of(t.name)
                got = bridge.insert_plugin(strip, dev)
            except LogicError as err:
                rep.warnings.append(f"{t.name}: {dev} failed ({err})")
                continue
            strip = strip_of(t.name)
            slot = len(bridge.strip_info(strip).inserts)          # Logic fills top-down: the new one is the last
            shown = ""
            if e.get("params"):
                try:
                    pr = bridge.set_plugin_params(index[t.name], slot, e["params"])
                    shown = ", ".join(f"{k} {v}" for k, v in pr.set.items())
                    rep.warnings += [f"{t.name}: {dev}: {m}" for m in pr.errors]
                except LogicError as err:
                    rep.warnings.append(f"{t.name}: {dev}: parameters not set ({err})")
            sc = ""
            if e.get("sidechain"):
                try:
                    src = bridge.set_side_chain(strip, got, e["sidechain"], nth=_nth(bridge.strip_info(strip).inserts, got, slot))
                    sc = f" <- {src}"
                    rep.tracks[t.name]["sidechain"] = "keyed from " + e["sidechain"]
                except LogicError as err:
                    rep.warnings.append(f"{t.name}: {dev}: side chain {e['sidechain']!r} not routed ({err})")
                    rep.tracks[t.name]["sidechain"] = "not routed"
            rep.tracks[t.name].setdefault("effects", []).append(got + sc + (f" ({shown})" if shown else ""))
        _ = existing

    # returns (busses + aux), sends, master
    letters = sorted(song.returns)
    if letters:
        say("returns and sends")
    bus_of = {x: BUS_LETTERS.index(x) + 1 for x in letters}
    aux_made: dict[str, str] = {}
    for t in midi_tracks:
        for k, (letter, db) in enumerate(sorted(t.sends.items())):
            if letter not in bus_of:
                continue
            try:
                shown = bridge.set_send(index[t.name], bus_of[letter], db, slot=k + 1)
                rep.tracks[t.name].setdefault("sends", []).append(f"{letter} (Bus {bus_of[letter]}) {shown}")
            except LogicError as err:
                rep.warnings.append(f"{t.name}: send {letter} failed ({err})")
    if letters:
        strips = bridge.strips()
        for x in letters:
            aux = next((s for s in strips if s.kind == "aux" and s.output.startswith("Bus") is False and s.name.startswith("Aux")), None)
            # Logic names the Aux after its bus input order of creation; match by bus number when possible
            for s in strips:
                if s.kind == "aux" and (s.name == f"Aux {bus_of[x]}" or s.name.endswith(f"Bus {bus_of[x]}")):
                    aux = s
            if aux is None:
                rep.warnings.append(f"return {x}: no Aux for Bus {bus_of[x]} appeared (does any track send to it?)")
                continue
            aux_made[x] = aux.name
            bridge.select_track(0)
            strip = aux.name
            shown_all = []
            for e in song.returns[x]:
                try:
                    got = bridge.insert_plugin(strip, e["device"])
                    slot = len(bridge.strip_info(strip).inserts)
                    shown = ""
                    if e.get("params"):
                        pr = bridge.set_plugin_params(aux.name, slot, e["params"])
                        shown = ", ".join(f"{k} {v}" for k, v in pr.set.items())
                        rep.warnings += [f"return {x}: {e['device']}: {m}" for m in pr.errors]
                    shown_all.append(got + (f" ({shown})" if shown else ""))
                except LogicError as err:
                    rep.warnings.append(f"return {x}: {e['device']}: {err}")
            rep.tracks[f"return {x}"] = {"instrument": f"— ({aux.name}, Bus {bus_of[x]})", "effects": shown_all}
    if song.master_effects:
        say("master chain")
        try:
            out = next((s for s in bridge.strips() if s.kind == "output"), None)
            if out is None:
                raise LogicError("no Stereo Out strip in the Mixer")
            bridge.select_track(0)
            strip = out.name
            shown_all = []
            for e in song.master_effects:
                got = bridge.insert_plugin(strip, e["device"])
                slot = len(bridge.strip_info(strip).inserts)
                shown = ""
                if e.get("params"):
                    pr = bridge.set_plugin_params(out.name, slot, e["params"])
                    shown = ", ".join(f"{k} {v}" for k, v in pr.set.items())
                    rep.warnings += [f"master: {e['device']}: {m}" for m in pr.errors]
                shown_all.append(got + (f" ({shown})" if shown else ""))
            rep.tracks["master"] = {"instrument": f"— ({out.name})", "effects": shown_all}
        except LogicError as err:
            rep.warnings.append(f"master: {err}")

    clips, markers = song.flatten()
    rep.clips = sum(1 for c in clips if not song.track(c.track).audio)
    rep.notes = sum(len(c.notes) for c in clips)
    if automation:
        try:
            n = write_automation(song, bridge, index, progress=say)
            rep.mode = f"automation written for {n} clip(s)"
        except LogicError as err:
            rep.warnings.append(f"automation: {err}")
    elif any(c.envelopes for c in clips):
        rep.warnings.append("section automation (volume, filter) is not written by default in Logic because it plays the automated bars "
                            "in real time: push with --automation")

    saved = None
    if save:
        try:
            saved = bridge.save_project_as(out_dir, title)
            remember_project(saved)
            say(f"saved {saved}")
        except LogicError as err:
            rep.warnings.append(f"project not saved: {err}")
    try:
        bridge.set_playhead(1, 1)
    except LogicError as err:
        rep.warnings.append(f"playhead: {err}")
    _save_record(song, {"title": song.title, "project": bridge.project, "projects": sorted(ours | {bridge.project or ""}),
                        "saved": str(saved) if saved else None, "tracks": {t.name: index[t.name] for t in midi_tracks},
                        "aux": aux_made, "time": time.time()})
    rep.mode = (rep.mode + "; " if rep.mode else "") + (f"saved as {saved.name}" if saved else "not saved")
    return rep


def clips_for(song: Song, track: str):
    return [c for c in song.flatten()[0] if c.track == track]


def _nth(inserts: list[str], name: str, slot: int) -> int:
    """Which occurrence (0-based) of `name` is at insert `slot` (1-based, top-down)?"""
    return sum(1 for x in inserts[: slot - 1] if x.lower() == name.lower())


def _aux_index(bridge: LogicBridge, aux_name: str) -> int:
    auxes = [s for s in bridge.strips() if s.kind == "aux"]
    for i, s in enumerate(auxes):
        if s.name == aux_name:
            return i
    return 0


def _global_record() -> Path:
    return Path.home() / ".cache" / "rick-rubin" / "logic-projects.json"


def our_projects() -> set[str]:
    """Titles of every Logic project rick-rubin has saved on this machine (so a push can close one of ours that is
    open, and never anything else)."""
    p = _global_record()
    try:
        return set(json.loads(p.read_text())) if p.exists() else set()
    except ValueError:
        return set()


def remember_project(path: Path) -> None:
    p = _global_record()
    p.parent.mkdir(parents=True, exist_ok=True)
    names = our_projects() | {path.stem, path.name}
    p.write_text(json.dumps(sorted(names)) + "\n")


def _load_record(song: Song) -> dict | None:
    p = push_record(song)
    if p.exists():
        try:
            return json.loads(p.read_text())
        except ValueError:
            return None
    return None


def _save_record(song: Song, data: dict) -> None:
    push_record(song).write_text(json.dumps(data, indent=1) + "\n")


# ============================================================================ automation (real time)
def cutoff_hz(v: float) -> float:
    """The preview's filter curve: 0..1 -> 60 Hz .. 18 kHz, exponential."""
    return 60.0 * (18000.0 / 60.0) ** max(0.0, min(1.0, v))


def write_automation(song: Song, bridge: LogicBridge, index: dict[str, int], progress=None,
                     params: tuple[str, ...] = ("volume", "filter", "cutoff")) -> int:
    """Write the sections' automation into Logic by playing the automated bars with the track in Latch mode and
    moving the control surface: the fader for 'volume', the AutoFilter's Cutoff for 'filter'/'cutoff' (the push
    inserted an AutoFilter on those tracks). Real time: each automated clip is played once per parameter."""
    say = progress or (lambda *_: None)
    clips, _ = song.flatten()
    done = 0
    for c in clips:
        if not c.envelopes or c.track not in index:
            continue
        for prm, pts in c.envelopes.items():
            if prm not in params:
                say(f"{c.track}: {prm} automation in {c.name} is not written (only {', '.join(params)})")
                continue
            if prm == "volume":
                done += bridge.write_fader_automation(index[c.track], c.start, c.length, pts, song.bpm, say)
            else:
                inserts = bridge.strip_info(index[c.track]).inserts
                slot = next((i + 1 for i, n in enumerate(inserts) if n.lower() == "autofilter"), None)
                if slot is None:
                    say(f"{c.track}: no AutoFilter on the strip, {prm} automation in {c.name} not written")
                    continue
                done += bridge.write_param_automation(index[c.track], slot, "Cutoff", c.start, c.length, pts, song.bpm, cutoff_hz, say, "AutoFilter")
    return done


# ============================================================================ capture = offline bounce
def capture_logic(song: Song, bridge: LogicBridge, out_path: str | Path, bars: tuple[int, int] | None = None,
                  tracks: list[str] | None = None, progress=None) -> dict:
    """Bounce the project Logic holds for `song` (offline) to `out_path`: the whole song or a bar range, with
    `tracks` soloed. Returns the same dict as live.capture_live."""
    say = progress or (lambda *_: None)
    import numpy as np

    from ..samples import read_audio
    b0, b1 = bars or (1, song.total_bars)
    rec = _load_record(song) or {}
    if rec.get("project") and bridge.app.main_window(rec["project"]) is not None:
        bridge.project = rec["project"]
        bridge._mixer = None
    elif bridge.app.main_window(safe_name(song.title)) is not None:
        bridge.project = safe_name(song.title)
        bridge._mixer = None
    else:
        raise LogicError(f"the song's project is not open in Logic (open projects: {[bridge.app.project_title(w) for w in bridge.app.project_windows()]}); push first")
    soloed = []
    if tracks:
        names = bridge.tracks()
        idx = rec.get("tracks") or {n: i for i, n in enumerate(names)}
        missing = [t for t in tracks if t not in idx]
        if missing:
            raise LogicError(f"cannot solo {missing}: not in the Logic project (push first)")
        for t in tracks:
            bridge.set_solo(idx[t], True)
            soloed.append(idx[t])
    try:
        say(f"bouncing bars {b0}-{b1} offline from Logic")
        out = bridge.bounce(out_path, b0, b1)
    finally:
        for i in soloed:
            try:
                bridge.set_solo(i, False)
            except Exception:  # noqa: BLE001
                pass
    sr, x = read_audio(out)
    return {"path": Path(out), "source": str(out), "bars": (b0, b1), "tracks": tracks, "seconds": len(x) / sr,
            "peak_db": float(20 * np.log10(np.abs(x).max() + 1e-12))}
