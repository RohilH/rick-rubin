# Research notes behind the defaults

These notes explain where the numbers in `house.py`, `analysis.py` and `SKILL.md` come from.
All of them are starting points, not rules. The hard rules are kept to things that break DJ
usability or mix correctness.

## Agent design (from browser-use/video-use)

- **Reading, not perceiving.** video-use gives the LLM a phrase-level transcript (~12 KB) instead of
  frames, and renders filmstrip+waveform PNGs only at decision points. That is the same idea as
  browser-use passing a structured DOM rather than screenshots. Here, `score.md` plays the transcript's
  role and `view` plays `timeline_view`'s.
- **EDL as source of truth → render → self-eval on the *rendered output* → fix, max 3 passes.**
  Here the EDL is `song.json` and the self-eval reads `preview.wav`.
- **Ask → confirm → execute → self-eval → persist**, with `project.md` session memory.
- **A short list of hard production rules, artistic freedom everywhere else.** Presets are framed as
  worked examples.
- Source: https://github.com/browser-use/video-use (README + SKILL.md).

## Ableton integration

- **AbletonOSC** (ideoforms) exposes much of the Live Object Model over OSC, including tracks,
  session clips, notes and devices. It creates clips in *session* slots and has no arrangement-clip
  creation. That is why ableton-use ships its own small remote script with a JSON-over-TCP protocol,
  following the pattern used by MCP bridges such as ableton-mcp/LiveMCP.
- **The Live Object Model provides the pieces the push needs:**
  - `Track.create_midi_clip(start_time, length)` creates an arrangement clip.
  - `Track.duplicate_clip_to_arrangement(clip, time)` is the fallback for older versions.
  - `Track.insert_device(name)` inserts native devices on Live 12.3+.
  - `Clip.add_new_notes` (Live 11+) adds notes.
  - `CompressorDevice.input_routing_type` routes the sidechain.
  - `Song.set_or_delete_cue` creates locators.
  - Source: https://docs.cycling74.com/apiref/lom/
- **Live API calls must run on Live's main thread.** The bridge therefore queues requests from its
  socket threads and drains them in `update_display`.

## Arrangement conventions

- House is arranged in 8/16/32-bar blocks. A common heuristic is a minor change every 8 bars and a
  major one every 16. Producers and DJs commonly recommend a 32-bar intro and outro so DJs can
  beat-match (gearspace "house music structure" thread; KVR forum).
- DJs need 16–32 bars of simple elements at the start and end of a track. A typical template is
  16 intro / 16 build / 32 drop / 16 breakdown / 32 drop (Lost Stories Academy, "What makes a track
  DJ-friendly").
- Breakdowns drop the drums (and usually the bass) for 8–32 bars. They resolve with a riser and/or
  a snare roll into a peak section of at least 32 bars (quadrophone, via Elektronauts). Deep-house
  templates often use repeating intro/breakdown/drop cycles with 24–32-bar drops (Mixed In Key,
  "How to arrange a dance music track").

## Groove, harmony and mix defaults (common practice)

- **Drums:**
  - four-on-the-floor kick;
  - clap/snare on 2 & 4;
  - off-beat open hat;
  - swung 16th closed hats with ghost notes.
- **Swing** is expressed MPC-style: 50% is straight and 66.7% is a triplet feel. House typically
  sits at 52–58%.
- **Bass** sits off the kick (off-beat or rolling 16ths), with the fundamental roughly in the
  40–80 Hz range, and is sidechained to the kick.
- **Harmony:**
  - minor or dorian keys;
  - 7th/9th voicings;
  - 9ths only where they are a whole step above the root, to avoid b9 clashes;
  - chords voice-led and kept above C2 so they stay out of the bass register.
- **Loudness** is measured with ITU-R BS.1770-4 (K-weighting plus gating), implemented in
  `analysis.py`. Measurements on the preview are relative, so the checks only compare sections
  with each other. For example, a breakdown should sit at least 3 LU below the drop.
