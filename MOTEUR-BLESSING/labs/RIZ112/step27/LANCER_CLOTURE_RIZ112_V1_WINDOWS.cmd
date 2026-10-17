@echo off
setlocal
cd /d "%~dp0.."
where py >nul 2>nul
if errorlevel 1 (set "PYTHON=python") else (set "PYTHON=py -3")
call step20\LANCER_RIZ112_STEP20.cmd
if errorlevel 1 exit /b 1
%PYTHON% -m unittest discover -s step27 -p "test_*.py" -q
if errorlevel 1 exit /b 1
%PYTHON% step27\release_gate.py --lab-root . --output step27\RECU_CLOTURE_INGENIERIE_V1.json
if errorlevel 1 exit /b 1
echo [OK] Cloture logicielle RIZ112 V1. IC reel: NON CALIBRE, aucune experience reelle.
endlocal
