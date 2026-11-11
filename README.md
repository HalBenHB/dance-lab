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
4. Your downloaded songs stay in the list under **Your songs** for next time. Press **+ Tag** to label a song, for example "Bachata" or "Monday class", then pick a tag above the list to see only those songs.

Keep the black window open while you use it, and close it when you're done.
If search or downloads stop working, double-click **`update.bat`**.

> Downloading from YouTube may go against YouTube's rules, and songs are copyrighted. Use downloads only for your own practice.

### With YouTube search, completely online

The full version runs on a hosting service, so it works from any phone or browser with no computer of yours switched on. It's at https://dance-lab.onrender.com/wheres-the-one/ and needs a password. The first visit after a quiet spell takes about a minute while the server wakes.

To set up your own, follow [docs/online.md](docs/online.md).

Songs you fetch this way are saved in the browser on that device. To keep them on the server and see them on every device, it needs a paid plan with a disk: see [Keeping songs on the host](docs/online.md#keeping-songs-on-the-host).

### If the count looks wrong

Press **1** on your keyboard (or the **This is the 1** button) at the moment you hear the one. More fixes are under **Fix the count** on the page. If the page isn't sure where the 1 is, it says so under the tempo. For a song in **Your songs**, your fixes are saved with it, and **Save this count** saves a count that was right; the song opens that way next time. To count a dance another way, such as Bachata as 1, 2, 3, tap or Jive with 7 8, use the **Timing** menu next to the dances.

Picking your dance also sets the speed. Many songs can be counted at two speeds, one twice the other, so the page uses the one that suits the dance: "Hit the Road Jack" counts at 173.6 BPM for Jive and 86.8 for Bachata. If a song's title names a dance, such as "Banto (Samba 51)", the page offers it with a button.

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
| `CLAUDE.md` | How to publish changes, for anyone (or any AI assistant) working on this |
| `library/` | Songs downloaded on your computer. Created on first download and never uploaded to GitHub |
| `tools/check-detection.js` | For developers: checks the beat detection against the counts saved for your songs |
| `docs/` | Detailed documentation: how it works, setup, design notes |

## Updating the websites

Pushing to `main` updates both websites automatically: GitHub Pages in about a minute and the online version in about 2–3 minutes. Work on another branch isn't live until it's merged into `main`.

The bottom of each page shows its version, such as "Version 1.0 · 11 November 2026", so you can see when a new one has arrived. If GitHub Pages still shows the old one, reload the page: browsers may keep it for up to 10 minutes.

Want to know how it works or change something? Start at [docs/README.md](docs/README.md).
