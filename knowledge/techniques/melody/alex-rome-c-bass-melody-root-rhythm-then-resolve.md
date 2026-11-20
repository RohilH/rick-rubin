---
title: Bass melody: one root note made into a two-bar rhythm, doubled with a new ending, stabs on top
topic: melody
genres: [tech house, bass house]
source: Alex Rome — 5 Melody Styles Every Hit Song Uses (https://youtu.be/cjyEdyEWXbQ?t=805)
status: untested
---
## What it is
The bassline is the track's melodic driver. It is written the way a melody is: a short motif, a repeat, and an ending
that answers. He says you can find one almost anywhere in tech house.

## When to use it
Tech house and bass house drops, and any groove section with no lead. If the bass is the tune, do not also write a
busy lead; give the top a vocal, stabs or an accent melody instead.

## How
1. Start on one root note and get used to it (said, [14:09](https://youtu.be/cjyEdyEWXbQ?t=849); his is G).
2. Break up the rhythm: move and shorten notes, and leave a couple of rests (said,
   [14:28](https://youtu.be/cjyEdyEWXbQ?t=868)).
3. Stop when it loops well over two bars (said, [14:52](https://youtu.be/cjyEdyEWXbQ?t=892)). In the frame most notes
   are still the root, with one short step to a neighbouring pitch (shown
   [15:28](https://youtu.be/cjyEdyEWXbQ?t=928)).
4. Treat it as a melody: duplicate the two bars and rewrite the end of the copy so the four bars resolve (said,
   [15:00](https://youtu.be/cjyEdyEWXbQ?t=900)). His second ending leaves the root upward, then falls below it (shown
   at 15:28).
5. Make more than one version and compare (said, [15:20](https://youtu.be/cjyEdyEWXbQ?t=920)).
6. On top, use short chord stabs instead of a held four-bar progression (said,
   [15:45](https://youtu.be/cjyEdyEWXbQ?t=945)). Shown at [16:20](https://youtu.be/cjyEdyEWXbQ?t=980): a piano,
   four-note chords, a stab on beat 1 and two close together around beat 4, silence between.
7. Variant: chords over a held bottom note, to keep the harmony stable while the bass moves (said,
   [16:28](https://youtu.be/cjyEdyEWXbQ?t=988)).

## In Rohil's setup
Write it in `song.py` as a two-bar motif variable and a four-bar phrase built from it with a rewritten last half bar;
keep two or three endings as `option()` choices for `rick-rubin ab`. Sound: a plucky tech house bass
(`../bass/moonboy-tech-house-pluck-bass-in-serum.md`); a flat sub will not show the rhythm
(`../bass/alex-rome-c-rhythmic-bass-needs-a-plucked-sound.md`). MOONBOY's offbeat method
(`../bass/moonboy-offbeat-bassline-and-its-variations.md`) is another way to reach the motif; this card adds the
four-bar question-and-answer shape and what goes on top.

## How to check it
`rick-rubin score <dir> --tracks Bass --bars 1-4`: bars 1 to 2 and 3 to 4 match except near the end, and rests exist;
`rick-rubin check` runs the music lint on it. `rick-rubin hits` on a bounce: the bass accents fall between kicks. The
test that matters is Rohil's: can he hum the bassline after one listen?

## Why it works
Repetition makes it a groove and the changed ending makes it a phrase: the ear hears a question and an answer every
four bars, which is what makes a line memorable (inferred; he says he applies to it what he would apply to any
melody).
