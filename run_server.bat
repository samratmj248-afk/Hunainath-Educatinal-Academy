@echo off
title Shree Hunainath Educational Academy - Django Server
cd /d "%~dp0"
echo ==============================================================================
echo Starting Shree Hunainath Educational Academy Server...
echo ==============================================================================
call venv\Scripts\activate.bat
python manage.py check
python manage.py runserver 0.0.0.0:8000
pause
