# ERROR INDEX - BuildHub

Capture initiale: 2026-09-18T16:58:00Z

> Vue humaine compacte. Source machine: `ERROR_LEDGER.jsonl`.

| event_id | phase | severity | error_class | root cause | status |
|---|---|---:|---|---|---|
| BH-20260918-001 | BUILD | HIGH | `POWERSHELL_ARGUMENTLIST_CARDINALITY` | CONFIRMED | RESOLVED |
| BH-20260918-002 | RUNTIME | HIGH | `PROCESS_LIFETIME_CONSOLE_INTERRUPT` | STRONG_CANDIDATE | OPEN |
| BH-20260918-003 | INSTALL | P0 | `PAYLOAD_COMPLETENESS_IMPORT_FAILURE` | CONFIRMED | OPEN |
| BH-20260918-004 | RECOVERY | P0 | `STALE_RECOVERY_REPLAY` | CONFIRMED | RESOLVED |
| BH-20260918-005 | INSTALL | HIGH | `CONTROL_JSON_ENCODING_BOM` | CONFIRMED | OPEN |
| BH-20260918-006 | RELEASE | P0 | `COMMIT_WITHOUT_TARGET_READBACK` | CONFIRMED | RESOLVED |
| BH-20260918-007 | RUNTIME | P0 | `HEARTBEAT_INSUFFICIENT` | CONFIRMED | PARTIAL |
| BH-20260918-008 | BUILD | P0 | `BUILD_IDEMPOTENCE_GAP` | STRONG_CANDIDATE | OPEN |
| BH-20260918-009 | RELEASE | P0 | `PARTIAL_PUBLICATION_RISK` | CONFIRMED | OPEN |
| BH-20260918-010 | BUILD | P0 | `EXTERNAL_QUOTA_SINGLE_POINT_OF_FAILURE` | CONFIRMED | DEFINED |

## Regles
- Append-only: ne pas reecrire une entree historique; une evolution future ajoute un nouvel evenement qui reference `supersedes_event_id` si necessaire.
- Deduplication par mecanisme causal; `occurrence_count` agrege les repetitions equivalentes.
- Aucun secret/token/mot de passe ne doit entrer dans le ledger.
- Un incident n est clos que si la preuve de correction et la regression correspondante existent.
