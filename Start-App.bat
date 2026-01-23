@echo off
REM ===========================================
REM Network Config Management - Windows Launcher
REM Double-click this file to start the app
REM ===========================================

echo Starting Network Config Management...
echo.

REM Run the shell script in WSL
wsl -d Ubuntu-24.04 --cd /mnt/d/NetworkMgmt/network-config-mgmt -- bash ./start-app.sh

pause
