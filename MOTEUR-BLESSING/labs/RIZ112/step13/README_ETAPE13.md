# RIZ112 — Étape 13 : sous-paramètres et anticipations (banc d'essai)

**But :** comparer des situations ayant les mêmes 112 rubriques sémantiques, avec valeurs initiales différentes, sans transformer ces rubriques en 112 coefficients arbitraires.

## Fichiers

- `hierarchy.py` et `REGISTRE_HIERARCHIE_112.json` : 112 rubriques → sous-paramètres → sous-sous-paramètres (998 *emplacements structurels*, non 998 facteurs estimés) et anticipations.
- `causal_demo.py` : modèle de dépendances thermiques **illustratif**, riz/eau/chaleur, matériel, couvercle, états et politiques conditionnelles ; `per_case_impact_contract` expose les 112 rôles.
- `build_stage13.py` : comparaison de six configurations de récipient et 100 situations synthétiques.
- `MARMITES_SCENARIOS_CONTROLES.json`, `POPULATION_100_HIERARCHIQUE.json` : résultats intégralement reproductibles avec graines fixées.
- `test_stage13.py`, `FULL_TEST_REPORT.json` : régressions et tests spécifiques.

## Démonstration

Depuis le dossier racine `RIZ112_CAHIER_MERE` :

```bash
python step13/build_stage13.py
python -m unittest discover -s step13 -p 'test_stage13.py' -q
python step13/causal_demo.py step6/examples/A_couvercle_ajuste_112.json --draws 1000
```

## Contraintes scientifiques

- `ic_demo_percent` = pourcentage de scénarios synthétiques atteignant une *qualité fictive* `Q* >= 85`, PAS P(vrai bon riz).
- Le seuil de décision de l'utilisateur, 0,25 (25%), ne doit pas être confondu avec Q* ≥ 85/100.
- Les constantes de matériaux, les résistances, les seuils, les pertes de débordement, les priors et les critères de qualité sont des **hypothèses pédagogiques**, pas une calibration.
- Les matériaux tels que le bois peuvent présenter des problèmes de sécurité en chauffe directe. **Ne pas utiliser le modèle comme instruction pratique de cuisson.**
- Les 14 définitions de la cible sont gelées ; elles ne sont PAS des observations futures utilisées pour prédire ; en cas de modification, le moteur refuse l'ancien contrat.
- Une variable inconnue reçoit si nécessaire un prior synthétique nommé et rapporté ; elle n'est pas remplacée silencieusement par zéro.
- Les politiques futures sont des anticipations non observées ; une planification impossible est corrigée dans le scénario sans effacer l'observation initiale.
- Les 112 rubriques restent auditées. Leur présence dans la trace ne prouve PAS 112 influences causales ou numériques. Seules les voies ayant une formule raccordée interviennent dans la simulation.
- L'apprentissage et la validation réels nécessitent des échantillons qualité Q observés avant de produire `scientific_ic_percent`.

**Sources indicatives :** https://www.engineeringtoolbox.com/thermal-conductivity-d_429.html ; https://pubmed.ncbi.nlm.nih.gov/28370117/ ; https://pubmed.ncbi.nlm.nih.gov/29792958/
