# RIZ112 → MATRICE | Expérience numérique de 1 000 scénarios

## Mandat et périmètre

Objectif de **méthode pour MATRICE** : utiliser l'analogie du riz pour auditer les dépendances, les interactions, la réponse aux variations, l'abstention et le contrôle des hypothèses avant T0. Cette expérience ne construit ni application supplémentaire ni prédicteur calibré de riz réel.

Ensemble de départ : dossier historique synthétique `step6/examples/A_couvercle_ajuste_112.json`, mécanismes H3 originaux et bilan théorique Step20. Chaque scénario possède les **112 rubriques structurelles**, mais **seules 9 grandeurs physiquement couplées** varient : 001, 033, 035, 036, 037, 038, 041, 042, 047. Les autres sont maintenues aux valeurs du dossier d'essai, donc cette expérience ne prouve pas toutes leurs influences.

## Méthode

- 1 000 combinaisons d'un plan d'expérience **Latin hypercube** sur 9 grandeurs, graine fixée `20261017` ; intervalles SYNTHÉTIQUES, non mesurés ni optimisés sur des essais réels.
- Source cohérente : une valeur de `case_inputs` égale à sa grandeur physique équivalente de `prestart.inputs`. Échec explicite sur contradictions ou variables après T0.
- 200 tirages H3 **Q\*** par combinaison, graine commune de simulation ; succès du *score fictif* si **Q\* ≥ 85**. Les pourcentages `IC_DEMO` sont la fraction de tirages qui franchissent ce seuil, pas une probabilité de qualité réelle.
- Bilan d'énergie/eau de Step20 distinct, théorique : aucune prédiction de quantité réellement évaporée, d'innocuité ou de résultat gustatif.
- Sélection a posteriori du scénario synthétique **SYN_0821** pour 18 perturbations univariées ±15 %. Cette sélection peut surajuster la démonstration : les contre-épreuves ne sont pas une validation hors échantillon.

## Résultats observés dans le programme, non en cuisine

| Diagnostic numérique | Résultat |
|---|---:|
| Combinaisons générées | 1 000 |
| Combinaisons évaluées par H3 | 690 |
| Abstentions H3 | 310 |
| Scénarios avec IC_DEMO ≥ 85 % | 20 |
| Scénarios satisfaisant deux marges physiques simplifiées | 664 |
| Intersection IC_DEMO ≥ 85 % et bilans physiques favorables | 20 |
| Mesures Q réelles / influences réelles prouvées | 0 / 0 |

Le modèle peut donc *atteindre* fictivement la zone IC_DEMO 85–100, mais la proportion 20/1 000 dépend du plan d'échantillonnage synthétique. Ce n'est pas « 2 % des cuissons réussissent ».

**Contre-épreuves sur SYN_0821 (IC_DEMO initial 91,5 %, tirages communs)** :

- Eau ajoutée -15 % → IC_DEMO 38,5 % ; eau +15 % → 38,0 %. Cette fonction synthétique a un optimum local ; davantage d'eau n'est pas toujours mieux selon le modèle.
- Durée -15 % → 60,0 % ; +15 % → 85,5 %.
- Masse de riz -15 % → 47,5 % ; +15 % → 70,5 %.
- Température initiale du riz ±15 % → **aucun changement détecté dans l'IC_DEMO** sur ces 200 tirages, même si certaines marges physiques intermédiaires changent. Ne pas forcer un effet fictif.

## Analogie pour MATRICE

1. **Réponse non linéaire** : une variation d'un facteur peut créer des transitions brusques, mais cela peut provenir des équations choisies et non de la nature.
2. **Contreposition / essais A-B** : ne pas récompenser aveuglément « plus » ou « moins » ; tester une variable dans les deux directions et dans plusieurs régimes.
3. **Abstention documentée** : 310 échecs de faisabilité du chemin H3 produisent `IC_DEMO=null`, jamais une fausse probabilité 0 %.
4. **Traçabilité stricte** : pré-T0, sources, formules, versions, graines, scénarios et refus doivent être inspectables.
5. **Transfert sans équivalence** : le riz est la maquette de raisonnement, pas la preuve que 112 causes ou 62 familles sportives sont estimables en pré-match. MATRICE reste pré-match exclusivement.

## Statut scientifique

`scientific_ic_percent = null`, `real_rice_trials = 0`, `user_approved_Q_formula = false`. Les simulations réduisent les incertitudes **logicielles et structurelles** ; elles ne valident pas la loi physique ni les causalités empiriques. Aucun utilisateur n'est tenu de cuisiner 1 000 fois. Une validation empirique optionnelle resterait nécessaire pour qualifier l'IC de réellement prédictif.

## Reproduire (dans le laboratoire actuel)

```bash
python -m unittest discover -s simulations/EXPERIENCE_1000 -p 'test_*.py' -q
python simulations/EXPERIENCE_1000/simuler_1000.py --n 1000 --draws 200 --output simulations/EXPERIENCE_1000/results
```

Documents : `RAPPORT_1000.json`, `SCENARIOS_1000_SYNTHETIQUES.csv`, `CONTREFACTUELS_18.json`. Les lignes CSV ne doivent jamais être importées comme observations réelles dans le registre Step22.
