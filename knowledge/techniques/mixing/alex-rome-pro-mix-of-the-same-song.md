---
title: Mix a song yourself, then pay a professional to mix the same song
topic: mixing
genres: [any]
source: Alex Rome — 10 Mixing Tips That Changed My Life (https://youtu.be/cU0tHoyJYjo?t=723)
status: untested
---
## What it is
A calibration exercise he sets his own students: finish your best mix of a track, then hire a professional mix
engineer to mix the same stems, and study the differences.

## When to use it
Once, on a track Rohil cares about and has taken as far as he can. It costs money, so it is for the point where
references alone have stopped teaching him anything.

## How
1. Mix the song to the end first, so there is something to compare (said).
2. Find an engineer on a freelance site; he walks through SoundBetter's mixing engineers list and also names Fiverr
   and AirGigs (said; shown [12:25](https://youtu.be/cU0tHoyJYjo?t=745)).
3. Pick someone with credits in the genre (inferred; he only shows that credited people are available).
4. Send the stems, get the mix back, and compare it with yours to see exactly where yours falls short (said).

## In Rohil's setup
The comparison is where the tools help. Bounce his mix and put the professional's file next to it in the project:
`rick-rubin reference compare <dir> refs/pro_mix.wav` and the same on his own bounce gives both against the shelf;
`rick-rubin split <dir> refs/pro_mix.wav` then `rick-rubin reference stems` compares drums with drums and bass with
bass; `rick-rubin width` on both shows what the engineer did with stereo. Write each difference down as a lesson in
`project.md` and as a `verdict`.

## How to check it
The exercise has worked when Rohil can name three specific differences with numbers (for example low-mid share, side
energy above 4 kHz, crest) and reproduce at least one of them in his own session.

## Why it works
A reference track is a different song; a professional mix of the same stems removes every variable except the
mixing, so every difference is a lesson (inferred from his claim that it shows exactly where to improve).
