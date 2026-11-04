# Changelog

Newest first. Each entry says what changed and why. Anything under **Removed** must not come back without the owner asking for it.

## 2026-11-04: First deployment to Render

**Fixed**

- Download errors disappeared after a few seconds. They now stay on the song's row.
- yt-dlp's warnings, which hold the real reason for a failure, were being discarded. They're now logged, and HTTP 403 and 429 count as YouTube blocking the server.
- The image installed Debian's Node 20, below yt-dlp's minimum of 22, so yt-dlp had no JavaScript runtime. The image now uses Deno.

**Added**

- A temporary self-test, `check_youtube()`, reporting on `/api/status`.

**Direction**

- YouTube blocks Render's address (HTTP 429 and 403), so try cookies from a spare account, then a residential proxy.

## 2026-11-04: Jive, Bachata and a draggable timeline

**Added**

- Bachata: 1, 2, 3, tap. The tap clicks but keeps the weight, so it's a hollow ring. Its tempo (28–32 MPM) comes from IDO rules, because no official WDSF figure was found.
- Jive: 1, 2, 3 a 4, 3 a 4. The basic takes 6 beats over 4-beat bars, so dances can now set a `cycle` length. See [dances.md](dances.md).
- **Start my basic here** (`#cycleStart`): lines the cycle up with where the dancer starts. Shown only for dances with a `cycle`.
- A 3-bar loop, the only length that repeats the Jive basic without a break.
- Timeline: a tap plays from that point. A sideways drag on the close-up moves the song with the pointer, forward or back, with mouse or touch. The owner asked for this to work on phones too.

**Changed**

- Pink and the accent click now follow the music's 1, not the slot's label or place. Nothing changes for 4-beat dances. In Jive, a label of 1 can fall on the music's 3.
- The tempo-fit sentence suggests **Double tempo** when a song reads about half of the chosen dance's range. A synthesized jive groove at 172 BPM read as 86.
- `#detail` uses `touch-action: pan-y`, so a page can still scroll from it on a phone.
- "How the counts work" has six cards in a 3-column grid. The `.grid.four` styles are gone.

**Direction**

- Try Jive and Bachata on real songs, and the timeline on a real phone.
- Add Paso Doble.

## 2026-11-04: Online mode

**Added**

- Online mode in `server.py`, switched on by `DANCE_LAB_PASSWORD`: password sign-in with a 30-day signed cookie, and a limit on wrong tries. The owner wanted the full counter online with no computer running.
- Songs in online mode are passed through to the browser and deleted from the server. `browserStore` keeps them in IndexedDB. This makes free hosting possible and keeps songs off a rented server.
- `Dockerfile`, `.dockerignore` and `render.yaml` for hosting on Render.
- `YT_PROXY` and `YT_COOKIES_FILE` settings, for when YouTube blocks the host.
- `docs/online.md`.

**Changed**

- yt-dlp now loads in the background, so the server starts listening immediately. `/api/status` no longer reports its version.
- At most two downloads run at once.

**Fixed**

- During development, a stray `PORT` variable made the server think it was hosted and refuse to start. Only `DANCE_LAB_HOSTED` means hosted now.

**Direction**

- Deploy to Render and find out whether YouTube blocks it. That decides whether a proxy or cookies are needed.
- Test on a real phone.

## 2026-11-03: Song library and documentation

**Added**

- `server.py`: local server with YouTube search (yt-dlp), m4a downloads into `library/`, a library index and an audio endpoint. It lets you check a new song's count at the studio without hunting for files.
- Song library panel in `wheres-the-one/index.html`:
  - search as you type, with pasted links supported
  - download progress
  - saved songs, with load, filter and two-click delete
  - automatic loading after a download
- `start.bat` (set up on first run, then start), `update.bat` (upgrade yt-dlp) and `requirements.txt`.
- `docs/` with separate files per topic. `README.md` was rewritten as a short guide for people.

**Changed**

- `.gitignore` now ignores `.venv/`, `__pycache__/`, `library/`, and `.webm` and `.opus` audio.
- `.gitattributes`: `.bat` files use CRLF.
- `loadFile(file, title)` takes an optional title and returns whether the load worked.

**Fixed**

- Pasting a link filtered "Your songs" by the link text and hid everything. Links no longer filter.
- Link lookups took about 10 s through yt-dlp. They now use oEmbed (about 0.9 s).

**Direction**

- Remember per-song fixes (the 1, tempo, nudge) in `library.json`.
- Add Jive and Paso Doble, which need patterns longer than 4 beats.
- Try `--lan` on a real phone at the studio.

## 2026-11-03: Ignore Git Bash crash logs (`a8eb128`)

**Changed**

- `.gitignore` ignores `*.stackdump`, after a stray `sh.exe.stackdump` appeared in the working tree.

## 2026-11-03: Dance Lab repo created (`78e51f3`)

**Added**

- `index.html`: home page with a tool card and the Latin dance tempo table.
- `wheres-the-one/index.html`: the counter as a standalone page, with a "← Dance Lab" link.
- Published on GitHub (`HalBenHB/dance-lab`) and GitHub Pages.

## Before the repo: claude.ai artifact prototype (2026-11-02 to 2026-11-03)

**Added**

- Where's the One as a private claude.ai artifact: in-browser beat and downbeat detection, Rumba and Cha-cha slots, timeline, speed, loop, click track, and the Fix the count tools.
- Samba: timings "1 a 2" and "1 a 2 a 3 a 4" (voltas), and `barBeats: 2` for MPM.

**Fixed**

- The example groove took about 15 s to build with Web Audio nodes. It's now synthesized directly.
- The downbeat guess put the 1 on beat 3 when the bass walked root to fifth. Harmony bands now start at 200 Hz.
- BPM showed about 123.0 instead of 124.0, because the median beat interval snapped to frame boundaries. It now uses the mean.

**Removed**

- The debug global `window.__wto`, used only while testing. Don't ship it; add it temporarily when needed (see [development.md](development.md)).
