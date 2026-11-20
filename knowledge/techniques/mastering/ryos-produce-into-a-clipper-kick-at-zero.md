---
title: Produce into a clipper or limiter from the first bar, with the kick at 0 dB
topic: mastering
genres: [progressive house, tech house, bass house, any]
source: RYOS — Giving Feedback On YOUR Tracks! (https://youtu.be/3I7jJyVczPQ?t=631)
status: untested
---
## What it is
A fixed, very simple master chain that is on from the start of a project, so the track is at release level
while it is being written and the balance is made against the kick.

## When to use it
Every new project. He raised it for two quiet submissions and for one that a template limiter had flattened.

## How
1. Put one clipper or brick-wall limiter on the master and nothing else (said: any clipper, he names
   StandardCLIP; for a more advanced producer a transparent limiter such as Pro-L, said,
   [1:26:31](https://youtu.be/3I7jJyVczPQ?t=5191)).
2. Set the kick's channel to 0 dB and do not move it again. Mix every other part around the kick (said,
   [12:31](https://youtu.be/3I7jJyVczPQ?t=751)).
3. If the clipping turns ugly, put a gain utility in front of the clipper and pull it down in steps of 1 or 2 dB
   until the distortion goes (said, [13:01](https://youtu.be/3I7jJyVczPQ?t=781)).
4. A mix that is already balanced but quiet: same chain, and raise the gain utility by 2 to 3 dB (said,
   [1:27:00](https://youtu.be/3I7jJyVczPQ?t=5220)).
5. Leave the heavier tools (he produces into a stereo imager and God Particle, and adds EQ and an inflator at
   the end) until you know how to manage them; overdone, they hurt more than they help (said,
   [15:01](https://youtu.be/3I7jJyVczPQ?t=901)). A crushed template master: turn it off and go back to step 1
   (said, [1:35:50](https://youtu.be/3I7jJyVczPQ?t=5750)).

## In Rohil's setup
Logic has no stock hard clipper; the nearest is a brick-wall limiter on Stereo Out: Logic's Limiter, or
Mastering The Mix LIMITER. What is lost: a clipper shaves peaks without the pumping a limiter can add, so keep
the limiter's gain reduction small and get level from the gain stage. In a session:
`rick-rubin logic insert "Stereo Out" Limiter` (read its parameter names first with `rick-rubin logic devices
"Limiter"`), and Logic's Gain plug-in before it for step 3. In a `song.py`: `song.master_effects`. Ryos also
says, as hearsay, that Logic sounds fine clipping its output with nothing on it; do not rely on that for a
bounce without checking for clipped samples.

## How to check it
`rick-rubin reference compare <dir>` on a bounce: integrated loudness should rise toward the references and crest
should fall toward theirs (for released tech house this repo has measured about -7.5 LUFS and 8.5 dB crest),
with no clipped samples reported. The kick's peak on its own bounce should sit at or just under 0 dBFS.

## Why it works
Loudness changes how balance and brightness are judged, so mixing at the final level removes a surprise at the
end; a fixed kick gives every other fader one reference instead of a moving target.
