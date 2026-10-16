# RIZ112 — routes fonctionnelles D014 (lot de raccordement V8)

Depuis la racine `RIZ112_CAHIER_MERE` :

```bash
python step8/functional_routes.py step6/examples/A_couvercle_ajuste_112.json
python -m unittest discover -s step8 -p 'test_*.py' -q
```

Le code lit les 62 ID EXACTS de `RESTANT_62_REGISTRE.json`. Les routes couvrent : 22 observations ou ressources, 3 prévisions, 26 plans et 11 politiques. Les rapports des trois cas synthétiques se trouvent dans `step8/reports/`. `calibrated_ic_percent` reste `null`. 044 reste sans formule ; le calcul Q réel n'est pas disponible. Les tests 22 sources + 26 plans + 11 branches mutation, plus les tests physiques et temporels, protègent la régression.

Un cas « traité » signifie une opération auditable, non un effet sportif/alimentaire mesuré. Ce lot ne prescrit aucune recette, ne rajoute aucune donnée après T0 et ne modifie pas la version sportive de MATRICE.
