# Night Shift — project memory

## Brief

A simple house track with a tech house bassline, as the example song of the Logic Pro render target.
126 BPM, F minor, about three minutes, DJ-friendly edges. Rendered with `rick-rubin --daw logic push`.

## Session 1 — 2026-10-09

**Strategy:** keep the parts few and let the arrangement do the work — kick, clap, two hats, rim and shaker on
their own tracks; one bass; one stab; one pad. Intro 16 / build 8 / drop 16 / breakdown 16 / build 8 / drop 16 /
outro 16. The bassline is the hook: offbeat 16ths around F1 with octave pops and the b7/b3 as passing notes,
answered in the second drop by a climb Ab–Bb–C.

**Decisions:**
- Drums on Logic's Drum Synth kit (the role's default on channel 10): a synthesised kit sits closer to tech house
  than the acoustic SoCal kit Logic picks for program 0. Rim on D1 (37), shaker on A#3 (70) — GM positions the kit
  honours.
- Bass: Logic's role patch (Pulse Bass, an ES2 patch) rather than a named instrument — it has the pulse-width
  movement the line wants without any sound design through the bridge. Sidechained from the kick.
- Stab on Retro Synth loaded bare (its default voice), compressed 3:1 so the offbeat stabs sit at one level;
  chords voiced above C2 (Ab2 C3 F3 and neighbours) so nothing but kick and bass lives below.
- Pad on the role's default patch, sent to the one ChromaVerb return along with clap and stab; volume rides in the
  builds (written in Logic with `--automation`).
- The breakdown has no kick; the pad's chords move (Fm7, Dbmaj7, Eb7, Cm7) so sixteen bars without drums develop.
- Both drops begin with the roll's silent last beat (`roll_gap`, `four_gap`).

**Rejected:**
- An 8-bar breakdown: too short for the pad to say anything; 16 with the chord movement reads better in the score.
- Hats as straight offbeats throughout: the ghosted and busy variants give the drop its lift; the straight pattern
  is kept for intro and outro.
- Octave pops to Ab2 in the second drop's answer: out of the house bass range (A-rule H5); Eb2 instead.

**Measured (offline preview, `rick-rubin eval`):** PASS, loudness follows the energy curve (r=0.72); drops at
-14.5 LUFS against -16.2 in intro/outro and -21 in the breakdown.

**Outstanding:** judge the sound on Logic's bounce (`--daw logic capture`), not the preview; the stab and pad
patches are Logic's defaults and may want a Library patch once heard.

## Session 2 — 2026-10-09, afternoon

**Measured on Logic's bounce (soloed, drop 1, bars 25-32):** kick -17 LUFS, bass -28, stab -42, pad -54, hats -49. Two
causes: Drum Synth is pitched by the note it receives (key tracking on), so the kick on C1 was a sub-kick and the hats on
F#1 were dull and quiet — the bridge now sends every hit of a single-voice drum instrument on C3; and the offline preview's
levels say nothing about Logic's patches (Retro Synth's and the pad's default voices are quiet). Faders rebalanced on the
Logic bounce, not the preview: kick -9, clap -7, hats -8, open hat -11, rim -10, shaker -16, bass -8, stab -3 with 6 dB of
make-up on its compressor, pad 0, limiter gain +3. Drum Synth voices: Punch Kick, Human Clap, Sharp Hat (hats and shaker,
different decay and tone), Smooth (open hat), a Percussion voice for the rim.

**Bounce of that push:** -23.8 LUFS overall, energy curve r=0.85, but the breakdown fell to -36 LUFS (pad too far back at -20)
and the kick had no sub at all (Drum Synth played at C3). Last round: kick notes on C2, pad -10, bass -12, limiter gain +6.
