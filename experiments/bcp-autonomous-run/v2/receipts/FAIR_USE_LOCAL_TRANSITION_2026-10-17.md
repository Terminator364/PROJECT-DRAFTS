# BCP V1/V2 — Provider policy correction and local cadence transition
Date: 2026-10-17 (Kinshasa).

## Reason
Football-Data public [Fair data usage policy](https://football-data.co.uk/contact.php): automated CSV downloads at most twice per week for private/research use, and repeated heavy bot/AI scraping discouraged. The earlier V1 10-minute and V2 30-minute schedules were excessively frequent. Provider [data page](https://football-data.co.uk/data) indicates datasets are updated at least twice weekly, not minute-by-minute.

## Actions completed on MBMPC
- Created `runtime/STOP` for V1 and `v2/runtime/STOP` for V2; confirmed original workers exited (PID 12640 and 13216 both not alive), with checkpoint statuses `stopped_by_user` and `stopped`.
- No source data were erased. Original final receipts reflect intentional interruption.
- Added `v2/local_audit.py`: **zero network traffic**, 60-second heartbeat, 300-second local validation of previously archived CSV files including immutable SHA-256, scores/date checks and independent snapshots.
- Started **local V1** worker PID `14632`, group E0 (two CSVs), using the original V1 deadline `1792257811.2164733` (~18:23 Kinshasa).
- Started **local V2** worker PID `8256`, all 10 CSVs, using the original V2 deadline `1792259901.2244275` (~18:58 Kinshasa).
- Both local workers verified `running`, 3 heartbeats, 1 completed local audit, 0 network requests in checkpoint (17:15 UTC).
- Disabled external fetch implementation in `v2/collector.py`, synchronized source to PC; verified guard present. `test_collector.py` regression: 7/7 tests passed again.

## Guardrails
Local analysis every 5 minutes is **not** new source collection. These workers will not gather injuries, latest xG, referees, or live data. Use only providers with explicit compatible access for frequent upstream refreshing. Before any future Football-Data automation, implement source-level 2/week limits and review terms/usage rights. Do not misrepresent cached source re-audits as new data.

Status: V1/V2 remote polling **stopped**, replacement local jobs **running** as of the verification timestamp. Their final completion is still to be verified.
