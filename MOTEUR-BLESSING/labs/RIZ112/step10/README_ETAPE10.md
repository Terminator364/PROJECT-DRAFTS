# RIZ-112 V10 : les 112 influences testées, sans falsifier un IC scientifique

## Exécution du contrôle de qualité gelé
À la racine `RIZ112_CAHIER_MERE` :

```bash
python step10/ic_integrity_v10.py step6/examples/A_couvercle_ajuste_112.json --draws 3000
python step10/test_stage10.py -q
```

Test de la réponse du simulateur V9 lorsqu'on modifie successivement les 112 cases :

```bash
python step10/case_intervention_audit.py
```

Le fichier `INTERVENTIONS_112_STAGE9.json` a été produit avec **3 000 tirages par intervention**. Ce recalcul peut solliciter le CPU sur une petite machine : utiliser le fichier fourni pour consulter les résultats sans les refaire.

**Résultats :** 11 modifications numériques du pourcentage, 5 abstentions, 92 sorties inchangées, 4 dérivées non mutables. Le gate V10 ajoute une abstention explicite si une des 14 définitions de qualité est modifiée. Il ne prétend pas 112 coefficients ; `scientific_ic_percent` reste nul.
