# BCP V2 — Reçu de construction, tests et démarrage (17 octobre 2026)

Projet : `Terminator364/PROJECT-DRAFTS`, branche `experiment/bcp-autonomous-data-run-2026-10-17`.

## Preuves constatées sur MBMPC

- Fichiers installés : `v2/collector.py`, `v2/test_collector.py`, `v2/matrice_62_registry.json`
- Dossier PC : `C:\Users\Lenovo\BCP_AUTONOMOUS_TEST_20261017\v2`
- Source de l'inventaire : `Terminator364/ChatGPT-PC`, branche `research/matrice-r8-g3-depth-audit-2026-10-14`, `MATRICE/R8_G3_DEEP_20261014/parameter_62_individual_audit_20261015/AUDIT_62_INDEX_COMPARATIF.csv`.
- Familles : **62**, identifiants uniques, `ic_effect=DISABLED`. Qualification : 4 `DERIVABLE_RESEARCH`, 9 `PARTIAL`, 2 `METADATA`, 47 `UNAVAILABLE_FROM_RESULT_ARCHIVES`.
- Tests : **7/7 OK**, incluant dates futures et du jour, résultats erronés, doublons, colonnes manquantes, 62 familles, archives immuables et idempotence.
- Première passe intégration : **COMPLETED**, run `BCP-V2-20261017T165656Z`, 10/10 sources, 2049 matchs antérieurs au jour, 10 objets SHA-256 archivés, 1 059 787 octets sources, reçu local `integration/receipt.json`.
- Worker indépendant : **RUNNING** au premier contrôle, run `BCP-V2-20261017T165821Z`, processus Windows `pythonw.exe` PID `13216`, initialisé le 2026-10-17 vers 16:58 UTC, seconde vérification du checkpoint à 16:59:05 UTC.
- Worker `runtime` après premier cycle : **10/10 sources validées**, **2049 matchs**, `heartbeat_utc=2026-10-17T16:59:05+00:00`.
- Durée programmée : **3600 sec**, refresh toutes les 1800 sec, signal d'activité 60 sec.

## Limites documentées

Ce reçu prouve un lancement indépendant et une première collecte complète, **pas** la clôture de l'heure entière. Pas d'IA indépendante ni de recherche autonome sur les 62 familles. Couverture de colonnes source ≠ couverture des phénomènes. Publication/availability historique des données non vérifiée : `RESEARCH_ONLY`, aucun test rétroactif PIT certifié, aucun IC calculé, aucun code officiel MATRICE modifié. Ne pas déployer ce prototype comme estimateur scientifique.

Les fichiers `runtime/manifest.json`, `runtime/coverage_62.json`, `runtime/events.jsonl`, `runtime/checkpoint.json` et, après exécution complète, `runtime/receipt.json` sont conservés localement sur MBMPC. Pas de synchronisation automatique du résultat final sur GitHub.
