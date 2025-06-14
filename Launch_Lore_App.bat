@echo off
cd /d "%~dp0"
call .venv\Scripts\activate
python -m Ward_DND_AI.main
