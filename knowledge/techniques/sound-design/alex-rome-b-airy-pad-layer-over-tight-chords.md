---
title: Loosen stiff pad chords with an airy second layer: unison, slow attack and release, too much reverb, a one-bar swell
topic: sound-design
genres: [progressive house, any]
source: Alex Rome — The Simplest Strategy for Building House Songs (it's like cheating) (https://youtu.be/kSXHTJJ7D34?t=326)
status: untested
---
## What it is
A pair of pads with opposite jobs. The "tight" one is the plain filtered saw that states the chords. The "loose"
one is the same patch made wide, slow and very wet, on its own track, which he calls a traveling pad. The contrast
between them is the effect.

## When to use it
Relaxed sections (intro, verse, breakdown) where held chords sound stiff and "in place". The patch move itself is
step 6 of `sound-design/alex-rome-filtered-saw-pad.md`; this card is about using it as a second layer and making
it breathe.

## How
1. Copy the tight pad to its own track (said, [5:26](https://youtu.be/kSXHTJJ7D34?t=326)).
2. Add unison to the saw: many voices sound looser than one (said,
   [5:46](https://youtu.be/kSXHTJJ7D34?t=346)). In the remix video the drop's airy chords are two oscillators at
   unison 10 and 9 with the cutoff pulled down (shown [5:30](https://youtu.be/bx8X7oiYhCg?t=330)).
3. Lengthen the release a lot, then the attack (said). Shown at [6:00](https://youtu.be/kSXHTJJ7D34?t=360): ENV 1
   release 4.79 s; the attack value is not in the frame.
4. Add "too much" reverb (said, [6:07](https://youtu.be/kSXHTJJ7D34?t=367)).
5. The notes can be loose: he says almost any notes can be scattered across it (said,
   [6:29](https://youtu.be/kSXHTJJ7D34?t=389)).
6. Make it swell: ShaperBox 3's volume shaper, one bar long, a ramp that rises through the bar and falls at its
   end, about half wet (shown [7:00](https://youtu.be/kSXHTJJ7D34?t=420): length 1 bar, mix 53 %, smoothing
   40 %). He calls it a very delicate swell (said, [6:50](https://youtu.be/kSXHTJJ7D34?t=410)).
7. A third colour is possible: a distorted pad made off camera (said,
   [7:10](https://youtu.be/kSXHTJJ7D34?t=430)).
8. When the drums enter halfway through the section he adds a wider layer of the chords too (said,
   [7:50](https://youtu.be/kSXHTJJ7D34?t=470)); that move has its own card,
   `alex-rome-c-narrow-pad-then-wide-layer-on-the-phrase.md`.

## In Rohil's setup
```
rick-rubin serum set init filter_1.on=on "filter_1.type=MG Low 24" filter_1.cutoff_hz=1500 osc_a.unison=9 \
    env_1.attack_ms=400 env_1.release_ms=4790 --save airy-pad --project <dir>
```
Cutoff and attack are our starting guesses; release and unison are from the frames. Reverb: Valhalla Supermassive
as an insert at a high mix. The swell without ShaperBox: Kickstart 2 set to one cycle per bar at about half depth
(`rick-rubin logic insert "Airy Pad" "Kickstart 2" "Loop Length=1.0" Mix=0.5`); what is lost is the rising ramp
shape, since Kickstart's curves are ducking shapes. An LFO on level inside the Serum patch gets closer. Unison
widens the lows, so low-cut this layer and keep the tight pad as the mono anchor.

## How to check it
`rick-rubin width <dir> airy.wav`: side energy well above the tight pad's. `rick-rubin serum describe` on a held
note: slow rise, a tail of several seconds. On a bounce of both layers the tight pad's attacks are still clear
(`rick-rubin hits`). The amount of reverb is for his ears.

## Why it works
The tight layer gives the chord changes a definite start; the loose one fills the time and the sides between
them. Either alone is stiff or vague; together they read as depth.
