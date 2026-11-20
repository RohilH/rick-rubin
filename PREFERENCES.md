# Rohil's standing preferences for music made with rick-rubin

These apply to every project. Each project's `CLAUDE.md` imports this file, so edit it here and every
project follows. Sections 2 to 7 are David Adams's (the upstream author's) and are kept because they are
right; the rest is how Rohil works.

## 1. Logic Pro is the DAW, and the open project is Rohil's

- Rohil works in Logic Pro on this Mac. Ableton Live is not installed. Read `skill/logic.md`; where a
  document says "capture from Live", the equivalent here is a bounce from Logic.
- There are two jobs. **A new track from a brief** is written as `song.py` and pushed into a new Logic
  project. **Help inside a project Rohil has open** is session mode (`rick-rubin logic ...`): read it, make
  one change, read the change back. Never rebuild his project to make a change.
- In his project: never close it, never save it, never answer a question Logic is asking, never delete a
  track or a region unless he asked for exactly that. Say what changed, with the value before and after.
- Rohil is usually at the Mac while the agent works. Logic may only come to the front for the steps that
  need it, and only when he is not typing. No keystrokes are ever sent to anything but Logic's own process.
- Nothing is written outside the project folder without his say-so, with two standing exceptions he has
  asked for: `~/.rick-rubin/` (backups, change logs, his verdicts) and, on request, a designed Serum preset
  installed into Serum's user presets.

## 2. No templates. The agent writes the music.

Every note, rhythm, voicing, groove number and section is written by the agent for this song, in
`song.py`. No generators, stock patterns, preset arrangements or named grooves — not as a starting
point either. Knowing what a genre does is expected; copying a stock part is not.

## 3. Explore. Do not one-shot.

Trying several approaches and iterating is how something becomes great. Taking the first thing that
works is how it becomes flat. This applies to everything:

- **Samples and loops.** Search widely and more than once, with different words. For each role,
  shortlist several candidates, download them, and compare them by measurement (`rick-rubin
  audition`, `notes`, `width`, `transcribe`) and in context (a zoomed `eval` or bounce with the
  candidate swapped in). Keep going until one is clearly right for *this* track — not merely
  acceptable. Write down what was rejected and why.
- **Instruments and presets.** Try more than one instrument or preset for each synth part
  (`serum search`, `serum list`), and compare them on audio bounced from Logic.
- **Drums, basslines, melodies, chords, arrangement.** Write alternative versions as variables in
  `song.py`, compare them in context, keep the best, and say what the others taught you. A part
  that was never compared against an alternative is a draft.
- **Mix decisions.** Change one thing, bounce, measure, compare. Keep the numbers.

Spending Splice credits on this exploration is expected. Work within the credit cap given for the
track, and report what was spent.

## 4. Judge on what the DAW plays

The offline preview is a sketch. Decisions about sound, balance, clipping, sidechain depth and width
are made on audio bounced from Logic (`rick-rubin --daw logic capture`, or `rick-rubin logic bounce` in
his own project), zoomed to the bars and tracks in question while iterating, and on a full bounce before
presenting.

## 5. Correct is not finished, and measured is not heard

A track that passes every check can still sound flat. Before presenting, compare a bounce with released
tracks (`rick-rubin reference compare`) and close the gaps it shows.

The agent measures; it cannot hear. So:

- Anything that is about how it *sounds* ends with something for Rohil to listen to: a bounce, or an
  audition file (`rick-rubin serum audition`), with before and after when a change was made.
- What he says is written down with `rick-rubin verdict` (it lands in the project and in
  `~/.rick-rubin/taste.md`). Read the taste file before making sound, mix or arrangement decisions. A
  pattern in his verdicts outranks a general rule.
- "Nothing has been judged by ear" is said plainly when it is true.

## 6. Read before writing around a sample

Before building parts around a vocal or melodic loop: `transcribe` it (which syllable lands where,
and how many ms off), read its `notes` (pitches **with octave**, cents, key fit), and check its
`width`. Fix or replace a sample that is late, out of tune or out of key before composing on top of it.

## 7. Say what happened

Report what was tried, what was kept, what was rejected and why, what was measured, and what is
still weak. No claim that something works in Logic unless it was pushed or changed there and read back
or bounced.

## 8. Mashups and edits (Rohil DJs)

- Match tempo with Logic's own tools (Smart Tempo, Flex & Follow: `rick-rubin split --bpm`, `rick-rubin
  conform`), not an offline stretcher. If Logic lacks a step, build it into the bridge rather than work
  around it.
- Two vocals never overlap. One drum line and one bassline per stretch of time, or they are EQ'd apart.
- Keys within one Camelot step (4A goes with 3A, 4A, 5A, 4B). Make the fewest transpositions, tell him both
  keys in Camelot, and let him choose the transposition if he wants to.
- Decide varispeed against pitch-kept stretching by measuring pitch, not by waveform correlation.
- Check before presenting: vocal overlaps, the drum and bass source per section, the keys.

## 9. Teach while doing

Rohil wants to get better as a producer, not only to get a result. When a technique is used, name it in a
line and say why it fits here; when it came from a creator he follows, say who (see `knowledge/` once it
exists). Leave him the before and after to listen to.
