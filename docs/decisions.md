# Design decisions

Each decision lists what was done, why, what else was considered, and what changing it would cost.

## Pages are single HTML files with no build step

- **What:** each tool is one `index.html` with inline CSS and JavaScript. There's no framework, bundler or package.json.
- **Why:** it has to work in three places without changes: GitHub Pages, double-clicking the file, and the local server. It was first built as a claude.ai artifact, which needs one self-contained file.
- **Alternatives considered:** React or Vite. They add a build step and a toolchain for a page with one screen.
- **Do not change because:** a build step breaks "double-click to open" and complicates GitHub Pages. If the file gets too big, split by moving code into `<script src>` files next to it, not by adding a bundler.

## All audio analysis happens in the browser

- **What:** decoding, beat tracking and the downbeat guess are hand-written JavaScript in the page.
- **Why:** songs never leave the device, it works on the public site, and it works without the server.
- **Alternatives considered:** librosa on the server (needs Python for every user); essentia.js or aubio compiled to WebAssembly (large downloads, and still not tuned for finding the 1).
- **Do not change because:** the public site has no server, so moving analysis there would break the main use.

## A hand-written beat tracker, tuned for dance music

- **What:** spectral-flux onsets, autocorrelation tempo with a prior centered on 110 BPM, Ellis dynamic-programming beats, and a downbeat score. See [beat-detection.md](beat-detection.md).
- **Why:** it's small, has no dependencies, and is about 200 lines anyone can read and tune. The 110 BPM center covers rumba (around 100), samba (around 100) and cha-cha (around 124), and avoids double or half tempo for them.
- **Do not change because:** the constants were checked against the example groove: 124.0 BPM, and every downbeat within 8 ms. After changing any constant, run the checks in [development.md](development.md).

## The downbeat bands start at 200 Hz

- **What:** `spectralFeatures` uses `lo = 200` for the 24 harmony bands.
- **Why:** with 60 Hz, a root-to-fifth bass line counted as a "chord change" on beat 3, and the example groove got the 1 on beat 3. Bass has its own feature (`bass`), so harmony should mean chords.
- **Do not change because:** lowering it brings that bug back.

## Tempo is the mean beat interval, not the median

- **What:** `S.ibi = (last − first) / (n − 1)`.
- **Why:** beat times are rounded to analysis frames (11.6 ms), so the median of intervals snaps to a grid. On the example it showed about 123.0 instead of 124.0 BPM.
- **Do not change because:** BPM and MPM on screen would be visibly wrong.

## The example groove is synthesized sample by sample

- **What:** `makeDemo()` adds sine, noise and envelope math into a `Float32Array`.
- **Why:** the first version used hundreds of Web Audio nodes in an `OfflineAudioContext` and took about 15 seconds to render. Direct synthesis takes milliseconds.
- **Do not change because:** the page opens with the example already analyzed. A slow example means a blank-looking tool for the first 15 seconds.

## Playback through `<audio>`, with a Web Audio fallback

- **What:** see "The player" in [architecture.md](architecture.md).
- **Why:** practicing at 75% speed needs the pitch kept, which only media elements do (`preservesPitch`). Web Audio playback changes pitch with speed.
- **Alternatives considered:** a time-stretching algorithm (WSOLA) in JavaScript. It's possible, but heavy for long songs.
- **Do not change because:** dropping the fallback breaks playback wherever blob-URL media is blocked. Dropping `<audio>` makes slow practice sound wrong.

## Pink means the 1, and only the 1

- **What:** `--one` colors the 1 in the big count, slot boxes, timeline lines, 8-bar ticks and overview. It's also used for focus rings and loop shading, which never sit next to counts.
- **Why:** the tool's whole job is "where's the one". Users learn "pink = one" in seconds.
- **Pink means the music's 1.** In Jive the dancer's count drifts across the bars, so the stage shows a pink 3 when a chassé lands on the music's 1, and a plain 1 when the rock step lands on the music's 3.
- **Do not change because:** reusing pink for other counts or as a general accent weakens the main signal. Pinking the dancer's 1 in Jive would flash pink on the music's 3 every other basic.

## Every dance uses a 4-beat grid

- **What:** beats are always grouped in fours (`countAt`, `barAt`), including 2/4 Samba, which is shown as "1 a 2, 3 a 4". Tempo in bars per minute uses each dance's `barBeats`.
- **Why:** one grid keeps detection, bar numbers, loops and 8-bar groups simple. Dancers often count samba choreography in fours anyway.
- **Alternatives considered:** a per-dance bar length, which touches detection, the loop maths and the overview ticks.
- **Do not change because:** many functions assume `% 4`.

## A longer pattern is a cycle on top of the grid

- **What:** a dance can set `cycle` (Jive: 6). `rebuildEvents` then places its slots by `placeInCycle`, while bars, loops, bar seeking and the timeline's numbers stay on the 4-beat grid.
- **Why:** the Jive basic is 6 beats. Bars are the music's and the cycle is the dancer's, and seeing the two side by side is the lesson.
- **Alternatives considered:** one 4-beat group of the rhythm (1, 2, 3 a 4), which is simpler but drops the second chassé and teaches the wrong count. Also a 3-bar pattern of 12 beats, which would need all the same code and list every slot twice.
- **Do not change because:** moving the cycle into `countAt` or `barAt` would break bar numbers, loops and the 8-bar dots.

## Tap plays, drag moves the song

- **What:** on the close-up timeline, a tap seeks and starts playing. A sideways drag of 8 px or more carries the song with the pointer: left goes forward, right goes back. Sound stops during the drag and resumes on release if it was playing. The overview also plays on a tap, but its drag still jumps to the pointer.
- **Why:** the owner asked for it, on phones too. Keeping the song under the finger is what dragging a waveform feels like.
- **Alternatives considered:** seeking on `pointerup`, which is simpler, but `click` is what phones reliably accept as permission to start audio. Playing sound during the drag, which would mean a burst of `<audio>` seeks.
- **Do not change because:** see the `touch-action` row under "What not to change".

## The server is optional, and the page detects it

- **What:** the song library panel appears only when `/api/status` answers.
- **Why:** the public site must keep working, and should never advertise YouTube downloading to visitors.
- **Do not change because:** making the page depend on the server breaks GitHub Pages and phones.

## yt-dlp is not pinned

- **What:** `requirements.txt` says `yt-dlp[default]` with no version.
- **Why:** YouTube changes all the time, and old yt-dlp versions stop working within weeks. `update.bat` exists for exactly this.
- **Do not change because:** a pinned version guarantees breakage later.

## Songs live in `library/` inside the repo, git-ignored

- **What:** the song folder is `library/` next to `server.py`, listed in `.gitignore`. Audio extensions are also ignored everywhere.
- **Why:** the owner chose this location. Ignoring it keeps copyrighted audio out of a public repo.
- **Do not change because:** committing songs would publish copyrighted material on GitHub.

## The online server keeps no songs

- **What:** online, `server.py` downloads a song to a temp folder, sends it to the browser, and deletes it. Each browser keeps its own songs in IndexedDB.
- **Why:** free hosting has a temporary disk, so server storage would mean paying for a disk. This also keeps copyrighted files off a rented server, and makes it possible to learn whether YouTube blocks the host before paying for anything.
- **Alternatives considered:** a paid persistent disk or cloud storage. That would share one library across devices, at a monthly cost.
- **Do not change because:** storing songs on the server raises the cost and the copyright exposure. Sharing songs across devices would need a deliberate decision on both.

## Online mode needs a password, and the image refuses to run without one

- **What:** `DANCE_LAB_PASSWORD` switches on sign-in. The Dockerfile sets `DANCE_LAB_HOSTED=1`, and the server exits in that mode if there's no password.
- **Why:** without it, a deployment is a public YouTube downloader under the owner's name.
- **Do not change because:** a missed setting must fail loudly, not run open.

## Only `DANCE_LAB_HOSTED` means "hosted", not `PORT`

- **What:** `PORT` is read only when `DANCE_LAB_HOSTED` is set.
- **Why:** the first version treated any `PORT` as a hosting service. Development tools and other software set `PORT` too, and `start.bat` then refused to run.
- **Do not change because:** that bug comes straight back.

## Sign-ins are signed cookies, not stored sessions

- **What:** the cookie holds an expiry and an HMAC of it, with a key derived from the password by PBKDF2.
- **Why:** free servers sleep and lose their memory. Stored sessions would mean signing in again after every sleep.
- **Do not change because:** a phone user would have to retype the password every time the server slept. Changing the password is how to sign everyone out.

## Pasted links use oEmbed

- **What:** `lookup_link()` asks YouTube's oEmbed endpoint for title and channel.
- **Why:** about 0.9 s instead of about 10 s through yt-dlp. Duration isn't included, so link results show no length.
- **Do not change because:** search-as-you-type feels broken at 10 seconds.

## Changes to the library need an `X-Dance-Lab` header

- **What:** `POST` and `DELETE` are refused without it. The page's `api()` sends it on every request.
- **Why:** it's a cheap, standard defense against other websites triggering downloads or deletes through the user's browser.
- **Do not change because:** removing it lets any open website delete your songs.

## Delete takes two clicks, done inside the page

- **What:** × becomes **Delete?** for 3 seconds.
- **Why:** browser `confirm()` dialogs are blocked in the claude.ai artifact viewer this page came from, and an inline confirm is calmer anyway.

## `.bat` files use CRLF

- **What:** `.gitattributes` has `*.bat text eol=crlf`, and everything else is LF.
- **Why:** `cmd.exe` can misread `goto` labels in LF-only batch files.
- **Do not change because:** `start.bat` uses labels for its error messages.

## The repo is the source of truth

- **What:** an older copy of Where's the One exists as a private claude.ai artifact (https://claude.ai/artifact/7MLTCgdXWaPUAosynVZPn1). It has no song library and no "← Dance Lab" link.
- **Why:** the artifact was the prototype. The repo version is a standalone document with a `<!doctype>` and its own reset CSS.
- **Do not change because:** editing the artifact doesn't update the repo or the site. Make changes here.

## What not to change

These look odd but are intentional:

| Thing | Where | Why it's right |
|---|---|---|
| `lo = 200` for bands | `spectralFeatures` | Stops bass lines from faking chord changes (see above) |
| `- 0.06 * player.rate` | `heardBeat` | Reaction time: people press "1" slightly after they hear it |
| `touch-action: pan-y` on `#detail` | `<style>` | A sideways drag moves the song, and an up-and-down one still scrolls the page. With `none`, a phone user whose finger lands on this big canvas can't scroll. The browser sends `pointercancel` when it takes over, so `endScrub` handles that too |
| `scrubbed` reset in `pointerdown` | `#detail` handlers | Desktop browsers send a `click` after a drag and phones don't, so it can't be reset in the `click` handler: the next real tap would be swallowed |
| Loop starts 0.03 s before the 1 | `setLoop` | So the 1 is heard in full every time the loop restarts |
| `v < lastOut && lastOut - v < 0.08` | `player.time()` | `<audio>` time updates in steps. Without this, the count flickers back and forth across a beat |
| `setInterval(…, 40)` next to `requestAnimationFrame` | after `frame()` | Animation frames stop in background tabs, and the click track must not |
| `ensureCtx()` when the Click select changes | wiring | Browsers unlock audio only during a user action |
| Decoding at 22,050 Hz | `loadFile` | Halves memory for long songs. Analysis only needs 11,025 Hz |
| `[hidden] { display: none !important; }` | `<style>` base reset | Components set `display: flex` and would otherwise ignore the `hidden` attribute |
| `log_message` does nothing | `Handler` | Keeps the console readable for non-developers; real events print their own lines |
| `handle_error` ignores `ConnectionError` | `Server` | Cancelled searches would otherwise print tracebacks |
| `t0 = half a window` | `spectralFeatures` | Converts frame numbers to the time at the center of the window, so beats line up with the audio |
| `import yt_dlp` inside functions | `search`, `run_download` | Importing takes seconds. The server has to be listening first, and a hosting service's health check is waiting |
| Cookie file copied to temp | `ydl_options` | yt-dlp writes back to its cookie file, and hosting services mount secret files read-only |
| Longer search pause when online | `onQuery` | A small server can't cancel a search once started, so fewer starts is the only protection |
