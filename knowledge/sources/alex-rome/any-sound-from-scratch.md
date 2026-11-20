---
creator: Alex Rome
title: How To Make Any Sound From Scratch (escape the preset trap)
url: https://youtu.be/p1-WmITJqBk
length: 0:24:04
published: 2025-05-31
digested: 2026-11-20
genres: [any, progressive house, bass house]
---
## What it is about
A three-step plan for learning one subtractive synth well enough to stop depending on presets, shown in Serum 2
inside Logic Pro at 123 BPM. Step one is the signal path (oscillator, filter, amp envelope). Step two is sounds
shaped only by the amp envelope: pads, plucks, an arp, and four kinds of bass. Step three is modulation: an envelope
or LFO turning a knob for you, with the filter-envelope pluck as the one sound he says everyone should learn. Every
patch starts from init and uses one oscillator, so the settings are few and all on screen.

## The main ideas
1. **Three blocks, in signal order.** The oscillator makes a raw wave and sets the timbre, the filter takes
   harmonics away, envelopes and LFOs shape it over time ([0:53](https://youtu.be/p1-WmITJqBk?t=53)).
2. **The wave's edges are its brightness.** Sine has no edges and one narrow band; triangle is a sine with corners;
   square and saw are full of harmonics ([2:25](https://youtu.be/p1-WmITJqBk?t=145)).
3. **Unison is width.** One voice shows as a thin line on a stereo meter; ten voices fill it. Voices multiply per
   note: three notes at unison 10 is thirty saws ([3:32](https://youtu.be/p1-WmITJqBk?t=212),
   [4:37](https://youtu.be/p1-WmITJqBk?t=277)).
4. **Two families of sound.** Amp-controlled: ENV 1 alone decides the shape (pad, pluck, bass). Modulated: a second
   envelope or an LFO moves the filter, which he hears as warmer ([6:44](https://youtu.be/p1-WmITJqBk?t=404),
   [17:01](https://youtu.be/p1-WmITJqBk?t=1021), [21:45](https://youtu.be/p1-WmITJqBk?t=1305)).
5. **Envelopes turn a knob once, LFOs turn it forever.** Anything you would automate by hand can be assigned
   ([17:22](https://youtu.be/p1-WmITJqBk?t=1042)).
6. **Decay only exists when sustain is down.** Sustain is a level, the others are times
   ([8:58](https://youtu.be/p1-WmITJqBk?t=538)).
7. **Any wave low-passed and played low is a bass.** Which wave decides its character; a pure sine is felt, not
   heard on small speakers, so give it harmonics with distortion ([12:41](https://youtu.be/p1-WmITJqBk?t=761),
   [14:48](https://youtu.be/p1-WmITJqBk?t=888)).
8. **Keep moving between modules, with chords looping and reverb on.** One sound becomes ten by going back to the
   oscillator after shaping the envelope ([10:31](https://youtu.be/p1-WmITJqBk?t=631),
   [8:31](https://youtu.be/p1-WmITJqBk?t=511)).
9. **Design the modulated sound closed, perform it open.** Leave the cutoff low so there is room to automate it up
   through the arrangement ([20:28](https://youtu.be/p1-WmITJqBk?t=1228)).

## Step by step
1. [1:22](https://youtu.be/p1-WmITJqBk?t=82) Init Serum, OSC A only, default saw, chords looping in the piano roll.
2. [1:55](https://youtu.be/p1-WmITJqBk?t=115) Filter 1 on, OSC A routed to it, type MG Low 24 ("tighter"), cutoff
   swept (2770 Hz in the frame at [2:12](https://youtu.be/p1-WmITJqBk?t=132)): the plain saw pad.
3. [2:25](https://youtu.be/p1-WmITJqBk?t=145) Wave tour in the Default Shapes table: sine, square, triangle, saw.
4. [3:32](https://youtu.be/p1-WmITJqBk?t=212) Unison up, watched on Ozone Imager 2; 10 voices said, 10 to 13 shown.
5. [5:22](https://youtu.be/p1-WmITJqBk?t=322) ENV 1 pluck: shown [6:24](https://youtu.be/p1-WmITJqBk?t=384) attack 1
   ms, decay 275 ms, sustain −inf, release 15 ms, OSC A up an octave, unison 10.
6. [7:06](https://youtu.be/p1-WmITJqBk?t=426) ADSR one knob at a time: slow attack, long release (with
   ValhallaVintageVerb Concert Hall, mix about 30 %, decay 7 s shown [8:55](https://youtu.be/p1-WmITJqBk?t=535)),
   mid sustain with short decay (shown [9:35](https://youtu.be/p1-WmITJqBk?t=575): A 29 ms, D 1.1 s, S −11.8 dB, R
   111 ms), then sustain off with decay 5.35 s (shown [10:15](https://youtu.be/p1-WmITJqBk?t=615)).
7. [10:31](https://youtu.be/p1-WmITJqBk?t=631) Back to the oscillator: sine up an octave, then square, same
   envelope.
8. [11:17](https://youtu.be/p1-WmITJqBk?t=677) Sine, sustain off, short decay, unison 1, Logic's Arpeggiator in
   front (rate 1/8 in the frame at [11:45](https://youtu.be/p1-WmITJqBk?t=705)).
9. [12:19](https://youtu.be/p1-WmITJqBk?t=739) Bass under a melody, notes in the octave below Logic's C1: saw with
   MG Low 24 pulled low; square with cutoff 512 Hz (shown [13:32](https://youtu.be/p1-WmITJqBk?t=812)); saw with
   unison 12 and cutoff 240 Hz, the reese (shown [14:10](https://youtu.be/p1-WmITJqBk?t=850)); sine with the filter
   open, a silent sub (shown [14:32](https://youtu.be/p1-WmITJqBk?t=872)).
10. [15:08](https://youtu.be/p1-WmITJqBk?t=908) Serum FX: Distortion on the sine. Tube, post filter, freq 425, Q 1.9
    shown [15:45](https://youtu.be/p1-WmITJqBk?t=945); then other types, ending on a diode
    ([16:41](https://youtu.be/p1-WmITJqBk?t=1001)).
11. [17:22](https://youtu.be/p1-WmITJqBk?t=1042) LFO 1 dragged onto OSC A level: the knob now moves by itself.
12. [18:03](https://youtu.be/p1-WmITJqBk?t=1083) The filter-envelope pluck: init saw, MG Low 24, cutoff fully closed
    (8 Hz), ENV 2 dragged onto cutoff, ENV 2 sustain off (shown [19:55](https://youtu.be/p1-WmITJqBk?t=1195): A 0.5
    ms, D 1.51 s). Then base cutoff 133 Hz reaching 1667 Hz (shown [20:55](https://youtu.be/p1-WmITJqBk?t=1255)),
    reverb on.
13. [21:18](https://youtu.be/p1-WmITJqBk?t=1278) Variants: square with unison 9 and decay 1.12 s (shown
    [21:35](https://youtu.be/p1-WmITJqBk?t=1295)); ENV 2 with a slower attack and sustain about 59 % plus a 1/4
    delay (shown [22:38](https://youtu.be/p1-WmITJqBk?t=1358)); ENV 2 removed and LFO 1 at 1/8 on the cutoff, then a
    triangle wave (shown [23:10](https://youtu.be/p1-WmITJqBk?t=1390),
    [23:25](https://youtu.be/p1-WmITJqBk?t=1405)).

## Tools the creator uses
- Serum 2 (his pick for power); he also recommends Vital (free) and, for simplicity, a synth the captions write as
  "Silent": most likely Sylenth1, which he uses in his chord video (inferred, not shown here).
- Logic Pro 11: piano roll, Arpeggiator MIDI effect, Channel EQ analyzer.
- iZotope Ozone Imager 2 as a free stereo meter for unison.
- ValhallaVintageVerb on the track while designing; Baby Audio Comeback Kid for the 1/4 delay.
- Free pack in his description: five Serum and five Vital presets of these sounds (not downloaded).
- Test material: chords and a melody from well-known tracks, used only to play the patches.

## Cards made from this video
- [The method: oscillator, filter, envelope, then
  modulation](../../techniques/sound-design/alex-rome-subtractive-method-brief-to-patch.md)
- [Filtered saw pad, widened with unison](../../techniques/sound-design/alex-rome-filtered-saw-pad.md)
- [Amp-envelope pluck and sine arp](../../techniques/sound-design/alex-rome-amp-envelope-pluck.md)
- [Filtered-wave bass: saw or square](../../techniques/sound-design/alex-rome-filtered-wave-bass.md)
- [Reese bass from one saw](../../techniques/sound-design/alex-rome-reese-from-one-saw.md)
- [Sine sub made audible with distortion](../../techniques/sound-design/alex-rome-sine-sub-with-distortion.md)
- [Filter-envelope pluck](../../techniques/sound-design/alex-rome-filter-envelope-pluck.md)
- [Filter swell and LFO movement from the same
  patch](../../techniques/sound-design/alex-rome-filter-swell-and-lfo-movement.md)

## Not covered or unclear
- The ENV 2 to cutoff amount is never stated; only the resulting range is readable (133 Hz to 1667 Hz at
  [20:55](https://youtu.be/p1-WmITJqBk?t=1255)).
- Unison detune and blend stay at Serum's defaults and are never discussed; the count shown drifts between 9 and 13.
- Distortion drive and mix are small knobs with no readout; the diode variant's settings are not visible.
- The LFO shape is edited by hand on screen (a lifted triangle, then a ramp); its points cannot be read.
- Comeback Kid shows 1/4 time; feedback and mix are not readable. The reverb's settings for the pluck are not shown.
- Wavetable synthesis, FM, noise, the second filter and the mod matrix are out of scope for the video.
- The captions' "respace" is the reese bass.
