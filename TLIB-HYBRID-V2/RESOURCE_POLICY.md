# TLIB — Resource & Durability Policy

This policy is a hard runtime constraint for TLIB on low-memory Windows PCs.

## Core principle

A 4 GB Windows PC commonly operates with 80–95% of physical RAM in use. TLIB must **not** treat that percentage alone as a fault.

The resource governor therefore prioritizes:
- TLIB's own RSS footprint;
- sustained CPU pressure;
- combined low-free-memory + high-TLIB-memory signals;
- foreground user interaction;
- persistence of the pressure across several samples.

## Adaptive profiles

### LOW_RAM_4_6GB
Applied automatically when total RAM is <= 6 GB.

Expected:
- 80–95% system RAM use can remain NORMAL.
- TLIB RSS should normally stay well below ~110 MB.
- Low free RAM alone does not pause TLIB.

Pressure logic:
- soft TLIB RSS reference: ~110 MB;
- hard TLIB RSS reference: ~180 MB;
- free memory becomes relevant mainly below ~110 MB and only in combination with TLIB pressure;
- critical free-memory reference: ~70 MB;
- CPU soft reference: ~88%;
- CPU hard reference: ~97%;
- pressure must persist across multiple samples before PAUSED.

### STANDARD
For machines above 6 GB, thresholds are wider but the same multi-signal logic applies.

## Runtime modes

- NORMAL: bounded opportunistic work.
- USER_ACTIVE: slows background enrichment while the cockpit is being used.
- THROTTLED: slows only after sustained combined pressure.
- PAUSED: temporary pause under sustained critical pressure; automatic recovery follows.

The user's foreground work always wins.

## SQLite

- WAL journal mode.
- NORMAL synchronous mode.
- cache target about 4 MB.
- queue/results survive worker or PC restarts.
- the database lives outside the code checkout and is never replaced by an update.

## Startup

- no full queue rebuild when the persistent queue already contains the corpus;
- reclassification only touches rows that need it;
- launcher/repair must prevent duplicate workers.

## Updates

- immutable deployment slots: download into a new slot, verify, preflight, then activate;
- the active slot is never overwritten in place;
- manifest blob hashes must match before activation;
- old slot remains available until the new worker passes build + commit health verification;
- automatic rollback on activation failure;
- failed updates are not retried in a tight loop;
- update discovery does not run during an interactive TLIB launch;
- on LOW_RAM_4_6GB, staging is deferred only when free RAM is critically small for staging itself, not merely because Windows is using 80–95%.

## UI

- background synchronization updates small counters only;
- no periodic full DOM rebuild;
- preserve scroll position, current view, expanded panels and user input;
- heavy lists load only on demand.

## Non-goal

TLIB must never maximize throughput at the expense of Windows responsiveness. Throughput is opportunistic and adaptive.
