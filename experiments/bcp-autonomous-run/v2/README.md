# BCP Autonomous Run V2 — Collecteur de farine (prototype isolé)

Date : 17 octobre 2026. Dépôt : `Terminator364/PROJECT-DRAFTS`, branche `experiment/bcp-autonomous-data-run-2026-10-17`.

## Ce qui existe réellement

- Inventaire **exact de 62 familles** importé de `Terminator364/ChatGPT-PC`, branche `research/matrice-r8-g3-depth-audit-2026-10-14`, chemin `MATRICE/R8_G3_DEEP_20261014/parameter_62_individual_audit_20261015/AUDIT_62_INDEX_COMPARATIF.csv`.
- 4 familles historiquement dérivables *à titre de recherche*, 9 familles partiellement renseignables, 2 de métadonnées et 47 sans source adéquate dans les résultats CSV utilisés.
- 5 championnats × 2 saisons = 10 fichiers source [Football-Data](https://www.football-data.co.uk/downloadm.php) ; validation structure, clubs, score final, dates, doublons.
- Exclusion des matchs datés du jour et futurs, métadonnées SHA-256, archives immuables par empreinte, états checkpoint, métriques descriptives historiques Over 1,5, registre couverture de 62 familles.
- Exécutable Python standard library, compatible PC Windows modeste sans modèles locaux ni API payante.

## Statut scientifique (contraintes strictes)

**RESEARCH_ONLY / OBSERVATION_ONLY.** La présence de colonnes et des historiques ne certifie pas les 62 familles. Les sources récupérées aujourd'hui ne prouvent pas quand chaque ligne a été **publiée ou disponible** à J−6/J−3/J−1/H−1 pour un replay historique. L'algorithme peut filtrer par *date du match*, mais cela **ne constitue pas une validation point-in-time complète**. Les variables xG, blessures, prédictions de composition, météo historique telle qu'anticipée, interactions et droits fournisseur nécessitent d'autres contrats et sources.

Les nombres descriptifs Over 1,5 sont des statistiques d'échantillon de recherche. **Aucun IC n'est calculé, aucun paramètre n'est opérationnalisé**, aucun modèle MATRICE 2.0/2.5 n'est modifié. Aucune intégration au Cahier mère canonique n'est prétendue; il faudra rattacher ces expériences au protocole de continuité après audit.

## Commandes

`python -m unittest -v test_collector` depuis le répertoire `v2` (7 tests hors ligne).

`python collector.py --once --output integration` : une passe sur dix fichiers, écrit `integration/receipt.json` puis s'arrête.

`python collector.py --duration 3600 --interval 60 --refresh 1800 --output runtime` : worker d'une heure, 1 heartbeat/min, une nouvelle collecte toutes les 30 min tant que le PC fonctionne. À relancer depuis le même répertoire en cas d'arrêt, et avant le deadline; aucun nouveau run après état `completed`. Fichier `runtime/STOP` : arrêt propre après l'étape courante.

Les artefacts sont enregistrés **sur le PC** sous `C:\Users\Lenovo\BCP_AUTONOMOUS_TEST_20261017\v2\` :
`checkpoint.json`, `manifest.json`, `coverage_62.json`, `events.jsonl`, `receipt.json`, `raw/<sha256>.csv`.

Pas de transfert automatique du journal complet vers GitHub dans cette V2; journal local et reçus GitHub manuels après vérification.

## Ce qui manque pour la V3

- Contrats par sous-paramètre (source, field ID, horodatages event/published/available/collected, droits, périodicité, qualité).
- Identification stable des rencontres et des joueurs; données événementielles couvrant davantage de ligues.
- Référentiels historiques authentiquement PIT, snapshots immuables de fixtures, audits de licences et de disponibilité.
- Orchestrateur adaptatif respectant bandes passantes, APIs, limites fournisseurs et tolérance aux coupures.
- Évaluation scientifique des effets **avant** toute promotion de paramètre.

Données de cette expérience jamais à injecter automatiquement dans un moteur IC approuvé.
