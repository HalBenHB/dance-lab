# Dance Lab online

Online mode gives you the full Where's the One from any browser or phone, with no computer of yours running: search YouTube, fetch a song, and see its count. It runs `server.py` on a hosting service, in a Docker container.

Online mode is live at https://dance-lab.onrender.com/wheres-the-one/. Full song downloads work there, but only through a proxy, because YouTube blocks Render's own address. See [If YouTube blocks the server](#if-youtube-blocks-the-server).

## How it differs from running on your computer

| | On your computer (`start.bat`) | Online |
|---|---|---|
| Address | `http://localhost:8766/wheres-the-one/` | `https://<your-service>.onrender.com/wheres-the-one/` |
| Search and downloads | Open | Need the password |
| Where songs are kept | `library/` on your computer | In each browser, on that device (IndexedDB), unless the host has a [lasting disk](#keeping-songs-on-the-host) |
| What the server keeps | Your songs | Nothing. Each song is deleted as soon as the browser has it |
| Switched on by | Default | `DANCE_LAB_PASSWORD` is set |

The GitHub Pages site is separate and doesn't change: it has no search bar.

## Keeping songs on the host

Set `DANCE_LAB_DATA` to a folder on a lasting disk, and online mode keeps songs and their tags there, the way your computer keeps them in `library/`. Every signed-in device then sees the same songs.

**The live service doesn't do this yet,** because Render's free plan can't: free web services can't have a persistent disk, and they [lose every file](https://render.com/docs/free) each time they sleep or redeploy.

On Render it takes a paid plan and a disk. From [Render's pricing page](https://render.com/pricing), in November 2026: the Starter instance is $7 a month and disks are $0.25 per GB per month. At about 5 MB a song, 1 GB holds roughly 200 songs.

1. In the Render service, change the instance type to **Starter**.
2. Add a persistent disk to the service: 1 GB, with the mount path `/var/data`.
3. On its **Environment** page, add `DANCE_LAB_DATA` with the value `/var/data/songs`.
4. Save and redeploy, then check that `keepsSongs` is `true` on `/api/status`.

Things to know:

- With a disk, a deploy [takes the service down for a few seconds](https://render.com/docs/disks), and it can't scale to more than one instance.
- Songs already saved in a browser stay in that browser, but the page stops listing them. Download them again to put them on the server.
- This stores copyrighted songs on a rented server, so keep the password to yourself.

The folder can't be inside the Dance Lab folder, because everything in there is served as pages without the password. The server refuses to start if it is.

## Setting it up on Render

You need a free [Render](https://render.com) account. Sign up with GitHub so it can see the repo. The repo already contains `render.yaml`, which describes the service.

1. In the Render dashboard, choose **New → Blueprint** and click **Connect** next to `HalBenHB/dance-lab`.
2. Give the Blueprint a name and keep the branch as `main`.
3. When it asks for `DANCE_LAB_PASSWORD`, enter a long password. Several random words work well. It's stored by Render and never goes in the repo.
4. Click **Deploy Blueprint** and wait for the first build, which takes a few minutes.
5. Open `https://<your-service>.onrender.com/wheres-the-one/`, sign in, and try a song.

If Render won't create the Blueprint on the free plan, create the service by hand: **New → Web Service**, connect the repo, choose the **Free** instance type, add the environment variable `DANCE_LAB_PASSWORD`, and set the health check path to `/api/status`. Render detects the Dockerfile.

You stay signed in for 30 days on each device. Changing the password signs everyone out.

Pushing to `main` redeploys the service automatically, usually within 2–3 minutes. To see which version is live, open `/api/status`: its `commit` should match the newest commit on `main`.

## What the free plan means

From [Render's free plan docs](https://render.com/docs/free):

- **It sleeps.** After 15 minutes without traffic, the service spins down. The next visit waits about a minute while it wakes.
- **Its disk is temporary.** Files are lost on every sleep and redeploy. That's why songs live in your browser.
- **Hours are limited.** There are 750 free instance hours a month, and sleeping doesn't count.
- **It's a small machine.** Expect searches and downloads to be slower than on your computer.

A paid plan removes the sleeping and is faster. You can change it later with no code changes.

## If YouTube blocks the server

YouTube often refuses downloads from hosting companies' addresses. When it does, the page says "YouTube is blocking this online server". Searching may still work.

This is what happened on Render's free plan, in November 2026:

| Setup | Result |
|---|---|
| Nothing added | Search works. Every download is refused with HTTP 429 or 403, on all 9 request types yt-dlp offers |
| Cookies from a spare Google account | A 19-second test clip downloads as format 18. Real songs are still refused with HTTP 429, even after waiting and retrying |
| Webshare free proxy, cookies still set | **Works.** YouTube offers the real audio stream (format 140), and a full song downloads, plays and stays saved |

Both fixes are settings on the Render service, with no code changes. Never commit a proxy password or cookies file. They contain login details.

### Proxy (the setting in use)

1. Sign up at [webshare.io](https://www.webshare.io) and choose the free plan. It needs no card, and gives 10 shared proxies and 1 GB a month.
2. On its **Proxy List** page, note one proxy's address, port, username and password.
3. In Render, open the service's **Environment** page and add `YT_PROXY` with the value `http://USERNAME:PASSWORD@ADDRESS:PORT`.
4. Save and redeploy.

1 GB is roughly 150 songs a month, at about 5 MB each plus searches. Check your usage in Webshare's dashboard. If these shared addresses get blocked or the allowance runs out, switch to another proxy from the list, or to a paid residential proxy, by changing the same setting. Comparison sites list residential proxies from about $1 per GB; check current prices. Residential proxies send your traffic through other people's home connections, so choose a provider that says those people agreed.

### Cookies

Cookies weren't enough by themselves on Render. If you do use them, use a spare Google account, because yt-dlp's documentation warns that an account used this way can be banned. The steps are in [yt-dlp's guide](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies). Add the file as a Render **Secret File** named `cookies.txt`, and set `YT_COOKIES_FILE=/etc/secrets/cookies.txt`.

### What the server does by itself

- **Waits and retries.** On HTTP 429 it tries up to 3 times, waiting 10 and then 30 seconds.
- **Accepts a video file.** If YouTube offers no audio-only stream, it takes a combined file such as format 18 and keeps just the audio, using ffmpeg.

## Keeping it working

YouTube changes often. When downloads start failing with other errors, get the newest yt-dlp: in Render, choose **Manual Deploy → Clear build cache & deploy**. A normal deploy may reuse the old version. `update.bat` only updates your computer's copy.

## Where your songs are

Without `DANCE_LAB_DATA`, songs and their tags are saved in the browser on each device, so a song fetched on your phone isn't on your laptop.

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
| `DANCE_LAB_DATA` | No | Folder on a lasting disk where songs and tags are kept. Without it, online mode keeps nothing. See [Keeping songs on the host](#keeping-songs-on-the-host) |
| `YT_PROXY` | No | Proxy URL for yt-dlp |
| `YT_COOKIES_FILE` | No | Path to a `cookies.txt`, copied to a temp folder because yt-dlp writes to it |
| `RENDER_GIT_COMMIT` | Set by Render | The deployed commit, shown as `commit` on `/api/status` |

## Other hosting services

`render.yaml` is Render-specific, but the Dockerfile runs on any service that hosts containers. Set `DANCE_LAB_PASSWORD`, and make sure the service provides `PORT` and HTTPS.
