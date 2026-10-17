@echo off
setlocal EnableExtensions
cd /d "%~dp0.." || exit /b 20
where py >nul 2>nul
if errorlevel 1 (set "PY=python") else (set "PY=py -3")
%PY% step16\riz112_unified.py --lab-root . --packet step6\examples\A_couvercle_ajuste_112.json --require-h3 --output step16\RESULTAT_AB_C.json
if errorlevel 1 goto :failed
%PY% step18\riz112_with_resources.py --lab-root . --packet step6\examples\A_couvercle_ajuste_112.json --assumptions step18\ASSUMPTIONS_EXEMPLE_SYNTHETIQUE.json --output step18\RESULTAT_EXEMPLE_SYNTHETIQUE.json
if errorlevel 1 goto :failed
%PY% step19\counterfactual_matrix.py --lab-root . --packet step6\examples\A_couvercle_ajuste_112.json --draws 100 --output step19\RESULTAT_PC_30_ROUTES.json
if errorlevel 1 goto :failed
%PY% -m unittest discover -s step19 -p "test_*.py" -q
if errorlevel 1 goto :failed
echo RIZ112_S19_LAUNCHER_OK
exit /b 0
:failed
echo RIZ112_S19_LAUNCHER_FAILED
exit /b 2
