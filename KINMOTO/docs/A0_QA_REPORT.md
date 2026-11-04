# FACTORY A0 — Rapport QA d'installation

Édition : 2026-11-04. Mandat : `KINMOTO|A0|GO`. Ce rapport ne certifie **aucun** jeu.

## Preuves déjà vérifiées
- `Terminator364/PROJECT-DRAFTS` : dépôt incubateur existant, privé, règle `NEW_PROJECT_BOOTSTRAP.md` lue.
- Politique root `AGENTS.md` et `CI_BUDGET_POLICY.json` : 0 GitHub-hosted minute/jour par défaut, pas de workflow automatique ; aucune CI hébergée KINMOTO activée.
- KINMOTO : 27 fichiers créés sur branche `kinmoto/factory-a0` et comparaison GitHub = **27 fichiers ajoutés, tous sous KINMOTO/**, avant les ajouts finaux de preuves.
- Test local gratuit : `PASS A0 local verification: 16 required files; 6 historical archives; zero hosted CI; no release changes`.
- Archives historiques : 6 ZIP avec SHA-256 complets, présents sur Drive, tailles lues et conformes.
- Source pack A0 supplémentaire : ZIP sur Drive, existence et taille contrôlées.
- Tickets : [A1](https://github.com/Terminator364/PROJECT-DRAFTS/issues/19), [A2](https://github.com/Terminator364/PROJECT-DRAFTS/issues/20), [A3](https://github.com/Terminator364/PROJECT-DRAFTS/issues/21).
- Aucune modification du jeu, ni des déploiements publics, ni des autres sous-projets.

## Critères restant à clôturer
- Fusion de la branche A0 après relecture des changements.
- Simulation de reprise par lecture indépendante du trio `PROJECT_STATE.json`, `NEXT_ACTION.md`, `docs/RUNBOOK_CHAT_WORK.md` sur la branche canonique.
- Mise à jour du statut A0 après fusion.

## Non testés par A0
- Nouvel environnement WebGL 3D, conduite, Android et iPhone réels, FPS, RAM, offline : `NOT_TESTED`.
- Quota Work/Plus : `UNKNOWN`; ne pas inventer de solde.

**Conclusion** : l'atelier est documentaire et peut conduire à A1 après vérification de la fusion. Le contrat de qualité V1 reste intact et n'est pas certifié.
