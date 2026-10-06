# Sunrise Dub
121 BPM · F dorian · swing 57% · 160 bars · 5:17 · deep / club

## Tracks
- Kick (kick) -3 dB, pan +0.0, inst '909 Core Kit'
- Clap (clap) -8 dB, pan +0.0, inst '909 Core Kit'
- Hats (hat) -13 dB, pan +0.0, inst '909 Core Kit' [swing]
- OpenHat (openhat) -14 dB, pan +0.0, inst '909 Core Kit'
- Perc (perc) -15 dB, pan +0.0, inst '909 Core Kit' [swing]
- Bass (bass) -6 dB, pan +0.0, inst 'Operator' [sidechain, swing]
- Chords (chords) -11 dB, pan +0.0, inst 'Electric Piano' [sidechain]
- Pad (pad) -15 dB, pan +0.0, inst 'Wavetable' [sidechain]
- Lead (lead) -12 dB, pan +0.0, inst 'Wavetable' [sidechain]
- Crash (crash) -16 dB, pan +0.0, inst '909 Core Kit'
- Riser (riser) -18 dB, pan +0.0, inst 'Wavetable'

## Sections
| # | section | kind | bars | time | energy | playing | fills | automation |
|---|---|---|---|---|---|---|---|---|
| 0 | **intro** | intro | 1-16 (16) | 0:00 | 2 | Kick, Hats[9-16], Perc[9-16] | Kick=kick_gap | — |
| 1 | **groove** | groove | 17-32 (16) | 0:31 | 4 | Kick, Clap, Hats, OpenHat, Perc, Bass[9-16], Crash[1-1] | Clap=clap_fill/8, Kick=kick_gap | Bass.filter 0.3→0.65 |
| 2 | **main** | groove | 33-48 (16) | 1:03 | 6 | Kick, Clap, Hats, OpenHat, Perc, Bass, Chords, Crash[1-1] | Clap=clap_fill/8, Kick=kick_gap | Chords.filter 0.45→0.8 |
| 3 | **breakdown** | breakdown | 49-64 (16) | 1:35 | 3 | Pad, Chords[1-8], Lead[9-16], Hats[9-16], Crash[1-1] | — | Pad.filter 0.35→0.55, Chords.filter 0.3→0.45 |
| 4 | **build** | build | 65-72 (8) | 2:06 | 6 | Pad, Lead, Hats, Riser | Clap=roll | Pad.filter 0.55→1.0, Lead.filter 0.5→1.0, Riser.filter 0.05→1.0 |
| 5 | **drop** | drop | 73-104 (32) | 2:22 | 9 | Kick, Clap, Hats, OpenHat, Perc=perc_drop, Bass, Chords, Lead, Crash[1-1] | Clap=clap_fill/8, Kick=kick_gap/16 | — |
| 6 | **bridge** | bridge | 105-112 (8) | 3:26 | 6 | Kick, Clap, Hats, Perc, Bass, Pad | Kick=kick_gap | — |
| 7 | **drop2** | drop | 113-144 (32) | 3:42 | 10 | Kick, Clap, Hats, OpenHat, Perc=perc_drop, Bass=bass_roll, Chords, Pad, Lead+12st, Crash[1-1] | Clap=clap_fill/8, Kick=kick_gap/16 | — |
| 8 | **outro** | outro | 145-160 (16) | 4:45 | 3 | Kick, Hats, Perc, Clap[1-8], Bass[1-8], OpenHat[1-8] | — | Bass.filter 0.65→0.2 |

## Energy curve (intended)
```
intro:▃2 groove:▄4 main:▆6 breakdown:▃3 build:▆6 drop:█9 bridge:▆6 drop2:█10 outro:▃3
```

## Arrangement map (1 char = 4 bars; █ plays, ▒ fill only)
```
         intrgroomainbreabudrop    brdrop2   outr
Kick     ████████████······██████████████████████
Clap     ····████████·····▒████████████████████··
Hats     ··██████████··██████████████████████████
OpenHat  ····████████······████████··██████████··
Perc     ··██████████······██████████████████████
Bass     ······██████······████████████████████··
Chords   ········██████····████████··████████····
Pad      ············██████········██████████····
Lead     ··············████████████··████████····
Crash    ····█···█···█·····█·········█···········
Riser    ················██······················
```

## Patterns  (events: beat.sixteenth note length-in-beats [vVEL if not 100]; '—' = no new notes, held notes ring on)
### kick  (1 bar, Kick) — four on the floor
  pitch C1  steps (16ths, | = bar): x...x...x...x...

### kick_gap  (1 bar, Kick) — kick drops out on beat 4 to set up the next phrase
  pitch C1  steps (16ths, | = bar): x...x...x.......

### clap  (1 bar, Clap) — backbeat on 2 & 4
  pitch D#1  steps (16ths, | = bar): ....x.......x...

### clap_fill  (1 bar, Clap) — pickup into next phrase
  pitch D#1  steps (16ths, | = bar): ....x.......x.gx

### roll  (4 bars, Clap) — 4-bar accelerating roll, last beat silent
  pitch D#1  steps (16ths, | = bar): g...g...g...g...|o.o.o.o.o.o.o.o.|oooooooxxxxxxxxx|xxxxxxxxxxxx....

### hats  (2 bars, Hats) — shuffle 16ths
  pitch F#1  steps (16ths, | = bar): g.xog.xog.xog.xo|g.xog.xog.xog.xo

### openhat  (1 bar, OpenHat) — off-beat open hat
  pitch A#1  steps (16ths, | = bar): ..x...x...x...x.

### perc  (1 bar, Perc) — syncopated rim/perc
  pitch D2  steps (16ths, | = bar): ...x..x....x..x.

### crash  (1 bar, Crash) — crash on the downbeat
  pitch C#2  steps (16ths, | = bar): X...............

### bass  (8 bars, Bass) — syncopated bass, roots of [1, 7, 4, 5]
  bar 1: 1.3 F0 0.75 v104; 2.4 F0 0.5 v104; 3.3 C1 0.5 v104; 4.3 F1 0.25 v104
  bar 2: 1.4 F0 0.5 v104; 2.3 F0 0.25 v104; 3.3 F0 0.75 v104; 4.4 D1 0.2 v96
  bar 3: 1.3 D#1 1 v104; 3.2 D#1 0.5 v104; 4.1 A#1 0.25 v104; 4.3 D#1 0.5 v104
  bar 4: 1.4 D#1 0.5 v104; 2.3 D#1 0.25 v104; 3.3 D#1 0.75 v104; 4.4 A#0 0.2 v96
  bar 5: 1.3 A#0 1 v104; 3.2 A#0 0.5 v104; 4.1 F1 0.25 v104; 4.3 A#0 0.5 v104
  bar 6: 1.4 A#0 0.5 v104; 2.3 A#0 0.25 v104; 3.3 A#0 0.75 v104; 4.4 A#1 0.25 v104
  bar 7: 1.3 C1 1 v104; 3.2 C1 0.5 v104; 4.1 G1 0.25 v104; 4.3 C1 0.5 v104
  bar 8: 1.3 C1 0.75 v104; 2.4 C1 0.5 v104; 3.3 G1 0.5 v104; 4.4 F0 0.2 v96

### chords  (8 bars, Chords) — held chords
  chords/bar: Fm9/D# | Fm9/D# | D#maj9/D | D#maj9/D | A#9/D | A#9/D | Cm9/D# | Cm9/D#
  bar 1: 1.1 Fm9/D#[D#3 F3 G3 G#3 C4] 2.75 v88; 4.1 Fm9/D#[D#3 F3 G3 G#3 C4] 0.75 v88
  bar 2: 1.1 Fm9/D#[D#3 F3 G3 G#3 C4] 2.75 v88; 4.1 Fm9/D#[D#3 F3 G3 G#3 C4] 0.75 v88
  bar 3: 1.1 D#maj9/D[D3 D#3 F3 G3 A#3] 2.75 v88; 4.1 D#maj9/D[D3 D#3 F3 G3 A#3] 0.75 v88
  bar 4: 1.1 D#maj9/D[D3 D#3 F3 G3 A#3] 2.75 v88; 4.1 D#maj9/D[D3 D#3 F3 G3 A#3] 0.75 v88
  bar 5: 1.1 A#9/D[D3 F3 G#3 A#3 C4] 2.75 v88; 4.1 A#9/D[D3 F3 G#3 A#3 C4] 0.75 v88
  bar 6: 1.1 A#9/D[D3 F3 G#3 A#3 C4] 2.75 v88; 4.1 A#9/D[D3 F3 G#3 A#3 C4] 0.75 v88
  bar 7: 1.1 Cm9/D#[D#3 G3 A#3 C4 D4] 2.75 v88; 4.1 Cm9/D#[D#3 G3 A#3 C4 D4] 0.75 v88
  bar 8: 1.1 Cm9/D#[D#3 G3 A#3 C4 D4] 2.75 v88; 4.1 Cm9/D#[D#3 G3 A#3 C4 D4] 0.75 v88

### pad  (8 bars, Pad) — held pad, one chord per change
  chords/bar: Fm9/D# | - | D#maj9/D | - | A#9/D | - | Cm9/D | -
  bar 1: 1.1 Fm9/D#[D#3 F3 G3 G#3 C4] 8 v70
  bar 2: —
  bar 3: 1.1 D#maj9/D[D3 D#3 F3 G3 A#3] 8 v70
  bar 4: —
  bar 5: 1.1 A#9/D[D3 F3 G#3 A#3 C4] 8 v70
  bar 6: —
  bar 7: 1.1 Cm9/D[D3 D#3 G3 A#3 C4] 8 v70
  bar 8: —

### lead  (8 bars, Lead) — 2-bar call/response hook on chord tones
  bar 1: 1.1 F4 0.4; 1.3 C5 0.4 v90; 2.3 C5 0.4 v90; 3.1 F4 0.4; 3.4 C5 0.25 v90; 4.3 C5 0.4 v90
  bar 2: 1.1 F4 0.4; 1.3 C5 0.4 v90; 2.3 C5 0.4 v90; 3.1 F4 0.4; 3.4 C5 0.25 v90; 4.3 F4 0.4 v90
  bar 3: 1.1 D#4 0.4; 1.3 A#4 0.4 v90; 2.3 A#4 0.4 v90; 3.1 D#4 0.4; 3.4 A#4 0.25 v90; 4.3 A#4 0.4 v90
  bar 4: 1.1 D#4 0.4; 1.3 A#4 0.4 v90; 2.3 A#4 0.4 v90; 3.1 D#4 0.4; 3.4 A#4 0.25 v90; 4.3 D#4 0.4 v90
  bar 5: 1.1 A#4 0.4; 1.3 F4 0.4 v90; 2.3 F4 0.4 v90; 3.1 A#4 0.4; 3.4 F4 0.25 v90; 4.3 F4 0.4 v90
  bar 6: 1.1 A#4 0.4; 1.3 F4 0.4 v90; 2.3 F4 0.4 v90; 3.1 A#4 0.4; 3.4 F4 0.25 v90; 4.3 A#4 0.4 v90
  bar 7: 1.1 C5 0.4; 1.3 G4 0.4 v90; 2.3 G4 0.4 v90; 3.1 C5 0.4; 3.4 G4 0.25 v90; 4.3 G4 0.4 v90
  bar 8: 1.1 C5 0.4; 1.3 G4 0.4 v90; 2.3 G4 0.4 v90; 3.1 C5 0.4; 3.4 G4 0.25 v90; 4.3 C5 0.4 v90

### riser  (8 bars, Riser) — 8-bar sustained riser; open its filter
  bar 1: 1.1 F3 32 v90
  bars 2-8: —

### bass_roll  (4 bars, Bass) — rolling bass, roots of [1, 7, 4, 5]
  bar 1: 1.2 F0 0.2 v80; 1.3 F0 0.2 v110; 1.4 F0 0.2 v88; 2.2 F0 0.2 v80; 2.3 F0 0.2 v110; 2.4 F0 0.2 v88; 3.2 F0 0.2 v80; 3.3 F0 0.2 v110; 3.4 F0 0.2 v88; 4.2 F0 0.2 v80; 4.3 F1 0.2 v110; 4.4 F0 0.2 v88
  bar 2: 1.2 D#1 0.2 v80; 1.3 D#1 0.2 v110; 1.4 D#1 0.2 v88; 2.2 D#1 0.2 v80; 2.3 D#1 0.2 v110; 2.4 D#1 0.2 v88; 3.2 D#1 0.2 v80; 3.3 D#1 0.2 v110; 3.4 D#1 0.2 v88; 4.2 D#1 0.2 v80; 4.3 D#2 0.2 v110; 4.4 D#1 0.2 v88
  bar 3: 1.2 A#0 0.2 v80; 1.3 A#0 0.2 v110; 1.4 A#0 0.2 v88; 2.2 A#0 0.2 v80; 2.3 A#0 0.2 v110; 2.4 A#0 0.2 v88; 3.2 A#0 0.2 v80; 3.3 A#0 0.2 v110; 3.4 A#0 0.2 v88; 4.2 A#0 0.2 v80; 4.3 A#1 0.2 v110; 4.4 A#0 0.2 v88
  bar 4: 1.2 C1 0.2 v80; 1.3 C1 0.2 v110; 1.4 C1 0.2 v88; 2.2 C1 0.2 v80; 2.3 C1 0.2 v110; 2.4 C1 0.2 v88; 3.2 C1 0.2 v80; 3.3 C1 0.2 v110; 3.4 C1 0.2 v88; 4.2 C1 0.2 v80; 4.3 C2 0.2 v110; 4.4 C1 0.2 v88

### perc_drop  (2 bars, Perc)
  pitch D2  steps (16ths, | = bar): ...x..x...x..x.x|...x..x....x.ox.
