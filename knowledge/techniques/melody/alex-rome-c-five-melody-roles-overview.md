---
title: Five melody roles (inline, pulse, accent, bass, lead) and how to tell which one a section needs
topic: melody
genres: [progressive house, tech house, bass house, any]
source: Alex Rome — 5 Melody Styles Every Hit Song Uses (https://youtu.be/cjyEdyEWXbQ?t=0)
status: untested
---
## What it is
A vocabulary for the melodic content of a section, sorted by job. The names are Alex Rome's own. It is a way to decide
what to write, not a set of parts: each row points to a card with the method and the reasoning.

## When to use it
At the brief stage, and when a section sounds incomplete: name which roles it already has, then ask which one is
missing. Most thin sections have a driver and no accent, or chords and no driver.

## How
| Role | What it is | Where he hears it | What carries the harmony | Card |
|---|---|---|---|---|
| Inline | a top line with a second line under it, same rhythm | trance, progressive house, piano house, much tech house | the melody itself | [inline](alex-rome-c-inline-melody-top-line-plus-harmony-line.md) |
| Pulse | one note in a repeating rhythm | Afro house, melodic house | chords moving underneath | [pulse](alex-rome-c-pulsing-one-note-melody.md) |
| Accent | sparse, short, washed-out notes in the background | any genre, behind a vocal | nothing; it decorates | [accent](alex-rome-c-accent-melody-behind-the-vocal.md) |
| Bass | the bassline is the tune | tech house | stabs on top, or nothing | [bass](alex-rome-c-bass-melody-root-rhythm-then-resolve.md) |
| Lead | the hook that sits on top of a drop | progressive house, big room, pop | chords and bass below | [lead](alex-rome-c-lead-melody-many-drafts-over-the-drop.md) |

Reading it (the first three points are his, the rest ours, inferred):
1. Inline, pulse, bass and lead are foreground drivers; a section normally has one in charge (said by example
   throughout).
2. Accent is the only pure background role and combines with any driver ([9:04](https://youtu.be/cjyEdyEWXbQ?t=544)).
3. The less the driver moves, the more freedom the chords have: a pulse accepts almost any progression
   ([7:35](https://youtu.be/cjyEdyEWXbQ?t=455)); a busy lead needs a plain one.
4. For Rohil's genres: tech house, bass melody plus accent; bass house, bass melody plus a short lead hook;
   progressive house, inline or lead in the drop, pulse or accent in the break.
5. Two drivers at once fight. If a second is wanted, stage them in time (break: inline; drop: lead).

## In Rohil's setup
Use the table when writing the brief for a `song.py` track: state per section which role drives and which accents,
then write each part by its card. In an open Logic project, `rick-rubin logic inspect` gives the track list; label
each melodic track with a role, and a section with no driver or no accent is the first thing to raise with him.

## How to check it
`rick-rubin score <dir> --bars <section>` shows what plays where: one track should hold the densest mid or high line
(the driver), and any second melodic track should be sparser and quieter. `reference compare` movement and density
rows show whether the section is as busy as the references.

## Why it works
Listeners follow one foreground line at a time; giving every other melodic part a supporting job stops parts competing
for that one slot (inferred).
