# Mashups, edits and remix recreations

Rohil DJs. A mashup that clashes in key, doubles the drums or lets two vocals talk over each other is
unusable in a set. The rules are his (PREFERENCES §8); the tools are Logic's own, driven through the bridge.

## The rules

1. **Tempo with Logic's tools.** Smart Tempo and Flex & Follow, not an offline stretcher: `split --bpm`,
   `conform`. If Logic cannot do a step from here yet, build it into the bridge.
2. **Two vocals never overlap.** Every vocal piece ends where the next is heard; echo throws die away before
   the next line.
3. **One drum line and one bassline at a time**, or they are EQ'd apart.
4. **Keys within one Camelot step** (4A goes with 3A, 4A, 5A, 4B). Fewest transpositions. Tell him both keys
   in Camelot; he may pick the transposition.
5. **Measure pitch to choose the stretch.** Varispeed (pitch follows tempo) or pitch-kept: decide from the
   measured pitch of the result against the bed (`notes`), not from waveform correlation. A conform that
   leaves the vocal tens of cents off the bed is wrong however well it lines up.

## The steps

```
rick-rubin init <dir> --title "A x B" --bpm <the bed's tempo> --key "<the bed's key>"
rick-rubin split <dir> refs/bed.wav                              # stems of the track that stays at its tempo
rick-rubin split <dir> refs/other.wav --bpm 128 --source-bpm 126 [--transpose N]   # the other, conformed first
rick-rubin conform <dir> refs/other.wav --bpm 128 [--flex-mode "Flex Time - Speed (FX)"]   # conform without splitting
rick-rubin notes <dir> stems/other-128/vocals.wav                # what the vocal sings: pitch with octave, cents
rick-rubin transcribe <dir> stems/other-128/vocals.wav           # which syllable falls where
rick-rubin width <dir> stems/bed/drums.wav
```

- **Read both tracks first**: tempo (Smart Tempo's analysis; pass `--source-bpm` when it finds half or
  double), key of each (from `notes` on the bass and vocal stems), the sections and their bar counts.
- **Find the grid from the hits, not the peaks.** A long kick's peak is tens of ms after its attack; a grid
  taken from peaks put a vocal 33 ms early once. Check a conformed stem's drums against the bed's grid.
- **Arrange** as a `song.py` with audio patterns (`skill/samples.md`: loops are placed unwarped on audio
  tracks) or, for a recreation of an existing edit, a build script that places regions through the bridge.
  Logic puts an imported file on the bar line whatever beat you ask for: pad a file that starts inside a
  bar with silence from the bar line.
- **Check before presenting**: vocal overlaps per section (zero), the drum source and the bass source per
  section (one each), both keys in Camelot, the loudness of the result against the bed's own (`reference
  stems`, `eval --live`).
- **Bounce and send both the mix and the facts**: what is from which track in each section, the keys, the
  transposition, what was not judged by ear.

## What the two finished projects taught (logs in `~/Documents/rr-mashups/*/project.md`)

- Logic's Stem Splitter removes a vocal cleanly enough that the instrumental carries none of it (measured
  -117 dB), and a vocal stem carries the track's drums about 49 dB down: high-pass the vocal around 130 Hz.
- A project that holds only one file can take that file's sample rate; a session in Rohil's own project
  converts the file instead and leaves his project's rate alone.
- Logic's bounce dialog cannot be given a range beyond what it offers (its position fields step by ten):
  bounce the project and trim offline.
- Flex bounces are written in bursts: a bounce is finished when its file has stopped growing and no progress
  window is up.
