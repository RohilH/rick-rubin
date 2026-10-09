# Demo: Night Shift, rendered into Logic Pro by the agent

The song is [`examples/night-shift`](../../examples/night-shift) — a simple house track with a tech house bassline,
every note written in `song.py`. These recordings show `rick-rubin --daw logic` building it in Logic Pro 11.2 and
bouncing it. The Mac had no loopback audio device, so the playback video carries Logic's own bounce of the song
laid under the picture in sync.

| | |
|---|---|
| `push.mp4` / `push.gif` | `rick-rubin --daw logic push --replace --automation examples/night-shift`, sped up (the real push took about 16 minutes): the MIDI file opens as a project, tracks are named, Drum Synth voices and Retro Synth are loaded, the mixer is set, effects and side chains are inserted and tuned, the return and master built, the pad's volume rides written, the project saved. |
| `play.mp4` / `play.gif` | Logic playing the finished project from bar 1, with the bounce as its audio. |
| `bounce.mp4` / `bounce.gif` | `rick-rubin --daw logic capture examples/night-shift`: the offline bounce and the measurements rick-rubin prints for it. |
| `night-shift.mp3` | the bounce (24-bit WAV in the project folder, MP3 here). |

Nothing in Logic was touched by hand. The bridge drives Logic through a MIDI file it opens as a project, macOS
accessibility, and a Mackie Control it emulates on a virtual MIDI port — see [`docs/LOGIC.md`](../LOGIC.md).
