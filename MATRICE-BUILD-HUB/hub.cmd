@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0launcher.ps1"
if errorlevel 1 (
  echo.
  echo MATRICE BUILD HUB a rencontre une erreur.
  echo Consulte les diagnostics affiches ou le dossier Downloads\MatriceBuildHub.
  pause
)
