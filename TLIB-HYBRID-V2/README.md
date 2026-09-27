# TLIB Hybrid Engine V2 — PC Worker Lab

Status: LAB / CANARY. No production L1 bulk enablement yet.

## Purpose
This prototype adds a low-RAM Windows worker to the existing TLIB Apps Script engine. It is designed to:
- keep Google Sheets/Drive as the control plane and durable project state;
- use the PC for deterministic bulk work when it is online;
- keep Desktop Commander out of the hot path after bootstrap;
- avoid GitHub Actions completely during ordinary development;
- never store secrets in GitHub, Drive, or Google Sheets.

## Current canary
The lab canary uses only public GitHub REST endpoints and a small seed copied from the real L1 queue. Results stay in a local SQLite database on the PC.

Commands:
```powershell
node src/tlib.mjs selftest
node src/tlib.mjs seed
node src/tlib.mjs canary --limit=10
node src/tlib.mjs dashboard
node src/tlib.mjs agent
```

Dashboard: http://127.0.0.1:8787

## Production path
1. Prove local canary and dashboard.
2. Add an Apps Script lease bridge for atomic work claiming.
3. Store GitHub auth only in Windows secure storage / Apps Script Properties.
4. Run 100-item authenticated L1 canary.
5. Increase batch size adaptively only when error/rate/RAM metrics stay healthy.

Do not split the current 120k Google Sheet just to solve scale. The first scaling move is to move hot transactional work to the PC SQLite queue while Sheets remains the observable control plane.
