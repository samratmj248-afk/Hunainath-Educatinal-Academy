@echo off
title Shree Hunainath Educational Academy - Ngrok Public Tunnel
cd /d "%~dp0"
echo ==============================================================================
echo Starting Ngrok Tunnel on Port 8000...
echo ==============================================================================
ngrok http 8000
pause
