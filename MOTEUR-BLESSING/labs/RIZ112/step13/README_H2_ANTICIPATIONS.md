# RIZ-112 H2 — Sous-paramètres imbriqués et anticipations *avant T₀*

## Exigence utilisateur

Une rubrique peut posséder plusieurs sous-paramètres, sous-sous-paramètres et anticipations. Plusieurs situations complètes avec les mêmes 112 rôles, mais des valeurs distinctes, doivent traverser **un même moteur** qui interprète leur effet combiné sur la probabilité de réussite. La présence d'une case dans un JSON ou une flèche conceptuelle ne constitue pas une preuve d'effet chiffré.

## Ce que H2 exécute effectivement

Le modèle H1 (`hierarchical_engine.py`) calcule déjà un chemin thermique *supposé* `matériau → conductivité k ; diamètre, épaisseur → résistance thermique ; chauffage → rendement effectif → eau et chaleur`. Le module H2 (`prospective_branches.py`) conserve ce chemin et ajoute trois classes de sous-paramètres :

1. **Profil du riz** : capacité théorique d'absorption (033), temps chaud théorique nécessaire (034), amidon de surface initial (030), fraction retirée au rinçage prévu (054). Ces nombres interviennent dans les **équations du noyau**, non dans des points arbitraires par variété.
2. **Eau initiale et disponibilité** : eau prévue (035), stock total déclaré avant T₀ (002), déficit d'hydratation théorique calculé par les mécanismes existants.
3. **Politique anticipée de correction** (087) : seuil de déficit simulé, dose maximale prévue et probabilité **hypothétique** d'exécution. Pour chaque état futur **simulé**, on compare `Q*_sans_correction` et `Q*_avec_politique` sur les **mêmes tirages**. Le moteur ne lit aucun capteur post-T₀ et ne prétend pas savoir ce que l'utilisateur fera réellement.

La correction disponible est plafonnée par `stock_initial_déclaré - eau_déjà_prévue`. Si ce stock est `UNKNOWN`, elle n'est pas inventée. Une correction peut rester neutre ou dégrader l'indicateur ; le calcul n'ajoute pas de bonus automatique. L'action 054 (rinçage) doit avoir été prévue avant de paramétrer sa fraction.

## Épreuve numérique synthétique

Dossier initial A, `eau prévue = 180 g`, `couvercle posé`, `cuivre supposé`, `diamètre = 18 cm`, `épaisseur = 2 mm`, politique 087 pré-déclarée : déclencheur déficit simulé `> 5 g`, dose `65 g`, adhésion hypothétique `0,75`, stock total `350 g`. À graine fixe et 1 000 tirages, `IC*_DEMO sans correction = 0,40 %` et `IC*_DEMO avec politique = 44,00 %`. **Les deux nombres sont entièrement fictifs** : ils n'estiment pas P(riz réellement réussi). Leur variation sert à vérifier la propagation d'une anticipation, pas à recommander un ajout d'eau ou à prédire une cuisson réelle.

**100 nouveaux scénarios hiérarchiques** : 112 rôles structurels représentés (`44 entrées directes + 37 actions + 13 politiques + 14 cibles + 4 rôles dérivés recalculés`), matériel et géométrie, profil du riz, eau, couvercle et politique variés ; 120 tirages par scénario. `22/100` scénarios ont un IC* différent avec politique, `78/100` non (seuil non atteint, ressource limitée, saturation par une autre dimension, etc.). Résultats et dossiers disponibles dans `H2_100_RESULTS.jsonl` et `H2_100_SCENARIOS_112.jsonl`.

## Contrôles

- 20 tests H1 + 21 tests H2 = 41 tests dans `step13`.
- Total corpus complet : **282/282 tests PASS** (22 étape 4, 31 étape 5, 10 journal, 42 étape 6, 36 étape 7, 19 étape 8, 25 étape 9, 20 étape 10, 13 étape 11, 23 étape 12, 41 étape 13).
- Tests particuliers : mêmes tirages aléatoires avec/sans correction ; le profil du riz influence les nœuds existants ; respect des stocks ; valeurs inconnues ne deviennent pas zéro mesuré ; source originale inchangée ; dérivées non saisies librement ; critères post-T₀ non utilisés.

## Limites / blocages

- `Q*_DEMO` reste le minimum de quatre indicateurs physiques *hypothétiques* et ne représente pas la mesure réelle de la réussite. Les autres 10 dimensions de Q ne sont toujours pas évaluées.
- Le modèle de mur de casserole est une analogie en régime permanent avec hypothèses fortes (contact, flux thermique). Aucune calibration de matériau, source de chaleur ou cuisson réelle.
- La `probabilité d'adhésion` est fournie comme hypothèse avant T₀. Une politique future ne peut être comptée comme exécutée avec certitude sans preuve de cette exécution.
- **Aucune conclusion** que les 112 rubriques modifient toutes `IC*_DEMO`. Le moteur doit continuer à traiter leurs sous-paramètres un par un selon une vraie relation de causalité et un test de sensibilité ; sans relation suffisante, l'absence d'effet restera explicitement signalée.
- Bois non homologué avec chaleur directe : **pas de test réel, pas de recette, pas de pourcentage de sécurité inventé**. Le moteur refuse le parcours non sûr et distingue un hypothétique insert métallique.

## Exécution

Depuis `RIZ112_CAHIER_MERE` :

```bash
python step13/prospective_branches.py --draws 1000
python step13/build_h2_cases.py
python -m unittest discover -s step13 -p 'test_*.py' -q
```

## Transfert vers MATRICE

Conserver la forme : **112 rubriques → arbre de sous-paramètres → équations couplées → anticipations futures fondées sur des informations pré-T₀ → moyenne/intégration sur les scénarios → IC**. Ne transférer aucun seuil, coefficient ou pourcentage de riz. Les paramètres sportifs doivent être estimés et testés séparément à la date de coupure prématch ; les politiques de correction ne sont pas des actions observées pendant le match.
