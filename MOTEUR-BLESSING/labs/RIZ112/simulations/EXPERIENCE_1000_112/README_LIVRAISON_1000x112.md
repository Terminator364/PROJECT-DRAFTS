# RIZ-112 | 1 000 scénarios × 112 rubriques + 1 000 IC synthétiques

Date du paquet : 17 octobre 2026. Objet : banc expérimental pour apprendre des dépendances, contrepositions et abstentions avant transfert de la **méthode** à MATRICE pré-match.

## Résultats

- 1 000 dossiers distincts, chacun avec R001–R112 (112 colonnes).
- **98 colonnes pré-T0 ou dérivées ont plusieurs valeurs distinctes**; les **14 rubriques R099–R112 restent NOT_OBSERVED_POST_T0**. On ne peut pas fabriquer leurs valeurs post-cuisson pour prétendre à de vrais labels.
- **1 000 IC_EXPLORATOIRE_PROXY_PCT** numériques, calculés avec le modèle Q* de démonstration existant (Step9) et **200 tirages par scénario** (200 000 tirages modélisés). Valeurs 0.0–94.0 % ; **12 scénarios ≥ 85 %** sous ce seul modèle.
- **IC_H3_ORIGINAL_PCT** : **690** résultats et **310 abstentions conservées** ; 20 des 690 anciens IC H3 sont ≥85 %. Le nouvel IC n'efface pas une abstention de H3.
- Les **9 grandeurs** de l'expérience historique Latin hypercube sont conservées dans les 1 000 scénarios. Les nouveaux rôles sont **des paramètres, états ou politiques SIMULÉS**, jamais des mesures.
- Seules les entrées reliées au noyau physique Q* influencent l'IC exploratoire. **112 colonnes présentes et variables ≠ 112 effets causaux prouvés.**
- L'**AUDIT_PRET0_1000.csv** applique un filtre de ressources et de planification distinct ; il ne modifie jamais l'IC et utilise des approximations déclarées (densité eau 1g/ml, réserve volume 20%). 303 scénarios passent ce crible hypothétique.

## Comment lire les fichiers

1. `RIZ112_1000_SCENARIOS_112_VARIABLES_ET_ICS.xlsx` : classeur lisible, 1 000 lignes, 112 colonnes R001...R112, IC exploratoire pour chaque scénario, colonne distincte IC H3, résumé et dictionnaire.
2. `RIZ112_1000_SCENARIOS_112_RUBRIQUES_1000_IC.csv` : référence tabulaire, séparateur `;` (UTF-8 BOM).
3. `DICTIONNAIRE_112_RUBRIQUES.csv` : sens des identifiants, rôle et niveau de preuve.
4. `RAPPORT_1000x112.json` : distribution et SHA256 de chaque CSV.
5. `AUDIT_PRET0_1000.csv` : garde-fous de ressources et de plan, explicitement hypothétiques.
6. `simuler_112_et_ics.py` + `test_1000x112.py` : code et 7 tests reproductibles, compatibles hors ligne avec les fichiers historiques inclus.

## Sources techniques nécessaires au recalcul

- `simulations/EXPERIENCE_1000/results/SCENARIOS_1000_SYNTHETIQUES.csv` : les 1 000 dossiers physiques originaux.
- `step9/ic_simulation_v1.py`, `step9/DEMONSTRATION_CONTRACT.json` et `reference/step4/riz112.py` : formules Q*, distributions Monte Carlo et noyau physique d'origine.
- `step26/REGISTRE_TRANSVERSAL_112.json` et `step6/examples/A_couvercle_ajuste_112.json` : taxonomie et dossier type.

Relancer, depuis la racine du laboratoire :

```bash
python simulations/EXPERIENCE_1000_112/simuler_112_et_ics.py --out simulations/EXPERIENCE_1000_112/results
python -m unittest discover -s simulations/EXPERIENCE_1000_112 -p "test_*.py" -q
```

**Limites importantes :** aucune vraie cuisson, aucune pondération Q approuvée, aucun taux de réussite réel, **scientific_ic_percent = null**. Un IC_DEMO ou exploratoire est un pourcentage de simulation dépendant des hypothèses. Les états d'actions PLANNED ne prouvent pas leur exécution. Les plans synthétiques peuvent présenter des contradictions réalistes ou une faisabilité insuffisante. L'analyse probabiliste pour MATRICE exigera des données sportives pré-match et une validation spécifique ; ne pas réutiliser tels quels les coefficients du riz.
