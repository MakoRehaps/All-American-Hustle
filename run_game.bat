@echo off
setlocal
cd /d "%~dp0"

if not exist "All American Hustle.exe" (
    echo Missing "All American Hustle.exe"
    pause
    exit /b 1
)

echo Preparing All-American Hustle...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\prepare_game.ps1"
if errorlevel 1 (
    echo.
    echo Game preparation failed. See the error above.
    pause
    exit /b 1
)

echo Starting All-American Hustle...
start "" "%~dp0All American Hustle.exe"
exit /b 0
