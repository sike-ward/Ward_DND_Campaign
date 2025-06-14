@echo off
cd /d "%~dp0"
echo Launching Obsidian Lore Assistant...
echo -----------------------------
call .venv\Scripts\activate.bat
python Ward_DND_AI\main.py
echo.
echo App exited. Press any key to close...
pause >nul
