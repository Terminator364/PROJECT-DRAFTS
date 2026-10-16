# MOTEUR BLESSING — REDRESSEMENT DE LA FORMULE DU RIZ

Date: 16 octobre 2026 — portée: moteur de prédiction pré-match Over 1,5 en temps réglementaire.

## Mandat original utilisateur, non négociable

L'analogie du riz exige un résultat produit par un système cohérent de variables, sous-variables, intervalles, ordre, dépendances, incompatibilités, compensations et scénarios, **pas** une liste de 112 cases « remplies ». Le seuil de 85/100 ne concerne que l'analogie du riz; il n'est pas un seuil automatiquement applicable au football. Pour MATRICE, cela s'applique aux 62 mondes canoniques et sous-paramètres, avec IC individualisé 0-100 construit avant le coup d'envoi.

## Déviation scientifique confirmée (preuve du code original)

- `code/moteur_v112.py:36-38`: en l'absence de modèle ajusté, `score_lambda` rend directement `lam` du championnat, sans utiliser les mécanismes dans une intensité révisée.
- `code/moteur_v112.py:87-100`: malgré `status=REFERENCE_ONLY_NO_SPORTS_TRAINING`, le nombre est placé dans le champ `ic_percent`, ce qui laisse croire à une vraie prédiction individualisée.
- `code/moteur.py:162-190`: les 62 mondes sont obligatoirement présents **par identifiant**; un objet `{}` vide satisfait la présence et aucune des recettes associées n'est calculable sans ses mesures.
- Les quatre packets réels du pilote contiennent **62/62 objets vides**, **0/240 entrées numériques**, **0 mécanisme transversal calculé**, **aucun modèle ajusté**, tandis qu'un nombre `ic_percent` apparaît sur les quatre sorties.
- Les deux matchs historiques de Premier League obtiennent exactement la même référence, **75,13396 %**, malgré des confrontations différentes. Il s'agit d'une baseline partagée, pas d'une analyse de leurs 62 mondes.
- Les 169+18+28+42 tests précédents portent sur des aspects de logiciel; ils ne certifient pas que la finalité « formule du riz » fonctionne sur de vraies données.

## Rôles des 62 mondes V1.1.2

- **55 PREDICTOR_CANDIDATE** : variables observées ou prévisionnelles, formules propres, mécanismes et interactions dont l'effet doit être appris et audité.
- **4 GATE** : identité, données, domaine, règles; gouvernent l'admissibilité plutôt que fournir 4 bonus.
- **1 PRIOR** : référence temporelle de base, jamais substitut du produit final.
- **2 OUTPUT_ONLY** : sorties dérivées; ne comptent pas comme causes indépendantes.
- Les **372 sous-paramètres proposés** restent des **propositions de recherche**, pas 372 mesures réelles validées. La structure n'est pas l'instrumentation.

## Contrat de calcul à imposer avant de prétendre « IC intégral »

1. **Instrumenter** les 62 mondes : chaque monde possède une ligne de traçabilité et un statut réel (`OBSERVED`, `COMPUTED`, `PARTIAL`, `UNKNOWN`, `GATE`, `OUTPUT_ONLY`). Rien n'est implicitement ajouté ou assimilé à zéro.
2. **Exécuter les recettes mathématiques** de chaque monde sur des entrées réelles et datées. Pour chaque sous-paramètre, documenter entrée, unité, domaine, formule, fenêtre et source originelle.
3. **Relier les mondes** par un graphe ordonné (DAG ou scénarios joints), en explicitant causalité proposée, dépendances, compatibilités, risques de double comptage et impossibilités.
4. **Propager les anticipations** (blessures, composition, météo, fatigue…) selon leur disponibilité **avant T**, avec scénarios corrélés et incertitudes, sans compter deux fois le même événement.
5. **Apprendre les effets et les interactions sur vrais matches historiques** avec pré-matches documentés, validation chronologique hors-échantillon, correction sur réussites ET échecs, ablations, comparaison aux références et calibration.
6. **Calculer une probabilité spécifique au match** via une fonction estimée des observations, interactions, règles et scénarios. Une forme possible, non figée : `IC = 100 × sum_s q_s × P_theta(G90 >= 2 | monde_1..monde_62, interactions, scénario_s)`. La formule concrète et les paramètres de `P_theta` doivent être appris et validés, jamais inventés.
7. **Sorties distinctes** : `reference_percent` (ligne de base) et `full_match_specific_ic_percent` (après preuve d'intégration + calibration). **Pas de pourcentage IC intégral** si le profil est vide, les données datées invérifiables ou le modèle absent. Émettre un rapport d'insuffisance, pas une note trompeuse.
8. **Audit contradictoire obligatoire** : chaque chiffre indique les mondes véritablement utilisés, les candidats écartés, les inconnues, la source et l'effet calibré; tester un retrait de monde, une permutation adverse ou un changement de scénario pour démontrer que le calcul n'est pas décoratif.

## Correctif livré maintenant : garde-fou et preuve négative, PAS nouvelle prévision

`rice_formula_integrity_gate.py` vérifie que les identifiants, rôles, présence réelle d'entrées, catalogue, résultats et audits de mécanismes correspondent. Il ne considère pas un simple libellé de monde comme sa participation. Il conserve la baseline dans un champ distinct et renvoie `full_match_specific_ic_percent: null` sur les quatre packets vides. Il n'accepte ni une prétendue preuve temporelle déclarative ni un modèle fictif pour débloquer le score.

`test_rice_formula_integrity_gate.py` : **13 tests PASS** avec les ZIP authentiques V4 et pilote, dans ChatGPT Linux. Cette couche ne remplace pas le travail scientifique encore absent : la reconstruction du vrai calcul 62-mondes et l'entraînement sur preuves pré-match.

## Priorité V5 proposée sans dérive

P0 — Empêcher les fausses sorties `IC` de référence et mettre en quarantaine les quatre résultats antérieurs.
P1 — Pipeline `observations brutes -> sous-paramètres -> recettes monde -> graphe de dépendances -> scénarios joints -> modèle entraîné -> score -> contre-audit`.
P2 — Faire la démonstration sur un match avec journal de **chacune des 62 lignes**, différencier `UNKNOWN`/ `COMPUTED`, montrer l'influence des changements d'entrées documentées.
P3 — Collecte des données historiques PIT, calcul sur matchs en mode rétrospectif scellé, tests d'échec et calibration indépendante.
P4 — Seulement alors autoriser l'expression « moteur complet et IC ». Ne pas modifier l'ADN R8 ni ses règles pré-match.

**État global après ce correctif : `RICE_FORMULA_OBJECTIVE_NOT_YET_MET`; moteur V4 `EXPERIMENTAL_NOT_APPROVED`.**

## Interface opérationnelle protégée (ajout)

`run_prematch_safe.py` exécute **le vrai `code/moteur_v112.py`** sur un packet, puis applique le contrat d'intégrité. Il préserve l'ancien calcul dans `raw_engine_percentage_preserved_for_audit_only`, mais n'expose plus de `full_match_specific_ic_percent` inventé.

Exemple : `python run_prematch_safe.py --engine-root <dossier_source_v4> --packet <packet_prematch.json> --output <audit.json>`.

**Quatre exécutions réelles de bout en bout PASS** avec les quatre packets du pilote ; dans les quatre cas, sortie `ABSTAIN_RICE_FORMULA_NOT_INTEGRATED`, `full_match_specific_ic_percent=null`. Cette interface est une protection, **pas** une implémentation de toutes les interactions prédictives demandées.
