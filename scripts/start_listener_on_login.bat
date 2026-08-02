@echo off
REM Arranca el listener al iniciar sesion (PC 24/7)
cd /d "%~dp0.."
if exist ".venv\Scripts\python.exe" (
  start "MLB Telegram Listener" ".venv\Scripts\python.exe" main.py listen
) else (
  start "MLB Telegram Listener" python main.py listen
)
