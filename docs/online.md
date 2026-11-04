# Dance Lab online

Online mode gives you the full Where's the One from any browser or phone, with no computer of yours running: search YouTube, fetch a song, and see its count. It runs `server.py` on a hosting service, in a Docker container.

> ⚠️ Note: this has only been tested on a local machine so far. Whether YouTube lets a given hosting service download is unknown until it's deployed (see [If YouTube blocks the server](#if-youtube-blocks-the-server)). The Dockerfile hasn't been built yet either, because Docker isn't installed on the development machine.

## How it differs from running on your computer

| | On your computer (`start.bat`) | Online |
|---|---|---|
| Address | `http://localhost:8766/wheres-the-one/` | `https://<your-service>.onrender.com/wheres-the-one/` |
| Search and downloads | Open | Need the password |
| Where songs are kept | `library/` on your computer | In each browser, on that device (IndexedDB) |
| What the server keeps | Your songs | Nothing. Each song is deleted as soon as the browser has it |
| Switched on by | Default | `DANCE_LAB_PASSWORD` is set |

The GitHub Pages site is separate and doesn't change: it has no search bar.

## Setting it up on Render

You need a free [Render](https://render.com) account. Sign up with GitHub so it can see the repo. The repo already contains `render.yaml`, which describes the service.

1. In the Render dashboard, choose **New → Blueprint** and click **Connect** next to `HalBenHB/dance-lab`.
2. Give the Blueprint a name and keep the branch as `main`.
3. When it asks for `DANCE_LAB_PASSWORD`, enter a long password. Several random words work well. It's stored by Render and never goes in the repo.
4. Click **Deploy Blueprint** and wait for the first build, which takes a few minutes.
5. Open `https://<your-service>.onrender.com/wheres-the-one/`, sign in, and try a song.

If Render won't create the Blueprint on the free plan, create the service by hand: **New → Web Service**, connect the repo, choose the **Free** instance type, add the environment variable `DANCE_LAB_PASSWORD`, and set the health check path to `/api/status`. Render detects the Dockerfile.

You stay signed in for 30 days on each device. Changing the password signs everyone out.

Pushing to `main` redeploys the service automatically.

## What the free plan means

From [Render's free plan docs](https://render.com/docs/free):

- **It sleeps.** After 15 minutes without traffic, the service spins down. The next visit waits about a minute while it wakes.
- **Its disk is temporary.** Files are lost on every sleep and redeploy. That's why songs live in your browser.
- **Hours are limited.** There are 750 free instance hours a month, and sleeping doesn't count.
- **It's a small machine.** Expect searches and downloads to be slower than on your computer.

A paid plan removes the sleeping and is faster. You can change it later with no code changes.

## If YouTube blocks the server

YouTube often refuses downloads from hosting companies' addresses. If that happens, the page says "YouTube is blocking this online server". Searching may still work. There are two fixes, and both are settings on the Render service, with no code changes:

| Fix | Setting | Trade-off |
|---|---|---|
| Residential proxy | Environment variable `YT_PROXY`, for example `http://user:pass@proxy.example.com:8000` | Costs money, usually charged per GB. A song is about 5 MB |
| Your YouTube cookies | Export a `cookies.txt` from your browser, add it as a Render **Secret File**, and set `YT_COOKIES_FILE=/etc/secrets/cookies.txt` | Free, but ties the downloads to your Google account. Use a spare account. Cookies expire, and may not be enough alone |

Try one, then download a song again. Never commit a proxy password or cookies file. They contain login details.

## Keeping it working

YouTube changes often. When downloads start failing with other errors, get the newest yt-dlp: in Render, choose **Manual Deploy → Clear build cache & deploy**. A normal deploy may reuse the old version. `update.bat` only updates your computer's copy.

## Where your songs are

Songs are saved in the browser on each device, so a song fetched on your phone isn't on your laptop.

They're removed if you clear that browser's site data. Browsers can also clear stored data when a device is low on space, and Safari may clear it after a long time without use. Adding the page to your phone's home screen helps. The page asks the browser to keep the data, but the browser decides. If a song disappears, download it again.

## Safety

- **Password:** everything except the pages and `/api/status` needs a sign-in. After 10 wrong passwords in 10 minutes, sign-in stops for everyone until the window passes. Devices already signed in keep working.
- **No accidental public downloader:** the Docker image sets `DANCE_LAB_HOSTED=1`, and the server refuses to start in that mode without a password.
- **Cookies:** the sign-in cookie is `HttpOnly`, `SameSite=Strict`, and `Secure` over HTTPS. It's signed with a key derived from the password, so sign-ins survive sleeping and restarts.
- **Copyright:** downloading from YouTube may go against YouTube's Terms of Service, and songs are copyrighted. Keep the password to yourself. Sharing it turns this into a downloader for other people.

## Settings reference

| Variable | Needed | What it does |
|---|---|---|
| `DANCE_LAB_PASSWORD` | Yes | Turns on online mode and sets the password |
| `DANCE_LAB_HOSTED` | Set by the Dockerfile | Listens on all interfaces, uses `PORT`, doesn't open a browser, and refuses to start without a password |
| `PORT` | Set by Render | The port to listen on. Ignored unless hosted, because on a computer it can mean something else |
| `YT_PROXY` | No | Proxy URL for yt-dlp |
| `YT_COOKIES_FILE` | No | Path to a `cookies.txt`, copied to a temp folder because yt-dlp writes to it |

## Other hosting services

`render.yaml` is Render-specific, but the Dockerfile runs on any service that hosts containers. Set `DANCE_LAB_PASSWORD`, and make sure the service provides `PORT` and HTTPS.
