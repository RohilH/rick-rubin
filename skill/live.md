# Ableton Live as the render target

Only for a Mac or PC with Ableton Live and the RickRubin control surface (`install.md`). Rohil's Mac has Logic Pro, not Live: there, read `skill/logic.md` instead, and where other files say "capture from Live" read "bounce from Logic".

## Hearing what Live plays: `capture`

`preview.wav` is this library's own sketch render. `capture` is the real thing: it adds a temporary audio track set to **Resampling**, records the arrangement from Live's master in real time (the whole song, or just `--bars`; `--tracks` solos them), copies the take into the project (`live.wav`, or `zoom/live_bars_...wav`), removes the track and restores solo/metronome/loop. It then prints the same loudness table as `eval`, the stereo report, and a `view` drawn from Live's audio. Capture after every push you intend to present, and judge mix decisions — sidechain depth, compressor settings, master clipping, width — on it rather than on the preview. A zoomed capture of 8 bars takes ~15 s; use those while iterating and one full capture at the end.

## Live is the one source of truth for sound

There is one mixer, and it is Ableton's. The offline preview plays the notes and samples so that rhythm, harmony, arrangement and rough balance can be read in seconds — it does not run Live's devices (no Saturator, Compressor, Limiter, EQ, Utility; returns are a rough stand-in), and it never will: an imitation that differs from Live would be a second truth. So anything about *sound* — loudness, density, width, what an effect does, what the master does — is decided on audio recorded from Live (`capture`, `ab --live`, `hits --live`), and that loop is kept short instead:

- `push --update` (and every `ab --live` candidate) redoes only what changed since the last push: a device parameter, fader, pan or send is set in place; a changed part or instrument rebuilds that one track; returns and master only when they differ. The report's first line says what it did. Use it for every push after the first.
- `watch` is hot reload: it keeps running, and every time `song.py` is saved it rebuilds the song and applies just the change in Live without stopping playback (`--bars 81-88 --play` loops that range), printing one line per save — what was updated, how long it took, any warnings; a `song.py` that does not build is reported and Live is left as it was. It is for a person listening while the song is edited; an agent measuring should still `capture`.
- Capture the fewest bars that answer the question (`--bars 81-84`, `--tracks ...`): recording is real time.
- If someone changed the set by hand, `--update` notices and does a full push.
