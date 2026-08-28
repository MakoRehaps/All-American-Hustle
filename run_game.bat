@echo off
setlocal
cd /d "%~dp0"

echo Preparing All-American Hustle...
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 tools\prepare_game.py
) else (
    python tools\prepare_game.py
)
if errorlevel 1 (
    echo.
    echo Game preparation failed. See the error above.
    pause
    exit /b 1
)

if not exist "All American Hustle.exe" (
    echo Missing "All American Hustle.exe"
    pause
    exit /b 1
)

start "" "All American Hustle.exe"
exit /b 0
