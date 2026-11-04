# Glossary

Use these terms exactly, in code, docs and messages.

## Dance and music terms

| Term | Meaning here | Not to be confused with | Where |
|---|---|---|---|
| **the 1** (the one) | The first beat of a bar, where the bar starts. Always drawn pink | "Beat 1 of the song" | Page title, `#setOne`, `S.k` |
| **count** | The number 1–4 of a beat within its group of four | Bar number | `countAt(i)`, `#bigNum` |
| **bar** | A group of 4 beats in this tool. For Samba, a musical bar is 2 beats (see `barBeats`) | Measure in 3/4 | `barAt(i)`, "Bar 7" on the stage |
| **8-bar group** | Eight bars in a row, shown as dots under the slots. Songs and routines are often built in 8-bar phrases | The detected song sections (there are none) | `#dots` |
| **&** (and) | Half a beat after a count. Cha-cha 4-&-1 | The samba "a" | Slot with `f: 0.5` |
| **a** | A quarter beat before the next count (¾ through the beat). Samba 1 a 2, Jive 3 a 4 | The cha-cha "&" | Slot with `f: 0.75` |
| **quick / slow** | Rumba timing: one beat (quick) or two beats (slow, 4-1) | Speed control | Rumba cues |
| **basic** | A dance's basic pattern of steps. In Jive, 6 beats: a rock step and two chassés | A bar | `DANCES.jive`, `#cycleStart` |
| **tap** | Bachata count 4: the foot touches the floor and the weight stays | A step | Bachata cue, slot with `hold` |
| **BPM** | Beats per minute | MPM | `#bpm` |
| **MPM** | Bars ("measures") per minute, the unit for ballroom tempos. BPM ÷ 4, or ÷ 2 for Samba | BPM | `#mpm`, `DANCES[*].mpm` |
| **competition tempo** | WDSF tempo range per dance in MPM (IDO for Bachata) | The song's own tempo | Tempo-fit sentence, home page table |

## Tool terms

| Term | Meaning | Where |
|---|---|---|
| **Where's the One** | The beat-counter tool. Use this name, not "beat tracker app" | `wheres-the-one/` |
| **Dance Lab** | The whole collection and the repo | `index.html`, repo name |
| **stage** | The big panel with the dance picker, big count, cue and slots | `.stage` |
| **big count** | The large number (or & / a) on the stage | `#bigNum` |
| **cue** | The word under the big count and in slot boxes (Quick, Cha, Ball…) | `slot.cue`, `#bigCue` |
| **slot** | One moment of a dance pattern within a 4-beat group or a cycle | `DANCES[*].slots` |
| **cycle** | A pattern's length in beats, when it doesn't fit the 4-beat group. Jive: 6 | `DANCES[*].cycle`, `placeInCycle(i, n)` |
| **step** | A slot where a foot moves; amber | `slot.step` |
| **hold** | A slot where the weight stays (rumba 1, bachata tap); hollow ring | `slot.hold` |
| **step lane** | The row of amber dots along the bottom of the timeline | `drawDetail` |
| **timeline** | The two canvases: **detail** (close-up) and **overview** (whole song) | `#detail`, `#overview` |
| **Fix the count** | The group of correction tools | Section heading |
| **sync nudge** | Manual audio and visual offset in ms | `S.offset`, `#offset` |
| **click track** | Metronome clicks: off, every beat, or **my steps** | `#click`, `S.clickEvents` |
| **example groove** | The synthesized 16-bar cha-cha the page opens with | `makeDemo()` |
| **song library** | Saved songs plus YouTube search, served by the local server | `#library`, `library/` |
| **Your songs** | The saved-songs list in the library panel | `#songs` |
| **local server** | `server.py` on your own computer, started by `start.bat` | — |
| **online mode** | `server.py` with `DANCE_LAB_PASSWORD` set: sign-in required, songs kept in the browser | `ONLINE`, `L.online`, [online.md](online.md) |
| **hosted** | Running in the Docker image on a hosting service (`DANCE_LAB_HOSTED`). Hosted always means online mode, but online mode can also be tried locally | `main()` in `server.py` |
| **backup player** | Web Audio playback used when `<audio>` can't load the file | `player.mode === 'buffer'` |

## Easily confused

| These sound alike | The difference |
|---|---|
| `S.k` and the 1 | `S.k` is an index offset (0–3); the 1 is the beat it marks |
| the 1 and the dancer's 1 | The 1 is the music's, and it's pink. In Jive the dancer's count also has a 1 (the rock step), which falls on the music's 1 or 3 |
| `S.cycleShift` and `S.offset` | `cycleShift` is how many beats after the 1 a cycle starts; `offset` is the sync nudge in seconds |
| `S.P` and `S.ibi` | `P` is the period in analysis frames, used for tracking; `ibi` is seconds between beats, used for display |
| `displayEvents` and `clickEvents` | Display covers every slot, including holds; click covers only what the current Click setting plays |
| beat time and display time | `S.beats` are song times; what you see and hear is `beat + S.offset` |
| `samba` and `sambaVolta` | Two `DANCES` entries behind one Samba button, chosen by the Timing select |

## Terms to avoid

| Don't say | Say | Why |
|---|---|---|
| downbeat (in the interface) | the 1 | Dancers say "the one"; "downbeat" is fine in code comments and docs about detection |
| measure | bar | Shorter, and matches MPM wording on the page |
| playlist | song library / Your songs | It isn't ordered or played in sequence |
| BPM for competition tempo | MPM | Ballroom rules use bars per minute |
| app | page or tool | They're web pages, nothing to install |
