@echo off
REM ===========================================
REM Network Config Management - Windows Launcher
REM Double-click this file to start the app
REM Requires: WSL2 + Docker running
REM ===========================================

echo Starting Network Config Management...
echo.

REM Auto-convert this file's Windows directory to a WSL path
for /f "delims=" %%i in ('wsl wslpath -u "%~dp0"') do set WSL_PATH=%%i

REM Remove trailing slash if present
if "%WSL_PATH:~-1%"=="/" set WSL_PATH=%WSL_PATH:~0,-1%

REM Run start-app.sh inside WSL using the default distro
wsl bash -c "cd '%WSL_PATH%' && bash start-app.sh"

pause
