# Dances and step patterns

## How a dance is described

Each dance is an entry in the `DANCES` table in `wheres-the-one/index.html`:

```js
chacha: { name: 'Cha-cha', counting: '2, 3, 4-&-1', mpm: [30, 32], slots: [
  { c: 2, label: '2', cue: 'Step', click: true, step: true },
  { c: 3, label: '3', cue: 'Step', click: true, step: true },
  { c: 4, label: '4', cue: 'Cha', click: true, step: true, link: true },
  { c: 4, f: 0.5, label: '&', cue: 'Cha', click: true, step: true, link: true },
  { c: 1, label: '1', cue: 'Cha', click: true, step: true }] },
```

| Field | Meaning |
|---|---|
| `name` | Shown in the tempo-fit sentence |
| `counting` | Shown as "Count it as …" |
| `mpm` | Competition tempo `[min, max]` in bars per minute, or `null` |
| `barBeats` | Beats per musical bar for MPM. Leave it out for 4; Samba uses 2 |
| `cycle` | Length of the pattern in beats, when it doesn't fit the 4-beat group. Leave it out for 4; Jive uses 6 |
| `slots` | The moments in each 4-beat group (or cycle), in the order the dancer counts them |

Each slot:

| Field | Meaning |
|---|---|
| `c` | Which count (1–4) the slot is attached to. With `cycle`, its place in the cycle (1–6 for Jive) |
| `f` | Fraction of a beat after that count (0 if left out). Cha-cha `&` = 0.5; Samba and Jive `a` = 0.75 |
| `label` | Text in the slot box and the big count |
| `cue` | Word under it, such as Quick, Slow, Cha, Ball |
| `click` | Plays in the **My steps** click track |
| `step` | A foot moves here: amber dot in the slot box and on the timeline |
| `link` | On the timeline, draw a bar from this step to the next slot (cha-cha-cha, rumba slow, samba 1-a-2) |
| `hold` | Weight stays; drawn as a hollow ring (the rumba 1, the bachata tap) |

Pink follows the music, not the label: a slot is drawn pink when it lands exactly on the music's 1. For 4-beat dances that's always the slot labelled `1`.

From the slots, `rebuildEvents()` makes `S.displayEvents`, with every slot of every bar placed in time. Those events drive:

- **The stage:** the latest event at or before now is the big number and the lit slot box.
- **The step lane** at the bottom of the timeline: dots, links and rings.
- **The click track** in **My steps** mode: slots with `click: true`. A slot on the music's 1 gets the accent click, a fraction slot gets the soft click, and the rest get the normal click.

**Every beat** mode ignores the slots and clicks every beat, accenting the 1.

## Built-in dances

| Key | Button | Count | Slots |
|---|---|---|---|
| `count` | Just count | 1, 2, 3, 4 | One per beat; no steps |
| `rumba` | Rumba | 2, 3, 4-1 | 2 quick, 3 quick, 4 slow (linked to 1), 1 hold |
| `chacha` | Cha-cha | 2, 3, 4-&-1 | 2, 3, then 4, &, 1 linked (the chassé) |
| `samba` | Samba, timing "1 a 2" | 1 a 2, 3 a 4 | 1, a (at 1.75), 2, then 3, a (at 3.75), 4 |
| `sambaVolta` | Samba, timing "1 a 2 a 3 a 4" | 1 a 2 a 3 a 4 | Cross on each beat, side on each a |
| `jive` | Jive | 1, 2, 3 a 4, 3 a 4 | Rock step on 1 and 2, then two chassés. A 6-beat `cycle` |
| `bachata` | Bachata | 1, 2, 3, tap | Steps on 1, 2 and 3, then a tap on 4 that clicks but keeps the weight (`hold`) |

The Samba button picks the variant shown in the **Timing** select (`#sambaVariant`). That select is visible only while Samba is chosen. `S.dance` stores the variant key (`samba` or `sambaVolta`), and the Samba button's pressed state covers both.

## Patterns longer than the bar

The Jive basic takes 6 beats and bars have 4, so the basic drifts across the bars. It repeats exactly every 3 bars (12 beats, two basics):

| Bar | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| 1 | **1** Rock | 2 Step | 3 a | 4 |
| 2 | **3** a | 4 | 1 Rock | 2 Step |
| 3 | **3** a | 4 | 3 a | 4 |

The top row and the pink lines on the timeline are the music's count. The table cells are what the dancer counts. So the stage can show a pink 3 (the music's 1 under the second chassé) and a plain 1 (the rock step on the music's 3).

- **Where the cycle starts:** by default on the first 1 of the song, plus `S.cycleShift` beats. **Start my basic here** (`#cycleStart`, shown only for dances with `cycle`) sets the shift so the dancer's 1 is on the current beat.
- **The shift follows the 1.** It's counted from `S.k`, so moving the 1 moves the basic with it. Anything that rebuilds the beat grid (`retrack`, `shiftHalf`) resets it to 0.
- **Loops:** only a 3-bar loop repeats the basic without a break. Every other loop length restarts it mid-pattern.
- **Bars don't change.** Bar numbers, the 8-bar dots, loops and bar seeking still use `% 4`. Only the placing of slots in `rebuildEvents` uses the cycle.

## Counts and tempos

These match the reference table on the home page.

| Dance | Time | Basic count | Competition MPM | BPM | In Where's the One |
|---|---|---|---|---|---|
| Rumba | 4/4 | 2, 3, 4-1 | 25–27 | 100–108 | Yes |
| Cha-cha | 4/4 | 2, 3, 4-&-1 | 30–32 | 120–128 | Yes |
| Samba | 2/4 | 1 a 2 | 50–52 | 100–104 | Yes |
| Jive | 4/4 | 1, 2, 3 a 4, 3 a 4 | 42–44 | 168–176 | Yes |
| Bachata | 4/4 | 1, 2, 3, tap | 28–32 | 112–128 | Yes |
| Paso Doble | 2/4 | 1, 2 | 60–62 | 120–124 | Not yet |

Tempos follow WDSF competition rules, except Bachata. No official WDSF figure for Bachata was found, so its range comes from the Bachata section of the [IDO rule list of September 2026](https://www.ido-dance.com/files/ido/downloads/2026/2026-September-LIST-of-IDO-rule-changes-after-AGAM-ADMs.pdf), for solo, duo and couples. Many social bachata songs run faster than that. Show and social routines in the other dances often use slower music, such as "Jesus to a Child" for rumba, which the counter reads at about 87 BPM, or 22 MPM.

Three timing facts the tool is built to show:

- The cha-cha **&** is **half** a beat.
- The samba and jive **a** is a **quarter** beat before the next count, later and quicker.
- The jive basic takes **6** beats, so the dancer's 1 meets the music's 1 only every other basic.

## Adding a dance

Example: Paso Doble, which marches one step per beat. Its music is in 2/4, so it needs `barBeats: 2` for MPM.

1. Add an entry to `DANCES`:

   ```js
   paso: { name: 'Paso Doble', counting: '1, 2, 3, 4', mpm: [60, 62], barBeats: 2, slots: [
     { c: 1, label: '1', cue: 'Step', click: true, step: true },
     { c: 2, label: '2', cue: 'Step', click: true, step: true },
     { c: 3, label: '3', cue: 'Step', click: true, step: true },
     { c: 4, label: '4', cue: 'Step', click: true, step: true }] },
   ```

2. Add a button inside `.dance-pick`: `<button type="button" data-dance="paso" aria-pressed="false">Paso Doble</button>`.
3. Optionally, add a card under "How the counts work", and change "Not yet" to "Yes" in the home page table.

You don't need any drawing or click code. For a pattern that doesn't fit 4 beats, add `cycle` and number `c` through the cycle; see `jive`. Keep cues short: at phone width, a slot box with 8 slots is about 31 px wide, and "Replace" didn't fit.

> ⚠️ Note: the tempo prior centers on 110 BPM, so a fast song can be detected at half tempo. A synthesized jive groove at 172 BPM read as 86. When a song reads about half of the chosen dance's range, the tempo-fit sentence says to press **Double tempo**, which gave 172.0 BPM on that groove.
