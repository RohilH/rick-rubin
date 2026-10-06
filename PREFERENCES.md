# David's standing preferences for music made with ableton-use

These apply to every song project. Each project's `CLAUDE.md` imports this file, so edit it here
and every project follows.

## 1. No templates. The agent writes the music.

Every note, rhythm, voicing, groove number and section is written by the agent for this song, in
`song.py`. No generators, stock patterns, preset arrangements or named grooves — not as a starting
point either. Knowing what a genre does is expected; copying a stock part is not.

## 2. Explore. Do not one-shot.

Trying several approaches and iterating is how something becomes great. Taking the first thing that
works is how it becomes flat. This applies to everything:

- **Samples and loops.** Search widely and more than once, with different words. For each role,
  shortlist several candidates, download them, and compare them by measurement (`ableton-use
  audition`, `notes`, `width`, `transcribe`) and in context (zoomed `eval` / `capture` with the
  candidate swapped in). Keep going until one is clearly right for *this* track — not merely
  acceptable. Write down what was rejected and why.
- **Instruments and presets.** Try more than one instrument or preset for each synth part
  (`ableton-use browse`, `serum list`), and compare them on audio captured from Live.
- **Drums, basslines, melodies, chords, arrangement.** Write alternative versions as variables in
  `song.py`, compare them in context, keep the best, and say what the others taught you. A part
  that was never compared against an alternative is a draft.
- **Mix decisions.** Change one thing, capture, measure, compare. Keep the numbers.

Spending Splice credits on this exploration is expected. Work within the credit cap given for the
track, and report what was spent.

## 3. Judge on what Live plays

The offline preview is a sketch. Decisions about sound, balance, clipping, sidechain depth and width
are made on audio recorded from Live (`ableton-use capture`), zoomed to the bars and tracks in
question while iterating, and on a full capture before presenting.

## 4. Read before writing around a sample

Before building parts around a vocal or melodic loop: `transcribe` it (which syllable lands where,
and how many ms off), read its `notes` (pitches **with octave**, cents, key fit), and check its
`width`. Fix or replace a sample that is late, out of tune or out of key before composing on top of it.

## 5. Say what happened

Report what was tried, what was kept, what was rejected and why, what was measured, and what is
still weak. No claim that something works in Live unless it was pushed and read back or captured.
