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

## Clôture vérifiée
- **PASS :** PR #22 fusionnée par squash, commit `e9446b1ab5d5381e8e8c1961d9110363b51a229a`.
- **PASS :** reprise simulée avec lecture indépendante de `PROJECT_STATE.json`, `NEXT_ACTION.md`, `docs/RUNBOOK_CHAT_WORK.md` depuis GitHub ; résultat A1 #19 identifié.
- **PASS :** `PROJECT_STATE.json` mis à jour sur main avec `A0_COMPLETE`.
- **PASS :** aucun workflow GitHub hébergé pour le commit de la branche A0 ; aucun workflow créé.
- **PASS :** aucun changement hors `KINMOTO/` dans le diff de A0.

## Non testés par A0
- Nouvel environnement WebGL 3D, conduite, Android et iPhone réels, FPS, RAM, offline : `NOT_TESTED`.
- Quota Work/Plus : `UNKNOWN`; ne pas inventer de solde.

**Conclusion** : A0 est clôturée sur main ; A1 reste **NOT_STARTED**. La certification qualité V1 demeure distincte. Le contrat de qualité V1 reste intact et n'est pas certifié.
