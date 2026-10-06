"""Syllable-accurate transcription of vocal samples, mapped onto the song grid.

The agent never listens (see SKILL.md); for a vocal that means it has to *read*
which syllable falls on which 16th, and how many milliseconds off it is. Three
stages, each doing the part it is good at:

1. **Words** — a local Whisper model, or the lyric you pass in (`text=`), which
   is better whenever you know it.
2. **Forced alignment** — a wav2vec2 CTC aligner (torchaudio's MMS_FA) pins every
   *letter* of those words to the audio at 20 ms resolution. This is far tighter
   than Whisper's own word times, which drift by 50-150 ms around chops and gaps.
3. **Onsets** — letters are grouped into syllables and each syllable is snapped
   to what the audio itself does: where its sound starts (`start_s`, the place
   to cut) and where it reaches full level (`vowel_s` — the vowel coming in after
   the consonant, which is the moment a listener hears as "the beat" of that
   syllable). The aligner's own letter times sit mid-sound, so they only bound
   the search. Grid positions and ms offsets are measured from `vowel_s`.

`retime_loop()` then uses those cut points to move every word (or syllable) onto
the grid — an audio quantize for a loop whose performance is loose.

Results are cached next to the sample as `<name>.words.json`; `score.md` prints
them under the audio pattern that uses the file.

Needs the optional dependencies: `pip install "ableton-use[transcribe]"`.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np

from .model import BEATS_PER_BAR, STEP, fmt_pos
from .samples import _resample, read_audio, write_wav24

HOP_S = 0.002          # envelope resolution
VOWELS = set("aeiouy")


@dataclass
class Syllable:
    text: str
    start_s: float       # where its sound begins — the cut point
    vowel_s: float       # where its vowel swells — what is heard as on/off the beat
    end_s: float
    beat: float          # vowel position in beats from the start of the file
    pos: str             # bar.beat.sixteenth of the nearest 16th (1-based)
    off_ms: float        # vowel after (+) / before (-) that 16th
    conf: float          # 0..1 alignment confidence


@dataclass
class Word:
    text: str
    start_s: float
    end_s: float
    beat: float
    pos: str
    off_ms: float
    conf: float
    syllables: list[Syllable] = field(default_factory=list)


def sidecar(path: str | Path) -> Path:
    return Path(path).with_suffix(".words.json")


# ============================================================================ audio
def envelope(x: np.ndarray, sr: int, win_s: float = 0.010) -> np.ndarray:
    """Smoothed RMS in dB relative to the file's loudest moment, one value per HOP_S."""
    m = x.mean(axis=1).astype(np.float64) if x.ndim > 1 else x.astype(np.float64)
    hop, win = max(1, int(HOP_S * sr)), max(2, int(win_s * sr))
    p = np.concatenate([[0.0], np.cumsum(m * m)])
    idx = np.arange(0, len(m) - 1, hop)
    hi = np.minimum(idx + win // 2, len(m))
    lo = np.maximum(idx - win // 2, 0)
    rms = np.sqrt((p[hi] - p[lo]) / np.maximum(1, hi - lo) + 1e-12)
    return 20 * np.log10(rms / (rms.max() + 1e-12))


def snap_onset(env_db: np.ndarray, t: float, before_s: float = 0.05, after_s: float = 0.03, floor_db: float = -45.0) -> float:
    """The steepest rise of the envelope near time `t` — where a sound actually starts.
    Returns `t` unchanged when nothing rises there (a syllable inside a held note)."""
    f = lambda s: int(max(0, min(len(env_db) - 1, round(s / HOP_S))))  # noqa: E731
    a, b = f(t - before_s), f(t + after_s)
    if b - a < 4:
        return t
    k = max(1, int(0.006 / HOP_S))                       # rise measured over 6 ms
    seg = np.maximum(env_db[a:b + k], floor_db)
    rise = seg[k:] - seg[:-k]
    i = int(np.argmax(rise))
    if rise[i] < 3.0:                                    # under 3 dB in 6 ms: no real onset
        return t
    return (a + i + k / 2) * HOP_S


def beat_point(env_db: np.ndarray, start: float, until: float, below_peak_db: float = 6.0) -> float:
    """Where a syllable that starts at `start` reaches (nearly) full level — its perceptual
    attack. For 'take' or 'some' that is the vowel coming in after the consonant; for a
    syllable that starts on its vowel it is the start itself. `until` bounds the search
    (a little past where the aligner heard the vowel)."""
    a = int(max(0, start / HOP_S))
    b = int(min(len(env_db), max(until, start + 0.02) / HOP_S))
    if b - a < 2:
        return start
    seg = env_db[a:b]
    hit = np.flatnonzero(seg >= seg.max() - below_peak_db)
    return start + int(hit[0]) * HOP_S


# ============================================================================ syllables
def syllabify(word: str) -> list[tuple[int, int, int]]:
    """Orthographic syllables of an English word as (first letter, first vowel letter, end) indices.
    'gonna' -> gon|na, 'take' -> take (silent e), 'crisis' -> cri|sis. Good enough to find nuclei;
    it does not need to be dictionary-perfect."""
    w = word.lower()
    is_v = [(c in VOWELS and not (c == "y" and i == 0)) for i, c in enumerate(w)]
    groups = []                                           # vowel groups: (start, end)
    i = 0
    while i < len(w):
        if is_v[i]:
            j = i
            while j + 1 < len(w) and is_v[j + 1]:
                j += 1
            groups.append((i, j + 1))
            i = j + 1
        else:
            i += 1
    # a final 'e' after a consonant is silent when there is another vowel ("take", "some"), except "-le" ("table")
    if len(groups) > 1 and groups[-1] == (len(w) - 1, len(w)) and w[-1] == "e" and not (len(w) > 2 and w[-2] == "l" and not is_v[len(w) - 3]):
        groups.pop()
    if not groups:
        return [(0, 0, len(w))]
    out = []
    start = 0
    for n, (vs, ve) in enumerate(groups):
        if n + 1 < len(groups):
            cons = groups[n + 1][0] - ve                   # consonants before the next nucleus
            end = ve + (0 if cons <= 1 else 1)             # one consonant goes to the next syllable; of several, the first stays
        else:
            end = len(w)
        out.append((start, vs, end))
        start = end
    return out


# ============================================================================ stages
def whisper_words(mono16: np.ndarray, model: str = "small.en", language: str | None = None) -> list[str]:
    try:
        from faster_whisper import WhisperModel
    except ImportError as e:  # pragma: no cover
        raise RuntimeError('transcription needs: pip install "ableton-use[transcribe]" (or pass the lyric as text=)') from e
    wm = WhisperModel(model, device="cpu", compute_type="int8")
    segs, _ = wm.transcribe(mono16, word_timestamps=True, vad_filter=False, condition_on_previous_text=False,
                            beam_size=5, language=language)
    return [w.word for s in segs for w in s.words]


def clean_words(words: list[str] | str) -> list[str]:
    """Lower-case words reduced to letters and apostrophes (what the aligner knows)."""
    if isinstance(words, str):
        words = words.split()
    out = [re.sub(r"[^a-z']", "", w.lower().replace("’", "'")).strip("'") for w in words]
    return [w for w in out if w]


def force_align(mono16: np.ndarray, words: list[str]) -> list[list[tuple[float, float, float]]]:
    """Per word, per letter: (start_s, end_s, score) from a wav2vec2 CTC forced aligner."""
    try:
        import torch
        import torchaudio
    except ImportError as e:  # pragma: no cover
        raise RuntimeError('alignment needs torch + torchaudio: pip install "ableton-use[transcribe]"') from e
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        bundle = torchaudio.pipelines.MMS_FA
        model, tok, aligner = bundle.get_model(), bundle.get_tokenizer(), bundle.get_aligner()
        wav = torch.from_numpy(np.ascontiguousarray(mono16, dtype=np.float32))[None]
        with torch.inference_mode():
            emission, _ = model(wav)
        spans = aligner(emission[0], tok(words))
    frame = wav.shape[1] / emission.shape[1] / bundle.sample_rate
    return [[(s.start * frame, s.end * frame, float(s.score)) for s in word] for word in spans]


def build_words(words: list[str], letters: list[list[tuple[float, float, float]]], env_db: np.ndarray, bpm: float,
                total_s: float) -> list[Word]:
    """Letters -> syllables -> audio-snapped, grid-mapped Words."""
    flat: list[tuple[int, str, float, float, float]] = []      # (word index, text, start, vowel, conf)
    for wi, (w, ls) in enumerate(zip(words, letters)):
        if len(ls) != len(w):                                  # aligner dropped a symbol: treat the word as one syllable
            sylls = [(0, 0, len(ls))]
            w = w[:len(ls)]
        else:
            sylls = syllabify(w)
        for a, v, b in sylls:
            if a >= len(ls):
                continue
            v = min(v, len(ls) - 1)
            start = snap_onset(env_db, ls[a][0])
            vowel = beat_point(env_db, start, max(ls[v][0] + 0.06, start + 0.08))
            flat.append((wi, w[a:b], start, vowel, float(np.mean([x[2] for x in ls[a:b]]))))
    for i in range(1, len(flat)):                               # keep them in order after snapping
        if flat[i][2] <= flat[i - 1][2]:
            flat[i] = (flat[i][0], flat[i][1], flat[i - 1][2] + HOP_S, max(flat[i][3], flat[i - 1][2] + HOP_S), flat[i][4])
    loud = env_db > -35.0
    out: list[Word] = []
    last_wi = None
    for i, (wi, text, start, vowel, conf) in enumerate(flat):
        nxt = flat[i + 1][2] if i + 1 < len(flat) else total_s
        a, b = int(start / HOP_S), min(len(loud), int(nxt / HOP_S))
        on = np.flatnonzero(loud[a:b])
        end = (a + int(on[-1]) + 1) * HOP_S if len(on) else nxt  # where its sound stops
        syl = _syllable(text, start, vowel, min(end, nxt), conf, bpm)
        if wi == last_wi:
            out[-1].syllables.append(syl)
            out[-1].end_s = syl.end_s
            out[-1].conf = round(float(np.mean([s.conf for s in out[-1].syllables])), 2)
        else:
            out.append(Word(words[wi], syl.start_s, syl.end_s, syl.beat, syl.pos, syl.off_ms, syl.conf, [syl]))
            last_wi = wi
    return out


def _syllable(text: str, start: float, vowel: float, end: float, conf: float, bpm: float) -> Syllable:
    beat = vowel * bpm / 60.0
    q = round(beat / STEP) * STEP
    return Syllable(text, round(start, 4), round(vowel, 4), round(end, 4), round(beat, 4), fmt_pos(q),
                    round((beat - q) * 60000.0 / bpm, 1), round(conf, 2))


# ============================================================================ public
def transcribe(path: str | Path, bpm: float, model: str = "small.en", language: str | None = None,
               text: str | None = None, save: bool = True) -> list[Word]:
    """Words and syllables of `path` with grid positions at `bpm` (for a conformed loop: the song tempo).
    Pass `text` when you know the lyric — the aligner then only has to place it."""
    sr, x = read_audio(path)
    mono16 = _resample(x.mean(axis=1, keepdims=True), sr, 16000)[:, 0].astype(np.float32)
    words = clean_words(text if text else whisper_words(mono16, model, language))
    if not words:
        result: list[Word] = []
    else:
        result = build_words(words, force_align(mono16, words), envelope(x, sr), bpm, len(x) / sr)
    if save:
        save_words(path, result, bpm, model if not text else "given text")
    return result


def save_words(path: str | Path, words: list[Word], bpm: float, source: str = "") -> None:
    sidecar(path).write_text(json.dumps({"file": Path(path).name, "bpm": bpm, "source": source,
                                         "words": [asdict(w) for w in words]}, indent=1) + "\n")


def load_words(path: str | Path) -> list[Word] | None:
    """Cached transcription for a sample, or None."""
    p = sidecar(path)
    if not p.exists():
        return None
    out = []
    for w in json.loads(p.read_text())["words"]:
        syl = [Syllable(**s) for s in w.pop("syllables", [])]
        out.append(Word(**w, syllables=syl))
    return out


def words_text(words: list[Word]) -> list[str]:
    """Compact lines for score.md, one per bar: 'beat.sixteenth syllable[±ms]'. A leading '-' continues
    the previous word; '?' marks a doubtful alignment; offsets under 10 ms are not shown."""
    by_bar: dict[str, list[str]] = {}
    for w in words:
        sylls = w.syllables or [Syllable(w.text, w.start_s, w.start_s, w.end_s, w.beat, w.pos, w.off_ms, w.conf)]
        for i, s in enumerate(sylls):
            bar, rest = s.pos.split(".", 1)
            off = f"{s.off_ms:+.0f}ms" if abs(s.off_ms) >= 10 else ""
            by_bar.setdefault(bar, []).append(f"{rest} {'-' if i else ''}{s.text}{'?' if s.conf < 0.3 else ''}{off}")
    return [f"  words bar {bar}: " + "; ".join(v) for bar, v in by_bar.items()]


def table(words: list[Word]) -> str:
    L = ["pos (bar.beat.16th)  vowel off   cut at    vowel at  ends      conf  syllable"]
    for w in words:
        for i, s in enumerate(w.syllables):
            L.append(f"{s.pos:<20} {s.off_ms:+7.0f}ms  {s.start_s:7.3f}s  {s.vowel_s:7.3f}s  {s.end_s:7.3f}s  {s.conf:.2f}  "
                     f"{'-' if i else ''}{s.text}" + (f"   ({w.text})" if i == 0 and len(w.syllables) > 1 else ""))
    return "\n".join(L)


# ============================================================================ re-timing
def retime_loop(src: str | Path, dst: str | Path, bpm: float, words: list[Word], by: str = "word", grid: int = 16,
                strength: float = 1.0, moves: dict[int, float | str] | None = None, fade_ms: float = 4.0) -> list[dict]:
    """Audio-quantize a loop: cut it at word (or syllable) starts and slide each piece so its
    vowel lands on the nearest 1/`grid` note. The file keeps its length.

    strength  0..1 — how far towards the grid each piece moves (1 = fully on it)
    moves     {piece number (1-based): target} to place a piece yourself; target is beats from the
              start of the file or a 'bar.beat.sixteenth' string
    Returns one row per piece: text, from/to beat, shift in ms. Also writes the shifted word timings
    next to `dst`, so the new file's score lines are right without transcribing again."""
    from .model import parse_pos
    sr, x = read_audio(src)
    spb = 60.0 / bpm
    step = BEATS_PER_BAR / grid
    units: list[tuple[str, float, float]] = []                  # (text, cut_s, anchor_s)
    for w in words:
        if by == "syllable":
            units += [(("-" if i else "") + s.text, s.start_s, s.vowel_s) for i, s in enumerate(w.syllables)]
        else:
            units.append((w.text, w.start_s, w.syllables[0].vowel_s if w.syllables else w.start_s))
    out = np.zeros_like(x)
    f = max(1, int(fade_ms / 1000 * sr))
    rows = []
    new_cuts = []
    for i, (text, cut, anchor) in enumerate(units):
        beat = anchor / spb
        target = round(beat / step) * step
        target = beat + (target - beat) * strength
        if moves and (i + 1) in moves:
            m = moves[i + 1]
            target = parse_pos(m) if isinstance(m, str) else float(m)
        shift = (target - beat) * spb
        new_cuts.append(cut + shift)
        rows.append({"n": i + 1, "text": text, "from_beat": round(beat, 3), "to_beat": round(target, 3),
                     "from_pos": fmt_pos(round(beat / STEP) * STEP), "to_pos": fmt_pos(round(target / STEP) * STEP),
                     "shift_ms": round(shift * 1000, 1)})
    bounds = [u[1] for u in units] + [len(x) / sr]
    # the lead-in before the first piece stays where it is
    pieces = [(0.0, bounds[0], 0.0)] if units and bounds[0] > 0 else []
    pieces += [(bounds[i], bounds[i + 1], new_cuts[i]) for i in range(len(units))]
    starts = [p[2] for p in pieces] + [len(x) / sr]
    for k, (a_s, b_s, at_s) in enumerate(pieces):
        a, b = int(round(a_s * sr)), int(round(b_s * sr))
        seg = x[a:b].copy()
        at = int(round(at_s * sr))
        room = int(round(starts[k + 1] * sr)) - at + f          # may run `f` samples into the next piece (crossfade)
        seg = seg[: max(0, min(len(seg), room, len(x) - at))]
        if at < 0:
            seg, at = seg[-at:], 0
        if len(seg) < 2 * f:
            continue
        ramp = np.linspace(0, 1, f, dtype=np.float32)[:, None]
        seg[:f] *= ramp
        seg[-f:] *= ramp[::-1]
        out[at:at + len(seg)] += seg
    write_wav24(dst, sr, out)
    # shifted timings for the new file
    shifted: list[Word] = []
    it = iter(rows)
    for w in words:
        if by == "syllable":
            sy = []
            for s in w.syllables:
                d = next(it)["shift_ms"] / 1000
                sy.append(_syllable(s.text, s.start_s + d, s.vowel_s + d, s.end_s + d, s.conf, bpm))
        else:
            d = next(it)["shift_ms"] / 1000
            sy = [_syllable(s.text, s.start_s + d, s.vowel_s + d, s.end_s + d, s.conf, bpm) for s in w.syllables]
        if sy:
            shifted.append(Word(w.text, sy[0].start_s, sy[-1].end_s, sy[0].beat, sy[0].pos, sy[0].off_ms, w.conf, sy))
    save_words(dst, shifted, bpm, f"retimed from {Path(src).name} by {by}, grid 1/{grid}, strength {strength:g}")
    return rows
