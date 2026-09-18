@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0local-phonemouse.ps1" %*
if errorlevel 1 (
  echo.
  echo BUILD LOCAL PHONEMOUSE EN ECHEC.
  pause
  exit /b 1
)
echo.
echo BUILD LOCAL PHONEMOUSE TERMINE.
pause
