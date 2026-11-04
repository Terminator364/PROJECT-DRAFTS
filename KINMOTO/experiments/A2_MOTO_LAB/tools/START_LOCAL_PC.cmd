@echo off
setlocal
cd /d "%~dp0.."
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0build_offline.ps1"
if errorlevel 1 (
  echo ECHEC BUILD - ne rien publier. & pause & exit /b 1
)
start "" "http://localhost:8789/"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0serve_local.ps1" -Port 8789
