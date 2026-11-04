"""Dance Lab local server.

Serves the Dance Lab pages and adds a song library to Where's the One:
search YouTube, save a song's audio (m4a) into library/, and load it.

    start.bat                  double-click on Windows; sets everything up
    python server.py           http://localhost:8766/wheres-the-one/
    python server.py --lan     also reachable from phones on the same Wi-Fi
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import socket
import sys
import threading
import time
import webbrowser
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse
from urllib.request import urlopen

try:
    import yt_dlp
except ImportError:  # the page then shows how to install it instead of the search bar
    yt_dlp = None

ROOT = Path(__file__).resolve().parent
LIBRARY = ROOT / "library"
INDEX = LIBRARY / "library.json"
PORT = 8766
AUDIO_TYPES = {
    ".m4a": "audio/mp4", ".mp4": "audio/mp4", ".webm": "audio/webm", ".opus": "audio/ogg",
    ".ogg": "audio/ogg", ".mp3": "audio/mpeg", ".wav": "audio/wav", ".flac": "audio/flac",
}
PRIVATE_DIRS = {".git", ".venv", ".claude", "__pycache__", "library"}
VIDEO_ID = re.compile(r"^[\w-]{11}$")
LINK_ID = re.compile(r"(?:[?&]v=|youtu\.be/|/shorts/|/embed/|/live/)([\w-]{11})")
ANSI = re.compile(r"\x1b\[[0-9;]*m")

lock = threading.Lock()
jobs: dict[str, dict] = {}
search_cache: dict[str, tuple[float, list]] = {}


def ydl_options(**extra) -> dict:
    opts = {"quiet": True, "no_warnings": True, "noprogress": True, "noplaylist": True}
    # YouTube needs a JavaScript runtime; yt-dlp only looks for Deno unless told otherwise
    if shutil.which("node") and not shutil.which("deno"):
        opts["js_runtimes"] = {"node": {}}
    opts.update(extra)
    return opts


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
    opts = ydl_options(
        format="bestaudio[ext=m4a]/bestaudio",
        outtmpl=str(LIBRARY / "%(title).90B [%(id)s].%(ext)s"),
        windowsfilenames=True,
        progress_hooks=[progress],
    )
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={job['id']}", download=True)
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
        if "Sign in to confirm" in text:
            message = "YouTube wants to check you're not a bot. Wait a few minutes and try again."
        elif "Private video" in text or "unavailable" in text.lower():
            message = "This video is private or not available in your country."
        else:
            message = f"The download failed ({text[:160]}). If this keeps happening, run update.bat."
        job.update(state="error", error=message)
        print(f"Download failed for {job['id']}: {text}")


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

    def send_json(self, data, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def from_page(self) -> bool:
        # Other websites can't send this header without a CORS preflight, which this server never allows.
        if self.headers.get("X-Dance-Lab") == "1":
            return True
        self.send_json({"error": "This request must come from the Dance Lab page."}, 403)
        return False

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
            return self.send_json({"ok": True, "downloader": yt_dlp is not None,
                                   "version": yt_dlp.version.__version__ if yt_dlp else None,
                                   "library": str(LIBRARY)})
        if path == "/api/library":
            with lock:
                return self.send_json({"songs": scan_library()})
        if path == "/api/search":
            if yt_dlp is None:
                return self.send_json({"error": "The downloader isn't installed. Run start.bat or update.bat."}, 503)
            query = arg("q")
            if len(query) < 2:
                return self.send_json({"results": []})
            try:
                return self.send_json({"results": search(query)})
            except Exception as err:
                return self.send_json({"error": f"Search failed ({clean_error(err)[:160]}). Check your internet connection."}, 502)
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

    def do_POST(self):
        if urlparse(self.path).path != "/api/download":
            return self.send_json({"error": "Unknown address."}, 404)
        if not self.from_page():
            return
        if yt_dlp is None:
            return self.send_json({"error": "The downloader isn't installed. Run start.bat or update.bat."}, 503)
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
        except json.JSONDecodeError:
            body = {}
        video_id = str(body.get("id", ""))
        if not VIDEO_ID.match(video_id):
            return self.send_json({"error": "That isn't a YouTube video."}, 400)
        return self.send_json(start_download(video_id), 202)

    def do_DELETE(self):
        url = urlparse(self.path)
        if url.path != "/api/library":
            return self.send_json({"error": "Unknown address."}, 404)
        if not self.from_page():
            return
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
    parser = argparse.ArgumentParser(description="Dance Lab local server")
    parser.add_argument("--port", type=int, default=PORT)
    parser.add_argument("--lan", action="store_true", help="also accept phones and tablets on the same Wi-Fi")
    parser.add_argument("--no-browser", action="store_true", help="don't open the browser")
    args = parser.parse_args()

    url = f"http://localhost:{args.port}/wheres-the-one/"
    try:
        server = Server(("0.0.0.0" if args.lan else "127.0.0.1", args.port), Handler)
    except OSError:
        print(f"Port {args.port} is busy. Dance Lab may already be running: open {url}")
        sys.exit(1)

    print(f"Dance Lab is running at {url}")
    if args.lan:
        print(f"On a phone on the same Wi-Fi: http://{lan_address()}:{args.port}/wheres-the-one/")
    if yt_dlp is None:
        print("Song search is off because yt-dlp isn't installed. Run start.bat or update.bat.")
    print(f"Songs are saved in {LIBRARY}")
    print("Close this window or press Ctrl+C to stop.")
    if not args.no_browser:
        threading.Timer(0.8, webbrowser.open, [url]).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
