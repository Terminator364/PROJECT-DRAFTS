@echo off
setlocal EnableExtensions
cd /d "%~dp0.." || exit /b 20
where py >nul 2>nul
if errorlevel 1 (set "PY=python") else (set "PY=py -3")
call step19\LANCER_RIZ112_STEP19.cmd
if errorlevel 1 goto :failed
%PY% step20\physical_influence_envelope.py --packet step6\examples\A_couvercle_ajuste_112.json --assumptions step20\ASSUMPTIONS_SYNTHETIQUES_NON_CALIBREES.json --output step20\RESULTAT_A_PC.json
if errorlevel 1 goto :failed
%PY% step20\build_register_112.py --lab . --out step20\REGISTRE_STEP20_112_PC.json
if errorlevel 1 goto :failed
%PY% -m unittest discover -s step20 -p "test_*.py" -q
if errorlevel 1 goto :failed
echo RIZ112_STEP20_LAUNCH_OK_REAL_IC_UNCALIBRATED
exit /b 0
:failed
echo RIZ112_STEP20_LAUNCH_FAILED
exit /b 2
