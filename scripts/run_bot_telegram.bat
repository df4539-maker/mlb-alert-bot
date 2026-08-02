@echo off
cd /d "%~dp0.."
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" main.py bot --telegram --days 1 --min-minutes 15 --stake 1
) else (
  python main.py bot --telegram --days 1 --min-minutes 15 --stake 1
)
