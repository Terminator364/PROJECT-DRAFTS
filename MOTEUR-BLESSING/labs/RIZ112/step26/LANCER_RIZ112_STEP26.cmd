@echo off
setlocal EnableExtensions
cd /d "%~dp0.." || exit /b 20
where py >nul 2>nul
if errorlevel 1 (set "PY=python") else (set "PY=py -3")
call step24\LANCER_RIZ112_STEP24.cmd
if errorlevel 1 goto :failed
%PY% step25\q_measurement_contract.py --step20 step20\PROTOCOLE_Q_14_SORTIES_DRAFT.json --step21 step21\PRIORITY_CONFIRMED_NO_WEIGHTS.json --out step25\PC_Q_CONTRACT.json
if errorlevel 1 goto :failed
%PY% step25\trial_prep.py --proposal step25\PC_Q_CONTRACT.json --priority step21\PRIORITY_CONFIRMED_NO_WEIGHTS.json --quality-draft step20\PROTOCOLE_Q_14_SORTIES_DRAFT.json --synthetic-packet step6\examples\A_couvercle_ajuste_112.json --out-template step25\PC_EMPTY_TEMPLATE.json --out-check step25\PC_READINESS_GATE.json
if errorlevel 1 goto :failed
%PY% step26\evidence_ledger.py --lab . --out step26\PC_REGISTRE_112.json
if errorlevel 1 goto :failed
for %%S in (25 26) do (
  %PY% -m unittest discover -s step%%S -p "test_*.py" -q
  if errorlevel 1 goto :failed
)
echo RIZ112_STEP26_LAUNCH_OK__Q_UNAPPROVED__IC_REAL_NULL
exit /b 0
:failed
echo RIZ112_STEP26_LAUNCH_FAILED
exit /b 2
