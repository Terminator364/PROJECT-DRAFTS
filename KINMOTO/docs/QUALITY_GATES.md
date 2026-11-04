# Contrat de validation — A0 et versions de jeu

## A0 (infrastructure)
- [ ] GitHub : dépôt privé d'incubation existant identifié, politique propriétaire lue.
- [ ] Fichiers canoniques de KINMOTO committés et relus depuis GitHub.
- [ ] Prototypes archivés avec SHA-256, statut et preuve d'emplacement.
- [ ] Aucun workflow automatique ou runner hébergé déclenché par KINMOTO.
- [ ] Tickets A1/A2/A3 créés avec critères et dépendances.
- [ ] Test de reprise en lisant uniquement PROJECT_STATE.json, NEXT_ACTION.md et RUNBOOK.
- [ ] Pas de modification d'une URL publique ni d'un dépôt produit existant.

## Jeu : portes NON substituables
- G1 Fonctionnel : conduite, missions, collisions, sauvegarde et économie reproductibles.
- G2 Visuel : vraie 3D sur matériel pris en charge, mêmes scènes avant/après, assets/licences.
- G3 Performance : FPS, stutters, RAM/taille/thermique si mesurables sur Android/PC.
- G4 Humain : session réelle 15–20 min, ressenti de conduite, contact roues/sol.
- G5 Légal et coûts : code et chaque asset autorisés, aucun service payant requis.

Verdicts : `PASS`, `FAIL`, `BLOCKED`, `NOT_TESTED`. Une réussite du build **n'implique pas** qualité produit ; seul le commanditaire autorise STABLE.
