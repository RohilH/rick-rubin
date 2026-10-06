"""Word-level transcription of vocal samples, mapped onto the song grid.

The agent never listens (see SKILL.md); for a vocal that means it needs to *read*
which word falls on which beat. `transcribe()` runs a local Whisper model for
the words, then tightens each word's start and end against the audio's own
energy envelope (Whisper's word times are loose around silences and chops), and
expresses them as Ableton-style `bar.beat.sixteenth` positions at a given tempo.

The result is cached next to the sample as `<name>.words.json`; `score.md` prints
it under the audio pattern that uses the file.

Needs the optional dependency: `pip install "ableton-use[transcribe]"`.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from .model import STEP, fmt_pos
from .samples import _resample, read_audio

HOP_S = 0.005


@dataclass
class Word:
    text: str
    start_s: float
    end_s: float
    beat: float          # beats from the start of the file
    pos: str             # bar.beat.sixteenth of the nearest 16th (1-based)
    off_ms: float        # how far the word starts after (+) / before (-) that 16th
    conf: float          # 0..1 from the model


def sidecar(path: str | Path) -> Path:
    return Path(path).with_suffix(".words.json")


def _envelope(x: np.ndarray, sr: int) -> np.ndarray:
    """RMS in dB relative to the file's loudest frame, one value per HOP_S."""
    m = x.mean(axis=1).astype(np.float64)
    hop = max(1, int(HOP_S * sr))
    n = len(m) // hop
    rms = np.sqrt((m[: n * hop].reshape(n, hop) ** 2).mean(axis=1) + 1e-12)
    return 20 * np.log10(rms / (rms.max() + 1e-12))


def snap_to_audio(words: list[tuple[str, float, float, float]], env_db: np.ndarray, floor_db: float = -30.0,
                  reach_s: float = 0.12, gap_s: float = 0.12) -> list[tuple[str, float, float, float]]:
    """Tighten (text, start, end, conf) against the envelope. The model's window for
    a word is widened a little at the front, cut into bursts of sound separated by
    at least `gap_s` of quiet, and the word becomes the longest burst — so a word
    never starts in silence or straddles a chop."""
    loud = env_db > floor_db
    f = lambda t: int(max(0, min(len(loud) - 1, round(t / HOP_S))))  # noqa: E731
    gap = max(1, int(gap_s / HOP_S))
    out = []
    prev_end = 0
    for text, s, e, conf in words:
        a, b = max(prev_end, f(s) - int(reach_s / HOP_S)), f(e)
        on = np.flatnonzero(loud[a:b + 1]) + a
        if b <= a or not len(on):
            out.append((text, s, e, conf))
            continue
        cuts = np.flatnonzero(np.diff(on) > gap)
        runs = [(r[0], r[-1] + 1) for r in np.split(on, cuts + 1)]
        # the burst that overlaps the model's own window the most (ties: the longer one)
        a2, b2 = max(runs, key=lambda r: (min(r[1], b) - max(r[0], f(s)), r[1] - r[0]))
        out.append((text, a2 * HOP_S, b2 * HOP_S, conf))
        prev_end = b2
    return out


def to_grid(words: list[tuple[str, float, float, float]], bpm: float) -> list[Word]:
    out = []
    for text, s, e, conf in words:
        beat = s * bpm / 60.0
        q = round(beat / STEP) * STEP
        out.append(Word(text, round(s, 3), round(e, 3), round(beat, 3), fmt_pos(q), round((beat - q) * 60000.0 / bpm, 1), round(float(conf), 2)))
    return out


def transcribe(path: str | Path, bpm: float, model: str = "small.en", language: str | None = None, save: bool = True) -> list[Word]:
    """Words of `path` with grid positions at `bpm` (for a conformed loop: the song tempo)."""
    try:
        from faster_whisper import WhisperModel
    except ImportError as e:  # pragma: no cover
        raise RuntimeError('transcription needs faster-whisper: pip install "ableton-use[transcribe]"') from e
    sr, x = read_audio(path)
    mono16 = _resample(x.mean(axis=1, keepdims=True), sr, 16000)[:, 0].astype(np.float32)
    wm = WhisperModel(model, device="cpu", compute_type="int8")
    segs, _ = wm.transcribe(mono16, word_timestamps=True, vad_filter=False, condition_on_previous_text=False,
                            beam_size=5, language=language)
    raw = [(w.word.strip().strip(",.!?").strip() or w.word.strip(), float(w.start), float(w.end), float(w.probability))
           for s in segs for w in s.words]
    words = to_grid(snap_to_audio(raw, _envelope(x, sr)), bpm)
    if save:
        sidecar(path).write_text(json.dumps({"file": Path(path).name, "bpm": bpm, "model": model,
                                             "words": [asdict(w) for w in words]}, indent=1) + "\n")
    return words


def load_words(path: str | Path) -> list[Word] | None:
    """Cached transcription for a sample, or None."""
    p = sidecar(path)
    if not p.exists():
        return None
    return [Word(**w) for w in json.loads(p.read_text())["words"]]


def words_text(words: list[Word]) -> list[str]:
    """Compact lines for score.md: one line per bar, 'beat.sixteenth word'; '?' marks a doubtful word."""
    by_bar: dict[str, list[str]] = {}
    for w in words:
        bar, rest = w.pos.split(".", 1)
        off = f"{w.off_ms:+.0f}ms" if abs(w.off_ms) >= 15 else ""
        by_bar.setdefault(bar, []).append(f"{rest} {w.text}{'?' if w.conf < 0.5 else ''}{off}")
    return [f"  words bar {bar}: " + "; ".join(v) for bar, v in by_bar.items()]
