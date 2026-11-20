---
title: A first mix in four passes: low cuts, a little OTT, sidechain, then a reference
topic: mixing
genres: [any, tech house, bass house, progressive house]
source: Alex Rome — Give me 19 mins, and I'll Improve your mixing skills by 126% (https://youtu.be/XrGZPWuiJ7o?t=43)
status: untested
---
## What it is
The order he gives every student for turning a "wall of instruments" into a clear rough mix. Each pass does one thing
to every track, so nothing is forgotten and each pass can be heard on its own.

## When to use it
When the arrangement is written and the track sounds crowded: the bass comes and goes, the kick is covered. Also as
the default mix order for a new `song.py` track before any finer work.

## How
1. **Low cuts.** Every instrument except kick, sub and drums gets a low cut, starting around 150 Hz (said,
   [1:04](https://youtu.be/XrGZPWuiJ7o?t=64)). Set each one while the bass plays (see
   `alex-rome-c-find-the-low-cut-against-the-bass.md`). The sub gets no EQ; a bass layer above it is cut like any
   other instrument (said, [4:50](https://youtu.be/XrGZPWuiJ7o?t=290)).
2. **Listen for the sub.** Play before and after. Pass when the sub can be followed all the way through (said,
   [5:53](https://youtu.be/XrGZPWuiJ7o?t=353)).
3. **OTT, a little on most things.** See `alex-rome-c-ott-amount-by-role.md`
   ([6:13](https://youtu.be/XrGZPWuiJ7o?t=373)).
4. **Sidechain everything melodic and the bass to the kick.** See
   `alex-rome-c-kickstart-on-the-instrument-group-keyed-by-the-kick.md` ([10:50](https://youtu.be/XrGZPWuiJ7o?t=650)).
5. **Reference.** A released track in the same genre with the same lead instrument, switched against the mix at
   matched loudness; note what differs in brightness, bass level and kick level, then fix it
   ([13:57](https://youtu.be/XrGZPWuiJ7o?t=837)).
6. Faders are not a separate pass in the video: levels are corrected as a result of step 5 (inferred).

## In Rohil's setup
All four passes use things he owns. `rick-rubin logic inspect` first: it lists every strip and its inserts, so the
tracks with no EQ, no OTT and no ducking are visible. Then one change at a time: `rick-rubin logic insert Piano
"Channel EQ"`, `rick-rubin logic insert Piano "OTT" Depth=30`, `rick-rubin logic insert Music "Kickstart 2" Mix=0.8`.
Pass 5 in numbers: `rick-rubin logic bounce bounces/drop.wav --bars 33-48`, then `rick-rubin reference compare <dir>
bounces/drop.wav`. For a `song.py` track the same order applies to the track definitions.

## How to check it
Bounce the same bars after each pass and run `rick-rubin compare <dir> pass0.wav pass1.wav pass2.wav pass3.wav`.
Expected: after pass 1 the low-mid share falls and the sub share rises; after pass 2 crest falls a little; after pass
3 the pump measure rises; after pass 5 `reference compare` shows fewer rows outside the references' range.

## Why it works
The passes go from removing conflicts (frequency, then time) to matching an outside target, so later decisions are
made on a mix that is already clear (inferred from the order; he presents it as the simplest order that works).
