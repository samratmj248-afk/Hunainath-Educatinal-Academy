@echo off
title Shree Hunainath Educational Academy Launcher
cd /d "%~dp0"
echo ==============================================================================
echo Launching Shree Hunainath Educational Academy (Server + Ngrok Tunnel)
echo ==============================================================================

start "Hunainath Django Server" cmd /c "run_server.bat"
timeout /t 3 /nobreak >nul
start "Hunainath Ngrok Tunnel" cmd /c "run_ngrok.bat"

echo.
echo Server and Tunnel launched in dedicated terminal windows!
echo Local URL: http://127.0.0.1:8000/
echo Admin CMS: http://127.0.0.1:8000/admin/
echo Credentials: admin / HunainathAdmin2026!
echo.
pause
