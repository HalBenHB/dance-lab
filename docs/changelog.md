# Changelog

Newest first. Each entry says what changed and why. Anything under **Removed** must not come back without the owner asking for it.

## 2026-11-11, version 1.1: Saved counts, not-sure warnings, and Jive from swing

The owner asked how to improve detection and check whether it's right, using "Hit the Road Jack" and "Sexbomb".

**Added**

- **Save this count**, and every fix to the 1 or the tempo, saves the song's dance, tempo and 1 with it in Your songs. The song opens that way next time; **Detect again** forgets it. See [decisions.md](decisions.md).
- `tools/check-detection.js` scores detection against those saved counts, so changes can be measured on many songs. See [development.md](development.md).
- A "not sure" line when the song's 8-bar stretches disagree about where the 1 is, or the beat isn't steady.
- Jive is offered when a song is swung at jive speed: "It sounds swung, like Jive." "Hit the Road Jack" now gets it.
- Jive timing "1 2 3 4 5 6 7 8: the music's count", one count a beat with no steps.
- "Sexbomb" in the results table: 123.0 BPM, inside competition Cha-cha, straight, and its 1 the clearest of the saved songs.

**Changed**

- The timeline's numbers follow your count. With an 8-count, they run 1 to 8 across two bars; the bar lines and the pink 1 stay on the music.

## 2026-11-11, version 1.0: The dance sets the speed, and titles suggest a dance

The owner danced "Hit the Road Jack" as Jive, which it is, and had to press **Double tempo**.

**Added**

- A version number at the bottom of both pages, so the owner can see on the website when a publish has arrived. This is version 1.0; each publish raises it. See [development.md](development.md).

- Picking a dance counts the song at the speed that dance is danced to: as detected, doubled or halved. A line under the tempo says when it was doubled or halved and which button goes back. See [beat-detection.md](beat-detection.md), step 10.
- When a song's title names a dance whose tempo fits the song, a button offers it, for example "The title says Samba at 51 bars per minute. **Count it as Samba**". A tempo in the title also settles the speed. Titles naming two fitting dances offer both.

**Direction**

- Suggest a dance from the sound once there are about five songs per dance whose dance is known. Tagging songs by dance would give that test set.

## 2026-11-05: The owner's counts, tags, and beats that follow the bass

**Fixed**

- "Hit the Road Jack" was counted half a beat off. Its handclaps are louder than anything else and sit exactly between the bass notes, so the beat lines locked onto them, and no choice of the 1 could be right. `bassBetweenBeats` now moves the grid half a beat when the bass hits and note changes both fall between the lines. The 1 now lands on the first bass note of every bar. The other saved songs don't move. See [beat-detection.md](beat-detection.md).
- Saved songs lists no longer jump back to the top when a row redraws.

**Added**

- Tags on songs, with a filter above **Your songs**. They're stored in `library.json`, or with the song in the browser when songs live there. The owner asked for playlists or tags; see [decisions.md](decisions.md) for why it's tags.
- `DANCE_LAB_DATA`: a folder on a lasting disk to keep songs and tags in, online too. `/api/status` reports `keepsSongs`, and the page chooses where songs live from that. It isn't turned on for the live service, because Render's free plan has no lasting disk.
- A **Timing** select for any dance with more than one count, driven by `group` in `DANCES`. It replaces the Samba-only select.
- Jive timing 1 2 3 a 4 5 a 6 7 8.

**Changed**

- Bachata now defaults to 1 2 3 4 5 6 7 8, the owner's count, with taps on 4 and 8. 1, 2, 3, tap is under **Timing**.
- Jive now defaults to 1 2 3 a 4 5 a 6, the owner's count. 1, 2, 3 a 4, 3 a 4 is under **Timing**.
- **Start my basic here** keeps your start on the same beat when you change to a timing of another length.

**Direction**

- Decide where online songs should live: a paid Render disk, or a free cloud storage bucket.
- Test on real Bachata songs. A synthesized groove with a strongly pushed bass read at two-thirds of its tempo.
- Stars and saving a song's details without its audio are still open from the last entry.

## 2026-11-05: Online downloads work

The owner downloaded a real song on the live server, and it played and stayed saved.

**Added**

- `fetch_audio` waits and retries on HTTP 429, up to 3 tries, because YouTube's limit on shared addresses comes and goes.
- `AUDIO_FORMAT` accepts a combined video file such as format 18 when no audio-only stream is offered, and keeps just the audio if ffmpeg is there.
- `/api/status` reports the deployed `commit` on Render, so anyone can check which version is live.
- `CLAUDE.md`, and a Publishing section in the docs: `main` is the live version.

**Changed**

- The Render service uses a free Webshare proxy (`YT_PROXY`), after cookies alone turned out not to be enough. See [online.md](online.md).

**Removed**

- The temporary self-test, `check_youtube()`, and its `youtubeCheck` field. It ran on every wake-up and used up the proxy allowance. If the server needs diagnosing again, add it back only for as long as that takes.

**Direction**

- Try removing the cookies, to take the spare Google account out of this.
- Add stars and playlists. The owner wants a song's details saved without its audio, with **Load** fetching the audio into that browser.

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
