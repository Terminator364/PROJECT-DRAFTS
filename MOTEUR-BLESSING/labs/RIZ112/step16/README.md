# RIZ-112 — V1.0 moteur de démonstration unifié (pré-T0)

**Objet** : chaîner les 112 rôles canoniques (108 fiches d'entrée/plan/cible + 4 prévisions dérivées), les diagnostics mathématiques H4A/H4B et **le noyau original H3**. Les 4 prévisions 043/044/046/048 ne sont pas des observations qu'on peut librement inventer.

## Utiliser le moteur

Python 3.10+ sans paquet payant. Conserver le dossier source complet `labs/RIZ112/` sur disque (step6, step9, step13, step14 et ce dossier `step16`). Ensuite :

```console
python step16/riz112_unified.py --packet step6/examples/A_couvercle_ajuste_112.json --lab-root . --require-h3 --output step16/RESULTAT_AB_C.json
```

Le chemin `--lab-root .` doit désigner `labs/RIZ112`, pas `step16`. L'interface produit trois simulations A/B/C pré-déclarées : puissance nominale, disponibilité énergétique 60%, eau prévue 180g. Les autres rubriques sont conservées et les entrées spécifiques de H3 font l'objet de la trace d'hypothèses. Les résultats incluent un **IC_DEMO** de Q* fictif et les diagnostics H4, les preuves de provenance et les garde-fous. `scientific_ic_percent` reste **null** (aucune préparation réelle et aucune calibration de Q≥85).

Pour vérifier le dossier de manière autonome :

```console
python -m unittest discover -s step16 -p 'test_*.py' -q
python -m unittest discover -s step14 -p 'test_*.py' -q
```

Le test de non-régression historique complet est `python step14/run_regression_h3.py`, idéalement dans un dossier versionné, en surveillant l'usage CPU/RAM. Sur Windows, double-cliquer `LANCER_RIZ112_WINDOWS.cmd` depuis `step16`.

## Ce qui est calculé / non calculé

1. H4A : sel/quantité, portions sèches, fraction massique de grains cassés et indice de rinçage.
2. H4B : résistance thermique hypothétique, distribution planifiée de température, actions, variété, impuretés, service et politiques.
3. H3 : simulations énergétiques et d'hydratation dont les chiffres correspondent seulement à **Q* artificiel**, via `anticipatory_physics_h3.py` existant. Aucune constante H4 n'est artificiellement ajoutée au score IC.
4. Quatre rubriques prévues par l'architecture ne sont pas inscrites comme observations dans les 108 fiches : `043/044/046/048` (prévisions/diagnostics dérivés). Le reçu le rend explicite.

## Critères de sortie

- Le moteur s'abstient sur IC_DEMO lorsque H3 n'est pas installé, plutôt que d'inventer un chiffre.
- Le moteur refuse les variables post-gel, états `UNKNOWN` contenant une valeur, identifiants manquants, anomalies d'unités H4 et dates sans fuseau.
- Les tests sur données synthétiques ne constituent **pas** la validation de l'IC de qualité réelle. Un protocole de mesure approuvé, de vrais essais et une calibration hors échantillon restent nécessaires.

**REUSE / ADAPT / BUILD ONLY IF GAP**. Ni moteur sportif ni dépôt MATRICE modifié. Version de travail H4A+H4B+H3 seulement; aucune dépense GitHub Actions.
