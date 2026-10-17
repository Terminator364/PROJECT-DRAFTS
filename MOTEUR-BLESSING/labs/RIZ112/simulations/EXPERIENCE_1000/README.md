# Expérience 1000 — simulation du riz comme banc d'essai MATRICE

**Pas un autre programme autonome :** module de simulation du laboratoire RIZ112 existant, sans second raccourci et sans dépendance cloud ou API. Reprend H3 Step14 et le bilan physique Step20, ne modifie pas la V1 clôturée.

Exécuter les six tests puis les 1000 cas depuis le répertoire `RIZ112_CAHIER_MERE` :

```
python -m unittest discover -s simulations/EXPERIENCE_1000 -p 'test_*.py' -q
python simulations/EXPERIENCE_1000/simuler_1000.py --n 1000 --draws 200 --output simulations/EXPERIENCE_1000/results
```

Le calcul simule 1000 plans de conditions initiales, 200 réalisations H3 par plan et 18 contrefactuels explicatifs. Variations cohérentes et sourcées (mode `SYNTHETIC_REHEARSAL_NOT_REAL_OBSERVATION`) des neuf couples Step20. Le champ H3 `OBSERVED` est conservé quand H3 le requiert, **uniquement comme valeur du monde simulé**, jamais comme observation du monde réel. Le registre de cuissons réelles Step22 demeure vide.

Voir `RAPPORT_FR.md` pour les limites et les interprétations. `RAPPORT_1000.json` contient les chiffres, les graines et le SHA-256 du CSV ; les rapports sont reproductibles sur un PC Windows Python 3.12 sans dépendance externe.
