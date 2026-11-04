# Setup and running

## Requirements

| Need | For | Notes |
|---|---|---|
| A modern browser (Chrome, Edge, Firefox, Safari) | Everything | Uses the Web Audio API, `OfflineAudioContext` and canvas |
| Internet | Fonts, YouTube | Pages load fonts from Google Fonts; without internet they fall back to system fonts |
| Python 3.10 or newer | Song library only | Developed on 3.13. Install from python.org and tick **Add python.exe to PATH** |
| Node.js or Deno | Song library only, recommended | yt-dlp needs a JavaScript runtime to talk to YouTube. Without one it warns, and some downloads may fail |
| ffmpeg | Optional | yt-dlp uses it to tidy the downloaded m4a. Downloads were tested with ffmpeg installed |

The pages alone need nothing installed.

## Running

### Pages only (no install)

Open the live site, https://halbenhb.github.io/dance-lab/, or double-click `index.html` in the repo. YouTube search and the song library stay hidden; **Load a song** works.

### With the song library (Windows)

Double-click `start.bat`. It:

1. Creates a private Python environment in `.venv/` (first run only).
2. Installs `requirements.txt` into it (first run only).
3. Runs `server.py`, which opens `http://localhost:8766/wheres-the-one/` in your browser.

Close the console window to stop it.

### With the song library (macOS, Linux, or by hand)

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python server.py
```

On Windows, the manual equivalent is:

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python server.py
```

### Server options

| Option | What it does |
|---|---|
| `--port 9000` | Use another port (default 8766) |
| `--lan` | Also accept phones and tablets on the same Wi-Fi (see below) |
| `--no-browser` | Don't open the browser on start |

Pass them through `start.bat` too, for example `start.bat --lan`.

There are no environment variables or config files. The song folder is always `library/` next to `server.py`.

## Updating the downloader

YouTube changes often, which breaks downloaders until they're updated. When search or downloads stop working, double-click `update.bat`, or run:

```bash
.venv\Scripts\pip install -U -r requirements.txt
```

## Phones at the studio

1. On the computer, run `start.bat --lan` from a terminal in the repo folder.
2. The console prints an address like `http://192.168.1.20:8766/wheres-the-one/`. Open it on a phone on the same Wi-Fi.
3. If Windows asks whether Python may use the network, allow **private networks** only.

> ⚠️ Note: with `--lan`, anyone on that Wi-Fi can search, download and delete songs in your library. Only use it on networks you trust.

Phones can also use the GitHub Pages site with songs from their own Files app, without the computer.

## Publishing to GitHub Pages

The repo is `HalBenHB/dance-lab`, and Pages serves `main` from the root. Pushing to `main` updates https://halbenhb.github.io/dance-lab/ within a minute or two.

To set Pages up again from scratch: **Settings → Pages → Build and deployment → Deploy from a branch**, branch `main`, folder `/ (root)`.

Only the static pages run on Pages. `server.py` is in the repo but does nothing there, and the page hides the search bar when no server answers.

## Troubleshooting

| Problem | Cause and fix |
|---|---|
| No search bar on the page | The page wasn't opened through the server. Start `start.bat` and use `http://localhost:8766/wheres-the-one/` |
| "Search is off: run update.bat…" | yt-dlp isn't installed in `.venv`. Run `update.bat` |
| "Port 8766 is busy" | Dance Lab is probably already running. Open the address it prints, or use `--port` |
| "Python wasn't found" | Install Python and tick **Add python.exe to PATH**, then run `start.bat` again |
| "YouTube wants to check you're not a bot" | YouTube is rate-limiting. Wait a few minutes; if it persists, run `update.bat` |
| "The download failed (…)" | Usually an outdated yt-dlp. Run `update.bat` |
| Numbers look early or late against the music | Audio delay, often from Bluetooth speakers. Use **Sync nudge** on the page |
| Slower speed also lowers the pitch | The browser couldn't play the file in an `<audio>` element, so the backup player is in use. Try another browser or file format |
| The pink 1 is on the wrong beat | Press `1` when you hear the one, or use **← Earlier / Later →** |
| Phone can't open the `--lan` address | Same Wi-Fi? Firewall allowed for private networks? Some guest networks block devices from seeing each other |
