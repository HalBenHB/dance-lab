# Working on Dance Lab

Read [architecture.md](architecture.md) and [decisions.md](decisions.md) first.

## Running it while you work

```bash
.venv\Scripts\python server.py --no-browser
```

Then open `http://localhost:8766/wheres-the-one/`. The server sends HTML with `Cache-Control: no-cache`, so a reload shows your edits. Restart the server after changing `server.py`.

For page-only changes, `python -m http.server` from the repo root also works, without the library panel.

To try online mode on your computer, set a password and use another port:

```bash
set DANCE_LAB_PASSWORD=local-test-only
.venv\Scripts\python server.py --no-browser --port 8767
```

Then open `http://localhost:8767/wheres-the-one/`. It uses a temp folder and IndexedDB, not `library/`.

## Fragile areas

- **Downbeat guess** (`guessDownbeat`). It's the least reliable part, and small weight changes flip songs between beat 1 and beat 3. Test any change against the example groove and at least one real song.
- **Timing between audio and display.** The display combines the `<audio>` clock (`player.time()`), the sync nudge (`S.offset`) and the click scheduling look-ahead (0.15 s times speed). A change to one of them shows up as early or late counts.
- **Song-load races.** `loadAudio` awaits analysis and then `player.load`. `loadToken` drops outdated loads. Any new `await` in that path must check the token afterwards.
- **`% 4` everywhere.** `countAt`, `barAt`, loops, bar seeking and the overview ticks all assume 4-beat groups. Changing the group size touches all of them. A dance's `cycle` only changes where its slots go.
- **yt-dlp and YouTube.** These break from the outside. Before debugging `server.py`, run `update.bat`, and look at the server console, which prints the raw yt-dlp error.
- **Download jobs live in memory.** Restarting the server forgets running jobs. The page then shows an error for them, and the file may be half-written in `library/`. yt-dlp leaves `.part` files, which the library ignores.
- **Threading.** `jobs` and `library.json` writes are protected by `lock`. Keep every write to `library.json` inside `with lock:`.
- **Two modes.** Song library changes must work with both `diskStore` and `browserStore`. Test on your computer and in online mode.
- **Background tabs.** The stage, clock and play button update from animation frames, which stop in hidden tabs and hidden test panes. A clock stuck at `0:00` there doesn't mean playback failed: check `audio.currentTime`.

## Checklist before committing

- [ ] The page script parses. This command prints nothing on success:

  ```bash
  node -e "const s=require('fs').readFileSync('wheres-the-one/index.html','utf8');new (require('vm').Script)(s.match(/<script>([\s\S]*)<\/script>/)[1])"
  ```

- [ ] `server.py` compiles: `.venv\Scripts\python -m py_compile server.py`
- [ ] The example groove reads **124.0 BPM** and **31.0 MPM** on Cha-cha. After pressing Play, the pink 1 lands on the strong kick at the start of each bar.
- [ ] Changed analysis? Also check the exact downbeats (below).
- [ ] Changed the page? Check the GitHub Pages behaviour: open the HTML file directly. The library panel must stay hidden and nothing may error.
- [ ] Changed the server? Run the safety checks (below).
- [ ] Light and dark mode both readable. Phone width (about 400 px) has no sideways scrolling.
- [ ] Never commit anything from `library/`, `.venv/` or audio files. `.gitignore` covers them; don't override it with `git add -f`.

### Checking downbeats precisely

There are no automated tests. To check detection, temporarily add `window.__wto = { S };` before `init();`, load the page, and run this in the console:

```js
const S = window.__wto.S;
S.beats.filter((t, i) => ((i - S.k) % 4 + 4) % 4 === 0).slice(0, 4)
// expect about [0.59, 2.53, 4.47, 6.40]: 0.6 + n × 1.935 s, within ±0.01
```

Remove the line before committing.

### Server safety checks

With the server running:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8766/server.py                 # 404
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8766/library/library.json      # 404
curl -s -o /dev/null -w "%{http_code}\n" -X POST -d '{"id":"jNQXAC9IVRw"}' http://localhost:8766/api/download   # 403
curl -s -o /dev/null -w "%{http_code}\n" "http://localhost:8766/api/audio?file=..%2Fserver.py"   # 404
```

For an end-to-end download test, use YouTube's first video, "Me at the zoo" (`https://youtu.be/jNQXAC9IVRw`, 19 s). Delete it from **Your songs** afterwards.

## Adding a new tool

1. Create `<tool-name>/index.html` as a complete document: `<!doctype html>`, charset and viewport metas, and the base reset from Where's the One.
2. Copy the `:root` tokens and both dark-mode blocks from an existing page.
3. Add `<a class="back" href="../">← Dance Lab</a>` above the title.
4. Add a card to `index.html` and a row to the file map in [README.md](../README.md) and [architecture.md](architecture.md).
5. If it needs the server, add routes under `/api/` in `server.py`, and hide the feature when `/api/status` doesn't answer.

## Advice for AI assistants

- Use the project's words: **the 1**, **count**, **slot**, **step lane**, **sync nudge**, **song library**. See [glossary.md](glossary.md).
- Don't hard-code a dance in drawing or click code; add or edit `DANCES` instead.
- Don't add libraries, frameworks or a build step to the pages.
- Don't move analysis to the server.
- Keep messages in plain language for dancers, not developers. Errors say what happened and what to do, for example "run update.bat".
- Ask before anything that publishes: pushing to `main` updates the public site.
- After editing `wheres-the-one/index.html`, update [architecture.md](architecture.md) if sections, state fields or ids changed, and add an entry to [changelog.md](changelog.md).

## Open questions

- **YouTube blocks the Render server,** so online downloads need a proxy or cookies ([online.md](online.md)). The proxy option was only tested against a dead address, and the cookie option with an empty file.
- **`check_youtube()` in `server.py` is temporary.** It reports through `/api/status` how YouTube treats the hosted server. Remove it, and the `youtubeCheck` field, once online downloads work.
- **Docker isn't installed on the development machine,** so Render's builds are the only test of the image. A `Download failed` line in Render's logs now includes yt-dlp's warnings.
- **Online mode on a real phone,** including how long iPhones keep songs in IndexedDB.
- **Remember fixes per song.** Where the 1 is, the tempo and the nudge are lost on reload. `library.json` could store them per file.
- **Paso Doble** isn't in the counter yet.
- **Jive and Bachata on real songs.** So far they've only been checked on synthesized grooves. How often real jive reads at half tempo, and how well the 1 is found, isn't known.
- **Timeline dragging on a real phone.** Touch was tested with simulated touch events and the phone-width view, not a real iPhone or Android. Check that a tap starts audio, that a sideways drag moves the song, and that an up-and-down swipe scrolls the page.
- **Each dance has one pattern.** Jive has only the basic, though many figures in every dance run on other counts. Each new pattern would be a new `DANCES` entry, like the Samba timings.
- **No automated tests.** The example groove could become a headless test (for example Node plus an `OfflineAudioContext` polyfill), but nothing runs today.
- **Untested without ffmpeg.** Every download test so far had ffmpeg installed.
- **Phones talking to the server.** `--lan` was written but hasn't been tested on a real phone.
