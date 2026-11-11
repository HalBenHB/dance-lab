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

## Move the beats half a beat when the bass says so

- **What:** `bassBetweenBeats` moves the whole grid half a beat when the bass hits and the bass note changes both fall clearly between the detected beats (each below 0.8 of the halfway value).
- **Why:** the owner tested "Hit the Road Jack" and the count was wrong. The handclaps sit between the bass notes and are 3 times stronger, so the beat tracker locked onto them. With the grid half a beat off, no choice of the 1 can be right. Moved, the existing guess puts the 1 on the first note of the bass line in every bar.
- **Alternatives considered:** teaching the tracker to ignore claps, which risks every song's tempo; leaving it to **Shift half a beat**, which needs the dancer to know what went wrong.
- **Do not change because:** requiring both measures is what stops it firing on a syncopated bass, which is common in Latin music. The other three real songs score 0.86 or higher on both measures and stay put. Loosen the 0.8 only after testing real songs.

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

- **What:** a dance can set `cycle` (Jive: 6, Bachata: 8). `rebuildEvents` then places its slots by `placeInCycle`, while bars, loops, bar seeking and the timeline's numbers stay on the 4-beat grid.
- **Why:** the Jive basic is 6 beats. Bars are the music's and the cycle is the dancer's, and seeing the two side by side is the lesson. The owner's Bachata count runs through 8 for the same reason: it spans two bars.
- **Alternatives considered:** one 4-beat group of the rhythm (1, 2, 3 a 4), which is simpler but drops the second chassé and teaches the wrong count. Also a 3-bar pattern of 12 beats, which would need all the same code and list every slot twice.
- **Do not change because:** moving the cycle into `countAt` or `barAt` would break bar numbers, loops and the 8-bar dots.

## Tap plays, drag moves the song

- **What:** on the close-up timeline, a tap seeks and starts playing. A sideways drag of 8 px or more carries the song with the pointer: left goes forward, right goes back. Sound stops during the drag and resumes on release if it was playing. The overview also plays on a tap, but its drag still jumps to the pointer.
- **Why:** the owner asked for it, on phones too. Keeping the song under the finger is what dragging a waveform feels like.
- **Alternatives considered:** seeking on `pointerup`, which is simpler, but `click` is what phones reliably accept as permission to start audio. Playing sound during the drag, which would mean a burst of `<audio>` seeks.
- **Do not change because:** see the `touch-action` row under "What not to change".

## The owner's counts are the defaults

- **What:** Bachata opens on 1 2 3 4 5 6 7 8 and Jive on 1 2 3 a 4 5 a 6. The older counts, and Jive with 7 8, are under **Timing**.
- **Why:** this is how the owner and their studio count. The steps and timing are the same; only the numbers said out loud change. In Jive, the numbers running on to 5 and 6 also make the two chassés easy to tell apart.
- **How it's built:** the new counts took over the keys `bachata` and `jive`, so a browser that had saved either one opens on the new default.
- **Do not change because:** making the older count the main entry again would change what those saved keys mean.

## Tags, not playlists

- **What:** a song can have several tags, and picking one shows only its songs. There are no ordered lists, and nothing plays one song after another.
- **Why:** the owner asked for playlists or tags. Dancers practice one song at a time, and one song often belongs in several groups, such as "Bachata" and "Monday class", which tags handle with far less to build.
- **Alternatives considered:** ordered playlists, which need their own screen for reordering, and playing the next song automatically. Add them if the owner wants a running order.

## The dance you pick decides half or double tempo

- **What:** `fitTempoToDance` counts the song at its detected speed, doubled or halved, whichever fits the chosen dance, and says so under the tempo. It runs when a song loads, when you pick a dance, and on **Detect again**, but not after **Half tempo**, **Double tempo** or **Tap along**.
- **Why:** the owner danced "Hit the Road Jack" as Jive and had to press **Double tempo**. Half and double are both honest readings of a beat, and the detector can't know which you dance to. The dance you picked can.
- **Alternatives considered:** a different tempo prior per dance, which would still miss songs near the edge of the range; only showing a button, which is what the old "press Double tempo" sentence already did.
- **Do not change because:** applying it after the manual tempo buttons would undo what the dancer just chose.

## Your fixes are the test set

- **What:** a song's count (dance, tempo, the time of one 1) is saved with it in Your songs by **Save this count** and by every fix to the 1 or the tempo. The song then opens that way. **Detect again** forgets it. `tools/check-detection.js` runs detection on every song and scores it against those saved counts.
- **Why:** the owner asked how to know whether detection is right. Only the dancer knows the right count, and the fixes they already make are that knowledge. With a test set, a change to detection is measured on many songs instead of judged on one.
- **Changing the dance doesn't change a saved count.** Dancers often pick the dance before loading the next song. When it did, it rewrote the previous song's saved dance; testing caught it.
- **Songs from a file aren't saved.** There's no library entry to keep the count in, and a song dropped on the page must never overwrite another song's count. That's why the page keeps the loaded song's entry in `S.song` rather than relying on the highlighted row.
- **Alternatives considered:** asking for the right answer song by song in a separate tool, which nobody would do; trusting that a close score means a wrong 1, which "Hit the Road Jack" disproved.

## "Not sure" comes from parts of the song disagreeing

- **What:** the 1 is guessed again in each 8-bar stretch. If fewer than 70% agree with the whole song, the page says it isn't sure. A beat that varies by more than 6% gets a warning too.
- **Why:** the margin between the best and second-best 1 for the whole song didn't separate right from wrong: "Hit the Road Jack" won by 0.17 and is right. Disagreement between stretches is something a dancer can act on: listen to the song in a few places.
- **Do not change because:** a warning on every song stops being read. The 70% line warns on the three songs whose 1 is hard to hear, and not on Sexbomb or Sway.

## Swing suggests Jive, from data in `DANCES`

- **What:** a dance marked `swing: true` is offered when the song is swung at that dance's speed. Today that's Jive.
- **Why:** swing is the clearest sound cue for any dance in the tool, and Jive is the only swing dance in it. "Hit the Road Jack" has a jive tempo and is swung, but its title doesn't say so.
- **Do not change because:** dropping the 1/3 check would offer Jive for songs whose tempo was misread at two-thirds.

## Dance suggestions come from the title, not yet from the sound

- **What:** a dance named in the song's title is offered as a button, and only if the song's tempo fits that dance. A tempo in the title also settles half or double.
- **Why:** practice uploads often name the dance and tempo ("Banto (Samba 51)"), which is close to certain. Telling dances apart by sound needs rhythm features tuned on songs whose dance is known, and the four saved songs aren't enough.
- **Do not change because:** dropping the tempo check would offer Jive for "Jive Talkin'". Offering instead of switching keeps the dance under your control.

## A version number, raised by hand on every publish

- **What:** the bottom of both pages says "Version 1.0 · 11 November 2026". Each publish raises the number and the date (see [development.md](development.md)).
- **Why:** the owner checks the website to see whether a change has gone live. GitHub Pages has no server and no build step, so the page can't know which commit it came from by itself.
- **Alternatives considered:** fetching the newest commit from GitHub, which says what's on GitHub, not what the browser loaded; a shared `version.js`, one more file for one line of text.
- **Do not change because:** the version is only useful if every publish raises it. If it's forgotten, the site looks unchanged after a publish.

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

## The online server keeps no songs, unless it's given a lasting disk

- **What:** online, `server.py` downloads a song to a temp folder, sends it to the browser, and deletes it. Each browser keeps its own songs in IndexedDB. If `DANCE_LAB_DATA` is set, songs and tags stay in that folder instead, and every device shares them.
- **Why:** free hosting has a temporary disk, so server storage would mean paying for a disk. This also keeps copyrighted files off a rented server, and makes it possible to learn whether YouTube blocks the host before paying for anything. The owner has since asked to keep songs on the host so they can be re-used, so the setting exists, but it stays off until the owner chooses where the songs should live.
- **Alternatives considered:** a free cloud storage bucket, which would work on the free plan but needs an account, keys and more code in `server.py`.
- **Do not change because:** keeping songs without a lasting disk would lose them at the next sleep, and setting a disk in `render.yaml` would break the free plan. Turning this on is a decision about cost and copyright for the owner to make.

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

## Online downloads go through a proxy

- **What:** the Render service sets `YT_PROXY` to a free Webshare proxy.
- **Why:** YouTube refused every download from Render's own address, and cookies alone only got a short test clip through. See the results in [online.md](online.md).
- **Alternatives considered:** other free hosts, which would probably hit the same block; hosting on the owner's own computer, which wouldn't be completely online.
- **Do not change because:** removing the proxy brings the block straight back.

## The image uses Deno, not Debian's Node

- **What:** the Dockerfile copies Deno from `denoland/deno`.
- **Why:** yt-dlp needs Node 22 or newer, and Debian's package is Node 20. yt-dlp then reports no JavaScript runtime. Deno is what yt-dlp recommends, and it finds it with no extra setting.
- **Do not change because:** going back to Debian's Node silently loses formats.

## Keep yt-dlp's warnings

- **What:** every download passes a `YdlLog`, and failures print its warnings to the server log.
- **Why:** "Failed to extract any player response" says nothing by itself. The HTTP errors explaining it arrive as warnings, and `no_warnings` was throwing them away.
- **Do not change because:** the next YouTube change would be undiagnosable again.

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
| `S.cycleShift = i - S.k`, not reduced to one cycle | `startCycleHere` | Dances now have cycles of different lengths. Reducing it would move your start when you change timing |
| Timeline numbers ignore a 6-count and a mid-bar start | `beatLabel` | The timeline counts the music. Following the dancer's count put 3s and 5s on the pink bar lines (see [dances.md](dances.md)) |
| `DANCE_LAB_DATA` refused inside the Dance Lab folder | `main()` in `server.py` | Everything in that folder is served as pages without the password |
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
