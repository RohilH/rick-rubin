# Command handlers for the ableton-use bridge. Pure Python, duck-typed against
# the Live Object Model so it can be unit-tested with a fake Live outside Ableton.
# Keep this file compatible with Python 3.7 (Live 11) — no walrus, no match.
import math
import traceback

BRIDGE_VERSION = "0.4.0"

FILTER_PARAM_NAMES = ("Frequency", "Filter Freq", "Filter 1 Freq", "Filter Frequency", "Cutoff", "Filter Cutoff", "Freq")
BROWSER_CATEGORIES = ("drums", "instruments", "sounds", "audio_effects", "user_library", "packs")


def _num(text):
    """First float in a Live display string: '-6.0 dB' -> -6.0, '-inf dB' -> -inf, '4.00 : 1' -> 4.0."""
    t = str(text).strip().replace(",", ".")
    if t.startswith("-inf"):
        return -math.inf
    out = ""
    for ch in t:
        if ch.isdigit() or ch in ".-+" or (ch in "eE" and out):
            out += ch
        elif out:
            break
    try:
        return float(out)
    except ValueError:
        return None


def _hz(text):
    """'632 Hz' -> 632.0, '3.56 kHz' -> 3560.0, anything else -> None."""
    t = str(text).lower()
    if "hz" not in t:
        return None
    v = _num(t)
    if v is None:
        return None
    return v * 1000.0 if "khz" in t else v


def filter_mapper(param, lo_hz=60.0, hi_hz=18000.0, grid=96):
    """0..1 -> raw value for a cutoff parameter, so that v sweeps lo_hz..hi_hz
    exponentially (the same curve the offline preview uses) whatever the
    parameter's own raw scale is. Falls back to norm_to_param when the display
    is not in Hz."""
    raws = [param.min + (param.max - param.min) * i / float(grid) for i in range(grid + 1)]
    hzs = [_hz(param.str_for_value(r)) for r in raws]
    if any(h is None or h <= 0 for h in hzs) or any(b < a for a, b in zip(hzs, hzs[1:])) or hzs[-1] <= hzs[0]:
        return lambda v: norm_to_param(param, v)
    logs = [math.log(h) for h in hzs]

    def to_raw(v):
        target = math.log(lo_hz * (hi_hz / lo_hz) ** max(0.0, min(1.0, float(v))))
        if target <= logs[0]:
            return raws[0]
        for i in range(grid):
            if logs[i] <= target <= logs[i + 1]:
                span = logs[i + 1] - logs[i]
                return raws[i] + (raws[i + 1] - raws[i]) * ((target - logs[i]) / span if span > 0 else 0.0)
        return raws[-1]
    return to_raw


def set_param_display(param, target, iters=40):
    """Set a parameter so its *display* value (dB, ms, Hz...) is `target`, by
    bisection over the raw range using str_for_value. Assumes monotonic display."""
    lo, hi = param.min, param.max
    f_lo, f_hi = _num(param.str_for_value(lo)), _num(param.str_for_value(hi))
    if f_lo is None or f_hi is None:
        raise ValueError("parameter %s has non-numeric display" % param.name)
    increasing = f_hi >= f_lo
    for _ in range(iters):
        mid = (lo + hi) / 2.0
        f = _num(param.str_for_value(mid))
        if f is None:
            break
        if (f < target) == increasing:
            lo = mid
        else:
            hi = mid
    # pick whichever bracket end displays closest to the target (display strings are rounded)
    best = min((lo, hi, (lo + hi) / 2.0), key=lambda v: abs((_num(param.str_for_value(v)) or 0) - target))
    param.value = best
    return param.str_for_value(param.value)


def norm_to_param(param, v):
    """Map a 0..1 control value onto a parameter. Frequency-like ranges get an
    exponential map so 0.5 sounds like 'half open'."""
    v = max(0.0, min(1.0, float(v)))
    lo, hi = param.min, param.max
    if lo > 0 and hi / lo > 100:
        return lo * (hi / lo) ** v
    return lo + v * (hi - lo)


def _rname(x):
    return getattr(x, "display_name", None) or (x.get("display_name") if isinstance(x, dict) else str(x))


class Handlers(object):
    def __init__(self, get_song, get_app, live_module=None, log=None):
        self._song = get_song
        self._app = get_app
        self._Live = live_module
        self._log = log or (lambda *a: None)
        self._browser_cache = {}

    # ------------------------------------------------------------------ dispatch
    def dispatch(self, req):
        cmd = req.get("cmd")
        args = req.get("args") or {}
        fn = getattr(self, "cmd_" + str(cmd), None)
        if fn is None:
            return {"ok": False, "error": "unknown command %r" % cmd}
        try:
            return {"ok": True, "result": fn(**args)}
        except Exception as e:  # noqa: BLE001
            self._log("ableton-use error in %s: %s" % (cmd, traceback.format_exc()))
            return {"ok": False, "error": "%s: %s" % (type(e).__name__, e)}

    @property
    def song(self):
        return self._song()

    def _track(self, index):
        return self.song.tracks[int(index)]

    # ------------------------------------------------------------------ info
    def cmd_ping(self):
        app = self._app()
        ver = None
        try:
            ver = "%d.%d.%d" % (app.get_major_version(), app.get_minor_version(), app.get_bugfix_version())
        except Exception:  # noqa: BLE001
            pass
        return {"bridge": BRIDGE_VERSION, "live_version": ver}

    def cmd_get_state(self, notes=False):
        s = self.song
        tracks = []
        for i, t in enumerate(s.tracks):
            clips = []
            for c in getattr(t, "arrangement_clips", []):
                d = {"name": c.name, "start": c.start_time, "length": c.length}
                if notes and getattr(c, "is_midi_clip", True):
                    try:
                        d["notes"] = len(c.get_notes_extended(0, 128, 0, c.length))
                    except Exception:  # noqa: BLE001
                        pass
                clips.append(d)
            tracks.append({
                "index": i, "name": t.name, "midi": bool(getattr(t, "has_midi_input", True)),
                "devices": [d.name for d in t.devices],
                "volume": t.mixer_device.volume.str_for_value(t.mixer_device.volume.value),
                "mute": bool(t.mute), "arrangement_clips": clips,
            })
        return {
            "tempo": s.tempo, "signature": [s.signature_numerator, s.signature_denominator],
            "song_length": getattr(s, "song_length", None),
            "cue_points": [{"name": c.name, "time": c.time} for c in s.cue_points],
            "tracks": tracks,
        }

    # ------------------------------------------------------------------ song
    def cmd_set_tempo(self, bpm):
        self.song.tempo = float(bpm)
        return self.song.tempo

    def cmd_set_signature(self, numerator=4, denominator=4):
        self.song.signature_numerator = int(numerator)
        self.song.signature_denominator = int(denominator)
        return True

    def cmd_transport(self, action, beat=None):
        s = self.song
        if beat is not None:
            s.current_song_time = float(beat)
        if action == "play":
            s.start_playing()
        elif action == "stop":
            s.stop_playing()
        return {"is_playing": bool(s.is_playing), "time": s.current_song_time}

    def cmd_set_loop(self, start, length, on=True):
        s = self.song
        s.loop_start = float(start)
        s.loop_length = float(length)
        s.loop = bool(on)
        return True

    def cmd_show_message(self, text):
        self._log(text, True)
        return True

    # ------------------------------------------------------------------ tracks
    def cmd_delete_tracks(self, names=None, indices=None):
        s = self.song
        names = set(names or [])
        idx = set(int(i) for i in (indices or []))
        doomed = [i for i, t in enumerate(s.tracks) if i in idx or t.name in names]
        if doomed and len(doomed) == len(s.tracks):
            s.create_midi_track(-1)  # Live needs at least one track
        for i in sorted(doomed, reverse=True):
            s.delete_track(i)
        return len(doomed)

    def cmd_create_midi_track(self, name, index=-1, color_index=None):
        s = self.song
        s.create_midi_track(int(index))
        i = len(s.tracks) - 1 if int(index) < 0 else int(index)
        t = s.tracks[i]
        t.name = name
        if color_index is not None:
            try:
                t.color_index = int(color_index)
            except Exception:  # noqa: BLE001
                pass
        return i

    def cmd_create_audio_track(self, name, index=-1, color_index=None):
        s = self.song
        s.create_audio_track(int(index))
        i = len(s.tracks) - 1 if int(index) < 0 else int(index)
        t = s.tracks[i]
        t.name = name
        if color_index is not None:
            try:
                t.color_index = int(color_index)
            except Exception:  # noqa: BLE001
                pass
        return i

    def cmd_set_track(self, index, name=None, volume_db=None, pan=None, mute=None, color_index=None):
        t = self._track(index)
        out = {}
        if name is not None:
            t.name = name
        if volume_db is not None:
            out["volume"] = set_param_display(t.mixer_device.volume, float(volume_db))
        if pan is not None:
            p = t.mixer_device.panning
            p.value = max(p.min, min(p.max, float(pan)))
        if mute is not None:
            t.mute = bool(mute)
        if color_index is not None:
            t.color_index = int(color_index)
        return out

    # ------------------------------------------------------------------ browser / devices
    def _find_browser_item(self, query, categories):
        key = (query.lower(), tuple(categories))
        if key in self._browser_cache:
            return self._browser_cache[key]
        browser = self._app().browser
        q = query.lower()
        best = None
        for cat in categories:
            root = getattr(browser, cat, None)
            if root is None:
                continue
            queue = list(root.children)
            seen = 0
            while queue and seen < 6000:
                item = queue.pop(0)
                seen += 1
                nm = item.name.lower()
                stem = nm.rsplit(".", 1)[0] if "." in nm else nm
                if item.is_loadable and (stem == q or nm == q):
                    best = item
                    break
                if item.is_loadable and q in nm and best is None:
                    best = item
                if item.is_folder or getattr(item, "children", None):
                    queue.extend(item.children)
            if best is not None and (best.name.lower().rsplit(".", 1)[0] == q):
                break
        self._browser_cache[key] = best
        return best

    def cmd_load_instrument(self, track, queries, categories=None):
        cats = categories or ["drums", "instruments", "sounds"]
        t = self._track(track)
        for q in queries:
            item = self._find_browser_item(q, cats)
            if item is not None:
                self.song.view.selected_track = t
                self._app().browser.load_item(item)
                return {"loaded": item.name, "query": q}
        return {"loaded": None, "tried": list(queries)}

    def cmd_insert_device(self, track, name):
        t = self._track(track)
        before = len(t.devices)
        if hasattr(t, "insert_device"):
            try:
                t.insert_device(name)
                return {"device": name, "method": "insert_device", "index": len(t.devices) - 1}
            except Exception:  # noqa: BLE001
                pass
        item = self._find_browser_item(name, ["audio_effects"])
        if item is None:
            raise ValueError("device %r not found" % name)
        self.song.view.selected_track = t
        self._app().browser.load_item(item)
        return {"device": item.name, "method": "browser", "index": len(t.devices) - 1 if len(t.devices) > before else None}

    def _simpler(self, t):
        for d in t.devices:
            if getattr(d, "class_name", "") in ("OriginalSimpler", "Simpler") or d.name == "Simpler":
                return d
        return None

    def cmd_load_sample(self, track, path, mode="classic", root=None, voices=None):
        """Put `path` in a Simpler on `track`. mode: 'oneshot' (drums: full sample per hit)
        or 'classic' (melodic). root = MIDI pitch the sample sounds at; Simpler's
        Transpose/Detune are set so incoming notes play at their true pitch."""
        t = self._track(track)
        dev = self._simpler(t)
        method = "existing"
        if dev is None:
            if hasattr(t, "insert_device"):
                try:
                    t.insert_device("Simpler", 0)
                    method = "insert_device"
                except Exception:  # noqa: BLE001
                    dev = None
            dev = self._simpler(t)
            if dev is None:
                item = self._find_browser_item("Simpler", ["instruments"])
                if item is None:
                    raise ValueError("cannot find Simpler")
                self.song.view.selected_track = t
                self._app().browser.load_item(item)
                method = "browser"
                dev = self._simpler(t)
        if dev is None:
            raise RuntimeError("Simpler did not load")
        dev.replace_sample(str(path))
        report = {"device": dev.name, "method": method, "sample": str(path)}
        try:
            dev.playback_mode = 1 if mode == "oneshot" else 0
            report["mode"] = mode
        except Exception as e:  # noqa: BLE001
            report["mode_error"] = str(e)
        for p in dev.parameters:
            if p.name == "Volume":
                try:
                    report["volume"] = set_param_display(p, 0.0)   # default is -12 dB; track volume does the mixing
                except Exception as e:  # noqa: BLE001
                    report.setdefault("param_errors", []).append("Volume: %s" % e)
        if voices is not None:
            try:
                dev.voices = int(voices)
            except Exception:  # noqa: BLE001
                pass
        if root is not None and mode != "oneshot":
            shift = 60.0 - float(root)
            semis = int(round(shift))
            cents = (shift - semis) * 100.0
            for p in dev.parameters:
                try:
                    if p.name == "Transpose":
                        report["transpose"] = set_param_display(p, semis)
                    elif p.name == "Detune":
                        report["detune"] = set_param_display(p, cents)
                except Exception as e:  # noqa: BLE001
                    report.setdefault("param_errors", []).append("%s: %s" % (p.name, e))
            if "transpose" not in report:
                report["warning"] = "no Transpose parameter found; notes will sound %+d st off" % (-semis)
        return report

    def _free_slot(self, t):
        for sl in t.clip_slots:
            if not sl.has_clip:
                return sl
        self.song.create_scene(-1)
        return t.clip_slots[len(t.clip_slots) - 1]

    def cmd_create_audio_clip(self, track, path, start, name=None, warping=False, envelopes=None, color_index=None):
        """Place an audio file in the arrangement at `start` (beats). Files are expected
        to be pre-conformed to the song tempo, so warping is off by default.

        Live only lets scripts write automation into Session clips, so a clip with
        envelopes is built in a free session slot and copied to the arrangement,
        where its envelopes become track automation."""
        t = self._track(track)
        start = float(start)
        envelopes = envelopes or {}
        env_report = {}
        if hasattr(t, "create_audio_clip") and not envelopes:
            method = "create_audio_clip"
            r = t.create_audio_clip(str(path), start)
            clip = r if hasattr(r, "start_time") else self._arrangement_clip_at(t, start)
            if clip is not None:
                self._dress(clip, name, color_index, warping)
        else:
            method = "session+duplicate"
            slot = self._free_slot(t)
            slot.create_audio_clip(str(path))
            self._dress(slot.clip, name, color_index, warping)
            env_report = self._apply_envelopes(t, slot.clip, envelopes)
            t.duplicate_clip_to_arrangement(slot.clip, start)
            slot.delete_clip()
            clip = self._arrangement_clip_at(t, start)
        if clip is None:
            raise RuntimeError("audio clip not found after creation at beat %s" % start)
        return {"start": clip.start_time, "length": clip.length, "method": method, "envelopes": env_report}

    def _dress(self, clip, name, color_index, warping=None):
        if warping is not None:
            try:
                clip.warping = bool(warping)
            except Exception:  # noqa: BLE001
                pass
        if name:
            clip.name = name
        if color_index is not None:
            try:
                clip.color_index = int(color_index)
            except Exception:  # noqa: BLE001
                pass

    def cmd_sidechain(self, track, source_track_name, threshold_db=-28.0, ratio=4.0, release_ms=120.0):
        """Insert a Compressor on `track` keyed from another track (the kick)."""
        t = self._track(track)
        comp = None
        for d in t.devices:
            if getattr(d, "class_name", "") in ("Compressor2", "Compressor") or d.name == "Compressor":
                comp = d
        if comp is None:
            self.cmd_insert_device(track, "Compressor")
            comp = t.devices[len(t.devices) - 1]
        routed = False
        types = getattr(comp, "available_input_routing_types", None) or []
        for rt in types:
            if source_track_name in str(_rname(rt)):
                comp.input_routing_type = rt
                routed = True
                break
        report = {"device": comp.name, "routed": routed}
        for p in comp.parameters:
            pn = p.name.lower()
            try:
                if pn in ("s/c on", "sidechain on", "s/c enabled", "sidechain"):
                    p.value = p.max
                elif pn == "threshold":
                    report["threshold"] = set_param_display(p, threshold_db)
                elif pn == "ratio":
                    report["ratio"] = set_param_display(p, ratio)
                elif pn == "release":
                    report["release"] = set_param_display(p, release_ms)
                elif pn == "attack":
                    report["attack"] = set_param_display(p, 0.5)
            except Exception as e:  # noqa: BLE001
                report.setdefault("param_errors", []).append("%s: %s" % (p.name, e))
        return report

    def _resolve_param(self, t, param, ensure=True):
        """'filter' | 'volume' | 'pan' | 'Device Name:Param Name'."""
        if param == "volume":
            return t.mixer_device.volume
        if param == "pan":
            return t.mixer_device.panning
        if ":" in param:
            dname, pname = param.split(":", 1)
            for d in t.devices:
                if d.name == dname:
                    for p in d.parameters:
                        if p.name == pname:
                            return p
            raise ValueError("parameter %r not found" % param)
        if param in ("filter", "cutoff"):
            # always an Auto Filter: instrument filters are often switched off (Simpler) or mean something else
            for d in t.devices:
                if "AutoFilter" in getattr(d, "class_name", "") or d.name == "Auto Filter":
                    for p in d.parameters:
                        if p.name in FILTER_PARAM_NAMES:
                            return p
            if ensure:
                self.cmd_insert_device(list(self.song.tracks).index(t), "Auto Filter")
                return self._resolve_param(t, param, ensure=False)
            raise ValueError("no Auto Filter on track %s" % t.name)
        for d in t.devices:
            for p in d.parameters:
                if p.name.lower() == param.lower():
                    return p
        raise ValueError("parameter %r not found on %s" % (param, t.name))

    # ------------------------------------------------------------------ clips
    def _arrangement_clip_at(self, t, start):
        best = None
        for c in t.arrangement_clips:
            if abs(c.start_time - start) < 1e-3:
                best = c
        return best

    def _add_notes(self, clip, notes):
        if not notes:
            return 0
        Live = self._Live
        if Live is not None and hasattr(Live, "Clip") and hasattr(Live.Clip, "MidiNoteSpecification"):
            specs = tuple(Live.Clip.MidiNoteSpecification(pitch=int(n[0]), start_time=float(n[1]), duration=float(n[2]),
                                                          velocity=float(n[3]), mute=False) for n in notes)
            clip.add_new_notes(specs)
        else:
            clip.set_notes(tuple((int(n[0]), float(n[1]), float(n[2]), int(n[3]), False) for n in notes))
        return len(notes)

    def cmd_create_clip(self, track, start, length, notes=None, name=None, envelopes=None, color_index=None):
        """Create an arrangement MIDI clip with notes [[pitch, start, dur, vel], ...]
        (times relative to clip start) and envelopes {param: [[beat, value01], ...]}.
        Clips with envelopes go through a session slot (see cmd_create_audio_clip)."""
        t = self._track(track)
        start, length = float(start), float(length)
        envelopes = envelopes or {}
        env_report = {}
        if hasattr(t, "create_midi_clip") and not envelopes:
            method = "create_midi_clip"
            clip = t.create_midi_clip(start, length)
            if clip is None or not hasattr(clip, "start_time"):
                clip = self._arrangement_clip_at(t, start)
            self._add_notes(clip, notes or [])
            self._dress(clip, name, color_index)
        else:
            method = "session+duplicate"
            slot = self._free_slot(t)
            slot.create_clip(length)
            self._add_notes(slot.clip, notes or [])
            self._dress(slot.clip, name, color_index)
            env_report = self._apply_envelopes(t, slot.clip, envelopes)
            t.duplicate_clip_to_arrangement(slot.clip, start)
            slot.delete_clip()
            clip = self._arrangement_clip_at(t, start)
        if clip is None:
            raise RuntimeError("clip not found after creation at beat %s" % start)
        return {"start": clip.start_time, "length": clip.length, "method": method, "envelopes": env_report}

    def _apply_envelopes(self, t, clip, envelopes):
        env_report = {}
        for param, pts in envelopes.items():
            try:
                p = self._resolve_param(t, param)
                env = clip.automation_envelope(p)
                if env is None:
                    env = clip.create_automation_envelope(p)
                step = 0.25
                pts = sorted(pts)
                to_raw = filter_mapper(p) if param in ("filter", "cutoff") else (lambda v, p=p: norm_to_param(p, v))
                for (b0, v0), (b1, v1) in zip(pts, pts[1:]):
                    b = b0
                    while b < b1 - 1e-9:
                        frac = (b - b0) / (b1 - b0) if b1 > b0 else 1.0
                        val = to_raw(v0 + (v1 - v0) * frac)
                        env.insert_step(b, min(step, b1 - b), val)
                        b += step
                env_report[param] = p.name
            except Exception as e:  # noqa: BLE001
                env_report[param] = "error: %s" % e
        return env_report

    def cmd_clear_arrangement(self, track):
        t = self._track(track)
        n = 0
        for c in list(t.arrangement_clips):
            t.delete_clip(c)
            n += 1
        return n

    # ------------------------------------------------------------------ locators
    def cmd_add_locator(self, name, beat):
        """Name the locator at `beat`, creating it if the playhead is there. Live applies
        a playhead move only after the current tick, so the client first calls
        transport(beat=...) and then this, as two separate requests."""
        s = self.song
        beat = float(beat)

        def find():
            for c in s.cue_points:
                if abs(c.time - beat) < 1e-3:
                    return c
            return None
        cue = find()
        if cue is None:
            if abs(s.current_song_time - beat) > 1e-3:
                s.current_song_time = beat
                return {"created": False, "retry": True}
            s.set_or_delete_cue()
            cue = find()
        if cue is None:
            return {"created": False, "retry": True}
        cue.name = str(name)
        return {"created": True}

    # ------------------------------------------------------------------ generic Live Object Model access
    def _lom_resolve(self, path):
        """'song.tracks[3].mixer_device.volume' -> object. Only attribute names and
        integer indices; roots are 'song' and 'app'."""
        obj = None
        for i, part in enumerate(str(path).split(".")):
            name, idx = part, []
            while name.endswith("]"):
                name, _, n = name[:-1].rpartition("[")
                idx.insert(0, int(n))
            if not name.replace("_", "a").isalnum() or name.startswith("_"):
                raise ValueError("bad path element %r" % part)
            if i == 0:
                if name not in ("song", "app"):
                    raise ValueError("path must start with 'song' or 'app'")
                obj = self.song if name == "song" else self._app()
            else:
                obj = getattr(obj, name)
            for n in idx:
                obj = obj[n]
        return obj

    def _jsonable(self, v, depth=0):
        if v is None or isinstance(v, (bool, int, float, str)):
            return v
        if isinstance(v, dict):
            return dict((str(k), self._jsonable(x, depth + 1)) for k, x in v.items())
        if depth < 3 and not hasattr(v, "name") and not hasattr(v, "display_name"):
            try:
                return [self._jsonable(x, depth + 1) for x in list(v)[:512]]
            except TypeError:
                pass
        for attr in ("display_name", "name"):
            n = getattr(v, attr, None)
            if isinstance(n, str):
                return n
        return str(v)

    def cmd_lom(self, path, op="get", value=None, args=None, attr=None, choose=None):
        """Read, write or call anything in the Live Object Model.
        get:  value at `path`.
        set:  path = value. With `choose`, pick the item of the list at path `choose`
              whose name contains `value` (routing types/channels, e.g. 'Resampling').
        call: path(*args)."""
        if op == "get":
            return self._jsonable(self._lom_resolve(path))
        if op == "call":
            return self._jsonable(self._lom_resolve(path)(*(args or [])))
        if op == "set":
            parent, _, name = str(path).rpartition(".")
            target = self._lom_resolve(parent)
            if choose:
                options = list(self._lom_resolve(choose))
                picks = [o for o in options if str(value).lower() in str(_rname(o)).lower()]
                if not picks:
                    raise ValueError("no %r among %s" % (value, [str(_rname(o)) for o in options]))
                exact = [o for o in picks if str(_rname(o)).lower() == str(value).lower()]
                value = (exact or picks)[0]
            setattr(target, name, value)
            return self._jsonable(getattr(target, name))
        raise ValueError("op must be get, set or call")

    # ------------------------------------------------------------------ batching
    def cmd_batch(self, commands):
        return [self.dispatch(c) for c in commands]
