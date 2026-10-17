# RIZ-112 V12 — 100 dossiers complets, effets tracés

Commande depuis la racine du dossier `RIZ112_CAHIER_MERE` :

```bash
python step12/full_variation_v12.py --count 100 --draws 500 --out step12/POPULATION_100_V12.json
python step12/probe_influences_v12.py > step12/COUNTERFACTUAL_112_V12.json
python step12/build_stage12.py
```

Voir `step12/POPULATION_100_COMPLETE_PACKET.jsonl` pour les JSON complets de 100 situations (une ligne par cas). Un même jeu de 14 cibles finales est utilisé pour permettre une comparaison. Les sorties numériques n'estiment QUE `P(Q*_DEMO>=85)` sous lois hypothétiques, pas la probabilité réelle de réussir le riz.

Les 26 lacunes de contribution locale restent dans `GAPS_26_UNRESOLVED.json`. Le modèle ne doit **pas** annoncer 112 effets quantifiés et causalement validés.
