# How Where's the One finds the count

Everything runs in the browser, in plain JavaScript, in `wheres-the-one/index.html`. Measured on the development machine, a 7-minute song takes about 5 seconds and the 33-second example about 2 seconds.

## Pipeline

### 1. Decode and resample (`loadFile`, `analyze`)

- `decodeAudioData` on an `OfflineAudioContext(2, 1, 22050)` decodes the file at 22,050 Hz. This keeps memory down for long songs.
- `analyze()` renders it through another `OfflineAudioContext` at **11,025 Hz, mono**. The browser does the resampling and the stereo mixdown.
- `makePeaks()` keeps the largest absolute sample per 1/100 s for drawing the waveform.

### 2. Spectral features (`spectralFeatures`)

A short-time FFT with a 512-sample Hann window and a hop of 128 samples, which gives about **86 frames per second** (`fps`). For each frame:

| Feature | How | Used for |
|---|---|---|
| `flux` | Sum over all bins of the rise in `log(1 + 10·magnitude)` since the previous frame | Onsets, so tempo and beats |
| `bass` | The same, for bins 1 to 7 (about 20–160 Hz) | Downbeat guess (bass hits) |
| `rms` | Frame loudness | Trimming beats in silence |
| `bands` | Mean log magnitude in 24 log-spaced bands, **200–5,000 Hz** | Downbeat guess (chord changes) |

`t0 = 256 / 11025` s, half a window, converts frame numbers into times. The loop yields to the browser every 4,000 frames so the progress bar can update.

### 3. Onset envelope (`onsetEnvelope`)

The flux minus its moving average over ±0.4 s, with negative values set to zero and the result divided by its RMS. Peaks of `O` are where new sounds start.

### 4. Tempo (`estimatePeriod`)

- Autocorrelation of `O` for lags covering 50–200 BPM.
- Each lag `L` is scored as `w(L) · (ac[L] + 0.5·ac[2L] + 0.25·(ac[2L−1] + ac[2L+1]))`. This rewards a period whose double is also strong.
- `w(L)` is a log-Gaussian centered on **110 BPM** with a standard deviation of 0.9 octaves. This is the tempo prior: it favors dance tempos, so it picks 92 BPM over 184 or 46.
- Parabolic interpolation around the best lag gives a fractional period `P` (in frames).

### 5. Beats (`trackBeats`)

This is dynamic-programming beat tracking, after Ellis (2007), "Beat Tracking by Dynamic Programming".

- **Local score:** `O` smoothed with a narrow Gaussian (standard deviation `P/32`).
- **Score of a beat at frame `t`:** its local score plus the best score of an earlier beat between `P/2` and `2P` frames before it, minus a penalty of `100 · (log(gap / P))²` (tightness 100).
- **The chain:** the last beat is the highest score within the last `2P` frames, and backtracking from it gives the beat chain.

This follows small tempo changes while staying close to `P`.

### 6. Trim silence (`trimSilent`)

Leading and trailing beats are dropped where the loudest frame within ±0.15 s is below 1% of the song's peak loudness (−40 dB). Without this, the beat chain continues through silent intros and endings.

### 7. The 1 (`guessDownbeat`)

Every 4th beat is a 1, so there are only four candidates: `k = 0, 1, 2, 3`. Each beat gets three features, z-scored across the song:

| Feature | Idea |
|---|---|
| Harmonic change | `1 − cos` similarity between the average `bands` of the 4 beats before and the 4 beats after (plus half the same measure over 2 beats). Chords usually change on the 1 |
| Bass hit | Highest `bass` flux within ±2 frames of the beat |
| Onset strength | Highest `O` within ±2 frames |

Each candidate `k` scores the mean of `harmonic + bass + 0.5 · onset` over its beats, and the best one wins.

> ⚠️ Note: `bands` start at 200 Hz on purpose. When they started at 60 Hz, a bass line walking root to fifth (A–E, D–A…) made beat 3 look like a chord change. The example groove then put the 1 on beat 3. The bass line has its own feature.

This is the weakest step. Songs where 1 and 3 sound alike, samba with the surdo accent on 2, and songs with pickups can all fool it. That's why the page has the Fix the count tools.

### 8. Tempo and bars per minute

- `S.ibi` = (last beat − first beat) / (number of beats − 1). This is the mean, not the median: the median is rounded to whole frames (11.6 ms) and showed 123.0 instead of 124.0 BPM on the example.
- BPM = 60 / `ibi`. MPM = BPM / `barBeats` (4, or 2 for Samba).

## Fix the count tools

All of these edit `S.beats`, `S.k` or `S.offset`, then rebuild events.

| Tool | What it does in code |
|---|---|
| **This is the 1** (`setOne`, key `1`) | Finds the beat nearest to now minus 60 ms (times speed) for reaction time, and sets `k` so that beat is a 1 |
| **← Earlier / Later →** (`moveOne`, keys `[` `]`) | `k ∓ 1` (mod 4) |
| **Half / Double tempo** (`changeTempo`) | Runs `retrack()` with `P × 2` or `P / 2`, limited to 40–240 BPM |
| **Shift half a beat** (`shiftHalf`) | Replaces beats with the midpoints between them, then guesses the 1 again |
| **Tap along** (`tap`, `useTaps`, key `T`) | Needs at least 6 taps; a pause over 2 s starts over. The median tap interval becomes `P` for `retrack()`. If the new beats sit more than a quarter beat away from the taps, it also shifts by half a beat |
| **Sync nudge** (`#offset`) | ±300 ms added to every beat when drawing and clicking. Saved per browser |
| **Detect again** | `retrack(S.periodAuto)` |

`retrack()` always guesses the 1 again and clears any loop.

## The example groove (`makeDemo`)

At 22,050 Hz, mono, there's a 0.6 s lead-in, then 16 bars at 124 BPM:

- kick on 1 (strong) and 3 (weak)
- cowbell on every beat
- güiro scrapes on 4, & and 1 (the cha-cha-cha)
- a sine bass on 1 (root) and 3 (fifth)
- chords on 1, 2& and 4, over Am, D, G, C

It is the test fixture for detection: expected downbeats are `0.6 + n · 1.935 s`. After the changes above, detection finds them within 8 ms at 124.0 BPM. It's synthesized directly into a `Float32Array`. An earlier version built it from Web Audio nodes and took 15 seconds to render.

## Known limits

- Assumes 4 beats per group, even for 2/4 Samba, which is shown as two bars.
- No time-signature detection. Waltz and other 3/4 music will be counted wrong.
- Songs with big tempo changes or rubato intros drift; tap along helps.
- Live recordings with weak drums give weak onsets and less stable beats.
