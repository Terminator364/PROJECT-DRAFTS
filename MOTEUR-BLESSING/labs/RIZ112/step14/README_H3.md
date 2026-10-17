# RIZ-112 — H3 : nouvelles anticipations physiques imbriquées

## Reprise
**Référence :** Cahier mère RIZ-112, D025–D027. Nouveau lot D028–D029. Code `RIZ112|CONTINUE`.

## Ce qui s'exécute désormais

- **006 — Source d'énergie** : sous-paramètre `source_uptime` dans [0,1]. Calcul `P1 = P_nominale × eta_interface × source_uptime` ; représente la disponibilité prospective de la source durant le temps prévu.
- **069 — Maintien du régime** : sous-paramètre `regulation_duty` dans [0,1]. Calcul `P2 = P1 × regulation_duty`. Deux fractions de disponibilité successives et distinctes, pas deux bonus ajoutés au Q.
- **039 — Température ambiante** : sous-paramètres `ambient_C` et `ambient_UA_W_per_K`. Pertes de démonstration `P_amb = UA × max(0,100°C - Tamb)`, puis puissance nette `max(0,P2 - P_amb)`. **Ne PAS appliquer cette soustraction à un rendement déjà mesuré net de pertes environnementales** : risque de double comptage ; exiger un rendement d'interface distinct.
- **025 — Longueur du grain** : longueur, rapport d'aspect, longueur de référence et `diffusion_ratio` **déclarés avant T0**, déterminant un temps chaud hypothétique `t = t_ref × [(L/aspect)/(Lref/aspectref)]² / diffusion_ratio` ; la longueur n'est pas à elle seule la longueur de pénétration, d'où l'aspect ratio explicite. Ce modèle est une analogie de diffusion, **pas** une loi expérimentale validée de cuisson du riz.
- **087 — Politique d'ajout d'eau** : branche de correction *pré-déclarée* avec seuil, quantité et probabilité d'exécution de démonstration ; le modèle estime « sans » et « avec », sur **les mêmes réalisations d'incertitude**.

Toutes les variantes gardent un IC **de démonstration Q\***, jamais une probabilité réelle de succès alimentaire. Les critères finaux restent cibles, jamais prédicteurs. Une trajectoire avec puissance nette nulle donne conventionnellement 0 % pour le proxy thermique du modèle, et `scientific_ic_percent = null`.

## Exécution minimale

Depuis la racine `RIZ112_CAHIER_MERE` :

```bash
python step14/anticipatory_physics_h3.py --material copper --ambient 24 --ambient-UA 1 --draws 1000
python step14/build_h3_cases.py
python step14/run_regression_h3.py
```

Le script `build_h3_cases.py` fait passer les 100 dossiers H2 de 112 rôles par des nouvelles sous-hypothèses (pré-T0), calcule une ablation à 3 000 tirages, produit un nouveau registre des 26 anciennes lacunes.

## Références des résultats

- `step14/H3_100_RESULTS.jsonl` — 100 nouveaux dossiers de scénario dérivés, rapports distincts
- `step14/H3_POPULATION_REPORT.json` — agrégats des 100 essais
- `step14/H3_ABLATIONS.json` — comparaisons ceteris paribus et mêmes tirages
- `step14/H3_26_CASES_LEDGER.json` — **4 chemins numériques hypothétiques nouveaux**, **22 lacunes restantes**, **0 effet empirique validé**
- `step14/H3_REGRESSION.json` — exécution des **309 tests**.

## Frontière de validité

Le seuil 85 est utilisé sur **Q\* fictif**, minimum de quatre substituts ; il n'existe pas d'expérience mesurant le vrai Q et de calibration. Les coefficients d'interface, de perte `UA`, de géométrie, les taux de disponibilité et de régulation sont des **hypothèses conditionnelles fournies**, pas des constantes universelles. Les probabilités générées n'autorisent ni instructions de cuisson, ni décisions de sécurité, ni transfert de coefficients à MATRICE.
