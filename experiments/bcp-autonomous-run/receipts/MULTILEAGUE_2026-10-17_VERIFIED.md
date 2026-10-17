# BCP Autonomous Test01 — Multi-league source coverage receipt (2026-10-17)

**Scope:** Isolated one-shot extension to the running, 60-minute, single-league worker. No change to that worker or MATRICE code.

- Device: `MBMPC` (Windows).
- Script: `experiments/bcp-autonomous-run/multileague_probe.py`.
- Local raw CSVs + manifest: `C:\Users\Lenovo\BCP_AUTONOMOUS_TEST_20261017\multi_league_probe\`.
- Source: https://www.football-data.co.uk/downloadm.php
- Seasons checked: 2025/26, 2026/27.
- Status: **10 of 10 downloads succeeded**, **2049 historical completed matches** accepted before the local execution date; 0 malformed rows under basic field/score/date rules.

| League code | League | 2025/26 | 2026/27 | Accepted total |
| --- | --- | ---: | ---: | ---: |
| E0 | English Premier League | 380 | 60 | 440 |
| D1 | German Bundesliga | 306 | 45 | 351 |
| SP1 | Spanish La Liga | 380 | 78 | 458 |
| I1 | Italian Serie A | 380 | 60 | 440 |
| F1 | French Ligue 1 | 306 | 54 | 360 |
| **TOTAL** | | **1752** | **297** | **2049** |

**Distinct limitations:** raw CSV availability does not prove pre-match historical timestamp availability; no historical published_at/available_at point-in-time contract demonstrated. This is a coverage and transport/format test, not a demonstration of completed collection of MATRICE's 62 parameter worlds, not an IC model and not a calibrated predictive validation. Source terms and redistribution permissions must be reviewed for any broader use. One-shot multi-league probe does not itself establish scheduled unattended fetching of these 10 source sets; the one-hour worker still polls E0 only.

**No upstream promotion:** Experimental branch `experiment/bcp-autonomous-data-run-2026-10-17` in `Terminator364/PROJECT-DRAFTS`. MATRICE R8 remains unchanged.
