---
title: End every track's chain with the same utility plug-ins for filter, volume, gain and pump, and automate those, not the sound
topic: workflow
genres: [progressive house, tech house, bass house, any]
source: RYOS — KSHMR asked me to remix his song.. here's how I did it (https://youtu.be/mvZPg8zv_ig?t=84)
status: untested
---
## What it is
A fixed set of "maintenance" plug-ins that he puts after the creative effects on nearly every track and
group: one filter, one volume control, one gain stage, one sidechain shaper. All arrangement automation
goes to these, so the sound-shaping plug-ins and the mixer fader are never touched by automation.

## When to use it
From the first track of a project. It pays off at arrangement time, when most transitions turn out to be
filter and volume moves.

## How
1. The set (shown on the atmosphere bed, [1:40](https://youtu.be/mvZPg8zv_ig?t=100); explained from
   [1:24](https://youtu.be/mvZPg8zv_ig?t=84)):
   - FabFilter Simplon for filtering;
   - Fruity Balance for volume automation;
   - a gain plug-in for very large moves ("add 60 dB"), often present and unused;
   - Kickstart 2 for sidechain, including automating how much.
2. Order: after reverb, delay and distortion, so filter, fades and pump act on the finished sound (shown on
   the bed and the arp chains, 1:40 and [12:05](https://youtu.be/mvZPg8zv_ig?t=725)).
3. Leave unused ones in place. Walking the chain he skips them: "this looks like maintenance stuff"
   ([11:34](https://youtu.be/mvZPg8zv_ig?t=694), [25:13](https://youtu.be/mvZPg8zv_ig?t=1513)).
4. What gets automated on one supporting track: a high-pass and a low-pass for the build, plus volume
   (said, [18:47](https://youtu.be/mvZPg8zv_ig?t=1127)); a low-pass that opens across the break
   ([7:03](https://youtu.be/mvZPg8zv_ig?t=423)); an EQ made thinner for the intro (18:26).
5. His verdict: filtering can feel mundane but is "critical"; a part that transitions well is usually a
   part with good filter automation (said, [19:08](https://youtu.be/mvZPg8zv_ig?t=1148)).
6. If one strip runs out of slots, route it to a second mixer track for the last steps (said,
   [18:26](https://youtu.be/mvZPg8zv_ig?t=1106)).

## In Rohil's setup
Logic equivalents, in the same order at the end of the strip: AutoFilter (or Channel EQ) for the filter,
the Gain plug-in for both volume automation and big gain moves, Kickstart 2 for the pump:
`rick-rubin logic insert Pad AutoFilter`, `rick-rubin logic insert Pad Gain`, `rick-rubin logic insert Pad
"Kickstart 2" Mix=0.6`. Automating the Gain plug-in instead of the channel fader keeps the fader free for
mixing, which is the point of his Fruity Balance. rick-rubin can insert and set these, and read them back
(`rick-rubin logic params Pad Gain`), but cannot write automation into his project: the curves are drawn in
Logic. Save the three as a channel-strip setting by hand to reuse. In a `song.py` this is unnecessary:
sections are separate tracks.

## How to check it
`rick-rubin logic inspect`: every sustained track ends with the same three inserts in the same order.
After automating, bounce a transition (`rick-rubin logic bounce t.wav --bars A-B --tracks Pad`) and look at
`rick-rubin spectrum` for its first and last bar: the filter move should be visible as lost or gained top.

## Why it works
Separating "what the sound is" from "what the arrangement does to it" means a transition can be changed
without altering the tone, and every track is automated the same way, so nothing has to be remembered.
