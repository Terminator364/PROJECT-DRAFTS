# MOTEUR / MATRICE R8 — V1 logique, novembre 2026 non affirmé
**Version de travail : 23 octobre 2026, D062–D066. Code unique : `Moteur/continue`.**

## Ce que calcule le système et ce qu'il ne calcule pas
La source R8 canonique comprend 62 familles et 355 sous-paramètres, distribués sur deux équipes (710 positions de preuve pré-match). Le système lit ces contrats originaux, récupère les 12 archives réelles, cartographie les dépendances documentaires et construit sept étapes **conceptuelles** : origine/provenance, capacités des équipes, contexte externe, création d'occasions, opposition défensive, conversion conditionnelle, branches conditionnelles de score.

**Aucun de ces 355 contrats n'est transformé automatiquement en coefficient positif ou négatif sur les buts.** Le moteur V0.2 comporte 31 entrées expérimentales, dont 10 soumises à des retenues sémantiques, et 324 autres entrées restent sans mécanisme individuel signé et justifié. Les 1 088 relations de source sont **documentaires** : ni causalités démontrées ni événements indépendants.

Les 355 fiches opérationnelles produites pour la source privée préservent les exigences de données, la provenance, les propriétaires d'anti-double-compte, six horizons de preuve et les conditions de scénarios **telles qu'elles sont écrites à l'origine**, même lorsqu'aucune définition prose n'existe. Une fiche complète n'est PAS une causalité calibrée.

## Deux modèles d'IC conditionnels, mathématiquement définis

**Modèle A : buts indépendants de Poisson**. Si `lambda_A` et `lambda_B` sont explicitement fournis comme hypothèses pré-match, alors :
`IC(Over 1,5) = 100 × (1 - exp(-(lambda_A + lambda_B)) × (1 + lambda_A + lambda_B))`.
Les taux ne sont pas estimés par les 355 seuls. Exemple **strictement synthétique** : taux supposés 1,1 et 0,9 ; résultat théorique 59,3994 %, **pas une prédiction réelle**.

**Modèle B : occasions projetées et conversion indépendante (Poisson-binomial)**. Pour chaque opportunité future **hypothétique** `i`, saisir `p_i = P(but | occasion projetée i)`. On calcule exactement `P(0)` et `P(1)` par récursion puis `P(≥2)=1-P(0)-P(1)`. Le moteur rejette IDs d'occasions partagées, sources hors catalogue et événements observés après T0. Exemple synthétique à quatre occasions `[0,2 ; 0,3 ; 0,1 ; 0,25]` : IC 19,75 %. Les nombres d'occasions et leurs probabilités sont des **hypothèses exogènes**, jamais une promesse de l'avenir.

**1 000 scénarios de sensibilité** : générateur `25 × 40` couples distincts de taux de buts supposés ; aucun match historique ni comparaison réelle n'est utilisé. Ne pas confondre avec 1 000 prédictions validées, les 1 000 ICS riz112, ou une précision de 85 %.

## Utilisation dans un clone de R8 privé

Le programme `moteur_unique_v1.py` accepte un répertoire de source R8, compile le registre V22, remonte les archives, route les 355 fiches, calcule au besoin l'IC de l'un ou des deux modèles, et écrit un `MANIFEST_SHA256.json` plus les résultats. Le corpus enrichi reste dans un dossier privé, pas dans le dépôt GitHub public.

```sh
python moteur_unique_v1.py --r8-repo-root /chemin/vers/ChatGPT-PC --outdir /chemin/prive/moteur-resultats --grid-1000
```

Pour un exemple **de laboratoire seulement**, ajouter `--fixture cas_pret0.json --rates taux_hypothetique.json --projected-shots occasions_hypothetiques.json`. Le JSON du cas inclut `fixture_id`, `analysis_asof_utc`, `kickoff_utc`, `facts`; l'hypothèse de taux inclut `source_kind: SYNTHETIC_ASSUMPTION_ONLY`, `declared_at_utc`, `lambda_A`, `lambda_B`; les occasions utilisent `projection_kind: HYPOTHETICAL_PRET0_SHOT_EVENTS` et des `shot_slot_id` distincts.

**Mode sans hypothèses** : le calcul numérique reste `null`. **Mode avec hypothèses** : un pourcentage conditionnel est délivré, avec `IC_calibrated: null` et `accuracy: null`. Une formule mathématiquement exacte sous ses hypothèses n'est pas une prédiction de match fiable sans validation historique.

## Critères de fiabilité qui restent obligatoires
Il faut encore obtenir des jeux de données sportifs publiés **avant chaque cutoff** (J−6 / J−5 / J−3 / J−1 / H−9 / H−1), vérifier leur identité et leurs droits, reconstruire la qualité/volume des occasions, estimer des taux pré-match à partir d'un modèle mesurable (et non de scores futurs), tester les corrélations, calibrer sur saisons temporellement séparées, puis publier métriques hors-échantillon (Brier, calibration, log-loss et erreurs par strate). Tant que cela n'est pas réalisé, l'IC numérique validé n'existe pas.

**Déploiement** : code public dans `Terminator364/PROJECT-DRAFTS/MOTEUR-BLESSING/labs/MATRICE_LOGIC_FIRST_V03/`. Le dépôt source `Terminator364/ChatGPT-PC`, branche R8 d'audit privée, est l'emplacement des reproductions et résultats enrichis. La branche canonique R8 reste inchangée. La validation intégrée D065–D066 doit être jugée uniquement sur ses reçus CI réels.
