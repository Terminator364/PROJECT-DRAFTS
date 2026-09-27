# TLIB — Resource & Durability Policy

This policy is a hard runtime constraint for TLIB on low-memory Windows PCs.

## Runtime priorities

- TLIB worker runs at below-normal OS priority when supported.
- Update/verification jobs also run below normal.
- User interaction has priority over background enrichment.
- Background work must pause under memory or CPU pressure.

## Resource governor

Default behavior:
- NORMAL: bounded work with an adaptive delay around 1.8 s.
- USER_ACTIVE: slow to about 5 s while the user interacts with the cockpit.
- THROTTLED: slow to about 6 s when memory/CPU headroom is low.
- PAUSED: stop enrichment for about 15 s when free RAM is critically low, worker RSS is excessive, or system CPU is saturated.

Current safety thresholds:
- pause if free RAM < 350 MB or free RAM < 9%;
- throttle if free RAM < 650 MB or free RAM < 16%;
- pause if TLIB worker RSS > 220 MB;
- throttle if TLIB worker RSS > 160 MB;
- pause near >92% measured CPU;
- throttle near >78% measured CPU.

These are conservative defaults and may be tuned from field evidence.

## SQLite

- WAL journal mode.
- NORMAL synchronous mode.
- cache target about 4 MB.
- queue/results survive worker or PC restarts.
- the database lives outside the code checkout and is not replaced during updates.

## Startup

- no full queue rebuild when the persistent queue already contains the staged corpus;
- reclassification only touches rows that need a new taxonomy or missing L1 fields;
- launcher performs repair rather than spawning duplicate workers.

## Updates

- stage first, verify outside the active checkout, then activate;
- verify Node syntax, UI JavaScript, views, subpages, controls and SQLite self-test;
- keep the old version until the new worker passes build+commit health verification;
- rollback automatically on failed activation;
- quarantine failed updates to avoid retry loops;
- automatic update discovery is rate-limited and must never poll continuously.

## UI

- background synchronization may update small counters only;
- no periodic full DOM rebuild;
- preserve scroll position, current view, expanded panels and user input;
- heavy lists load only on demand.

## Non-goal

TLIB must not maximize throughput at the expense of Windows responsiveness. Throughput is opportunistic; the user's foreground work always wins.
