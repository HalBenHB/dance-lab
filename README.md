# Dance Lab

Practice tools for Latin dance: hear the count, find the 1, and drill your steps to the music.

Every tool is a single HTML file with no build step and no server code. Open it in a browser and it works. Songs you load are analyzed in the browser and never uploaded.

## Tools

### Where's the One (`wheres-the-one/`)

Load a song (MP3, M4A, WAV, OGG, FLAC) and watch its count while it plays.

- A big live count, with the 1 of every bar in pink
- The step pattern for the dance you pick, lit up on each count:
  - **Just count:** 1, 2, 3, 4
  - **Rumba:** 2, 3, 4-1
  - **Cha-cha:** 2, 3, 4-&-1
  - **Samba:** 1 a 2 (basic, whisks, walks), or 1 a 2 a 3 a 4 (voltas)
- A scrolling timeline with beat lines, bar numbers and step dots, plus a whole-song overview
- Practice controls: speed 50–100% (pitch stays the same), loop 1/2/4/8 bars, click track on every beat or on your steps only
- Fix-the-count tools: "This is the 1", move the 1 earlier or later, half or double tempo, shift by half a beat, tap tempo, and a sync nudge for Bluetooth delay
- Compares the song with competition tempo in bars per minute (MPM)

Keyboard: `Space` play/pause, `1` this is the 1, `T` tap, `←` `→` previous/next bar, `[` `]` move the 1.

## Using it

**On your computer:** double-click `index.html`. It opens in your browser. The fonts come from Google Fonts, so they need internet; everything else works offline.

**With a local server (optional):**

```bash
python -m http.server 8000
```

Then open http://localhost:8000.

**On your phone or for others:** put it on GitHub Pages (below) and open the link. On a phone, load songs from the Files app.

## Put it online with GitHub Pages

1. Create an empty repository named `dance-lab` on github.com.
2. Connect and push this folder:

   ```bash
   git remote add origin https://github.com/<your-username>/dance-lab.git
   git push -u origin main
   ```

3. On GitHub, open **Settings → Pages**. Under **Build and deployment**, choose **Deploy from a branch**, branch `main`, folder `/ (root)`, and save.
4. After a minute the site is at `https://<your-username>.github.io/dance-lab/`.

Anyone with the link can use it. Their songs stay on their own device.

## Project structure

```
dance-lab/
├─ index.html              Home page: list of tools and a tempo reference table
├─ wheres-the-one/
│  └─ index.html           The beat counter (HTML, CSS and JavaScript in one file)
└─ README.md
```

## How Where's the One finds the beat

All analysis runs in the browser with the Web Audio API and plain JavaScript:

1. **Decode and downsample** the song to mono at 11 025 Hz.
2. **Onset strength:** a short-time FFT (512 samples, hop 128, about 86 frames per second) and spectral flux, so the envelope rises wherever new sound starts.
3. **Tempo:** autocorrelation of the onset envelope, weighted toward dance tempos (around 110 BPM), with parabolic interpolation for a fractional period.
4. **Beats:** dynamic-programming beat tracking (Ellis, 2007). It picks a chain of strong onsets spaced about one period apart, allowing small tempo drift. Beats in silence at the start and end are trimmed.
5. **The 1:** each of the four possible bar positions is scored by bass hits, onset strength and harmonic change (chords usually change on the 1). The best one wins. This step is the most likely to be wrong, which is why the page has the fix-the-count tools.

Playback uses an `<audio>` element so slower speeds keep the pitch. If a browser can't play the file that way, the page falls back to Web Audio playback, where slower speeds also lower the pitch.

The page opens with a built-in example: 16 bars of cha-cha at 124 BPM, synthesized in the page.

## Adding a tool

1. Make a folder with an `index.html`, for example `routine-planner/index.html`.
2. Copy the color and font tokens (the `:root` block) from an existing page so the tools look alike, including the dark-mode blocks.
3. Add a "← Dance Lab" link (`href="../"`) at the top and a card for the tool on the home page.

## Ideas for next tools

- Jive and Paso Doble patterns in Where's the One
- A routine planner: figures mapped to bars and song sections, with counts
- Per-dance figure notes (timing, footwork, common mistakes)
- A practice log

## Also published as a Claude artifact

Where's the One was first built as a private page on claude.ai: https://claude.ai/artifact/7MLTCgdXWaPUAosynVZPn1. This repository is the source of truth. The artifact copy has no "← Dance Lab" link.
