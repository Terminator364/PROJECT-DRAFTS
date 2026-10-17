# Step25 — proposition de mesure Q, préparation d'essais et refus d'IC inventé

**Priorité confirmée par l'utilisateur : tendreté 101 et séparation des grains 102.** Une priorité ordinale ne fixe pas les poids numériques. Cette étape propose deux modes à soumettre à validation : (a) portes non compensatoires pour 101/102, puis critères secondaires ; (b) pondération à deux niveaux, uniquement si ses poids et ses règles sont approuvés. **Aucun des deux modes n'est activé.** Le seuil Q≥85 n'est pas opérationnel tant que Q n'est pas défini.

Le contrat `PROTOCOLE_Q_MESURES_PROPOSE_NON_APPROUVE.json` contient les 14 critères 099–112, leurs pistes de mesure, la provenance exigée, la possibilité de trois prélèvements spatiaux, la variabilité inter-évaluateurs et les éléments encore à décider. Les quantités, délais, seuils de séparation et poids restent non validés. La sécurité alimentaire (099) n'est pas une note de goût; aucun examen sensoriel ne certifie l'innocuité.

`FICHE_VIDE_PRE_POST_T0.json` prépare la collecte mais ne contient ni essai réel, ni prétendue mesure. Les renseignements réels doivent être saisis avant T0 et après T0 **dans des enregistrements séparés**, par les fonctions de `step22/trial_registry.py`. `CONTROLE_PRECALIBRATION_ZERO.json` prouve le refus de calibration du Step23, et qu'un paquet synthétique ne peut pas être présenté comme une cuisson réelle.

`q_measurement_contract.py` est une vérification de protocole **non approuvé**, pas un calculateur Q; `trial_prep.py` produit une fiche vide contrôlée et un contrôle de refus. Aucun effet des 112 rubriques sur Q réel n'est annoncé.

Exécution depuis le dossier `RIZ112_CAHIER_MERE` :

```bash
python -m unittest discover -s step25 -p 'test_*.py' -q
python step25/q_measurement_contract.py --step20 step20/PROTOCOLE_Q_14_SORTIES_DRAFT.json --step21 step21/PRIORITY_CONFIRMED_NO_WEIGHTS.json --out step25/PROTOCOLE_Q_MESURES_PROPOSE_NON_APPROUVE.json
python step25/trial_prep.py --proposal step25/PROTOCOLE_Q_MESURES_PROPOSE_NON_APPROUVE.json --priority step21/PRIORITY_CONFIRMED_NO_WEIGHTS.json --quality-draft step20/PROTOCOLE_Q_14_SORTIES_DRAFT.json --synthetic-packet step6/examples/A_couvercle_ajuste_112.json --out-template step25/FICHE_VIDE_PRE_POST_T0.json --out-check step25/CONTROLE_PRECALIBRATION_ZERO.json
```

**Porte suivante** : recueillir explicitement l'accord de l'utilisateur sur les échelles, la méthode et l'agrégation ; sans cet accord, ne pas écrire `APPROVED` ni attribuer un vrai Q. Même après accord, réaliser de vraies cuissons indépendantes et une validation hors échantillon avant un IC réel. L'échantillon exploratoire de 12 essais du Step23 n'est pas une garantie de puissance statistique.
