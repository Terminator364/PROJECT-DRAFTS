# RIZ-112 — 1 000 scénarios × 112 rubriques + 1 000 IC_DEMO

**Livraison réelle :** 1 000 scénarios différents, 112 colonnes de rubriques `R001` à `R112` dans chacun, **1 000 IC_DEMO H3** (200 tirages H3 par scénario), aucune abstention, et les **1 000 dossiers pré-T0 complets** avec sources et horodatages hypothétiques. Aucun IC réel de cuisson n'a été calculé. Aucune vraie cuisson ni probabilité empirique.

## Fichiers à consulter

- `RIZ112_1000_SCENARIOS_112_RUBRIQUES_IC_DEMO.xlsx` : tableur quatre onglets — *Synthese*, *1000_scenarios*, *Dictionnaire_112*, *IC_demo_85_plus*.
- `RIZ112_1000_SCENARIOS_112_RUBRIQUES_IC_DEMO.csv` : les 1 000 lignes, 112 rubriques et IC pour filtrer/exploiter.
- `1000_DOSSIERS_PRE_T0_COMPLETS_112.jsonl` : dossier de chaque scénario, avec valeurs, états, timestamps et source **SYNTHÉTIQUE**. Les 4 rubriques dérivées ont des placeholders ou bilans ; les 14 sorties post-T0 sont des contrats non mesurés.
- `DICTIONNAIRE_112_VARIABLES.json` : noms, groupes et limites des 112 rôles, identification des rubriques qui changent.
- `RAPPORT_1000_IC_112.json` : comptes, graine, seuil et SHA256 du CSV.
- `AUDIT_1000_SCENARIOS.jsonl` : traces d'options H3 et de bilans physiques ; elles ne constituent pas des observations.
- `generer_1000_112_ics.py`, `packets_complets.py`, `test_livraison_1000_112.py` : reproduction et tests avec les sources originales sous `RIZ112_CAHIER_MERE/`.

## Définition de « 112 variables »

Les **112 rubriques sont présentes dans chaque ligne**. Elles ne sont pas 112 causes indépendantes et ne peuvent pas toutes être modifiées avant cuisson. Au sein de ce lot, **39 rubriques changent effectivement** (valeur ou statut) ; les **73 autres** sont fixes, inconnues, déduites sans méthode de prévision ou réservées aux sorties non observées après cuisson. Le modèle H3 ne calcule pas 112 coefficients d'influence.

En particulier, `R099`–`R112` ne peuvent pas être pris comme caractéristiques de prédiction : leur observation est postérieure à T0. La préférence de l'utilisateur pour la tendreté `101` et la séparation `102` est une **priorité ordinale**, pas une pondération approuvée.

## Plan numérique

L'ancienne série donnait 690 IC et 310 abstentions principalement parce que l'eau ajoutée dépassait le stock fixé arbitrairement à 350 ml. La nouvelle génération **contraint le stock d'eau synthétique `R002` à être au moins égal au dosage `R035`**, et conserve la balance, la passoire et les autres ressources indispensables aux actions initiales. Les cases sont calculées avec **H3 original** et le bilan physique théorique Step20 sans réécrire leurs lois.

Ce nouvel échantillonnage étant **conditionné à la faisabilité du plan**, les proportions d'IC_DEMO ≥85 ne sont **pas comparables** à une probabilité de qualité du riz réel ni directement aux 20/1000 de l'ancien plan.

## Reproduction (hors ligne)

Dans le dossier de livraison extrait (Python 3.10+ requis) :

```bash
python generer_1000_112_ics.py --n 1000 --draws 200 --dest .
python packets_complets.py
python -m unittest -v test_livraison_1000_112.py
```

Les moteurs originaux sont inclus dans `RIZ112_CAHIER_MERE/` pour permettre ce contrôle hors ligne. **Jamais** charger ces lignes dans le registre d'expériences réelles : `source_class=SYNTHETIC_REHEARSAL_NOT_REAL_OBSERVATION`.

## Transfert de méthode vers MATRICE

Cette maquette teste des dépendances, les contrôles de sources, les interdictions de fuite future, les seuils de refus, et les scénarios contrefactuels. Elle n'entraîne pas MATRICE sportive et ne fournit aucune probabilité de match. L'équivalent sportif devra conserver le gel des données pré-match et apprendre ses probabilités de vrais matchs vérifiables, jamais depuis la cuisine synthétique.
