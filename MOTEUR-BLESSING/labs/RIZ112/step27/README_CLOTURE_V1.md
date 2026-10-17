# RIZ-112 — clôture d’ingénierie V1 (Step27)

Le moteur reçoit des données pré-T0, conserve les **112 rubriques** et utilise ses mécanismes historiques H3/H4 ainsi que ses bilans physiques Step20. Les audits ne démontrent **aucun effet empirique sur Q** : 9 mécanismes intermédiaires, 29 routes de planification, 14 cibles post-T0, 60 autres rôles. Cette ventilation ne prouve ni 112 contributions indépendantes ni 112 variations de score.

## Terminé maintenant
- Exécutable hors ligne sur Windows 11 faible RAM ; raccourci bureau.
- Codes, rapports, journal et checkpoints GitHub réutilisables par `Moteur/continue`.
- Schémas de collecte pré-T0/post-T0, blocage des dossiers synthétiques présentés comme réels et vérificateur des essais.
- Proposition **concrète mais non approuvée** de Q et de porte non compensatoire, sans implémenter un coefficient imaginaire comme fait acquis.
- Contrôle de clôture reproductible par `python step27/release_gate.py --lab-root . --output step27/RECU_CLOTURE_INGENIERIE_V1.json`.

## Exigences externes impossibles à automatiser honnêtement
1. Accord utilisateur explicite sur échelles, seuils et pondérations proposés. L’utilisateur n’a confirmé que la priorité tendreté (101) + séparation (102).
2. Vraies cuissons horodatées avec données initiales gelées **avant** T0 ; observations sensorielles/physiques **après** T0, indépendantes du modèle. Le compteur est actuellement **0**.
3. Calibration et vérification temporelle hors-échantillon des IC prédictifs. Aucun seuil de 12 essais ne garantit une puissance statistique suffisante.

**RIZ-112 logiciel = clôturable. RIZ-112 IC réel = non validé**, preuve de production absente. Le score `scientific_ic_percent` reste `null`. Ce rapport est une clôture technique, jamais une certification du riz ni de sa sécurité alimentaire.

La proposition numérique est dans `PROPOSITION_Q_DECISION_A_VALIDER.json`, volontairement NON ACTIVÉE.
