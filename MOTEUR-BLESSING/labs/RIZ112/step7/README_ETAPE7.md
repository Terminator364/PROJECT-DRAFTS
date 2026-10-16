# RIZ-112 — Étape 7, graphe préstart et contraintes de faisabilité

Ce laboratoire **ne prescrit pas la préparation du riz**. Il étudie un moteur prédictif à partir de données préstart JSON pour transposer une méthode rigoureuse à MATRICE.

- `graph_governor.py` : inspecte les 169 dépendances déclarées, retire de la projection préstart 19 arcs invalides, valide un DAG de 150 arcs / 112 cases, puis exécute 10 vérifications de faisabilité. Refuse tout IC en l'absence d'études réelles.
- `build_stage7.py` : écrit des rapports sur les 3 exemples synthétiques, plus `GAPS_112_V7.json`, dossier justifié de ce qui est calculé, relié, orphelin ou destiné à la mesure finale.
- `test_graph_governor.py` et `test_gap_ledger.py` : 36 tests contraires, y compris les fuites depuis les cibles, cycles et incohérences.

Exécution depuis la racine du Cahier mère :

```sh
python step7/graph_governor.py step6/examples/A_couvercle_ajuste_112.json
python step7/build_stage7.py
python -m unittest discover -s step7 -p 'test_*.py' -q
```

La variable « température initiale », par exemple, peut déjà changer un calcul thermique tout en ne disposant pas d'un chemin Q explicitement justifié dans le graphe contractuel. Elle ne doit ni disparaître ni obtenir une flèche/pondération inventée simplement pour dépasser un indicateur de couverture.

Lire `AUDIT_CINQ_CYCLES_ETAPE7.md` puis `GAPS_112_V7.json`. Les 112 rôles sont opérationnels, mais **l'IC reste `null`**.
