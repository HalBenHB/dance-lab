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
| `slots` | The moments in each 4-beat group, in the order the dancer counts them |

Each slot:

| Field | Meaning |
|---|---|
| `c` | Which count (1–4) the slot is attached to |
| `f` | Fraction of a beat after that count (0 if left out). Cha-cha `&` = 0.5; Samba `a` = 0.75 |
| `label` | Text in the slot box and the big count. A label of `'1'` is drawn pink |
| `cue` | Word under it, such as Quick, Slow, Cha, Ball |
| `click` | Plays in the **My steps** click track |
| `step` | A foot moves here: amber dot in the slot box and on the timeline |
| `link` | On the timeline, draw a bar from this step to the next slot (cha-cha-cha, rumba slow, samba 1-a-2) |
| `hold` | Weight stays; drawn as a hollow ring (the rumba 1) |

From the slots, `rebuildEvents()` makes `S.displayEvents`, with every slot of every bar placed in time. Those events drive:

- **The stage:** the latest event at or before now is the big number and the lit slot box.
- **The step lane** at the bottom of the timeline: dots, links and rings.
- **The click track** in **My steps** mode: slots with `click: true`. A slot on 1 gets the accent click, a fraction slot gets the soft click, and the rest get the normal click.

**Every beat** mode ignores the slots and clicks every beat, accenting the 1.

## Built-in dances

| Key | Button | Count | Slots |
|---|---|---|---|
| `count` | Just count | 1, 2, 3, 4 | One per beat; no steps |
| `rumba` | Rumba | 2, 3, 4-1 | 2 quick, 3 quick, 4 slow (linked to 1), 1 hold |
| `chacha` | Cha-cha | 2, 3, 4-&-1 | 2, 3, then 4, &, 1 linked (the chassé) |
| `samba` | Samba, timing "1 a 2" | 1 a 2, 3 a 4 | 1, a (at 1.75), 2, then 3, a (at 3.75), 4 |
| `sambaVolta` | Samba, timing "1 a 2 a 3 a 4" | 1 a 2 a 3 a 4 | Cross on each beat, side on each a |

The Samba button picks the variant shown in the **Timing** select (`#sambaVariant`). That select is visible only while Samba is chosen. `S.dance` stores the variant key (`samba` or `sambaVolta`), and the Samba button's pressed state covers both.

## Counts and tempos

These match the reference table on the home page.

| Dance | Time | Basic count | Competition MPM | BPM | In Where's the One |
|---|---|---|---|---|---|
| Rumba | 4/4 | 2, 3, 4-1 | 25–27 | 100–108 | Yes |
| Cha-cha | 4/4 | 2, 3, 4-&-1 | 30–32 | 120–128 | Yes |
| Samba | 2/4 | 1 a 2 | 50–52 | 100–104 | Yes |
| Jive | 4/4 | 1, 2, 3 a 4, 3 a 4 | 42–44 | 168–176 | Not yet |
| Paso Doble | 2/4 | 1, 2 | 60–62 | 120–124 | Not yet |

Tempos follow WDSF competition rules. Show and social routines often use slower music, such as "Jesus to a Child" for rumba, which the counter reads at about 87 BPM, or 22 MPM.

Two timing facts the tool is built to show:

- The cha-cha **&** is **half** a beat.
- The samba **a** is a **quarter** beat before the next count, later and quicker.

## Adding a dance

Example: Jive, which has a 6-count basic over 1½ bars. The grid shows 4-beat groups, so describe one 4-beat group of the rhythm. For the chassés, "3 a 4" means steps at 3, 3.75 and 4:

1. Add an entry to `DANCES`:

   ```js
   jive: { name: 'Jive', counting: '1, 2, 3 a 4', mpm: [42, 44], slots: [
     { c: 1, label: '1', cue: 'Rock', click: true, step: true },
     { c: 2, label: '2', cue: 'Replace', click: true, step: true },
     { c: 3, label: '3', cue: 'Chassé', click: true, step: true, link: true },
     { c: 3, f: 0.75, label: 'a', cue: 'Close', click: true, step: true, link: true },
     { c: 4, label: '4', cue: 'Chassé', click: true, step: true }] },
   ```

2. Add a button inside `.dance-pick`: `<button type="button" data-dance="jive" aria-pressed="false">Jive</button>`.
3. Optionally, add a card under "How the counts work", and change "Not yet" to "Yes" in the home page table.

You don't need any drawing or click code. If a dance needs a pattern longer than 4 beats (true for the Jive basic), the slot model needs a cycle length. That's an open item in [development.md](development.md).

> ⚠️ Note: the tempo prior centers on 110 BPM. Jive at about 172 BPM may be detected at half tempo (86). Users can fix it with **Double tempo**.
