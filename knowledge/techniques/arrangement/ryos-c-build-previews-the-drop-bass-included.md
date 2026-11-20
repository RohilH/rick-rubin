---
title: A build that previews the drop behind filters: chords, both basses with their pump, leads, a looped fragment
topic: arrangement
genres: [progressive house]
source: RYOS — Making Progressive House MAGIC | Studio Time with Ryos EP. 51 (https://youtu.be/srkGlUWW3pg?t=1472)
status: untested
---
## What it is
An 8-bar build made after the drop exists. It adds to `ryos-pg-build-by-filtering-everything-away.md`: here the
drop's basses also play in the build, a piece of the melody is looped, and the risers are chosen by role.

## When to use it
The drop is written and the build is empty. Read the earlier card first; this one lists what is new.

## How
1. Chord beds (strings, horns) enter on bar 1 of the build through a high-pass and a low-pass placed on the
   chord group, so one automation serves all layers (said, [24:32](https://youtu.be/srkGlUWW3pg?t=1472)).
2. Both drop basses play their drop notes behind a filter (FabFilter Simplon). He keeps their sidechain on so
   the build has some groove (said, [24:55](https://youtu.be/srkGlUWW3pg?t=1495)).
3. The leads come in filtered and the filter opens slowly ([25:18](https://youtu.be/srkGlUWW3pg?t=1518)).
4. Option: loop one fragment of the melody instead of playing it through. He says progressive house often
   should let the melody run, and chooses the loop here by ear
   ([25:39](https://youtu.be/srkGlUWW3pg?t=1539); shorter repeated lead clips shown 29:45).
5. Build drums: a classic build snare, a build kick, a clap; then adjust their rhythms so they complement
   each other ([26:00](https://youtu.be/srkGlUWW3pg?t=1560), 27:16).
6. Automate the snare's pitch upward across the build; he calls this what makes it sound like progressive
   house (said, [29:27](https://youtu.be/srkGlUWW3pg?t=1767); a "Channel pitch" clip on the snare, shown 29:45).
7. FX by role ([27:16](https://youtu.be/srkGlUWW3pg?t=1636) to 29:05; four lanes shown 29:45): a downlifter
   over the first half; one riser with character (a laser, his "dirty pong"); one plain riser as the body the
   others are layered with; one more for size.
8. End: the leads stop about half a bar early (gap shown 29:45), a reversed lead and the buzzy chords fill
   the last two bars (shown 31:20), and the drop's downbeat gets a crash pair plus one more hit
   ([30:34](https://youtu.be/srkGlUWW3pg?t=1834)).

## In Rohil's setup
Group filter: Logic's AutoFilter or Channel EQ on the chord bus (make the bus by hand; session mode cannot).
rick-rubin cannot write automation into his project, so the sweeps are drawn in Logic. Bass in the build:
`rick-rubin logic insert "Bass Bus" AutoFilter`, with Kickstart 2 after it so the pump stays. Snare pitch:
automate the sampler's pitch or transpose slices of the roll. Risers and downlifters from Splice, checked
with `rick-rubin audition <dir> <files...>` for length and brightness. In a `song.py` the build is its own
section with its own filtered tracks.

## How to check it
`rick-rubin spectrum <dir> --mix --bars 25-26` against `--bars 31-32` (first and last two bars of the build):
energy above 2 kHz should rise and the low band should stay below the drop's. `rick-rubin reference compare`:
the step in loudness from the last build bar to the first drop bar inside the references' range.

## Why it works
Hearing the drop's own bass and lead muffled tells the listener what is coming, so the drop lands as a
release. The kept pump carries the dance pulse through a section that has no full kick.
