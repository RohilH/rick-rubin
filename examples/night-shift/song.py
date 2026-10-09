"""Night Shift — 126 BPM, F minor. A simple house track with a tech house bassline, written for the Logic Pro
render target (`rick-rubin --daw logic push examples/night-shift`).

Shape: a drums-led 16-bar intro, an 8-bar build, a 16-bar drop where the bassline arrives, a 16-bar breakdown
on the pad, a second build with a kick roll, a bigger second drop, a 16-bar outro that strips back to the
drums. 96 bars, about three minutes.

Every note here is written out by hand; see project.md for what was tried and why.
"""
from rick_rubin import Song

song = Song("Night Shift", bpm=126, key="F minor", swing=56)

# ---------------------------------------------------------------- tracks
# Drums: one Logic Drum Synth per voice, each on its own track so the mixer, sends and automation can treat
# them apart, as a house producer would. Drum Synth is a single-voice analogue-style drum: its Sound Category
# and Sound Model pick the voice, Decay / Tone / Pitch shape it (names as Logic's edit view shows them).
kick = song.add_track("Kick", "kick", volume_db=-9, instrument="Drum Synth",
                      instrument_params={"Sound Category": "Kicks", "Sound Model": "Punch Kick", "Decay": 42, "Tone": 20})
clap = song.add_track("Clap", "clap", volume_db=-7, sends={"A": -16}, instrument="Drum Synth",
                      instrument_params={"Sound Category": "Snares and Claps", "Sound Model": "Human Clap", "Decay": 40})
hats = song.add_track("Hats", "hat", volume_db=-8, pan=0.15, swing=True, instrument="Drum Synth",
                      instrument_params={"Sound Category": "Hats and Cymbals", "Sound Model": "Sharp Hat", "Decay": 18})
ohat = song.add_track("Open Hat", "openhat", volume_db=-11, pan=-0.1, swing=True, instrument="Drum Synth",
                      instrument_params={"Sound Category": "Hats and Cymbals", "Sound Model": "Smooth", "Decay": 55})
rim = song.add_track("Rim", "perc", volume_db=-10, pan=-0.3, swing=True, sends={"A": -20}, instrument="Drum Synth",
                     instrument_params={"Sound Category": "Percussion", "Decay": 25})
shaker = song.add_track("Shaker", "shaker", volume_db=-16, pan=0.3, swing=True, instrument="Drum Synth",
                        instrument_params={"Sound Category": "Hats and Cymbals", "Sound Model": "Sharp Hat", "Decay": 10, "Tone": 70})
# Bass: the role's default Logic patch (a synth bass) ducked against the kick — the tech house pump.
bass = song.add_track("Bass", "bass", volume_db=-7, sidechain=True,
                      effects=[{"device": "Channel EQ"}])
# Stab: Retro Synth's own voice, short; one compressor keyed from the kick does both the glue and the pump.
stab = song.add_track("Stab", "stab", instrument="Retro Synth", volume_db=-3, pan=-0.1, sends={"A": -12},
                      effects=[{"device": "Compressor", "sidechain": "Kick",
                                "params": {"Threshold": -18, "Ratio": 3, "Attack": 10, "Release": 90, "Make Up": 6, "Auto Gain": "Off"}}])
# Pad: the role's default pad, wide and far back.
pad = song.add_track("Pad", "pad", volume_db=0, sends={"A": -9}, sidechain=True)

song.add_return("A", [{"device": "ChromaVerb", "params": {"Dry": 0, "Wet": 100, "Decay": 1800}}])
song.master_effects = [{"device": "Limiter", "params": {"Gain": 3}}]

# ---------------------------------------------------------------- drums
four = song.pattern("four", kick, "x...x...x...x...")
four_gap = song.pattern("four_gap", kick, "x...x...x.......", desc="the roll's silent last beat before a drop")
roll = song.pattern("roll", kick, "x...x...x.x.x.x.|x.x.x.x.xxxxxxxx", desc="2-bar kick roll into the drop")
roll_gap = roll.variant("roll_gap", bars={2: "x.x.x.x.xxxx...."}, desc="roll, then a beat of air")

clap2 = song.pattern("clap2", clap, "....x.......x...")
clap_fill = song.pattern("clap_fill", clap, "....x.......x.xx", desc="a flam into the next phrase")

offs = song.pattern("offs", hats, "..x...x...x...x.", desc="offbeat 8ths")
offs_ghost = song.pattern("offs_ghost", hats, "..x.g.x...x.g.x.", desc="offbeats with 16th ghosts — the shuffle")
offs_busy = song.pattern("offs_busy", hats, "g.x.g.x.g.x.g.xg", desc="drop hats: ghosts on every beat, a pickup at the end")

oh_24 = song.pattern("oh_24", ohat, "......o.......o.", desc="open hat on the and of 2 and 4")
oh_every = song.pattern("oh_every", ohat, "..o...o...o...o.", desc="every offbeat, quieter — the breakdown's air")

rim_a = song.pattern("rim_a", rim, "...x..x....x..x.", pitch=37, desc="rimshot push: e-of-1, a-of-2, e-of-3, a-of-4")
rim_b = rim_a.variant("rim_b", add={1: "2.1 D1 0.25 v60"}, desc="plus a soft one on the 2")

shk = song.pattern("shk", shaker, "xoxoxoxoxoxoxoxo", pitch=70, desc="16ths, loud-soft")

# ---------------------------------------------------------------- bass (F minor: F G Ab Bb C Db Eb)
# Tech house: the kick owns the downbeats, the bass owns the 16ths between them. Root F1 with octave pops and
# the b7 / b3 as passing notes. Two bars, then a two-bar answer that climbs to C2 and falls back.
line = song.pattern("line", bass, [
    "1.3 F1 0.2 v112; 1.4 F1 0.15 v78; 2.2 F1 0.2 v104; 2.3 F2 0.15 v88; 3.3 F1 0.2 v112; 3.4 Eb1 0.15 v84; 4.2 F1 0.2 v104; 4.4 Ab1 0.15 v92",
    "1.3 F1 0.2 v112; 1.4 F1 0.15 v78; 2.2 F1 0.2 v104; 2.3 F2 0.15 v88; 3.3 F1 0.2 v112; 3.4 Eb1 0.15 v84; 4.2 F1 0.2 v104; 4.3 F2 0.15 v86; 4.4 C2 0.15 v96",
], desc="the tech house line: offbeat 16ths, octave pops, b7 and b3 passing notes")
line_m = line.variant("line_m", mono=True)
line_up = line.variant("line_up", bars={
    2: "1.3 F1 0.2 v112; 1.4 F1 0.15 v78; 2.2 Ab1 0.2 v104; 2.3 Eb2 0.15 v88; 3.3 Bb1 0.2 v112; 3.4 Bb1 0.15 v84; 4.2 C2 0.2 v108; 4.3 Eb2 0.15 v86; 4.4 C2 0.15 v96",
}, mono=True, desc="second drop: the answer climbs Ab–Bb–C")
line_break = song.pattern("line_break", bass, ["1.3 F1 0.35 v96; 3.3 F1 0.35 v96", "1.3 F1 0.35 v96; 3.3 Eb1 0.35 v90"],
                          desc="build 2: the line reduced to its skeleton, so the full line hits on the drop")

# ---------------------------------------------------------------- stab & pad (chords from F minor; everything above C2)
stab_a = song.pattern("stab_a", stab, [
    "1.3 [Ab2 C3 F3] 0.3 v104; 2.4 [Ab2 C3 F3] 0.25 v88; 3.3 [G2 Bb2 Eb3] 0.3 v104; 4.2 [Ab2 Db3 F3] 0.25 v92",
    "1.3 [Ab2 C3 F3] 0.3 v104; 2.4 [Ab2 C3 F3] 0.25 v88; 3.3 [G2 Bb2 Eb3] 0.3 v104; 4.4 [Bb2 Db3 F3] 0.25 v96",
], desc="Fm, Eb (1st inv), Db/F, Bbm stabs on the offbeats, answering the bass")
stab_sparse = stab_a.variant("stab_sparse", drop=lambda n: n.start % 4 > 2.0, desc="only the first two stabs per bar — the build")

pad_chords = song.pattern("pad_chords", pad, [
    "1.1 [F3 Ab3 C4 Eb4] 8",
    "",
    "1.1 [Db3 F3 Ab3 C4] 8",
    "",
], bars=4, desc="Fm7 then Dbmaj7, two bars each")
pad_break = song.pattern("pad_break", pad, [
    "1.1 [F3 Ab3 C4 Eb4] 8", "", "1.1 [Db3 F3 Ab3 C4] 8", "",
    "1.1 [Eb3 G3 Bb3 Db4] 8", "", "1.1 [C3 Eb3 G3 Bb3] 8", "",
], bars=8, desc="the breakdown adds Eb7 and Cm7 so the 16 bars move")

# ---------------------------------------------------------------- sections
intro = song.add_section("intro", 16, kind="intro", energy=3, desc="drums-led: kick and offbeat hats, clap from bar 9, rim from bar 13",
                         parts={kick: four, hats: offs, clap: clap2.at(9), rim: rim_a.at(13)},
                         fills={clap: clap_fill.every(8)})
build1 = song.add_section("build1", 8, kind="build", energy=5, desc="pad and open hat arrive; the kick rolls into the drop",
                          parts={kick: [four.at(1, 6), roll_gap.at(7, 8)], hats: offs_ghost, clap: clap2, ohat: oh_24, rim: rim_b, pad: pad_chords},
                          automation={pad: {"volume": [0.25, 1.0]}})
drop1 = song.add_section("drop1", 16, kind="drop", energy=8, desc="the bassline arrives with the stabs",
                         parts={kick: four, hats: offs_busy, clap: clap2, ohat: oh_24, rim: rim_b, shaker: shk, bass: line_m, stab: stab_a},
                         fills={clap: clap_fill.every(8), kick: four_gap})
breakdown = song.add_section("breakdown", 16, kind="breakdown", energy=4, desc="no kick: pad chords move, stabs thin out, hats and open hat keep time",
                             parts={hats: offs, ohat: oh_every, pad: pad_break, stab: stab_sparse.at(9)},
                             automation={pad: {"volume": [0.6, 1.0]}})
build2 = song.add_section("build2", 8, kind="build", energy=6, desc="kick back, bass skeleton, clap flams, roll with a beat of air",
                          parts={kick: [four.at(1, 6), roll_gap.at(7, 8)], hats: offs_ghost, clap: clap2, rim: rim_b, bass: line_break, pad: pad_chords, stab: stab_sparse},
                          fills={clap: clap_fill.every(4)},
                          automation={pad: {"volume": [1.0, 0.5]}})
drop2 = song.add_section("drop2", 16, kind="drop", energy=9, desc="everything, the climbing bass answer in the second half",
                         parts={kick: four, hats: offs_busy, clap: clap2, ohat: oh_24, rim: rim_b, shaker: shk,
                                bass: [line_m.at(1, 8), line_up.at(9, 16)], stab: stab_a, pad: pad_chords},
                         fills={clap: clap_fill.every(8), kick: four_gap})
outro = song.add_section("outro", 16, kind="outro", energy=3, desc="drums-led again: hats and rim leave, kick and clap to the end",
                         parts={kick: four, hats: offs.at(1, 8), clap: clap2, rim: rim_a.at(1, 8), ohat: oh_24.at(1, 4)})
song.arrange(intro, build1, drop1, breakdown, build2, drop2, outro)
