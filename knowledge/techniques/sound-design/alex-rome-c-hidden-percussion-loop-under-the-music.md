---
title: Hidden rhythms: a very quiet percussion loop chosen because it follows the main sound
topic: sound-design
genres: [progressive house, tech house, bass house, any]
source: Alex Rome — 7 Useful Layering Techniques and Why They Work (https://youtu.be/u8ozR9cnCTU?t=882)
status: untested
---
## What it is
A small drum or percussion loop tucked under a section at a level where it is barely noticed. It is not the drums; the
real drums come in later and are meant to be heard. He rates this the most valuable of the seven and says it is why
professional tracks sound full.

## When to use it
A section that is "technically done" and still feels like it lacks the last few percent of depth, especially a break
or verse with chords, vocal and little else.

## How
1. Collect several short drum or percussion loops (said, [15:21](https://youtu.be/u8ozR9cnCTU?t=921)).
2. Turn each well down and test them one at a time against the section's instruments (said,
   [15:42](https://youtu.be/u8ozR9cnCTU?t=942)).
3. Reject a loop with low-end content that collides with the chords, even if its groove is good (said,
   [16:03](https://youtu.be/u8ozR9cnCTU?t=963)).
4. Keep the loop whose accents line up with the rhythm of the main sound. His winner is a reggaeton-type pattern that
   happens to follow the chord rhythm (said, [16:10](https://youtu.be/u8ozR9cnCTU?t=970)).
5. Level: "really quiet", barely there (said, [16:23](https://youtu.be/u8ozR9cnCTU?t=983)). The only readable fader in
   that view is at −6.2 dB and may belong to another lane (shown [15:55](https://youtu.be/u8ozR9cnCTU?t=955)).
6. The loop need not come from the track's genre. The file on screen is a Splice percussion loop with 94 in its name,
   possibly its original tempo (shown at 15:55); conformed to the song, any groove is a candidate (inferred).
7. Bring the vocal back in and check that the section still sounds simple (said,
   [16:28](https://youtu.be/u8ozR9cnCTU?t=988)).

## In Rohil's setup
Splice is the source; this is the exploration PREFERENCES asks for. Download four to six candidates, then `rick-rubin
audition <dir> samples/raw/perc_a.wav samples/raw/perc_b.wav ...` to compare low-end content and transients before
listening, and `rick-rubin sample` to conform the keepers to the song tempo. High-pass the chosen loop (Channel EQ low
cut around 300 Hz) so step 3 cannot happen. In Logic: `rick-rubin logic add-audio <loop> --bar 17 --name "Hidden
perc"`, then `rick-rubin logic set "Hidden perc" volume=-18` as a starting level (ours).

## How to check it
`rick-rubin hits <dir> bounce.wav --bars` on the section with the loop: its strongest steps should coincide with the
chord or lead onsets. `rick-rubin compare` with and without: loudness within about 0.5 dB, a little more high and air
share, more transient density. If Rohil can pick the loop out on first listen, it is too loud.

## Why it works
Quiet transients between the main hits keep the ear's sense of pulse going, so sustained parts feel like they are
moving; matching accents make it reinforce the existing rhythm instead of adding a second one (inferred).
