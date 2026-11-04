# Dance Lab documentation

This folder is the detailed documentation for Dance Lab. The [main README](../README.md) is the short, human-friendly version. These files explain how things work, why they were built this way, and what to be careful about when changing them.

They are written for developers and for AI assistants working on the code. If you are an AI assistant, read [architecture.md](architecture.md), [decisions.md](decisions.md) and [development.md](development.md) before editing anything.

## Project snapshot

- **Purpose:** practice tools for Latin dancers. The main tool, Where's the One, finds the beats and the 1 of each bar in any song and shows the dance steps on each count.
- **Runtime:** static HTML, CSS and JavaScript pages that run in any modern browser. An optional server for the song library uses Python 3.10+ (developed on 3.13) and [yt-dlp](https://github.com/yt-dlp/yt-dlp). It runs on your computer or, in a Docker container, on a hosting service.
- **Architecture:** each tool is one self-contained HTML file with no build step and no framework. The server is one Python file using only the standard library plus yt-dlp.
- **Maturity:** a working personal tool, used by one dancer and their studio. No automated tests. Online mode has not been deployed yet.
- **Key constraints:**
  - Every page must keep working as a plain static file on GitHub Pages, without the server.
  - Songs a user loads from their device are never uploaded. In online mode, the server keeps no song after passing it to the browser.
  - No build tools.

## Files in this folder

| File | What it covers |
|---|---|
| [setup.md](setup.md) | Installing, running, updating, GitHub Pages, phones, troubleshooting |
| [online.md](online.md) | Running the full version on a hosting service: setup, limits, YouTube blocks, settings |
| [architecture.md](architecture.md) | How the pieces fit: file map, page structure, state, server, dependencies |
| [beat-detection.md](beat-detection.md) | How Where's the One finds the tempo, the beats and the 1, step by step |
| [dances.md](dances.md) | How step patterns are described, the built-in dances, and how to add one |
| [song-library.md](song-library.md) | YouTube search, downloads, the library folder, and the server API reference |
| [decisions.md](decisions.md) | Design decisions with their reasons, and what not to change |
| [development.md](development.md) | Fragile areas, how to test changes, checklists, open questions |
| [glossary.md](glossary.md) | The project's own terms (count, the 1, slot, MPM…) and terms to avoid |
| [changelog.md](changelog.md) | What changed, when and why, and where the project is heading |
