"""Offline audio preview — a tiny numpy synth so the agent can *check* the song
without Ableton (cf. video-use's preview render + self-eval).

It is a sketch renderer, not a production synth: the goal is a faithful picture
of rhythm, harmony, density, low-end balance, sidechain pump and filter moves so
`analysis` can measure them. Final sound design happens in Live.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

from ..model import BEATS_PER_BAR, DRUM_MAP, Song

SR = 44100

# base low-pass cutoff per role (Hz) — filter automation 0..1 sweeps 60 Hz -> this value
BASE_CUTOFF = {
    "bass": 900.0, "sub": 300.0, "chords": 4500.0, "stab": 4500.0, "keys": 5000.0, "organ": 5000.0,
    "pad": 3000.0, "lead": 6000.0, "arp": 6000.0, "pluck": 5000.0, "riser": 12000.0,
}
DUCK_DEPTH = {"bass": 0.8, "sub": 0.85}


@dataclass
class PreviewResult:
    path: Path
    sr: int
    duration_s: float
    peak_dbfs_premaster: float
    stems: dict[str, Path]


def _env(n: int, sr: int, a: float, d: float, sustain_len: int | None = None) -> np.ndarray:
    t = np.arange(n) / sr
    att = np.clip(t / max(a, 1e-4), 0, 1)
    if sustain_len is None:
        return att * np.exp(-t / max(d, 1e-4))
    rel = np.ones(n)
    if sustain_len < n:
        rel[sustain_len:] = np.exp(-(np.arange(n - sustain_len)) / (max(d, 1e-4) * sr))
    return att * rel


def _saw(freq: float, n: int, sr: int, phase: float = 0.0) -> np.ndarray:
    ph = (phase + freq * np.arange(n) / sr) % 1.0
    return 2.0 * ph - 1.0


def _hz(p: float) -> float:
    return 440.0 * 2 ** ((p - 69) / 12)


class _Voices:
    def __init__(self, sr: int, seed: int = 0):
        self.sr = sr
        self.rng = np.random.default_rng(seed)
        self._cache: dict[str, np.ndarray] = {}

    def noise(self, n):
        return self.rng.standard_normal(n).astype(np.float32)

    def drum(self, kind: str) -> np.ndarray:
        if kind in self._cache:
            return self._cache[kind]
        sr = self.sr
        if kind == "kick":
            n = int(0.45 * sr)
            t = np.arange(n) / sr
            f = 48 + 110 * np.exp(-t / 0.035)
            ph = 2 * np.pi * np.cumsum(f) / sr
            x = np.sin(ph) * np.exp(-t / 0.28) + 0.25 * np.exp(-t / 0.004) * self.noise(n)
            x = np.tanh(1.6 * x)
        elif kind in ("clap", "snare"):
            n = int(0.3 * sr)
            t = np.arange(n) / sr
            bursts = sum(np.exp(-np.clip(t - o, 0, None) / 0.008) * (t >= o) for o in (0, 0.011, 0.022))
            env = 0.6 * bursts + np.exp(-t / 0.09) * (t >= 0.022)
            x = sosfilt(butter(2, [900, 4000], "bandpass", fs=sr, output="sos"), self.noise(n)) * env * 2.2
            if kind == "snare":
                x += 0.5 * np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.06)
        elif kind in ("hat", "openhat", "shaker"):
            dec = {"hat": 0.035, "openhat": 0.22, "shaker": 0.05}[kind]
            n = int((dec * 6) * sr)
            t = np.arange(n) / sr
            x = sosfilt(butter(4, 7000, "highpass", fs=sr, output="sos"), self.noise(n)) * np.exp(-t / dec) * 1.4
        elif kind in ("perc", "rim", "tom"):
            n = int(0.15 * sr)
            t = np.arange(n) / sr
            fr = 820 if kind != "tom" else 160
            x = np.sin(2 * np.pi * fr * t) * np.exp(-t / 0.035) + 0.3 * self.noise(n) * np.exp(-t / 0.004)
        elif kind in ("crash", "ride", "fx"):
            n = int(1.8 * sr)
            t = np.arange(n) / sr
            x = sosfilt(butter(2, 5000, "highpass", fs=sr, output="sos"), self.noise(n)) * np.exp(-t / 0.6) * 0.8
        else:
            n = int(0.1 * sr)
            x = self.noise(n) * np.exp(-np.arange(n) / sr / 0.02)
        x = x.astype(np.float32)
        self._cache[kind] = x
        return x

    def tone(self, role: str, pitch: int, dur_s: float) -> np.ndarray:
        sr = self.sr
        f = _hz(pitch)
        if role in ("bass", "sub"):
            rel = 0.02
            n = int((dur_s + rel) * sr)
            t = np.arange(n) / sr
            x = 0.8 * np.sin(2 * np.pi * f * t) + (0.35 * _saw(f, n, sr) if role == "bass" else 0)
            env = _env(n, sr, 0.003, rel, int(dur_s * sr))
            return (x * env).astype(np.float32)
        if role in ("pad",):
            rel = 0.4
            n = int((dur_s + rel) * sr)
            x = (_saw(f * 0.997, n, sr) + _saw(f * 1.004, n, sr, 0.3) + 0.5 * _saw(f / 2, n, sr, 0.6)) / 2.5
            return (x * _env(n, sr, 0.35, rel, int(dur_s * sr)) * 0.6).astype(np.float32)
        if role == "riser":
            n = int(dur_s * sr)
            t = np.arange(n) / sr
            ramp = t / max(dur_s, 1e-3)
            fr = f * (1 + ramp)
            x = 0.5 * np.sin(2 * np.pi * np.cumsum(fr) / sr) + 0.6 * self.noise(n)
            return (x * ramp ** 1.5 * 0.5).astype(np.float32)
        if role in ("lead", "arp", "pluck"):
            rel = 0.08
            n = int((dur_s + rel) * sr)
            t = np.arange(n) / sr
            sq = np.sign(np.sin(2 * np.pi * f * t))
            x = 0.6 * _saw(f, n, sr) + 0.4 * sq
            return (x * _env(n, sr, 0.004, rel, int(dur_s * sr)) * np.exp(-t / 0.6) * 0.6).astype(np.float32)
        # chords / stab / keys / organ / anything else
        rel = 0.12
        n = int((dur_s + rel) * sr)
        t = np.arange(n) / sr
        x = (_saw(f * 0.996, n, sr) + _saw(f * 1.005, n, sr, 0.5)) / 2
        return (x * _env(n, sr, 0.004, rel, int(dur_s * sr)) * (0.55 + 0.45 * np.exp(-t / 0.25)) * 0.6).astype(np.float32)


def _drum_kind(role: str, pitch: int) -> str:
    if role in ("drums", "fx"):
        inv = {v: k for k, v in DRUM_MAP.items()}
        return inv.get(pitch, "perc")
    return role


def _filter_curve(points: list[tuple[float, float]], n: int, sr: int, spb: float) -> np.ndarray:
    """points: sorted (abs_beat, value) with NaN-breaks; returns per-sample value (default 1)."""
    v = np.ones(n, dtype=np.float32)
    for seg in points:
        (b0, v0), (b1, v1) = seg
        i0, i1 = int(b0 * spb * sr), int(b1 * spb * sr)
        i1 = min(i1, n)
        if i1 > i0:
            v[i0:i1] = np.linspace(v0, v1, i1 - i0)
    return v


def _lp_sos(fc: float, sr: int, q: float = 0.707) -> np.ndarray:
    """RBJ biquad low-pass as a 1-section SOS (closed form, far cheaper than butter())."""
    w = 2 * np.pi * fc / sr
    alpha = np.sin(w) / (2 * q)
    cw = np.cos(w)
    b0 = b2 = (1 - cw) / 2
    b1 = 1 - cw
    a0, a1, a2 = 1 + alpha, -2 * cw, 1 - alpha
    return np.array([[b0 / a0, b1 / a0, b2 / a0, 1.0, a1 / a0, a2 / a0]])


def _apply_lowpass(x: np.ndarray, cutoff: np.ndarray, sr: int, block: int = 256) -> np.ndarray:
    """Time-varying 12 dB/oct low-pass. Cutoff is quantised to 1/24 octave and
    runs of equal cutoff are filtered in one call, so static regions are cheap."""
    n = len(x)
    centers = np.minimum(np.arange(0, n, block) + block // 2, n - 1)
    fc = np.clip(cutoff[centers], 30, sr * 0.45)
    keys = np.round(24 * np.log2(fc)).astype(int)
    out = np.empty_like(x)
    zi = np.zeros((1, 2))
    i = 0
    nb = len(keys)
    while i < nb:
        j = i
        while j + 1 < nb and keys[j + 1] == keys[i]:
            j += 1
        s, e = i * block, min(n, (j + 1) * block)
        out[s:e], zi = sosfilt(_lp_sos(2 ** (keys[i] / 24), sr), x[s:e], zi=zi)
        i = j + 1
    return out


class _SampleBank:
    """Loads project samples (mono, at the render rate) and makes pitched copies
    the way Simpler's classic mode does: resample by 2^(semitones/12), cut at
    note-off and apply a short release."""

    def __init__(self, song: Song, sr: int):
        self.song, self.sr = song, sr
        self._cache: dict[str, np.ndarray] = {}
        self._pitched: dict[tuple, np.ndarray] = {}

    def get(self, rel: str) -> np.ndarray:
        if rel not in self._cache:
            from ..samples import _resample, read_audio
            sr, x = read_audio(self.song.resolve(rel))
            self._cache[rel] = _resample(x, sr, self.sr).mean(axis=1).astype(np.float32)
        return self._cache[rel]

    def pitched(self, rel: str, semis: float, dur_s: float, release_s: float = 0.05) -> np.ndarray:
        key = (rel, round(semis, 3), round(dur_s, 3))
        if key in self._pitched:
            return self._pitched[key]
        x = self.get(rel)
        ratio = 2 ** (semis / 12)
        n_out = int(len(x) / ratio)
        y = np.interp(np.arange(n_out) * ratio, np.arange(len(x)), x).astype(np.float32)
        hold, rel_n = int(dur_s * self.sr), int(release_s * self.sr)
        if hold < len(y):
            y = y[: hold + rel_n].copy()
            tail = len(y) - hold
            if tail > 0:
                y[hold:] *= np.linspace(1, 0, tail, dtype=np.float32)
        self._pitched[key] = y
        return y


def render_preview(song: Song, out_path: str | Path, sr: int = SR, stems_dir: str | Path | None = None,
                   seed: int = 0, tracks: list[str] | None = None) -> PreviewResult:
    """`tracks` renders only those tracks (a solo). They are still ducked by the
    kick even when the kick itself is not among them, as they would be in Live."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    clips, _ = song.flatten()
    spb = 60.0 / song.bpm
    total = int((song.total_bars * BEATS_PER_BAR * spb + 2.0) * sr)
    voices = _Voices(sr, seed)

    # sidechain key: kick onsets
    kick_times = sorted({c.start + n.start for c in clips for n in c.notes
                         if song.track(c.track).role == "kick" and not song.track(c.track).mute})
    duck = np.ones(total, dtype=np.float32)
    if kick_times:
        rel = int(0.55 * spb * sr)
        shape = 1 - (1 - np.linspace(0, 1, rel)) ** 2
        for kt in kick_times:
            i = int(kt * spb * sr)
            j = min(total, i + rel)
            duck[i:j] = np.minimum(duck[i:j], shape[: j - i])

    stems: dict[str, np.ndarray] = {}
    smp = _SampleBank(song, sr)
    for trk in song.tracks:
        if trk.mute or (tracks and trk.name not in tracks):
            continue
        buf = np.zeros(total, dtype=np.float32)
        mine = [c for c in clips if c.track == trk.name]
        env_pts = []
        for c in mine:
            if c.audio:
                data = smp.get(c.audio)
                for s0, ln, off in c.segments:
                    i = int((c.start + s0) * spb * sr)
                    a = int(off * spb * sr)
                    seg = data[a: a + int(ln * spb * sr)]
                    j = min(total, i + len(seg))
                    buf[i:j] += seg[: j - i]
            for n in c.notes:
                t0 = c.start + n.start
                i = int(t0 * spb * sr)
                if trk.sample:
                    if trk.is_drum:
                        w = smp.get(trk.sample)            # Simpler one-shot: full sample, pitch ignored
                    else:
                        w = smp.pitched(trk.sample, n.pitch - (trk.sample_root or 60), n.dur * spb)
                elif trk.is_drum:
                    w = voices.drum(_drum_kind(trk.role, n.pitch))
                else:
                    w = voices.tone(trk.role, n.pitch, n.dur * spb)
                atk = float(trk.instrument_params.get("Ve Attack", 0) or 0) if trk.sample else 0.0
                if atk > 0.5:                                  # Simpler's amp attack in ms: fade the hit in
                    k = min(len(w), int(atk / 1000.0 * sr))
                    w = w.copy()
                    w[:k] *= np.linspace(0, 1, k, dtype=np.float32)
                j = min(total, i + len(w))
                buf[i:j] += w[: j - i] * (n.vel / 127.0)
            for param, pts in c.envelopes.items():
                if param in ("filter", "cutoff"):
                    for (b0, v0), (b1, v1) in zip(pts, pts[1:]):
                        env_pts.append(((c.start + b0, v0), (c.start + b1, v1)))
        synth_tone = not trk.is_drum and not trk.sample and not trk.audio
        if synth_tone or env_pts:
            # synths get a role-typical tone filter; samples are only filtered by automation (an Auto Filter in Live)
            base = BASE_CUTOFF.get(trk.role, 16000.0) if synth_tone else 18000.0
            ctrl = _filter_curve(env_pts, total, sr, spb)
            cutoff = 60.0 * (base / 60.0) ** ctrl
            buf = _apply_lowpass(buf, cutoff, sr)
        if trk.ducked:
            depth = DUCK_DEPTH.get(trk.role, 0.55)
            buf *= 1 - depth * (1 - duck)
        stems[trk.name] = buf * (10 ** (trk.volume_db / 20))

    L = np.zeros(total, dtype=np.float32)
    R = np.zeros(total, dtype=np.float32)
    for trk in song.tracks:
        if trk.name not in stems:
            continue
        p = (trk.pan + 1) / 2
        L += stems[trk.name] * np.cos(p * np.pi / 2) * np.sqrt(2)
        R += stems[trk.name] * np.sin(p * np.pi / 2) * np.sqrt(2)
    peak = float(max(np.abs(L).max(), np.abs(R).max(), 1e-9))
    peak_db = 20 * np.log10(peak)
    # gentle master: normalise, soft-clip, -1 dBFS ceiling
    g = 1.25 / peak
    L, R = np.tanh(L * g) * 0.89, np.tanh(R * g) * 0.89
    stereo = np.stack([L, R], axis=1)
    wavfile.write(out_path, sr, (np.clip(stereo, -1, 1) * 32767).astype(np.int16))

    stem_paths: dict[str, Path] = {}
    if stems_dir:
        sd = Path(stems_dir)
        sd.mkdir(parents=True, exist_ok=True)
        for name, s in stems.items():
            p = sd / f"{name}.wav"
            wavfile.write(p, sr, (np.clip(s * g * 0.89, -1, 1) * 32767).astype(np.int16))
            stem_paths[name] = p
    return PreviewResult(out_path, sr, total / sr, peak_db, stem_paths)
