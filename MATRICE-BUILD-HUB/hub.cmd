@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0hub.ps1"
if errorlevel 1 (
  echo.
  echo MATRICE BUILD HUB a rencontre une erreur.
  pause
)
