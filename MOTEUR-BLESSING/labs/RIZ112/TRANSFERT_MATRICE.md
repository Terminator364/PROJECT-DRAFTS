# Contrat de transfert RIZ-112 → MATRICE

Ce laboratoire est **un banc d'essai pour la méthode**, et non un changement de métier ou de finalité du moteur sportif.

## Critères obligatoires avant transposition

1. Données JSON pré-T₀ typées (observation, hypothèse, action annoncée, règle de contrôle, sortie ciblée). Chaque valeur a une source, un instant de disponibilité et un niveau de vérification indépendant.
2. Chaque monde/case porte **sa propre formulation mathématique** lorsque pertinente. Un champ inventorié mais non consommé n'est pas compté comme « actif ».
3. Un graphe de dépendances prouve quelles entrées ont modifié quelles sorties ; analyses contrefactuelles quantifient les effets conjoints et signalent redondances.
4. Aucune preuve de disponibilité rétrospective fabriquée ; aucun résultat d'un match déjà joué ne rentre dans l'analyse pré-match.
5. Une prédiction IC n'est fournie que si sa chaîne complète est numériquement active, son domaine valide, son apprentissage et sa calibration réels, et son audit hors-échantillon réussis. Une baseline est étiquetée BASELINE_ONLY, jamais MOTOR_FULL.
6. L'incertitude jointe et les données UNKNOWN doivent être représentées ; les variables de garde, sorties et indicateurs composites ne deviennent pas des bonus indépendants.
7. Pas de paramètre live : horodatage de gel avant le coup d'envoi ; cible sportive = **Over 1,5 buts réglementaires 90 minutes**, pas prolongation/penalty.

## Critère anti-régression des quatre matchs du 16 octobre

Le pilote conservé dans `mb1/pilots/20261016_four_matches` avait **0 observations mondes et 0 mécanisme transversal calculé**. Il serait techniquement interdit de présenter son unique Poisson de ligue comme IC construit depuis les 62 mondes. L'expérience RIZ-112 doit servir à construire un test qui rejette explicitement cette erreur de couverture et de traçabilité, sans prétendre que toute case est obligatoirement un prédicteur indépendant.

## Interface de reprise souhaitée

- `input_snapshot.json`: données pré-T₀ avec hash, horodatages et schéma.
- `mechanism_graph_trace.json`: graphe et lignée des calculs actifs, unités, intervalles et contraintes.
- `label_protocol.json`: définition pré-enregistrée de l'événement observé, **pas disponible pendant l'inférence**.
- `model_card.json`: données d'apprentissage, sélection, calibration, hors-échantillon et limites.
- `prediction.json`: IC calibré ou abstention expliquée, nombre de mondes effectivement utilisés et preuves.

Le transfert n'est pas exécuté dans MATRICE à ce stade ; il devra être autorisé par une revue d'interface et suivi dans la feuille de route MATRICE, sans effacer ses propres checkpoints.

## Leçon opérationnelle de l'étape 6 — anti-faux « tous mondes intégrés »

Adapter le contrat 112 à MATRICE en remplaçant la grille par les **62 mondes canoniques**, chaque monde portant : `ROLE`, `SOURCE/PIT`, `FORMULE_EFFECTIVEMENT_EVALUÉE`, `CONTRIBUTION_DIRECTE_OU_DEPENDANCE`, `OBSERVATION_CONNUE/UNKNOWN`, `SORTIE_SEULEMENT`, `COEFFICIENT_CALIBRÉ_OU_NON`, `ÉTAT_FILTRE`. Une preuve de 62/62 rôles validés est distincte de 62/62 contributions quantitatives. Les mondes de gouvernance et les sorties doivent participer à l'admissibilité ou à la définition de la tâche, **jamais comme des bonus de buts ou des observations futures**.

**Condition de non-régression** : rejeter tout rapport présentant un IC Over 1,5 issu du seul prior Poisson comme si les 62 mondes avaient contribué. L'absence d'une formule pertinente se rapporte comme `NOT_MODELED` / `ABSTAIN` et non une valeur zéro déguisée.
