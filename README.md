# Dance Lab

Practice tools for Latin dance.

The main tool is **Where's the One**. It plays a song and shows you the count while it plays: every beat, where each bar's 1 is, and where your feet go in Rumba, Cha-cha, Samba, Jive and Bachata. You can slow the song down, loop a few bars, and add a click track.

With its server running, either on your computer or online, it also has a search bar: find a song on YouTube, fetch it, and check its count right away.

**Live site (no search bar):** https://halbenhb.github.io/dance-lab/

## How to use it

### Quickest: the website

1. Open https://halbenhb.github.io/dance-lab/wheres-the-one/
2. Click **Load a song** and pick an audio file (MP3, M4A, WAV…).
3. Pick your dance and press **Play**.

Works on phones too. Your song stays on your device; nothing is uploaded.

### With YouTube search (on your computer)

You need [Python](https://www.python.org/downloads/) installed once.

1. Double-click **`start.bat`**. The first time, it sets itself up, which takes about a minute.
2. Your browser opens Where's the One with a search bar on top.
3. Type a song name, click **Download**, and the song loads into the counter.
4. Your downloaded songs stay in the list under **Your songs** for next time.

Keep the black window open while you use it, and close it when you're done.
If search or downloads stop working, double-click **`update.bat`**.

> Downloading from YouTube may go against YouTube's rules, and songs are copyrighted. Use downloads only for your own practice.

### With YouTube search, completely online

Run the server on a hosting service, and use the full version from any phone or browser with no computer of yours switched on. You set it up once, with a password so only you can use it. Steps are in [docs/online.md](docs/online.md).

Songs you fetch this way are saved in the browser on that device.

### If the count looks wrong

Press **1** on your keyboard (or the **This is the 1** button) at the moment you hear the one. More fixes are under **Fix the count** on the page.

## What's in this repo

| File or folder | What it does |
|---|---|
| `index.html` | Home page: the list of tools and a table of dance tempos |
| `wheres-the-one/index.html` | The beat counter. All of it lives in this one file |
| `server.py` | Small program for YouTube search and the song library, on your computer or online |
| `start.bat` | Double-click to start Dance Lab on your computer (sets things up the first time) |
| `update.bat` | Double-click to update the YouTube downloader when it stops working |
| `requirements.txt` | The extra Python package the server needs (yt-dlp) |
| `Dockerfile`, `render.yaml` | Recipe for running the server online on Render |
| `library/` | Songs downloaded on your computer. Created on first download and never uploaded to GitHub |
| `docs/` | Detailed documentation: how it works, setup, design notes |

Want to know how it works or change something? Start at [docs/README.md](docs/README.md).
