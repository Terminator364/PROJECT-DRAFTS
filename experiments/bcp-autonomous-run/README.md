# BCP Autonomous Run — Test 01 (17 octobre 2026)

Test de **60 minutes** sur le PC Windows MBMPC, sans logiciel payant ni service cloud obligatoire.

## Objectif

Valider qu'un processus indépendant de la conversation ChatGPT sait collecter, vérifier, analyser et journaliser des données historiques de football, en conservant des checkpoints et des fichiers exploitables après fermeture de la conversation.

## Sources

- https://www.football-data.co.uk/mmz4281/2526/E0.csv
- https://www.football-data.co.uk/mmz4281/2627/E0.csv

Données historiques, uniquement matchs terminés **datés avant le jour d'exécution**; les matchs du jour, non terminés ou incohérents sont exclus. Aucun traitement live, aucune cote, aucune proposition de pari, aucune prédiction.

## Exécution

`python run.py` exécute 3600 secondes; un heartbeat toutes les 60 secondes, téléchargement/contrôle des deux fichiers toutes les 600 secondes, traitement initial immédiat. Standard library Python uniquement.

Sur MBMPC, dossier local `C:\Users\Lenovo\BCP_AUTONOMOUS_TEST_20261017` : `run.py`, `runtime\checkpoint.json`, `runtime\events.jsonl`, `runtime\analysis.json`, `runtime\raw\*.csv`, `runtime\receipt.json`.

Pour reprendre après un arrêt : relancer exactement `python run.py` dans le même dossier et avant l'échéance. Si la machine est éteinte, aucun travail ne s'exécute; les checkpoints restent conservés. La mission est bornée par l'échéance initiale.

Pour demander un arrêt propre : créer le fichier `runtime\STOP`. La prise en compte intervient au début du cycle suivant. Aucun fichier de projet MATRICE ou RIZ-112 n'est modifié.

## Contraintes

- Les données dérivées sont exploratoires; le calcul des statistiques actuelles **ne remplace pas** une validation temporelle stricte dans une simulation historique, ni la preuve d'un effet causal de chaque paramètre.
- Le worker n'est **pas** une IA autonome. Il exécute un traitement programmé.
- Les preuves de progression sont sur le PC; le dépôt GitHub conserve le code et les reçus de démarrage vérifiés. Pas de promesse de synchronisation automatique du journal complet sur GitHub en l'absence de droits d'écriture disponibles sur le PC.
- Branche isolée : `experiment/bcp-autonomous-data-run-2026-10-17`. Ne pas fusionner automatiquement dans `main`.
