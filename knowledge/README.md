# Knowledge: what the producers Rohil follows teach, as things the copilot can act on

Rohil is early in his production career. He wants to make progressive house eventually and is starting with
tech house and bass house. He asked for the videos of creators he follows to be digested for (1) production
insights and higher-level themes, (2) technical tricks for making specific sounds, (3) music theory and design,
so that the copilot can help him make tracks that sound complete.

This folder is that digest. It is text the agent reads and applies by hand. It is never a source of canned
notes, patterns or presets (see `CLAUDE.md`): a card says how and why, the agent still writes the part.

```
knowledge/
  PRINCIPLES.md                  the themes that recur across creators: read this first
  FINISHED.md                    "is this track finished?": one checklist merged from every creator
  genres/<genre>.md              tech house, bass house, progressive house: what a track consists of
  INDEX.md                       one line per card and per source, by topic and by genre
  TOOLS.md                       every tool the creators use, who has it, what to buy and what not to
  sources/<creator>/<slug>.md    one digest per video
  techniques/<topic>/<creator>-<slug>.md   one card per technique
```

Raw transcripts and frames are not kept here (they are the creators' work, and large). They live in
`~/.rick-rubin/knowledge-raw/<video id>/`.

## Writing rules

- Our own words. No transcript passages; at most a few words in quotation marks when the wording itself is the
  point. A digest is much shorter than the video.
- Every claim about a setting says where it came from: **said** (the creator says the number), **shown** (read off
  the screen in a frame, with the timestamp), or **inferred** (our reading; say so).
- Timestamps as links: `https://youtu.be/<id>?t=<seconds>`.
- Translate to Rohil's setup. He works in Logic Pro 11 on a Mac with Serum 2, Vital, Kickstart 2, Trackspacer 2.5,
  OTT, Valhalla Supermassive, Mastering The Mix (BASSROOM, MIXROOM, LEVELS, LIMITER, REFERENCE, RESO, STEREOVAULT,
  FUSER, ANIMATE, FASTERMASTER), Ozone Imager 2, Splice, and Logic's own plug-ins. When a creator uses Ableton, FL
  Studio or a plug-in he does not own, name the nearest thing he has and what would be lost.
- Where rick-rubin can do a step, give the command (see `SKILL.md`, `skill/serum.md`, `skill/logic.md`,
  `skill/mix.md`): e.g. `rick-rubin serum set init osc_a.unison=7 osc_a.detune=0.2 --save supersaw`,
  `rick-rubin logic insert Bass "Kickstart 2" Mix=0.6`. Serum keys must be real ones (`rick-rubin serum params
  --group osc` lists them); do not invent keys.
- Where a technique can be checked by measurement, say which number should move and which way (`serum describe`,
  `width`, `eval`, `reference compare`, `spectrum`).
- A card is tested only when someone ran it on this Mac and wrote the numbers down. New cards are `status: untested`.

## A source digest (`sources/<creator>/<slug>.md`)

```markdown
---
creator: <name>
title: <video title>
url: https://youtu.be/<id>
length: <h:mm:ss>
published: <yyyy-mm-dd>
digested: <yyyy-mm-dd>
genres: [progressive house | tech house | bass house | any]
---
## What it is about            (3 to 6 sentences)
## The main ideas               (the higher-level themes, most important first; each 1 to 3 sentences with a timestamp)
## Step by step                 (what is built or shown, in order, with timestamps; only for tutorials)
## Tools the creator uses       (DAW, synths, effects, sample packs; and what for)
## Cards made from this video   (links to techniques/...)
## Not covered or unclear       (what could not be read from captions or frames)
```

At most about 120 lines.

## A technique card (`techniques/<topic>/<creator>-<slug>.md`)

Topics: `sound-design`, `drums`, `bass`, `harmony`, `melody`, `arrangement`, `mixing`, `mastering`, `workflow`,
`mindset`.

```markdown
---
title: <what it does, in plain words>
topic: <one topic>
genres: [..]
source: <creator> — <video title> (https://youtu.be/<id>?t=<seconds>)
status: untested
---
## What it is                  (1 to 3 sentences)
## When to use it
## How                         (numbered steps; each setting marked said / shown / inferred)
## In Rohil's setup            (Logic, Serum 2 and his plug-ins; rick-rubin commands where one applies)
## How to check it             (the measurement, and which way it should move)
## Why it works                (1 to 3 sentences)
```

At most about 45 lines. One technique per card. Prefer fewer, sharper cards over many thin ones: a card must be
something a producer could act on tomorrow.
