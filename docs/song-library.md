# Song library and YouTube search

This part works only when the page is served by `server.py`, either on your computer (start it with `start.bat`) or online. On GitHub Pages, or when you open the HTML file directly, the panel stays hidden.

This page mainly describes the version on your computer. [online.md](online.md) covers what changes online: a sign-in, and songs kept in the browser instead of `library/`.

> ⚠️ Note: downloading from YouTube may go against YouTube's Terms of Service, and the songs are copyrighted. This feature is for personal practice. `library/` is git-ignored so songs are never published, and it must stay that way.

## What the user sees

- **Search bar** (`#q`). Typing searches YouTube after a 450 ms pause (at least 2 characters). **Enter** searches immediately. A pasted link (`watch?v=`, `youtu.be/`, `/shorts/`, `/embed/`, `/live/`) shows that one video. While a search runs, old results are dimmed.
- **YouTube list** (`#results`): thumbnail, title, channel and length, with **Download**. While downloading, the row fills with pink and shows "Saving N%". Videos already in the library show **Saved** and **Load**.
- **Your songs** (`#songs`): everything in `library/`, newest first. Typing in the search bar filters this list by title, channel and tag, unless the text is a link. **Load** analyzes the song; the loaded one is highlighted and shows **Loaded**. **×** turns into **Delete?** for 3 seconds, and a second click deletes.
- **Tags:** **+ Tag** on a song opens a box that suggests the tags you already have. A song can have up to 20, each up to 40 characters, and **×** on a tag removes it. Tags that differ only by capitals count as one, and a new tag takes the spelling you already use. The row above the list (`#tagFilter`) shows only the songs with the tag you pick, so a tag also works as a simple playlist.
- **After a download** finishes, the song is loaded right away and the page scrolls to the count.

## Files on disk

```
library/
├─ George Michael - Jesus to a Child (Official Music Video) [zNBj4EV_hAo].m4a
├─ my-own-recording.mp3        ← copied in by hand, still listed
└─ library.json
```

- Downloads are named `<title, at most 90 bytes> [<video id>].<ext>`, with characters Windows can't handle replaced.
- The format is `bestaudio[ext=m4a]/bestaudio`: YouTube's AAC m4a stream (format 140) when there is one, otherwise the best audio there is (often `.webm`). Browsers can play both.
- `library.json` is a list, newest first:

  ```json
  [
    {
      "file": "Me at the zoo [jNQXAC9IVRw].m4a",
      "title": "Me at the zoo",
      "channel": "jawed",
      "duration": 19,
      "youtube_id": "jNQXAC9IVRw",
      "added": "2026-11-03T18:10:42+00:00",
      "tags": ["Monday class"]
    }
  ]
  ```

  `tags` is left out until a song has had one. A song can also have a saved `count`, from **Save this count** or a fix to the 1 or the tempo: `{"dance": "jive", "bpm": 173.59, "one": 0.36, "saved": "…"}`, where `one` is the time in seconds of one of the song's 1s. The page opens the song that way, and `tools/check-detection.js` measures detection against it.

- Audio files with no entry (`.m4a .mp4 .webm .opus .ogg .mp3 .wav .flac`) get one on the fly: the title is the file name, and `youtube_id` is `null`. Entries whose file is missing are dropped.

## API reference

The server listens on `http://localhost:8766` (`--port` changes this). All responses are JSON unless noted. Errors look like `{"error": "message for the user"}`.

| Method | Path | Request | Response |
|---|---|---|---|
| GET | `/api/status` | — | `{"ok": true, "online": bool, "signedIn": bool, "downloader": bool, "keepsSongs": bool}`, plus `"library": "C:\\…\\library"` when not online, and `"commit"` on Render. `keepsSongs` says the server stores songs, so the page should use `diskStore`. Never needs a sign-in |
| POST | `/api/login` | `{"password": "…"}` and header `X-Dance-Lab: 1` | `{"ok": true}` and a session cookie. 401 for a wrong password, 429 after too many. Online mode only |
| GET | `/api/search?q=…` | `q`: words or a YouTube link | `{"results": [{"id", "title", "channel", "duration"}]}`. `duration` (seconds) is `null` for links. Errors: 502 if the search fails, 503 if there's no downloader |
| POST | `/api/download` | `{"id": "<11-char video id>"}` and header `X-Dance-Lab: 1` | 202 with a job: `{"id", "state", "percent", "error", "song"}` |
| GET | `/api/jobs?id=…` | — | The job. `state` is `queued`, `downloading`, `done` or `error`; on `done`, `song` is the new library entry |
| GET | `/api/library` | — | `{"songs": [ …entries as in library.json… ]}` |
| GET | `/api/audio?file=…` | `file`: name as in the library | The audio bytes, with the right `Content-Type`. No range requests (the page downloads the whole file into a Blob) |
| POST | `/api/tags` | `{"file": "<name as in the library>", "tags": ["…"]}` and header `X-Dance-Lab: 1` | `{"tags": […]}` as saved: the song's whole list, tidied. 404 if there's no such song |
| POST | `/api/count` | `{"file": "…", "count": {"dance", "bpm", "one"}}`, or `"count": null` to forget it, and header `X-Dance-Lab: 1` | `{"count": {…}}` as saved, with unknown or out-of-range fields left out and `saved` added. 404 if there's no such song |
| DELETE | `/api/library?file=…` | Header `X-Dance-Lab: 1` | `{"ok": true}` |

Starting a download that is already running returns the existing job instead of starting another. At most two downloads run at once; others wait as `queued`.

In online mode, every path except `/api/status` and `/api/login` returns 401 without a sign-in. Unless `DANCE_LAB_DATA` is set, `/api/audio` deletes the file after sending it, so it works only once per download.

## How the server talks to YouTube

- **Search:** `yt_dlp.YoutubeDL(...).extract_info("ytsearch12:<query>")` with `extract_flat="in_playlist"`. Flat mode returns titles and durations without resolving each video, so it takes about 3 seconds. Channels, playlists, live streams and upcoming streams are filtered out.
- **Links:** `https://www.youtube.com/oembed?format=json&url=…` gives title and channel in about 0.9 s. Fully resolving a link through yt-dlp took about 10 s. If oEmbed fails (some videos block embedding), yt-dlp is used instead.
- **Cache:** results stay in memory for 10 minutes. The cache is cleared when it passes 200 queries.
- **JavaScript runtime:** since late 2025, yt-dlp needs a JavaScript runtime to solve YouTube's challenges, and it only looks for Deno by default. `ydl_options()` sets `js_runtimes={"node": {}}` when Node is installed and Deno isn't. Without either, yt-dlp warns, and some formats can go missing.
- **Error messages** are rewritten for people, for example "YouTube wants to check you're not a bot…" or "private or not available in your country". Anything else suggests running `update.bat`.

## Security

On your computer, the server is for one person. It is still careful about two things (online mode adds a password; see [online.md](online.md)):

1. **Other websites.** Any page open in the same browser could send requests to `localhost:8766`.
   - `POST` and `DELETE` require an `X-Dance-Lab: 1` header. A cross-site page can't send a custom header without a CORS preflight, and the server never answers preflights, so it can't download, delete or change tags.
   - Reads (search, library) have no CORS headers, so other sites can't read the responses.
2. **File access.**
   - `/api/audio` and `DELETE` use only the base name of `file` (`Path(name).name`) and only accept audio extensions, so `../server.py` returns 404.
   - Static serving refuses `.git`, `.venv`, `.claude`, `__pycache__` and `library`, plus top-level `.py`, `.bat` and `.txt` files.

By default it listens on `127.0.0.1` only. `--lan` listens on all interfaces, which lets anyone on the Wi-Fi use the library. The README and setup docs warn about this.

## How the page finds the server

At startup, `initLibrary()` calls `/api/status` with a 2.5 s timeout (skipped for `file://`).

- **It answers:** the panel shows. If `online` is true and `signedIn` is false, a password form replaces the search bar; songs already saved on the device stay available. If `downloader` is false, the search input is disabled and says to run `update.bat`.
- **It doesn't answer:** the panel stays hidden. The `#libraryOff` hint appears only when the page is on a local host (`localhost`, `127.x`, private IP ranges or `file:`). The public GitHub Pages site never shows it.

## Loading a library song

`loadFromLibrary()` gets the bytes from `L.store` (`/api/audio` on your computer, IndexedDB online), wraps them in a `File`, and calls the same `loadFile(file, title)` as **Load a song**. A library song goes through exactly the same decoding, analysis and playback as a song picked from disk.
