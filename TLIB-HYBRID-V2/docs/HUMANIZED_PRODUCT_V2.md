# TLIB Humanized Product V2

## North star

TLIB is not a GitHub scanner. It is a personal technical library that progressively turns discovered resources into useful, searchable knowledge.

The user-facing vocabulary is:

- **L0 — Repérage**: “J'ai trouvé quelque chose.”
- **L1 — Vérification**: “Je sais ce que c'est.”
- **L2 — Compréhension**: “Je sais à quoi ça sert, pour qui, comment, avec quelles limites.”
- **L3 — Conversation**: “Je peux parler avec ma bibliothèque.”

## Visible surfaces

### Accueil
Shows the four levels, current work, PC worker state, Apps Script state, and three primary actions: Search, Explore, Manager.

### Explorer
Human cards, not raw database rows. Search by name, language, description or topic.

### Fiche
Explains the resource in plain language and exposes technical details only in a secondary block.

### Manager
Human operational view:
- what is running;
- what is waiting;
- what is blocked;
- what the PC is doing;
- what Apps Script is doing;
- safe canary controls.

### Technique
Raw counters, queue states, paths and diagnostics for maintenance only.

## Runtime split

- **Apps Script**: always-on coordinator, L0 discovery, durable state, future atomic leases.
- **PC Worker**: bounded deterministic L1 work, SQLite cache/queue, local dashboard, future L2 preprocessing.
- **AI**: not used for every L1 entity. Reserved for L2 semantic work and ambiguous cases.
- **Google Sheets**: control plane and observability, not the future high-volume transactional database.
- **Drive**: durable project artifacts.
- **Desktop Commander**: bootstrap/repair only, never the hot path.

## Scale

Do not shard the 120,694 rows merely because the number looks large. First move hot transactional work to SQLite and introduce stable leases. If sharding becomes necessary later, shard cold data by stable entity hash/generation while retaining one global entity identity space.

## Immediate gates

1. Humanized cockpit running on the PC.
2. Local SQLite self-test.
3. 10-item L1 fixture canary.
4. Apps Script lease bridge implementation.
5. Secure GitHub authentication.
6. 100-item live L1 canary.
7. Adaptive 1k ramp.
8. L2 schema + first semantic cohort.
