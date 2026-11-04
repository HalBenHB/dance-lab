# Architecture

## The big picture

```
                         Browser
 ┌─────────────────────────────────────────────────────────────┐
 │ index.html (home)            wheres-the-one/index.html       │
 │                              ┌────────────────────────────┐  │
 │                              │ audio file ─► analyze()    │  │
 │                              │   ─► beats, the 1 ─► events│  │
 │                              │   ─► frame loop: stage,    │  │
 │                              │      timeline, clicks      │  │
 │                              │ song library panel ─┐      │  │
 │                              └─────────────────────┼──────┘  │
 └────────────────────────────────────────────────────┼─────────┘
                       only when served by server.py  │ fetch /api/*
                                                      ▼
                     server.py (your computer or online) ─► yt-dlp ─► YouTube
                              │
                              ├─► on your computer: library/ (m4a files + library.json)
                              └─► online: temp file, passed to the browser, then deleted
```

There are two layers:

1. **Static pages.** Each tool is one HTML file with its CSS and JavaScript inline. These pages are the whole product on GitHub Pages. All audio analysis happens in the browser.
2. **Optional server.** `server.py` serves the same pages and adds a small JSON API for YouTube search, downloads and the song library. The page detects it and shows the search panel only when it answers. It runs on your computer, or online with a password (see [online.md](online.md)).

## File map

| Path | Role |
|---|---|
| `index.html` | Home page. A card for each tool and a reference table of counts and competition tempos for the five Latin dances. No JavaScript |
| `wheres-the-one/index.html` | The beat counter: markup, styles and about 1,000 lines of JavaScript in one IIFE |
| `server.py` | Python HTTP server: static files, `/api/*`, download jobs, library index |
| `start.bat` | Windows launcher. Creates `.venv` and installs requirements on the first run, then starts `server.py` |
| `update.bat` | Upgrades yt-dlp inside `.venv` |
| `Dockerfile`, `.dockerignore` | The online image: Python, Deno, ffmpeg, yt-dlp, `server.py` and the pages. Sets `DANCE_LAB_HOSTED=1` |
| `render.yaml` | Render Blueprint: a free Docker web service that asks for `DANCE_LAB_PASSWORD` |
| `requirements.txt` | `yt-dlp[default]`, unpinned on purpose (see [decisions.md](decisions.md)) |
| `library/` | Downloaded songs plus `library.json`. Created on demand and git-ignored |
| `.venv/` | Private Python environment. Git-ignored |
| `.gitattributes` | LF everywhere, except CRLF for `.bat` files |
| `.claude/launch.json` | Local preview config for Claude Code. Git-ignored |
| `docs/` | This documentation |

## Inside `wheres-the-one/index.html`

### Markup, top to bottom

| Element id or class | What it is |
|---|---|
| `header.top` | Title, "← Dance Lab" link, **Load a song** button and the hidden `#file` input |
| `#library` | Song library panel: search input `#q`, result list `#results`, saved songs `#songs`. Hidden unless the server answers |
| `#libraryOff` | One-line hint to use `start.bat`. Shown only on local hosts without a server |
| `.song` | Song name, tempo (BPM), bars per minute (MPM), length, tempo-fit sentence, progress bar |
| `.stage` | Dance picker, Samba timing select, big count `#bigNum`, cue `#bigCue`, step slots `#slots`, bar number and 8-bar dots |
| `.timeline` | Two canvases: `#detail` (a few seconds around the playhead) and `#overview` (the whole song) |
| `.transport` | Previous/next bar, Play, clock, speed, click track, loop, zoom |
| Fix the count | Six tool cards: set the 1, half/double tempo, shift half a beat, tap along, sync nudge, detect again |
| How the counts work | Four reference cards and the keyboard shortcut list |

### Script sections, in file order

1. **Helpers and dance table:** `$`, `store` (localStorage with try/catch), `DANCES` (see [dances.md](dances.md)).
2. **State `S`:** one object for everything about the loaded song and the view.
3. **Search helpers:** `upperBound`, `lowerBound`, `nearestBeat`, `countAt`, `barAt`.
4. **Analysis:** `fft`, `spectralFeatures`, `onsetEnvelope`, `estimatePeriod`, `trackBeats`, `trimSilent`, `guessDownbeat`, `makePeaks`, `analyze`. See [beat-detection.md](beat-detection.md).
5. **Example groove:** `makeDemo` synthesizes 16 bars of cha-cha at 124 BPM in a `Float32Array`; `toWav` wraps it as a WAV blob.
6. **Playback:** `player`, which has two modes (below), plus `playClick`, `resetSchedule` and `scheduleClicks` for the click track.
7. **Beat grid state:** `rebuildEvents`, `afterBeatsChange`, `retrack`.
8. **UI:** colors from CSS tokens (`readColors`), `renderSlots`, `updateSongInfo`, `updateStage`, `drawDetail`, `drawOverview`, `frame`.
9. **Actions:** play, bar seek, set or move the 1, tempo changes, half-beat shift, loop, tap tempo, `loadAudio`, `loadFile`.
10. **Song library:** state `L`, `api()`, `initLibrary`, search, download polling, load and delete.
11. **Wiring and `init()`.**

### State

`S` holds:

| Field | Meaning |
|---|---|
| `feats` | Analysis features (onset envelope `O`, bass flux, loudness, bands, `fps`, `t0`) |
| `peaks` | Waveform peaks, 100 per second, normalized |
| `P`, `periodAuto` | Current and originally detected beat period, in analysis frames |
| `beats` | Beat times in seconds (song time, before the sync nudge) |
| `ibi` | Mean time between beats (first to last), used for BPM |
| `k` | Which beat index is a 1: beat `i` has count `((i - k) mod 4) + 1` |
| `dance` | Key into `DANCES` |
| `displayEvents` | Every slot of the dance pattern placed in time, used by the stage and the step lane |
| `clickEvents` | What the click track plays, depending on the Click setting |
| `offset` | Sync nudge in seconds, added to every beat when drawing and clicking |
| `rate`, `loop`, `zoom`, `taps` | Speed, loop window, timeline zoom, tap-tempo times |
| `shown`, `dirty` | Render bookkeeping: index of the event on screen, and whether to redraw |

`L` (song library) holds search results, saved songs, download jobs, the loaded library file, and search timers. `L.online` says whether the server is in online mode, and `L.store` is where songs live: `diskStore` (the server's `library/`) or `browserStore` (IndexedDB database `dance-lab`, store `songs`). Library code goes through `L.store` and doesn't care which one it has.

Saved per browser in `localStorage`, with keys prefixed `wto:`: `dance`, `click`, `offset` and `zoom`. Nothing else persists in the page.

### Data flow when a song loads

```
File or Blob ─► decodeAudioData (22,050 Hz)
            ─► analyze(): resample to 11,025 Hz mono ─► peaks + spectral features ─► onset envelope ─► period P
            ─► player.load() (blob URL in <audio>, or Web Audio fallback)
            ─► retrack(P): trackBeats ─► trimSilent ─► beat times ─► guessDownbeat ─► k
            ─► rebuildEvents(): dance slots in time ─► display and click events
            ─► frame loop picks it up
```

`loadAudio` uses a `loadToken` counter, so a slow analysis of an old file can't overwrite a newer one.

### The frame loop

`frame()` runs on every `requestAnimationFrame`. It handles loop wrap-around, schedules clicks, and redraws the stage and both canvases, but only while playing or when `S.dirty` is set. A 40 ms `setInterval` also schedules clicks, because animation frames pause in background tabs.

### The player

`player` hides two playback modes behind one interface: `load`, `play`, `pause`, `seek`, `setRate`, `time`, `isPlaying`.

- **media** (normal): an `<audio>` element plays a blob URL. Changing speed keeps the pitch (`preservesPitch`). Its clock updates in steps, so `time()` interpolates between updates and never runs backwards by less than 80 ms.
- **buffer** (fallback): a Web Audio `AudioBufferSourceNode`. Used when the `<audio>` element fails to load the blob within 5 seconds. Its timing is exact, but changing speed changes the pitch.

## Inside `server.py`

- **`Handler`** (a `SimpleHTTPRequestHandler` subclass) serves static files from the repo root and routes `/api/*`. It refuses `.git`, `.venv`, `.claude`, `__pycache__`, `library` and top-level `.py`, `.bat` and `.txt` files.
- **`Server`** (a `ThreadingHTTPServer` subclass) ignores connection errors, which happen whenever the page cancels a search it no longer needs.
- **Search** runs yt-dlp in flat mode (`ytsearch12:`). Pasted links use YouTube's oEmbed endpoint, which is much faster. Results are cached for 10 minutes.
- **Downloads** run in a background thread per video id, tracked in `jobs`. The page polls `/api/jobs`.
- **Library index:** `library/library.json` is rewritten atomically (temp file, then rename) under a lock. `scan_library()` also lists audio files that were copied into `library/` by hand.
- **yt-dlp loads in the background.** Importing it takes seconds, so the server starts listening first and uses `find_spec` to report whether it's installed.
- **Online mode** turns on when `DANCE_LAB_PASSWORD` is set. API calls then need a signed session cookie, songs go to a temp folder, and each is deleted once it has been sent. Details are in [online.md](online.md).

API details are in [song-library.md](song-library.md).

## Patterns used

There are almost no classes. The structure comes from a few deliberate patterns:

> **Single-file module (IIFE)** in `wheres-the-one/index.html`
> All code is inside `(() => { 'use strict'; … })()`, with no globals and no imports. The page must work as a plain file and on GitHub Pages with no build step. Do not split it into modules or add a bundler without changing that constraint first.

> **Data-driven dance patterns** in `DANCES`
> Rendering, the step lane and the click track are all generated from a dance's `slots` table. Adding a dance means adding data, not code. Do not hard-code dance names in drawing or click logic. The only dance-specific branches are `barBeats` and the Samba timing select.

> **One interface, two playback engines** in `player`
> The rest of the page calls `player.*` and never touches `<audio>` or Web Audio directly. Keep it that way, or the fallback mode silently breaks.

> **One interface, two song stores** in `L.store`
> `diskStore` and `browserStore` both offer `list`, `blob` and `remove`. Only the online branch of `download()` knows about the difference, because it has to move the song into the browser. Don't call `/api/library` directly from other code, or online mode breaks.

> **Dirty-flag rendering** via `S.dirty` and `S.shown`
> The stage DOM is touched only when the displayed event changes, and the canvases redraw only when playing or dirty. Any code that changes what's on screen while paused must call `markDirty()`, and set `S.shown = -2` if the big count should refresh.

> **Request tokens and abort controllers**
> `loadToken` (song loading) and `L.searchCtl` (search) make sure only the latest request updates the page. Keep both when you touch loading or search.

## External dependencies

| Dependency | Pinned? | Used for | Why this one | Caution |
|---|---|---|---|---|
| Google Fonts: Big Shoulders Display, Hanken Grotesk, IBM Plex Mono | No (a CSS link) | Typography | Display face for big counts, readable body face, mono for numbers | Canvas text also names these families. Keep the fallback stacks |
| yt-dlp (`yt-dlp[default]`) | No, on purpose | YouTube search and download | The maintained standard; `[default]` includes `yt-dlp-ejs` for YouTube's JavaScript challenges | Pinning breaks downloads within weeks. Update with `update.bat` |
| Node.js or Deno | System install | JavaScript runtime that yt-dlp needs for YouTube | Most people already have Node | `ydl_options()` enables Node only when Deno is missing |
| ffmpeg | System install, optional | yt-dlp's m4a container fix-up | Present on the development machine | Untested without it |
| `i.ytimg.com` | n/a | Thumbnails in search results and the library | No API key needed | Thumbnails hide on error; nothing breaks offline |
| YouTube oEmbed | n/a | Fast title lookup for pasted links | About 0.9 s instead of about 10 s through yt-dlp | Falls back to yt-dlp when it fails |

There are no JavaScript libraries, and nothing to install for the pages.

## Visual design tokens

Both pages define the same tokens on `:root`, with dark values under `prefers-color-scheme: dark` and `[data-theme="dark"]`:

| Token | Use |
|---|---|
| `--bg`, `--surface`, `--surface-2`, `--line` | Page, cards, raised controls, borders (neutrals tinted slightly violet) |
| `--ink`, `--muted` | Text |
| `--one`, `--one-soft` | Pink accent. Always means **the 1**, plus focus rings and loops |
| `--step` | Amber for steps (feet) |
| `--wave`, `--wave-played` | Waveform before and after the playhead |
| `--font-display`, `--font-body`, `--font-mono` | The three font roles |

Keep pink reserved for the 1. The whole tool depends on "pink = one".
