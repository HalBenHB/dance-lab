# Changelog

Newest first. Each entry says what changed and why. Anything under **Removed** must not come back without the owner asking for it.

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
