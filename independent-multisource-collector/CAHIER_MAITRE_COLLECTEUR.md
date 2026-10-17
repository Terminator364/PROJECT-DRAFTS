# COLLECTEUR AUTONOME MULTISOURCES — Cahier maître du projet indépendant

**Création : 17 octobre 2026.**  
**Racine PC :** `C:\Users\Lenovo\Documents\COLLECTEUR_AUTONOME_MULTISOURCES`  
**Dépôt de développement isolé :** `Terminator364/PROJECT-DRAFTS` / `experiment/bcp-autonomous-data-run-2026-10-17` / `independent-multisource-collector`

## 1. Identité et frontières du projet

Ce dossier est **le dossier maître du COLLECTEUR**, projet autonome distinct de MATRICE et de BCP. Il rassemble le code, les données sportives, les références de MATRICE, les sources, les journaux, les checkpoints, les rapports et les preuves. Ce n'est **pas** le Cahier mère canonique de MATRICE et il n'a aucune autorité pour modifier le moteur, les coefficients ou la feuille de route ADN R8. Les références copiées depuis `Documents\MATRICE_R8_G3_WORKSPACE` sont documentaires et ne doivent jamais être modifiées comme si elles étaient l'original.

Source des priorités : document `FAVORIS_COMPETITIONS_CAPTURE_CANDIDATS_R7.md` de l'ADN R8. Premières ligues : **Premier League** (E0) et **Serie A** (I1). Les autres favoris sont dans le périmètre futur mais **ne sont pas activés**.

## 2. Organisation du dossier maître

- `00_GOUVERNANCE` : charte, contrats sources, règles, décisions et limites de validité.
- `01_CONTINUITE_R8\WORKSPACE` : **copie d'archive** du workspace R8 (215 fichiers, original intact ailleurs).
- `02_BCP_COLLECTE\TEST_20261017` : **copie d'archive** des 125 fichiers V1/V2 et leurs sources.
- `03_FOURNISSEURS\OPENFOOTBALL_SHA256` : copies brutes immuables, empreintes SHA-256.
- `04_COMPETITIONS` : futur référentiel des compétitions/fournisseurs.
- `05_JOURNEES` : résultats de réconciliation par journée et par compétition.
- `06_AUDITS` : tests et contre-audits à approfondir.
- `07_EXECUTION` : `MASTER_STATE.json`, `LAST_RECEIPT.json`, `STOP` manuel le cas échéant.
- `08_RAPPORTS` : `LATEST_TWO_LEAGUES.json` et rapports scientifiques.
- `09_JOURNAUX` : `master_events.jsonl` journal append-only.
- `standalone_controller.py`, `third_party_adapter.py` : contrôleur et recoupement de trois sources.

## 3. Stratégie de fonctionnement

- **Une minute** : signal d'activité et checkpoint du programme local.
- **Cinq minutes** : relire les archives et réconcilier les rencontres Premier League et Serie A.
- **Une fois toutes les 24 heures au maximum** : télécharger les deux fichiers OpenFootball (données CC0 publiques, mais données amont pas garanties à jour).
- **Football-Data** : **aucun téléchargement périodique activé** ; anciens CSV utilisés depuis le cache. Respect de l'automatisation légère du fournisseur (au plus deux fois par semaine).
- **TheSportsDB** : **aucun téléchargement périodique activé** ; échantillon de 15 rencontres par ligue précédemment archivé et recoupé localement. Vérifier les limitations de la clé publique avant toute extension.
- Aucun service cloud payant, aucun modèle IA payant, aucun scraping ou contournement de site privé.

## 4. Scientifique : règles non négociables

Tous les rapports ont le statut **RESEARCH_ONLY_NOT_PIT_CERTIFIED**. Les buts/résultats déjà connus sont des données historiques et ne doivent **jamais** entrer comme features d'une prévision reconstituée antérieure au match. Pour construire une vraie « farine » pré-match, il faudra des preuves `published_at`/`available_at` à chaque horizon J−6/J−3/J−1/H−1, des droits compatibles et une validation indépendante. Les 62 familles sont un **registre d'observation**, pas un ensemble d'effets opérationnels. Aucun IC n'est calculé par ce projet.

Les conflits restent explicites, les alias non réconciliés restent bloqués, les scores du jour et des jours futurs ne sont pas admis. Le suivi d'octobre précède septembre puis août. Chaque famille nécessite un contrat spécifique, un plan de recherche, les sources alternatives et un contrôle de provenance.

## 5. Exécution et preuve

Depuis la racine du dossier maître :
- `python standalone_controller.py --once --offline` : un audit local sans aucune requête réseau.
- `python standalone_controller.py --hours 24` : processus indépendant, limité à 24 h pour ce premier lancement; arrêt possible par création de `07_EXECUTION\STOP`.
- Un seul processus maître est admis simultanément.
- La machine doit rester allumée; pas de redémarrage automatique configuré à ce stade.
- Les copies originales dans `Documents\MATRICE_R8_G3_WORKSPACE` et `C:\Users\Lenovo\BCP_AUTONOMOUS_TEST_20261017` restent intactes.
- GitHub contient le code et les reçus de vérification; **les journaux locaux ne sont pas automatiquement poussés** sur GitHub.

## 6. Continuité

Code de reprise local proposé : **`COLLECTEUR/CONTINUE`**. Toujours relire `07_EXECUTION\MASTER_STATE.json`, `09_JOURNAUX\master_events.jsonl`, `08_RAPPORTS\LATEST_TWO_LEAGUES.json`, puis la charte, avant toute modification. Ne jamais redémarrer le chantier à zéro. Toute extension doit passer par un test et un contre-audit; toutes les preuves sont conservées.

Ce projet est indépendant, mais doit rester interopérable avec le fournisseur de « farine » prévu par MATRICE sans muter ses données validées.
