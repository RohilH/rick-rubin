---
title: A quiet counter-melody made of short vocal chops that answer the main vocal, transposed into key
topic: melody
genres: [any, tech house, bass house, progressive house]
source: Alex Rome — An Insanely Simple Arrangement System (escape the loop trap) (https://youtu.be/ZkRds6iTfhQ?t=501)
status: untested
---
## What it is
The second change he makes in the third section of his two-loop demo: instead of opening up the chords, which he
is saving for later, he adds a relaxed counter-melody from two unrelated vocal samples that respond to the main
hook.

## When to use it
A section needs one more change and the big moves (filter opening, new chord layer, drums) are either used or
being held back. In a remix: ad-libs and one-word chops between the main phrases.

## How
1. The need: drums have just been layered (one change), the section still wants a second, and opening the chords
   would spend the peak too early (said, [8:01](https://youtu.be/ZkRds6iTfhQ?t=481)).
2. Choose something "relaxed", "not too aggressive", "a nice response" to the main vocal (said,
   [8:21](https://youtu.be/ZkRds6iTfhQ?t=501)).
3. He drags in two short vocal samples (shown [9:00](https://youtu.be/ZkRds6iTfhQ?t=540): an ad-lib and a vocal
   riff; in the Splice list at [0:30](https://youtu.be/ZkRds6iTfhQ?t=30) they are tagged 165 BPM, C minor and
   156 BPM, A# minor).
4. They are not in the song's key, so each is transposed (said, [8:42](https://youtu.be/ZkRds6iTfhQ?t=522)). The
   song's vocal is tagged G# minor (shown, 0:30); the amounts he uses are not shown.
5. Placement: the two chops alternate, each about two bars, from the start of the section onward, and move to a
   third track when the next section starts (shown [11:40](https://youtu.be/ZkRds6iTfhQ?t=700)).
6. Run the transition check on the join before going on (said, [9:07](https://youtu.be/ZkRds6iTfhQ?t=547)).

## In Rohil's setup
Find candidates in Splice (several, PREFERENCES §3), then read each before using it: `rick-rubin notes <dir>
chop.wav` for its pitches and key, `rick-rubin conform <dir> chop.wav --bpm 126 --transpose N` to bring it to
tempo and key with Logic's own stretching. In his video the chops play while the main vocal continues; Rohil's
rule is that two vocals never overlap (PREFERENCES §8), so use `rick-rubin transcribe` on the main vocal to find
its gaps and put the answers there, or use the chops only where the main vocal rests. For a hip-hop acapella the
natural sources are its own ad-libs: cut them from the stem rather than importing a second singer (inferred).
The synth version of this role is `melody/alex-rome-c-accent-melody-behind-the-vocal.md`.

## How to check it
`rick-rubin notes` on the conformed chop: in key, within a few cents. `rick-rubin transcribe` on a bounce of both
vocal tracks: no answer starts while a main phrase is sounding. Level: the answer sits clearly under the main
vocal; confirm with a bounce and his verdict.

## Why it works
A response in the gaps adds a second voice without adding harmony or low end, so it changes the section while
leaving the bigger moves unspent.
