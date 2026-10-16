# RIZ112 — moteur IC de démonstration V9 : calcul disponible, validation non prétendue

## Mandat
L'utilisateur demande de finir la chaîne et d'obtenir un moteur qui émet déjà un IC. Cette livraison **exécute un calcul probabiliste conditionnel sur un critère fictif** et conserve la frontière avec une probabilité fiable de réussir du vrai riz. Pas de recette. Toutes les entrées sont figées à T0.

## Exécuter sans dépendances payantes
Depuis la racine `RIZ112_CAHIER_MERE` :

```bash
python step9/ic_simulation_v1.py step6/examples/A_couvercle_ajuste_112.json --draws 3000 -o step9/A_couvercle_ajuste_IC_DEMO.json
python step9/build_stage9.py
python -m unittest discover -s step9 -p 'test_*.py' -q
```

Le code appelle le **véritable pipeline V8**, et donc les contrats V6, le contrôle des relations V7 et les 62 routes D014 V8. Il exécute ensuite un Monte-Carlo sur les équations V4 et un agrégateur par **minimum** de quatre dimensions fictives, plutôt que 112 coefficients additionnés. Les huit distributions de paramètres incertains, leurs corrélations et les échelles des dimensions sont complètement paramétrables dans `DEMONSTRATION_CONTRACT.json`.

### Chiffres obtenus (3000 tirages, graine 20261016)
- A couvercle ajusté : 62,40 % **IC_DEMO** (intervalle Monte-Carlo 95 % environ [60,65 ; 64,12]).
- B couvercle fuyant : 36,83 % **IC_DEMO** ([35,13 ; 38,58]).
- C chaleur faible : 0,10 % **IC_DEMO** ([0,03 ; 0,29]).

Il s'agit de `P(Q*_DEMO>=85 | X, hypothèses)` et **NON** de `P(Q_réel>=85|X)` : aucun vrai essai de cuisson, mesure Q approuvée, apprentissage ni calibration. Dans toutes les sorties JSON, `scientific_ic_percent` et `real_Q_probability_percent` restent **null**. Les intervalles Monte-Carlo reflètent seulement l'erreur d'échantillonnage de la simulation et pas l'incertitude sur la validité du modèle.

### Contre-épreuves indispensables
- En A, retrancher 60 g d'eau prévue fait baisser l'IC_DEMO de 62,40 % à 44,87 %.
- En A, modifier une seule échelle de définition du *Q fictif* le fait baisser à 38,20 %. Cette sensibilité empêche de traiter l'IC_DEMO comme une vérité établie.
- Absence de couvercle alors que son placement est prévu → `ABSTAIN_PRESTART_CONTRADICTION`; ne pas fabriquer un pourcentage.
- Injection de score final ou de date post-T0 → rejet.
- Les 14 critères Q sont traités comme définitions de cible. Quatre dimensions approximatives sont simulées, les dix autres restent NON MODÉLISÉES. Une erreur d'assurance qui prétendrait que les 112 déterminent numériquement Q est interdite.

### Conception mathématique
Pour un tirage j, calculer `W_target`, `T_hot`, `E_evap`, `W_absorb`, `W_free`, `S_residual` via le graphe de masse/énergie. Définir (scales fictives déclarées dans JSON) :

`q_hyd = min(1, W_absorb / W_target)`

`q_heat = min(1, T_hot / hot_time_needed_min)`

`q_free = max(0, 1 - W_free / (rice_mass * free_water_scale))`

`q_starch = max(0, 1 - S_residual / surface_starch_scale)` **(effet de texture NON VALIDÉ)**

`Q*_j = 100 * min(q_hyd, q_heat, q_free, q_starch)`

`IC_DEMO = 100 * sum(Q*_j>=85) / N`.

Chaque tirage échantillonne des paramètres conjointement avec un bruit latent partagé entre efficacité thermique et évaporation. C'est un algorithme d'incertitude **déclarée**, pas une distribution mesurée. Il n'y a pas de somme de 112 bonus.

### Critère de clôture
**Chaîne logicielle capable de produire un IC de démonstration : oui.** 112 cases couvertes par leurs rôles/gardes/scénarios : oui. **112 effets sur Q réel : non.** IC scientifique et objectif supérieur à 85/100 en conditions réelles : non démontré. Restent protocole Q, vraies données appariées, entraînement et validation hors échantillon. Ne jamais présenter l'IC fictif comme un pronostic réel ou le copier dans MATRICE.
