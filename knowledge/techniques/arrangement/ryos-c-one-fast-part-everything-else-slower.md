---
title: Give the speed to one part: under a fast melody, slow the chords, hold the bass, drop the rhythmic piano
topic: arrangement
genres: [progressive house, tech house, bass house, any]
source: RYOS — Making Progressive House MAGIC | Studio Time with Ryos EP. 51 (https://youtu.be/srkGlUWW3pg?t=85)
status: untested
---
## What it is
A budget for rhythm. Only one part gets to be busy; every other part is simplified until it supports that one.
In this track the busy part is the melody, and he removes competing rhythm three separate times.

## When to use it
When a section feels cluttered although every part sounds good alone, or when a new part is "sick" but the
drop gets harder to follow with it in.

## How
1. Name the busy part. Here: a melody of six notes per bar ([1:04](https://youtu.be/srkGlUWW3pg?t=64)).
2. Chords: the starting MIDI has six chords in four bars (shown, 1:15). His first move is to thin them, so the
   chords "anchor" the melody (said, [1:25](https://youtu.be/srkGlUWW3pg?t=85)).
3. Bass: he wants a rhythmic bass, writes a galloping one with pitch bends, likes it, then calls it "too
   crazy" for this melody and switches to one held note per bar (said,
   [2:08](https://youtu.be/srkGlUWW3pg?t=128) to [4:18](https://youtu.be/srkGlUWW3pg?t=258); shown 4:10).
4. A held bass still needs movement, so it comes from pitch, not rhythm: the last bar of the loop bends down
   like a tape stop, and later every bass layer is linked to that one pitch automation (said, 3:37 and
   [10:53](https://youtu.be/srkGlUWW3pg?t=653)). How to draw it: `sound-design/ryos-b-pitch-bend-dives-on-the-lead.md`.
5. Keep the rejected version, muted, for another section or another track: he leaves it "in the back pocket".
6. Dance piano: its chord stabs are a second rhythm against the melody, so it is deleted from the drop:
   "simpler is the move for this track" (said, [18:43](https://youtu.be/srkGlUWW3pg?t=1123)).
7. The rule depends on the melody. In his previous episode the melody was slower, and the bass and the dance
   piano copied its rhythm (`ryos-pg-bass-copies-melody-rhythm-with-slides.md`,
   `ryos-pg-dance-piano-with-supersaw-stabs.md`). Either the other parts share the lead's rhythm, or they stay
   out of its way; what he avoids is a second, different rhythm (inferred from the two videos).

## In Rohil's setup
For the house remix of a hip-hop vocal, the rap is the busy part (our application, not his): start with a
held or simple offbeat bass and one chord per bar, and add rhythm elsewhere only where the vocal rests. In a
`song.py`, write the busy and the simple version of a part as variables and compare both in context
(PREFERENCES §3). In his Logic project, mute the alternative instead of deleting it:
`rick-rubin logic set "Bass busy" mute=on`.

## How to check it
`rick-rubin score <dir> --bars A-B`: count onsets per bar for each pitched track. One track should be clearly
ahead (here 6 against 1 or 2). `rick-rubin hits <dir> --tracks Lead Bass Chords` shows whether two parts put
accents on different sixteenths in the same bar; that is the clash he removes. Then bounce both versions for
Rohil to hear.

## Why it works
A listener follows one rhythm at a time. A second independent rhythm in the same register is heard as noise
around the first, while long notes underneath make the fast part sound faster by contrast.
