@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0windows\INSTALLER.cmd" (
  echo ERREUR : dossier windows absent ou extraction incomplete.
  pause
  exit /b 1
)
call "%~dp0windows\INSTALLER.cmd"
endlocal