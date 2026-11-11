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
| `mpm` | Competition tempo `[min, max]` in bars per minute, or `null`. Also decides whether a song is counted at its detected speed, double or half (see below) |
| `barBeats` | Beats per musical bar for MPM. Leave it out for 4; Samba uses 2 |
| `cycle` | Length of the pattern in beats, when it doesn't fit the 4-beat group. Leave it out for 4; Jive uses 6 and Bachata 8 |
| `group` | Which dance this is another way of counting: the key of that dance's main entry. Leave it out on the main entry, which is the default |
| `timing` | Text in the **Timing** select. Leave it out to use `counting` |
| `inTitle` | A pattern that finds the dance's name in a song title, such as `/\bsamba\b/i`, so the page can offer the dance. Main entries only |
| `swing` | `true` when the dance is danced to swung music (Jive), so a swung song can be offered as this dance. Main entries only |
| `slots` | The moments in each 4-beat group (or cycle), in the order the dancer counts them |

Each slot:

| Field | Meaning |
|---|---|
| `c` | Which count (1–4) the slot is attached to. With `cycle`, its place in the cycle (1–6 for the Jive basic) |
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
| `jive` | Jive, the default timing | 1 2 3 a 4 5 a 6 | Rock step on 1 and 2, then two chassés. A 6-beat `cycle` |
| `jive8` | Jive, timing "1 2 3 a 4 5 a 6 7 8" | 1 2 3 a 4 5 a 6 7 8 | The basic plus two steps on 7 and 8. An 8-beat `cycle` |
| `jiveCount8` | Jive, timing "1 2 3 4 5 6 7 8: the music's count" | 1 2 3 4 5 6 7 8 | One count a beat, cues One to Eight, no steps. An 8-beat `cycle`, for counting the music in eights |
| `jiveRepeat` | Jive, timing "1, 2, 3 a 4, 3 a 4" | 1, 2, 3 a 4, 3 a 4 | The basic, with both chassés counted 3 a 4. A 6-beat `cycle` |
| `bachata` | Bachata, the default timing | 1 2 3 4 5 6 7 8 | Steps on 1, 2, 3 and 5, 6, 7, with taps on 4 and 8 that click but keep the weight (`hold`). An 8-beat `cycle` |
| `bachataTap` | Bachata, timing "1, 2, 3, tap" | 1, 2, 3, tap | The same steps counted in one bar |

A dance's button picks the entry shown in the **Timing** select (`#timing`), which lists every entry of that `group`, the main entry first. The select is visible only for dances with more than one entry. `S.dance` stores the entry's key, and the button's pressed state covers the whole group. Going back to a dance keeps the timing you picked for it until the page reloads; after that, the saved dance opens with its saved timing and the others with their defaults.

## Patterns longer than the bar

The Jive basic takes 6 beats and bars have 4, so the basic drifts across the bars. It repeats exactly every 3 bars (12 beats, two basics):

| Bar | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| 1 | **1** Rock | 2 Step | 3 a | 4 |
| 2 | **5** a | 6 | 1 Rock | 2 Step |
| 3 | **3** a | 4 | 5 a | 6 |

The top row and the pink lines on the timeline are the music's count. The table cells are what the dancer counts. So the stage can show a pink 5 or 3 (the music's 1 under a chassé) and a plain 1 (the rock step on the music's 3).

The 8-count patterns, Bachata and Jive with 7 8, fit two bars exactly, so the music's 1 falls on the dancer's 1 and 5 every time.

- **Where the cycle starts:** by default on the first 1 of the song, plus `S.cycleShift` beats. **Start my basic here** (`#cycleStart`, shown only for dances with `cycle`) sets the shift so the dancer's 1 is on the current beat.
- **The shift follows the 1.** It's counted from `S.k`, so moving the 1 moves the basic with it. Anything that rebuilds the beat grid (`retrack`, `shiftHalf`) resets it to 0. It isn't reduced to one cycle, so your start stays on the same beat when you change to a timing of another length.
- **Loops:** the 6-count Jive repeats without a break only on a 3-bar loop. The 8-count patterns repeat on 2, 4 or 8 bars. Every other loop length restarts the pattern mid-way.
- **Bars don't change.** Bar numbers, the 8-bar dots, loops and bar seeking still use `% 4`. Only the placing of slots in `rebuildEvents` uses the cycle.

## The dance sets the speed, and the title can suggest a dance

- **Speed:** a song can usually be counted at two speeds, one twice the other. When you pick a dance, the page counts the song at whichever speed fits that dance's tempo, and says so under the tempo if it doubled or halved it. "Hit the Road Jack" is 86.8 BPM on Bachata and 173.6 on Jive. See [beat-detection.md](beat-detection.md), step 10.
- **Suggestions:** if the song's title names a dance other than the one chosen, and the song's tempo fits that dance, a line under the tempo offers it: "The title says Samba at 51 bars per minute. **Count it as Samba**". A tempo in the title also settles the speed. See step 11.
- **Swing:** a swung song whose tempo fits a dance with `swing: true` is offered too: "It sounds swung, like Jive." See step 13.

Apart from swing, nothing listens to the style of the music, so the page can't tell Cha-cha from Bachata at the same speed. That's an open question in [development.md](development.md).

## Timeline numbers follow your count

The numbers above the close-up timeline are what you count on each beat (`beatLabel`). For 4-beat dances that's the bar's 1 to 4. For a longer pattern it's your own count: Bachata and the 8-count Jive timings run 1 to 8 across two bars, and the 6-count Jive runs 1 to 6, drifting across the bars like the stage does. The bar lines, the bar numbers and the pink 1 stay on the music, so in 8 counts the pink numbers are your 1 and 5.

## Counts and tempos

These match the reference table on the home page.

| Dance | Time | Basic count | Competition MPM | BPM | In Where's the One |
|---|---|---|---|---|---|
| Rumba | 4/4 | 2, 3, 4-1 | 25–27 | 100–108 | Yes |
| Cha-cha | 4/4 | 2, 3, 4-&-1 | 30–32 | 120–128 | Yes |
| Samba | 2/4 | 1 a 2 | 50–52 | 100–104 | Yes |
| Jive | 4/4 | 1 2 3 a 4 5 a 6 | 42–44 | 168–176 | Yes |
| Bachata | 4/4 | 1 2 3 4 5 6 7 8 | 28–32 | 112–128 | Yes |
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

You don't need any drawing or click code. For a pattern that doesn't fit 4 beats, add `cycle` and number `c` through the cycle; see `jive`. To add another way of counting a dance, add an entry with `group` set to that dance's key; it appears under **Timing** with no other code. Keep cues short: at phone width, a slot box with 8 slots is about 31 px wide, and "Replace" didn't fit. Patterns with more than 8 slots wrap to rows of 5 at phone width.

> ⚠️ Note: a new dance's `mpm` also decides when a song is counted at double or half speed for it, and its widened range must stay under an octave wide, so that only one reading fits. All the built-in dances are well under it. To have the page offer the dance from song titles, add `inTitle`.
