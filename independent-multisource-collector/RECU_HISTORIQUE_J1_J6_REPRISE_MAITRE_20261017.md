# COLLECTEUR / HISTORIQUE — Reçu J1→J6, correspondance R8 et reprise du maître unique

**Date : 17 octobre 2026, contrôle final autour de 18:59 UTC (19:59 Kinshasa).**
**Dossier maître unique :** `C:\Users\Lenovo\Documents\COLLECTEUR_AUTONOME_MULTISOURCES`
**Dépôt d'expérimentation :** `Terminator364/PROJECT-DRAFTS`, branche `experiment/bcp-autonomous-data-run-2026-10-17`.

## 1. Bibliothèque historique créée depuis archives déjà téléchargées

- 2 ligues favorites : Premier League anglaise, Serie A italienne.
- **12 journées complètes au total (J1–J6 pour chaque ligue), 120 fiches de rencontre**, score/résultat 90 min archivé et tous les champs CSV d'origine.
- À côté de l'index canonique `05_JOURNEES/HISTORIQUE_J1_ACTUEL` (qui conserve notamment J7 non résolue et 720 squelettes d'horizons), une **couche complémentaire** de 120 fichiers individuels sous `05_JOURNEES/HISTORIQUE_J1_J6/{PREMIER_LEAGUE,SERIE_A}/J01..J06/MATCHS/`.
- 12 synthèses, 12 grilles `COUVERTURE_62_ET_L3.json`, 744 entrées de famille et **1308 références L3** (109 sous-contrats × 12 journées).
- 62 familles R8 listées; les 109 contrats L3 documentés couvrent **20 familles** dans les lots consultés ; **42 autres n'ont pas été inventées**. Le statut opérationnel de toutes les familles du prototype reste `OBSERVATION_ONLY`, sans activation de l'IC.
- Résultats historiques de 100 rencontres concordants sur deux sources (50/ligue), 20 résultats seulement source Football-Data dans les snapshots; le pilote TheSportsDB n'a pas validé indépendamment ces 20 résultats.
- Présence de `FTHG`, `FTAG`, tirs, xG et cartons **comme observations post-match**. Les historiques antérieurs à une rencontre sont sélectionnés par **date strictement antérieure** et non selon les éventuels résultats du même jour ou futurs. Publication originale avant J−6/J−4/J−3/J−1/H−1/H0 : **non attestée**.
- Tests séparés : 5/5 du contre-audit `test_historical_matchdays_20261017_crossaudit.py`, et 11/11 déjà présents de la bibliothèque/horizons/backfill ; **16/16 vérifiés sur le PC**.

## 2. Un seul programme maître avec collecte historique

- L'ancienne instance PID 13876 a été arrêtée **proprement** au moyen du fichier STOP; elle a marqué son état `stopped_by_user`.
- Le maître unique a été redémarré avec le **routeur historique**, PID vérifié **2540**.
- Vérification : **1 seul processus Python autonome lié au projet** sur MBMPC.
- Module réseau `historical_provider_backfill.py` à **4 requêtes max par cycle de 5 minutes** selon conditions gratuites du fournisseur TheSportsDB.
- Queue historique documentée : **42 couples date/ligue** à traiter (premières journées jusqu'au dernier jour terminé).
- Premier cycle vérifié : **4/42 dates analysées**, **38 dates encore à contrôler**, **10 matchs recoupés** (1+3+3+3), **0 conflit de score** sur ces comparaisons. Les matchs live et futurs sont exclus. `historical_http_request_count=4` au contrôle.
- Les dates vérifiées sont enregistrées; elles ne sont pas interrogées de nouveau au prochain cycle, sauf changement futur explicite de politique. La limite gratuite de 3 événements/date/ligue rend le recoupement partiel.
- `MASTER_STATE.json` et `THESPORTSDB_HISTORIQUE/BACKFILL_STATUS.json` établissent cette progression; **ne pas présumer de l'achèvement des 38 dates restantes**.

## 3. Essai contrôlé de données enrichies

- Événement historique public TheSportsDB `2494000`, Arsenal-Coventry J1 le 21 août 2026.
- Endpoints libres contrôlés ponctuellement : `lookuplineup.php`, `lookuptimeline.php`, `lookupeventstats.php`.
- **5 entrées de composition**, **5 de chronologie**, **5 statistiques** renvoyées, à cause des limites gratuites. Les données brutes sont dans `03_FOURNISSEURS/THESPORTSDB_HISTORIQUE/EVENT_DETAIL_PROBE/` avec SHA-256 et registre `ASSESSMENT.json`.
- Cet échantillon **ne suffit pas** à reconstituer 11 titulaires, toutes les statistiques, ou tous les mécanismes des 62 familles. Il ne prouve pas la disponibilité des données à J−n ou H0; il est marqué **HISTORICAL_RESEARCH_ONLY**.

## 4. Vérité scientifique

Les faits produits pendant et après le match servent de **labels historiques**, de mécanismes à étudier et de références pour construire les variables des prochaines rencontres. Les données historiques de matchs antérieurs ne peuvent être utilisées dans un replay J−n que lorsque leur **publication et disponibilité** à cet horizon sont établies. La simple date du match ne suffit pas. Les 720 horizons sont des squelettes **non certifiés point-in-time**.

Le projet est autonome et indépendant de MATRICE; il n'a modifié ni la feuille directrice ADN R8 ni les coefficients IC. Aucun modèle d'apprentissage validé n'a été entraîné par ce reçu.

## 5. Ordre de mission à la prochaine reprise

1. Lire `07_EXECUTION/MASTER_STATE.json`, `03_FOURNISSEURS/THESPORTSDB_HISTORIQUE/BACKFILL_STATUS.json` et l'index unique.
2. Achever la queue historique en vérifiant chaque passage sans surcharger l'API.
3. Confronter `H0_ASOF_BEFORE_KICKOFF` aux sources d'équipes/compositions officiellement datées; garder `UNKNOWN` lorsque non prouvé.
4. Auditer famille par famille la disponibilité réelle des 62 familles puis sous-paramètre L3; ne jamais transformer un champ téléchargé en coefficient d'IC.
5. Éviter toute seconde instance permanente; ne pas créer un autre « dossier maître ».

**Code de continuité :** `COLLECTEUR/CONTINUE`.
