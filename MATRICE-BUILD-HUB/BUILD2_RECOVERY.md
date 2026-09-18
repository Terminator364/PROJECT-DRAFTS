# BUILD 2 — RECOVERY

Continuation code: **BUILD2 CONTINUE**

## Authority already ingested
- PROJECT-DRAFTS issue #1: P2PCR95 18-point field backlog.
- Issue #1 comment: PhoneMouse 17-point autonomous-builder addendum.
- PROJECT-DRAFTS issue #2: BUILD 2 unified convergence authority.

## Current engineering branch
`build2-unified-lanes-20260918`

## Core invariants
One shared BuildHub core, isolated project lanes, namespaced run state/heartbeat/receipts/logs/artifacts, one bounded global heavy-build slot, stable run_id/idempotence, zero-manual normal flow, named operations only, atomic publication.

## P2PCR95 pinned candidate
Branch `beta03-field-socket-fallback-20260918`
SHA `c673f2a9f36477c35c65e9d87dec04590ef9551c`
Marker `release/BUILD_READY_BUILD1.json`

## PhoneMouse mandatory transfer
Low-RAM Gradle profile; cache/local-first; deterministic BETA11 reconstruction; canonical overrides only; CRLF/LF guard; beta11_preflight; signing continuity; atomic canonical publication; heartbeat/readback; crash recovery; no duplicate build; adaptive resource gate; local builder BREAK_GLASS_ONLY.

## ChatGPT-PC
Formal project-specific BuildHub packet not yet observed. Search and ingest it on resume; do not invent.

## Next atomic implementation action
Wire `managed-app/lane_runtime.py` into bridge operation dispatch behind BUILD 2 branch only; add doctor/heartbeat/get_receipt/cancel_build contracts and regression tests before packaging or field deployment.

## Promotion rule
Do not replace BUILD 1 terrain until BUILD 2 static/unit regression passes. Then deploy transactionally with rollback and prove PhoneMouse + P2PCR95 E2E plus fresh-app APK creation.
