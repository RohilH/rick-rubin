# Genres: what each does, and which checks apply

Knowledge, not parts to copy. House is the genre the lint and these notes were written for; anything else says so in the song.

## Telling the lint what the song is

The checks default to club house: 118-130 BPM, DJ-friendly intro and outro, drops that follow a build. A song in another genre declares it in `song.py`,
with the reason, and the lint then says what it did not check:

```python
song.meta["lint"] = {"tempo": [85, 100], "off": ["H3-dj-friendly", "H8-energy"], "why": "a hip-hop beat, not a club track"}
```

`tempo` is the expected range; `off` lists rule ids (`rick-rubin check` prints them: H1-tempo, H2-phrasing, H3-dj-friendly, H5-bass, H8-energy, ...). Structure errors cannot be
switched off. This changes what is checked, never what is written. Ask Rohil which genre a track is before switching anything off.

## The genres Rohil makes

Tech house and bass house now, progressive house as the goal. What each consists of, as the creators he follows teach it:
`knowledge/genres/tech-house.md`, `knowledge/genres/bass-house.md`, `knowledge/genres/progressive-house.md`. Read the one for the
track in hand before the notes below, which are upstream's general house notes.

## House

- **Tempo/feel:** deep 118–122 with heavy swing (56–58%); classic/garage-tinged 122–125 (53–55%); tech 124–128, nearly straight (50–53%).
- **Drums:** kick every beat; clap/snare on 2 and 4; open hat on every off-beat 8th; closed hats as swung 16ths with accent/ghost velocities; a syncopated rim/perc for movement. Fills on the last bar of 8-bar phrases. Drop the kick on beat 4 before a new phrase (`kick_gap`).
- **Bass:** off-beat 8ths (classic), rolling 16ths that skip the downbeat (tech), syncopated dub lines with octave pops and approach notes (deep). Roots sit around 40–80 Hz. Sidechain to the kick.
- **Harmony:** minor or dorian. Deep: held min7/min9 voicings, 2 bars per chord. Classic: piano/organ stabs on off-beats, 1 bar per chord. Tech: one chord stab, harmony mostly implied by the bass. Voice-lead and keep chords between ~F2 and G4.
- **Arrangement:** intro 16–32 (drums) → groove (clap, open hat, filtered bass) → main (chords in) → breakdown (drums & bass out; pad + hook) → build (4-bar roll accelerating to 16ths, riser, filters opening, silent last beat) → drop 32 (everything) → bridge 8 (breath) → drop 2 (one new layer or the hook up an octave) → outro 16–32 (strip back to drums).
- **Energy:** something enters or leaves every 8 bars; the breakdown must feel like a valley (≥3 LU quieter in eval) or the drop won't land.
