"""Dance Lab server.

Serves the Dance Lab pages and adds a song library to Where's the One:
search YouTube, fetch a song's audio (m4a), and load it.

On your computer:
    start.bat                  double-click on Windows; sets everything up
    python server.py           http://localhost:8766/wheres-the-one/
    python server.py --lan     also reachable from phones on the same Wi-Fi

Online (see docs/online.md): set DANCE_LAB_PASSWORD. Search and downloads then
need a sign-in, and songs are only passed through to the browser, which keeps them.
Optional: YT_PROXY (proxy URL) and YT_COOKIES_FILE (cookies.txt path) for yt-dlp.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import importlib
import importlib.util
import json
import os
import re
import shutil
import socket
import sys
import tempfile
import threading
import time
import webbrowser
from datetime import datetime, timezone
from http.cookies import CookieError, SimpleCookie
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse
from urllib.request import urlopen

HAS_DOWNLOADER = importlib.util.find_spec("yt_dlp") is not None  # yt-dlp itself loads in the background; it's slow
PASSWORD = os.environ.get("DANCE_LAB_PASSWORD", "")
ONLINE = bool(PASSWORD)
YT_PROXY = os.environ.get("YT_PROXY", "")
YT_COOKIES_FILE = os.environ.get("YT_COOKIES_FILE", "")

ROOT = Path(__file__).resolve().parent
LIBRARY = Path(tempfile.gettempdir()) / "dance-lab-songs" if ONLINE else ROOT / "library"
INDEX = LIBRARY / "library.json"
PORT = 8766
SESSION_COOKIE = "dance_lab_session"
SESSION_SECONDS = 30 * 24 * 3600
MAX_FAILED_LOGINS = 10  # per 10 minutes
TEMP_SONG_SECONDS = 3600  # online: songs the browser never collected are removed after this long
AUDIO_TYPES = {
    ".m4a": "audio/mp4", ".mp4": "audio/mp4", ".webm": "audio/webm", ".opus": "audio/ogg",
    ".ogg": "audio/ogg", ".mp3": "audio/mpeg", ".wav": "audio/wav", ".flac": "audio/flac",
}
PRIVATE_DIRS = {".git", ".venv", ".claude", "__pycache__", "library"}
VIDEO_ID = re.compile(r"^[\w-]{11}$")
LINK_ID = re.compile(r"(?:[?&]v=|youtu\.be/|/shorts/|/embed/|/live/)([\w-]{11})")
ANSI = re.compile(r"\x1b\[[0-9;]*m")
# A blocked server may only be offered combined video files such as format 18, so accept them too.
AUDIO_FORMAT = "bestaudio[ext=m4a]/bestaudio/best"
RETRY_WAITS = (10, 30)  # seconds; YouTube's rate limit on shared hosting addresses comes and goes
BLOCKED = re.compile(r"Sign in to confirm|not a bot|IP is likely being blocked|HTTP Error (403|429)")

lock = threading.Lock()
download_slots = threading.Semaphore(2)  # small online servers run out of memory with more
jobs: dict[str, dict] = {}
search_cache: dict[str, tuple[float, list]] = {}
failed_logins: list[float] = []
SESSION_KEY = hashlib.pbkdf2_hmac("sha256", PASSWORD.encode(), b"dance-lab-session", 200_000) if ONLINE else b""


class YdlLog:
    """Keeps yt-dlp's warnings, which usually hold the real reason behind a failure."""

    def __init__(self):
        self.warnings: list[str] = []

    def debug(self, msg):
        pass

    def error(self, msg):
        pass

    def warning(self, msg):
        self.warnings.append(ANSI.sub("", str(msg)))


def ydl_options(**extra) -> dict:
    opts = {"quiet": True, "no_warnings": True, "noprogress": True, "noplaylist": True}
    # YouTube needs a JavaScript runtime; yt-dlp only looks for Deno unless told otherwise
    if shutil.which("node") and not shutil.which("deno"):
        opts["js_runtimes"] = {"node": {}}
    if YT_PROXY:
        opts["proxy"] = YT_PROXY
    if YT_COOKIES_FILE:
        # yt-dlp writes back to its cookie file, and hosting services mount secret files read-only
        copy = Path(tempfile.gettempdir()) / "dance-lab-cookies.txt"
        if not copy.exists():
            shutil.copyfile(YT_COOKIES_FILE, copy)
        opts["cookiefile"] = str(copy)
    opts.update(extra)
    return opts


def audio_options() -> dict:
    opts = {"format": AUDIO_FORMAT}
    if shutil.which("ffmpeg"):  # keeps the audio of a combined file as it is and drops the video
        opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "best"}]
    return opts


def session_signature(expires: str) -> bytes:
    return hmac.new(SESSION_KEY, expires.encode(), hashlib.sha256).hexdigest().encode()


def new_session() -> str:
    expires = str(int(time.time()) + SESSION_SECONDS)
    return f"{expires}.{session_signature(expires).decode()}"


def valid_session(token: str) -> bool:
    expires, _, signature = token.partition(".")
    if not expires.isascii() or not expires.isdigit() or int(expires) < time.time():
        return False
    return hmac.compare_digest(signature.encode(), session_signature(expires))


def now_iso(ts: float | None = None) -> str:
    return datetime.fromtimestamp(ts or time.time(), timezone.utc).isoformat(timespec="seconds")


def clean_error(err: Exception) -> str:
    text = ANSI.sub("", str(err))
    return re.sub(r"^(ERROR: )?(\[[\w:]+\] )?([\w-]{11}: )?", "", text).strip()


# ---------- library ----------

def read_index() -> list[dict]:
    try:
        return json.loads(INDEX.read_text("utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def write_index(songs: list[dict]) -> None:
    LIBRARY.mkdir(exist_ok=True)
    tmp = INDEX.with_suffix(".tmp")
    tmp.write_text(json.dumps(songs, ensure_ascii=False, indent=2), "utf-8")
    tmp.replace(INDEX)


def scan_library() -> list[dict]:
    """Saved songs, newest first. Audio files dropped into library/ by hand are included too."""
    songs = [s for s in read_index() if (LIBRARY / s["file"]).is_file()]
    known = {s["file"] for s in songs}
    if LIBRARY.is_dir():
        for p in LIBRARY.iterdir():
            if p.is_file() and p.suffix.lower() in AUDIO_TYPES and p.name not in known:
                songs.append({"file": p.name, "title": p.stem, "channel": "", "duration": None,
                              "youtube_id": None, "added": now_iso(p.stat().st_mtime)})
    songs.sort(key=lambda s: s.get("added") or "", reverse=True)
    return songs


# ---------- YouTube ----------

def search(query: str) -> list[dict]:
    key = query.lower()
    hit = search_cache.get(key)
    if hit and time.time() - hit[0] < 600:
        return hit[1]
    link = LINK_ID.search(query)
    results = None
    if link:
        try:
            results = [lookup_link(link.group(1))]
        except Exception:  # oEmbed refuses some videos; let yt-dlp try
            pass
    if results is None:
        import yt_dlp
        target = f"https://www.youtube.com/watch?v={link.group(1)}" if link else f"ytsearch12:{query}"
        with yt_dlp.YoutubeDL(ydl_options(skip_download=True, extract_flat="in_playlist")) as ydl:
            info = ydl.extract_info(target, download=False)
        entries = info.get("entries") if "entries" in info else [info]
        results = [
            {"id": e["id"], "title": e.get("title") or "", "channel": e.get("channel") or e.get("uploader") or "",
             "duration": e.get("duration")}
            for e in entries or []
            if e and e.get("id") and e.get("ie_key", "Youtube") == "Youtube"
            and e.get("live_status") not in ("is_live", "is_upcoming")
        ]
    if len(search_cache) > 200:
        search_cache.clear()
    search_cache[key] = (time.time(), results)
    return results


def lookup_link(video_id: str) -> dict:
    """Title and channel for a pasted link, via YouTube's oEmbed endpoint (much faster than yt-dlp)."""
    watch = f"https://www.youtube.com/watch?v={video_id}"
    with urlopen(f"https://www.youtube.com/oembed?format=json&url={quote(watch, safe='')}", timeout=8) as r:
        data = json.load(r)
    return {"id": video_id, "title": data.get("title") or "", "channel": data.get("author_name") or "", "duration": None}


def fetch_audio(video_id: str, opts: dict, log: YdlLog) -> dict:
    import yt_dlp
    for wait in (*RETRY_WAITS, None):
        del log.warnings[:]
        try:
            with download_slots, yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)
        except Exception as err:
            if wait is None or "HTTP Error 429" not in f"{err} {' '.join(log.warnings)}":
                raise
        print(f"YouTube is rate-limiting {video_id}; trying again in {wait} seconds")
        time.sleep(wait)
    raise AssertionError("unreachable")


def start_download(video_id: str) -> dict:
    with lock:
        job = jobs.get(video_id)
        if job and job["state"] in ("queued", "downloading"):
            return job
        job = jobs[video_id] = {"id": video_id, "state": "queued", "percent": 0, "error": None, "song": None}
    threading.Thread(target=run_download, args=(job,), daemon=True).start()
    return job


def run_download(job: dict) -> None:
    def progress(d: dict) -> None:
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            job["state"] = "downloading"
            if total:
                job["percent"] = min(99, round(100 * d.get("downloaded_bytes", 0) / total))

    LIBRARY.mkdir(exist_ok=True)
    log = YdlLog()
    opts = ydl_options(
        outtmpl=str(LIBRARY / "%(title).90B [%(id)s].%(ext)s"),
        windowsfilenames=True,
        progress_hooks=[progress],
        logger=log,
        **audio_options(),
    )
    try:
        if ONLINE:
            remove_old_temp_songs()
        info = fetch_audio(job["id"], opts, log)
        path = Path(info["requested_downloads"][0]["filepath"])
        song = {"file": path.name, "title": info.get("title") or path.stem,
                "channel": info.get("channel") or info.get("uploader") or "",
                "duration": info.get("duration"), "youtube_id": job["id"], "added": now_iso()}
        with lock:
            write_index([song] + [s for s in scan_library() if s["file"] != song["file"]])
        job.update(state="done", percent=100, song=song)
        print(f"Saved: {path.name}")
    except Exception as err:  # yt-dlp raises many error types; the page shows the message
        text = clean_error(err)
        details = " ".join(log.warnings)
        if BLOCKED.search(text) or BLOCKED.search(details):
            message = ("YouTube is blocking this online server. It needs a proxy or cookies: see docs/online.md."
                       if ONLINE else "YouTube wants to check you're not a bot. Wait a few minutes and try again.")
        elif "Requested format is not available" in text or "No video formats found" in text:
            message = "YouTube isn't offering this video to the server. Try another upload of the song."
        elif "Private video" in text or "unavailable" in text.lower():
            message = "This video is private or not available in your country."
        else:
            fix = "redeploy the server with a cleared build cache" if ONLINE else "run update.bat"
            message = f"The download failed ({text[:160]}). If this keeps happening, {fix}."
        job.update(state="error", error=message)
        print(f"Download failed for {job['id']}: {text}")
        for warning in log.warnings:
            print(f"  yt-dlp warning: {warning}")


def remove_old_temp_songs() -> None:
    now = time.time()
    for p in LIBRARY.iterdir():
        if p.is_file() and p != INDEX and now - p.stat().st_mtime > TEMP_SONG_SECONDS:
            p.unlink(missing_ok=True)


# ---------- HTTP ----------

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, format, *args):  # keep the console for messages people need to read
        pass

    def end_headers(self):
        if not self.path.startswith("/api/"):
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def send_json(self, data, status: int = 200, cookie: str | None = None) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(body)

    def from_page(self) -> bool:
        # Other websites can't send this header without a CORS preflight, which this server never allows.
        if self.headers.get("X-Dance-Lab") == "1":
            return True
        self.send_json({"error": "This request must come from the Dance Lab page."}, 403)
        return False

    def has_session(self) -> bool:
        if not ONLINE:
            return True
        try:
            morsel = SimpleCookie(self.headers.get("Cookie", "")).get(SESSION_COOKIE)
        except CookieError:
            return False
        return morsel is not None and valid_session(morsel.value)

    def signed_in(self) -> bool:
        if self.has_session():
            return True
        self.send_json({"error": "Please sign in."}, 401)
        return False

    def login(self, password: str) -> None:
        now = time.time()
        with lock:
            failed_logins[:] = [t for t in failed_logins if now - t < 600]
            blocked = len(failed_logins) >= MAX_FAILED_LOGINS
            right = ONLINE and hmac.compare_digest(password.encode(), PASSWORD.encode())
            if not right and not blocked:
                failed_logins.append(now)
        if blocked:
            return self.send_json({"error": "Too many wrong tries. Wait 10 minutes and try again."}, 429)
        if not right:
            time.sleep(1)
            return self.send_json({"error": "Wrong password."}, 401)
        secure = "; Secure" if self.headers.get("X-Forwarded-Proto") == "https" else ""
        cookie = f"{SESSION_COOKIE}={new_session()}; Path=/; Max-Age={SESSION_SECONDS}; HttpOnly; SameSite=Strict{secure}"
        return self.send_json({"ok": True}, cookie=cookie)

    def do_GET(self):
        url = urlparse(self.path)
        first = url.path.strip("/").split("/")[0]
        if first == "api":
            return self.api_get(url.path, parse_qs(url.query))
        if first in PRIVATE_DIRS or first.endswith((".py", ".bat", ".txt")):
            return self.send_error(404)
        return super().do_GET()

    def api_get(self, path: str, qs: dict) -> None:
        arg = lambda name: (qs.get(name) or [""])[0].strip()
        if path == "/api/status":
            status = {"ok": True, "online": ONLINE, "signedIn": self.has_session(), "downloader": HAS_DOWNLOADER}
            if not ONLINE:
                status["library"] = str(LIBRARY)
            if os.environ.get("RENDER_GIT_COMMIT"):  # lets anyone check which version is live
                status["commit"] = os.environ["RENDER_GIT_COMMIT"][:7]
            return self.send_json(status)
        if not self.signed_in():
            return None
        if path == "/api/library":
            with lock:
                songs = scan_library()
            return self.send_json({"songs": songs})
        if path == "/api/search":
            if not HAS_DOWNLOADER:
                return self.send_json({"error": "The downloader isn't installed. Run start.bat or update.bat."}, 503)
            query = arg("q")
            if len(query) < 2:
                return self.send_json({"results": []})
            try:
                return self.send_json({"results": search(query)})
            except Exception as err:
                hint = "" if ONLINE else " Check your internet connection."
                return self.send_json({"error": f"Search failed ({clean_error(err)[:160]}).{hint}"}, 502)
        if path == "/api/jobs":
            job = jobs.get(arg("id"))
            return self.send_json(job) if job else self.send_json({"error": "No such download."}, 404)
        if path == "/api/audio":
            return self.send_audio(arg("file"))
        return self.send_json({"error": "Unknown address."}, 404)

    def send_audio(self, name: str) -> None:
        path = LIBRARY / Path(name).name
        if not name or path.suffix.lower() not in AUDIO_TYPES or not path.is_file():
            return self.send_json({"error": "That song isn't in your library any more."}, 404)
        self.send_response(200)
        self.send_header("Content-Type", AUDIO_TYPES[path.suffix.lower()])
        self.send_header("Content-Length", str(path.stat().st_size))
        self.end_headers()
        with path.open("rb") as f:
            shutil.copyfileobj(f, self.wfile)
        if ONLINE:  # the browser has it now, and an interrupted transfer raises before this line
            path.unlink(missing_ok=True)

    def do_POST(self):
        path = urlparse(self.path).path
        if path not in ("/api/download", "/api/login"):
            return self.send_json({"error": "Unknown address."}, 404)
        if not self.from_page():
            return None
        try:
            body = json.loads(self.rfile.read(min(int(self.headers.get("Content-Length") or 0), 65536)) or b"{}")
        except ValueError:
            body = {}
        if not isinstance(body, dict):
            body = {}
        if path == "/api/login":
            return self.login(str(body.get("password", "")))
        if not self.signed_in():
            return None
        if not HAS_DOWNLOADER:
            return self.send_json({"error": "The downloader isn't installed. Run start.bat or update.bat."}, 503)
        video_id = str(body.get("id", ""))
        if not VIDEO_ID.match(video_id):
            return self.send_json({"error": "That isn't a YouTube video."}, 400)
        return self.send_json(start_download(video_id), 202)

    def do_DELETE(self):
        url = urlparse(self.path)
        if url.path != "/api/library":
            return self.send_json({"error": "Unknown address."}, 404)
        if not self.from_page() or not self.signed_in():
            return None
        name = Path((parse_qs(url.query).get("file") or [""])[0]).name
        path = LIBRARY / name
        if not name or path.suffix.lower() not in AUDIO_TYPES or not path.is_file():
            return self.send_json({"error": "That song isn't in your library any more."}, 404)
        with lock:
            path.unlink()
            write_index([s for s in read_index() if s["file"] != name])
        print(f"Deleted: {name}")
        return self.send_json({"ok": True})


class Server(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):
        if isinstance(sys.exc_info()[1], ConnectionError):  # the page cancelled a search it no longer needs
            return
        super().handle_error(request, client_address)


def lan_address() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "<this computer's IP>"
    finally:
        s.close()


def main() -> None:
    hosted = bool(os.environ.get("DANCE_LAB_HOSTED"))  # set by the Dockerfile
    if hosted and not ONLINE:
        print("DANCE_LAB_PASSWORD isn't set. Set a password first, so strangers can't use your downloader.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Dance Lab server")
    # hosting services say which port to use; on a computer, PORT may mean something else entirely
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT") or PORT) if hosted else PORT)
    parser.add_argument("--lan", action="store_true", help="also accept phones and tablets on the same Wi-Fi")
    parser.add_argument("--no-browser", action="store_true", help="don't open the browser")
    args = parser.parse_args()

    url = f"http://localhost:{args.port}/wheres-the-one/"
    try:
        server = Server(("0.0.0.0" if args.lan or hosted else "127.0.0.1", args.port), Handler)
    except OSError:
        print(f"Port {args.port} is busy. Dance Lab may already be running: open {url}")
        sys.exit(1)

    print(f"Dance Lab is running at {url}")
    if args.lan:
        print(f"On a phone on the same Wi-Fi: http://{lan_address()}:{args.port}/wheres-the-one/")
    if HAS_DOWNLOADER:
        threading.Thread(target=importlib.import_module, args=("yt_dlp",), daemon=True).start()
    else:
        print("Song search is off because yt-dlp isn't installed. Run start.bat or update.bat.")
    if ONLINE:
        print("Online mode: sign-in required. Songs go to the browser and aren't kept here.")
    else:
        print(f"Songs are saved in {LIBRARY}")
    print("Close this window or press Ctrl+C to stop.")
    if not args.no_browser and not hosted:
        threading.Timer(0.8, webbrowser.open, [url]).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
