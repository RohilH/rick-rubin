---
title: Start the track around someone else's vocal, then replace it with your own
topic: workflow
genres: [tech house, any]
source: MOONBOY — HOW TO TECH HOUSE | Full Tutorial (Odd Mob, Chris Lake, Mau P) (https://youtu.be/JqKaSvHImB0?t=1054)
status: untested
---
## What it is
A way to get past the blank page: use the acapella of a record you like as a placeholder, build drums and
bass around it until the track has its own identity, then take the placeholder out and put an original or
sampled vocal in its place.

## When to use it
When an idea will not start without a hook, or when Rohil wants a track "with the vibe of" a specific
record. He already makes edits and mashups, so the first half of this is his normal workflow.

## How
1. Three sources of a vocal, with his trade-offs ([16:53](https://youtu.be/JqKaSvHImB0?t=1013)):
   - a hired vocalist: slow, expensive, contracts; but original, and their audience comes with them (said);
   - a remix: fast, because the vibe already exists; but it stays a remix and may be blocked on YouTube or
     SoundCloud (said);
   - vocal samples: fast, a library to mix and match; but the popular ones are in many other tracks (said).
2. His own use of the second: write the idea around a remix vocal (an Eli Brown track for this video), keep
   going until the instrumental is unique, then remove the placeholder and replace it
   (said, [17:34](https://youtu.be/JqKaSvHImB0?t=1054)).
3. Inferred: note the placeholder's tempo, key, phrase lengths and where its syllables land before removing
   it, so the replacement can fill the same holes in the groove.

## In Rohil's setup
- Placeholder: `rick-rubin split <dir> refs/track.wav --stems vocals --bpm 130` gives the acapella at the
  project tempo; `rick-rubin transcribe` and `rick-rubin notes` record what it does (PREFERENCES §6).
- Replacement: Splice vocals; shortlist several, `rick-rubin audition <dir> <files...>`, `notes` for key fit
  (keys within one Camelot step), and conform with `rick-rubin conform <dir> file.wav --bpm 130`.
- Make it less recognisable than the pack original with the tune and vocoder cards.
- Keep the placeholder version as an edit for DJ sets; only the replaced version is a release candidate.

## How to check it
After the swap, `rick-rubin transcribe <dir> samples/new_vocal.wav`: stressed syllables land on the same
16ths the bass leaves free (compare with `rick-rubin hits --tracks Bass`), and `notes` shows it in key. Then
a bounce for him to hear, both versions.

## Why it works
A finished vocal gives the tempo, key, phrase length and mood at once, so every other decision has something
to answer to; and a track written to leave room for a vocal still has that room when the vocal changes.
