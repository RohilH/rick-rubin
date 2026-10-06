"""{title} — {bpm} BPM, {key}.

The whole song lives in this file; every other command rebuilds from it.
Notation and API: SKILL.md, "Writing a song". Nothing here is pre-written on purpose.
"""
from ableton_use import Song

song = Song("{title}", bpm={bpm}, key="{key}", swing=50)

# tracks    kick = song.add_track("Kick", "kick", sample="samples/kick.wav", volume_db=-7)
# patterns  four = song.pattern("four", kick, "x...x...x...x...")
# sections  intro = song.add_section("intro", 8, energy=3, parts={{kick: four}})
