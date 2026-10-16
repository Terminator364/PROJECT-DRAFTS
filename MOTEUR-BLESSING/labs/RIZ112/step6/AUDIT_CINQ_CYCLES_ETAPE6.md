# Construction → Audit → Contre-audit → Correction → Ré-audit, RIZ-112 étape 6

**CYCLE 1 — CONSTRUCTION :** intégration des 112 fiches canoniques au même contrat temporel ; 44 entrées pré-T₀, 4 dérivations/projections, 37 opérations prévues, 13 politiques de réaction possibles, 14 critères finaux strictement post-T₀. Réutilisation sans modification du noyau physique de l'étape 4. Trois dossiers démonstratifs pré-T₀.

**CYCLE 2 — AUDIT :** lecture et traitement des 112 entrées ; 15 cases du noyau dans les équations existantes, 2 dérivations explicites 043/048, 95 cases sans chemin physique numérique indépendant. Aucun IC n'est produit. Chaque case possède une trace `role/status/dependencies/operation` ; la valeur ou le statut est effectivement lu ou calculé.

**CYCLE 3 — CONTRE-AUDIT :** tests de suppression des 44 cases d'entrées, 37 plans, 13 politiques et 14 sorties (chaque groupe), fuite d'une cible post-T₀, labels auto-déclarés, incohérence entre driver physique et registre, ports d'hypothèses / types de données, couvercle et balance absents, chronologie future, scénarios contrefactuels, et non-addition d'un effet de sel non modélisé. Réfutation explicite de « 112 effets prédictifs indépendants ».

**CYCLE 4 — CORRECTIONS :** (a) refus d'une case driver physique déclarée UNKNOWN alors que le noyau possède la valeur ; (b) contrôle des unités, types et domaines, incl. booléens, fractions, non-négativité ; (c) distinction nouvelles dérivations 043 et 048 des effets indépendants ; (d) obligation du protocole Q de rester DRAFT.

**CYCLE 5 — RÉ-AUDIT :** test unitaire V6 **42/42 PASS**, anciennes batteries **22/22** originales, **31/31** étape 5, **10/10** du journal. **Total 105/105 PASS** dans le conteneur ChatGPT Python 3.13, pas de test Windows réalisé dans cette reprise. ZIP et empreinte à renseigner à la clôture.

**NON VALIDÉ :** physique du riz (hypothèses simplificatrices), 95 rôles sans lien numérique physique distinct, qualité Q approuvée, provenance temporelle indépendante, données d'apprentissage réelles, calibration / IC, performance footballistique, installation Windows.
