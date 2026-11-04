# KIN MOTO — FACTORY 3.0 (incubation A0)

**Projet :** jeu moto-taxi 3D/PWA inspiré de Kinshasa. **Budget :** 0 FC supplémentaire obligatoire.

**Statut :** atelier documentaire A0, **pas** une nouvelle version jouable ni une V1 acceptée.

**Dépôt d'incubation** : `Terminator364/PROJECT-DRAFTS`, sous-dossier `KINMOTO/`. ⚠️ **État vérifié : le dépôt est PUBLIC malgré son README racine qui le décrit comme privé. A1 SUSPENDU jusqu'à décision de confidentialité.** Le dépôt dédié sera envisagé après validation de l'architecture, conformément à `../NEW_PROJECT_BOOTSTRAP.md`. Aucun autre projet du dépôt ne doit être modifié.

**Règles de priorité** : lire `../AGENTS.md` et `../CI_BUDGET_POLICY.json` avant toute opération. Actions hébergées = **0 min par défaut**, aucun workflow automatique. Les scripts `scripts/` s'exécutent localement.

## Documents de référence
- `docs/CHARTER.md` : charte maîtresse, vision et gouvernance ;
- `docs/RUNBOOK_CHAT_WORK.md` : protocole conversation pilote ↔ Work ;
- `docs/AUDIT_TECHNIQUE_QA.md` : audit contradictoire et contrôles ;
- `DECISIONS.md` : décisions actées, propositions et interdictions ;
- `PROJECT_STATE.json` : état machine lisible ;
- `NEXT_ACTION.md` : prochaine opération ;
- `docs/HISTORICAL_ARCHIVES.md` : manifeste de conservation des prototypes ;
- `tasks/` : tickets A1/A2/A3 ;
- `docs/SESSION_LOGS/` : journal et preuves de reprise.

## Comment travailler
1. Ouvrir `PROJECT_STATE.json` puis `NEXT_ACTION.md` et le ticket actif.
2. Vérifier les interdits (0 FC, pas de publication STABLE, pas de secrets).
3. Réaliser **un ticket borné sur branche**, tests et captures à l'appui.
4. Écrire le commit, rapport QA, anomalies et action suivante.
5. Soumettre la version de test à validation humaine avant publication.

## Commande locale à coût nul
```bash
python KINMOTO/scripts/verify_factory.py KINMOTO
```

## Continuité
`KINMOTO|SYNC` (lecture et résumé) ; `KINMOTO|A0|GO` (infrastructure) ; `KINMOTO|WORK|CONTINUE` ; `KINMOTO|AUDIT` ; `KINMOTO|SAVE` ; `KINMOTO|RELEASE|CHECK`.

Ces codes ne créent aucune automatisation en arrière-plan ; seul le dépôt et les preuves font foi.
