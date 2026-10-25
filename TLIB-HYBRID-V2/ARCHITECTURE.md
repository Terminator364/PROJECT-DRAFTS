# Architecture

## Existing engine
TLIB V1.1 already proved L0 FAST-INGEST:
- 120,694 L0 entities
- frontier drained
- Apps Script tick every 15 minutes
- L1 GraphQL path exists but is disabled until authenticated GitHub access is configured.

## Hybrid target
```
Google Sheets / Drive
        |
   Apps Script
        |
  lease/commit API
        |
  TLIB-PC-Agent
  |    |      |
SQLite GitHub dashboard
```

## Responsibilities

### Apps Script
- always-on lightweight orchestrator;
- owns canonical queue state and leases;
- recovers expired leases;
- writes compact metrics and milestones;
- keeps working when the PC is off.

### PC worker
- runs only when Windows is available;
- processes bounded batches;
- deterministic metadata enrichment, filtering, normalization and scoring;
- local SQLite WAL database for crash-safe work;
- resumes after network or power loss;
- never loads the full 120k population in memory.

### AI
Not part of L1 bulk ingestion. AI is reserved for L2 semantic understanding or ambiguous cases after deterministic filtering.

## Lease protocol planned for Phase B
A work item transitions:
PENDING -> LEASED -> DONE
or
PENDING -> LEASED -> RETRY

Each lease carries:
- lease_id
- worker_id
- leased_at
- lease_expires_at
- attempt
- entity_id

Expired leases return to PENDING. Commits are idempotent by entity_id + enrichment_version.

## Scale policy
Google Sheets remains a control plane, not the long-term transactional database.
Do not arbitrarily split at 75k/100k yet. If cold data must be sharded later, shard by stable entity hash prefix or generation while keeping a single logical entity_id namespace.

## RAM policy
Target normal resident memory: well below 250 MB on the 4 GB Windows PC.
- sequential/low-concurrency network work;
- bounded result windows;
- SQLite rather than in-memory maps;
- adaptive concurrency can be added only after measurement.

## Security
- no GitHub token in repository;
- no secret in Drive/Sheets;
- dashboard binds to 127.0.0.1 only;
- public repo contains code and non-sensitive public repository names only;
- production credentials are introduced only after the canary succeeds.
