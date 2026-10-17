# BCP / MATRICE — Octobre 2026, pilote mult_source à deux compétitions

**Vérification effectuée sur MBMPC le 17 octobre 2026.** Périmètre issu de `MATRICE/GOUVERNANCE/FAVORIS_COMPETITIONS_CAPTURE_CANDIDATS_R7.md`, branche R8 du dépôt `Terminator364/ChatGPT-PC`. Le fichier documente les intitulés transcrits de captures SofaScore, non un accès connecté au compte SofaScore.

## Périmètre & critères
- Premier League (E0) et Serie A (I1), saison 2026-2027.
- Point de coupure **exclusif** : 2026-10-17 (date seulement). Les matchs du 17 octobre et au-delà restent **SANS résultat admis** dans ce pilote, même si un fournisseur affiche un score.
- Ordre d'examen : octobre, septembre, août, puis éventuellement journées antérieures d'autres saisons.
- Deux sources complètes de calendrier/résultats disponibles : fichiers archivés Football-Data (CSV) et OpenFootball/football.json (JSON).
- Troisième source : TheSportsDB API v1 gratuite, `eventsseason`, qui n'a renvoyé **que 15 rencontres par ligue** pour ce test; ne pas la considérer comme couverture exhaustive.
- Aucune requête nouvelle à Football-Data n'a été émise au moment de l'audit ; CSV lus dans le cache local existant conformément à la politique de consultation légère.
- Aucune extraction non officielle de SofaScore ni contournement de restrictions d'accès.

## Résultats vérifiés sur le PC

| Indicateur | Premier League | Serie A |
| --- | ---: | ---: |
| Journées programmées saison entière (OpenFootball) | 38 | 38 |
| Matchs calendrier saison entière (OpenFootball) | 380 | 380 |
| Matchs CSV historiques admissibles (avant 17/10) | 60 | 60 |
| Identités date + clubs réconciliées / 60 | 60 | 60 |
| Scores identiques entre les deux sources | 50 | 50 |
| Matchs d'octobre avec scores uniquement Football-Data | 10 | 10 |
| Matchs dans l'échantillon TheSportsDB recoupés **sur 3 sources** | 15 | 15 |
| Conflits de score observés dans le sous-ensemble comparable | 0 | 0 |
| Alias de clubs restés inconnus | 0 | 0 |
| Tests unitaires dédiés au croisement | \- | 5/5 (ensemble) |

OpenFootball donne la grille complète, mais la dernière rencontre ayant un score archivé dans ses snapshots consultés se situe en septembre : la fraîcheur du score d'octobre y est insuffisante. L'absence de score chez OpenFootball **n'est pas une contradiction** avec Football-Data.

### Journées les plus proches de la date d'étude
- Premier League : J6 **10-12 octobre**, 10 scores Football-Data ; J7 **17-19 octobre**, exclue comme source d'issues au cutoff du 17 ; J8 **23-25 octobre**, futur.
- Serie A : J6 **10-12 octobre**, 10 scores Football-Data ; J7 **16-19 octobre**, 1 fixture le 16 (**Frosinone–Sassuolo**) sans score confirmé dans les instantanés ; J8 **23-25 octobre**, futur.
- Premier League septembre : J3, J4, J5, 30/30 scores concordants; août : J1, J2, 20/20.
- Serie A septembre : J3, J4, J5, 30/30 scores concordants; août : J1, J2, 20/20.

## Fichiers locaux et preuve
- `C:\Users\Lenovo\BCP_AUTONOMOUS_TEST_20261017\v2\openfootball_E0_2627.json`
- `C:\Users\Lenovo\BCP_AUTONOMOUS_TEST_20261017\v2\openfootball_I1_2627.json`
- `v2/provider_snapshots/thesportsdb_E0_2627.json`, `thesportsdb_I1_2627.json`
- `v2/matchday_pilot/E0_matchdays.json`, `I1_matchdays.json`, `summary.json`, `three_source_audit.json`
- Scripts versionnés : `matchday_crosscheck.py`, `third_source_check.py`, `test_matchday_crosscheck.py`. Les 5 tests de croisement sont **OK**.

## Faisabilité & limites

Ce pilote **réconcilie identités et scores**, mais il ne collecte pas encore xG, blessures, forme médicalement attestée, statistiques tactiques, arbitres publiés, météo publiée avant T ni tous les 62 mondes. Le croisement de plusieurs sites ne prouve pas que leurs informations viennent de sources primaires indépendantes. Les données publiées après le coup d'envoi ne doivent jamais entrer dans un replay PIT pré-match. Pour tout calcul d'IC futur, ajouter `published_at`, `available_at`, preuve et droits de chaque assertion à J−6/J−3/J−1/H−1, puis valider hors échantillon.

Sources et limites :
- Football-Data : https://football-data.co.uk/contact.php (automatisation légère au maximum deux téléchargements par semaine).
- OpenFootball : https://github.com/openfootball/football.json (public domain, JSON généré quotidiennement, sources TXT amont éventuellement mises à jour manuellement).
- TheSportsDB : https://www.thesportsdb.com/docs/api (V1 gratuite, accès saison limité).
- Autres pistes **non encore intégrées** : https://github.com/hudl/open-data (StatsBomb Open Data pour certains événements/lineups); https://open-meteo.com/en/docs/historical-forecast-api (prévisions archivées; ne pas confondre avec météo observée). Conditions et couverture à auditer.

**Statut : PILOTE TERMINÉ, PAS DE CERTIFICATION HISTORIQUE PIT.** Aucun moteur MATRICE officiel modifié; aucun collecteur externe minute-par-minute activé.
