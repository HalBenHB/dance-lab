@echo off
rem Updates the song downloader (yt-dlp). Run this when YouTube search or downloads stop working.
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" python -m venv .venv
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -U -r requirements.txt
echo.
echo Done. Start Dance Lab again with start.bat.
pause
