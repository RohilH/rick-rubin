# Exploring and reading: candidates, measurements, pictures

## Exploring

Great tracks come from comparing options, not from accepting the first one. You cannot hear, so exploring means *measuring several things and reading the difference*. Budget most of a session for it.

- **Samples, per role.** Search more than once with different words (character, genre, era, gear: "rubbery", "909", "dusty", "tight short"). Download a shortlist — typically 4–8 for the sounds that define the track (kick, bass, main hook, vocal), 2–4 for supporting ones — into `samples/raw/` and run `audition` on them together. Read the table for what the role needs: a kick's fundamental and decay (does it leave room for the bass? is its pitch in key?), a hat's centroid and length, a clap's body vs. snap, a bass one-shot's octave and sustain. Then test the finalists **in context**: point the track at each in turn and compare a zoomed `eval`/`capture` of the same bars. Log every candidate in `samples/manifest.json` — used or rejected, with the reason.
- **Loops and vocals.** `transcribe`, `notes` and `width` each candidate before choosing; a loop that is late, flat or in the wrong key costs more to fix than to replace.
- **Instruments and presets.** `browse "sounds/<category>"` lists Live's presets, `browse plugins` the plug-ins, `serum list/show` reads Serum patches. Try several for each synth part: load each (`instrument="<name>"`), `capture --bars ... --tracks <that track>`, and compare spectrum, level and width.
- **Parts.** Write two or three genuinely different basslines / hooks / hat grooves as separate variables, swap them into the same section, and compare — score them against the vocal's syllables and notes, kick collisions, register, density. Keep the winner, note what the others taught you, delete the losers from `song.py` once the log has them.
- **Arrangement and mix.** Change one thing at a time, capture the affected bars, compare numbers.

**Candidates are `option()` choices.** Do not copy `song.py`, comment blocks in and out, or script your own build-push-capture loops: name the thing you are unsure about and let `ab` run the candidates.

```python
from rick_rubin import option
HAT_GHOST = option("hatghost", 60)          # the default is the song; a switched value takes the default's type, so give numbers as numbers (6.0, not "6")
BASS = option("bass", "muted")              # if BASS == "reese": ... elif BASS == "organ": ...
```

```
rick-rubin ab <dir> hatghost=35 hatghost=80 --bars 81-84 --tracks Hats --hits     # offline, seconds
rick-rubin ab <dir> bass=reese bass=organ wide:tops=pan,verb=short --bars 81-96 --live   # pushed to Live and recorded, one by one
```

`ab` prints one column per candidate (the song as it stands first, then each change against it): loudness, peak, crest, energy per band, side % overall / above 4 kHz / below 150 Hz, mono loss, transient contrast, clipped samples; `--hits` adds the per-step levels, `--reference` puts every candidate against the reference tracks (movement, repeats and texture changes are how arrangement candidates differ — plain loudness will not show a layer swapped for another). Files land in `ab/<label>.wav` for `reference compare`, `spectrum`, `width --png`. After a `--live` run Live holds the song as it stands again. Keep a winner by making it the option's default; `score.md` lists every option and its value. `--set name=value` in front of any command (`rick-rubin --set bass=reese capture <dir> --bars 81-96`) runs just that command with the choice switched.

**Did the groove survive?** `hits` prints the peak level of every 16th step of a soloed track, bar by bar, with the velocities you wrote underneath — from the preview, a file, or Live (`--live`). Simpler's velocity curve is steep: accents and ghosts that look 40 velocity steps apart can come out 25 dB apart, and a ghost more than ~18 dB under the accent is gone in a mix. Read `hits --live` once for every velocity-driven part.

Stop exploring a question when one option is clearly right for this track and you can say why — not when the first one passes lint.

## One vocabulary for how things sound

Every sample you import and every Serum preset in the index is measured the same way and described with the same words, so you can search either by character:

| | words |
|---|---|
| length | `short` (< 0.3 s) · `long` (> 2 s) |
| attack | `snappy` (< 5 ms) · `soft-attack` (30–120 ms) · `slow-attack` (> 120 ms) |
| decay | `tight` (< 120 ms) · `ringing` (> 600 ms) · `sustained` |
| brightness | `dark` · `warm` · `bright` · `airy` (spectral centroid under 400 Hz / to 1.2 k / to 4 k / above) |
| low end | `subby` (> 35% below 60 Hz) · `bassy` (> 60% below 200 Hz) · `no-low-end` |
| width | `mono` · `wide` · `very-wide` · `wide-low-end` |
| pitch | `pitched` · `unpitched` · `melodic` |
| dynamics | `punchy` (crest > 14 dB) · `dense` (crest < 8 dB) |

- **Samples.** `rick-rubin sample ...` prints the measured row and character on import and records it in `samples/manifest.json` (`analysis`); anything dropped into `samples/raw/` is measured the first time you run `rick-rubin samples <dir>`. Search and sort the whole project library: `samples <dir> snappy dark`, `samples <dir> --sort sub`, `samples <dir> pitched --not wide`, `samples <dir> --like samples/raw/kick_03.wav`. So when candidates come back from Splice: download, then read their character before you choose.
- **Serum presets.** `rick-rubin serum index` plays every installed preset once — on the key that makes it *sound* around C2, so a bass patch set two octaves down is measured in the same register as everything else — and records the same measurements plus patch facts and the patch's own octave offset; it takes a few minutes the first time and is incremental afterwards. Then `serum search bass subby mono --sort sub`, `serum search pad wide slow-attack --not reverb`, `serum search pluck snappy bright --folder Leads`, `serum search --like "BS Gunman Reese"`. Words can be character, folder, tag, `mono`/`poly`, engine (`wavetable sample granular spectral sub noise`), FX names (`reverb delay distortion chorus ...`) or macro names; `--not WORD ...` excludes. `oct -2` in the label means the patch sounds two octaves under the key you play: write its notes two octaves higher than you want to hear (or reset its oscillator octave with `serum_params`). Six presets do not render within 30 s and are left out.

The words are coarse on purpose: use them to narrow 700 options to 10, then compare those 10 with `audition`, `serum view` and in context.

## Pictures of the things producers look at

Tables are exact and stay the primary view; these pictures are for when a shape says more than numbers. Each command prints the PNG's path — Read it.

- `rick-rubin audition <dir> <files...> --png <name>` — **sample comparer**: every candidate's waveform on one time and level scale (length, punch, decay at a glance), their spectra overlaid, key numbers beside each.
- `rick-rubin spectrum <dir> [files...] [--tracks Kick Bass ...] [--bars A-B] [--mix]` — **spectrum analyzer**: overlaid spectra of files, of soloed tracks (at their real relative level), and/or the mix. Where two curves sit on top of each other they compete; decide EQ moves from it, then make them with Channel EQ / Auto Filter in `effects`.
- `rick-rubin width <dir> [file] [--bars A-B] --png` — **stereo imager**: vectorscope (a vertical line is mono, a round cloud is wide), correlation over time, width by band with wide-low-end and out-of-phase bands in red.
- `rick-rubin serum view "<preset>" --note F1 [--set macro_1=80] --out views/x.png` — **Serum patch panel**: the wavetable frame each oscillator plays, the envelopes, filters/voices/FX chain, macro values and what each moves, and a played note's level, waveform and spectrum.
- `rick-rubin view` — the arrangement: notes, audio clips, automation, the notes a vocal sings in a lane under its waveform, waveform and spectrogram of the mix.

## Zooming in

`view` draws a grid that follows the zoom: bar lines always, quarter-note lines at 16 bars or fewer, lighter eighth-note lines (and `.2 .3 .4` beat labels) at 8 or fewer, faint 16th lines at 4 or fewer. To judge timing — swing, pushed or late hits, a vocal against the grid — zoom to 4 bars or fewer.

`score`, `eval`, `view`, `width` and `capture` all take `--bars A-B`; all but `width` take `--tracks ...` too. Use the zoom whenever a question is local — "is the bass ducking under the kick in the drop?" is `eval --bars 41-48 --tracks Kick Bass` plus `view` on the same slice, not a re-read of the whole song. Bar numbers are always the song's. A solo render is normalised on its own, so compare shapes and ratios inside it, not its level against the full mix.
