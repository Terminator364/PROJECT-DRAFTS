# MOTEUR — D072L, laboratoire logique R8 (24 octobre 2026)

Ce paquet complète, sans remplacer, le moteur `MATRICE_LOGIC_FIRST_V03/moteur_logique_v1.py` du dépôt public `Terminator364/PROJECT-DRAFTS`.

## Ce qui a été réalisé

- 355 propositions source R8 × 2 équipes = 710 cases logiques, 62 mondes.
- 12 règles AND typées par monde et équipe, évaluées de chaque côté (24 évaluations), distinguant `SUPPORTED_COOCCURRENCE`, `INDETERMINATE`, `PREMISE_FALSE`, `CONTRADICTED`.
- 1000 scénarios synthétiques de 710 états, chacun des 710 emplacements parcourant TRUE/FALSE/UNKNOWN.
- Aucun lien documentaire confondu avec une causalité ; aucun signe d'effet de but inventé ; IC réel et IC issu directement des 355 = `null`.

## Tester/Exécuter

Placer `moteur_logique_v2.py` et `test_moteur_logique_v2.py` à côté des fichiers upstream `moteur_logique_v1.py` et `test_moteur_logique_v1.py` disponibles dans :

https://github.com/Terminator364/PROJECT-DRAFTS/tree/main/MOTEUR-BLESSING/labs/MATRICE_LOGIC_FIRST_V03

Depuis ce répertoire :

```
python -m unittest -v test_moteur_logique_v2
python moteur_logique_v2.py --source-graph CHEMIN_SOURCE_GRAPH_355_D060.json --fixture CHEMIN_ENTREE_FICTIVE.json --outdir SORTIE
python moteur_logique_v2.py --source-graph CHEMIN_SOURCE_GRAPH_355_D060.json --grid-1000 --outdir SORTIE
```

**Confidentialité :** le graphe authentique `SOURCE_GRAPH_355_D060.json` demeure uniquement sur la branche privée R8; il n'est pas copié dans cette archive. Ne pas remplacer ce graphe par le graphe de test pour une certification authentique.

## Niveau de preuve

- `8/8` tests locaux réussis **avec adaptateur V1 de laboratoire et graphe synthétique**, pas une vérification Python sur les originaux privés.
- `D071` E2E original : reçu privé PASS encore indisponible lors du contrôle du 24/10.
- `D070` : les 1000 IC numériques synthétiques à 112 entrées restent une livraison *distincte* ; D072L teste la propagation logique, pas la justesse sportive.

## Continuité

Code `Moteur/continue`. Prochaine porte : vérifier le vrai graphe R8 privé avec le programme Python V1+V2, apporter les contre-exemples et enrichir les sous-paramètres sans attribuer de causalité non établie.