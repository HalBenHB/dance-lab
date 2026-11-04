@echo off
rem Dance Lab: double-click to start. The first run sets up the song downloader.
rem Run "start.bat --lan" to also open it on phones on the same Wi-Fi.
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Setting up Dance Lab for the first time. This takes about a minute...
  python -m venv .venv
  if errorlevel 1 goto nopython
  ".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r requirements.txt
  if errorlevel 1 goto failed
)

".venv\Scripts\python.exe" server.py %*
if errorlevel 1 pause
goto :eof

:nopython
echo.
echo Python wasn't found. Install it from https://www.python.org/downloads/
echo (tick "Add python.exe to PATH"), then run start.bat again.
pause
goto :eof

:failed
echo.
echo Setup didn't finish. Check your internet connection, then run update.bat.
pause
