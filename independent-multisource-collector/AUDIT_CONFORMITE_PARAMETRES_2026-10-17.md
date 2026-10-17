# Audit de conformité — données téléchargées versus paramètres MATRICE R8

Date : 17 octobre 2026. **Projet indépendant** `COLLECTEUR_AUTONOME_MULTISOURCES` sur MBMPC; audit **en lecture seule**, aucun processus supplémentaire persistant.

## Verdict
**PARTIELLE — NON CERTIFIÉE PRÉMATCH (PIT).** Le registre recopie exactement les 62 identifiants des familles gelées R8, mais cela ne valide aucune des 62 familles pour le calcul de l'IC. Les modes 4 DERIVABLE_RESEARCH / 9 PARTIAL / 2 METADATA / 47 UNAVAILABLE_FROM_RESULT_ARCHIVES sont une *qualification préliminaire des champs candidats*, pas un taux de conformité ni une preuve d'utilité prédictive. Aucune activation du moteur MATRICE.

## Contrôles effectués directement sur les archives du PC

Deux fichiers CSV datés de la saison 2026-2027, filtrés à la date exclusive du 17 octobre 2026, identités et SHA-256 vérifiés.

| Famille de données (colonnes sources) | Premier League (60 matchs) | Serie A (60 matchs) | Statut |
| --- | --- | --- | --- |
| Date, Time, HomeTeam, AwayTeam, FTHG, FTAG, FTR | 60/60 lignes renseignées | 60/60 | Identité de base et scores historiques, pas `fixture_id` stable |
| HS AS HST AST (tirs/tirs cadrés) | 60/60 | 60/60 | Champs historiques observés, **pas** une variable future à T |
| HxG AxG (étiquetage xG fournisseur à préciser) | 60/60 | 60/60 | Complétude apparente du champ ≠ définition/licence validée ni xG prématch |
| Cartons/fautes HY AY HR AR HF AF | 60/60 | 60/60 | Observations historiques, ne prouvent pas suspensions actuelles |
| Referee (arbitre) | 60/60 | **0/60** | Non homogène par ligue; date de désignation non conservée |
| B365H/D/A, B365>2.5/<2.5 | 60/60 | 60/60 | Cotes historiques brutes **non admises** comme PIT sans publication datée |
| Source de calendrier OpenFootball | 380 fixtures | 380 | Calendrier, sans horodatage historique certifié de disponibilité |
| Recoupement des scores CSV et OpenFootball | 50/60 | 50/60 | 10 scores par ligue restés mono-source en octobre |
| Recoupement troisième fournisseur TheSportsDB | 15/15 | 15/15 | Petit échantillon gratuit, non représentatif de la couverture d'octobre |

La nouvelle collecte toutes les 5 minutes auprès de TheSportsDB ne conserve que les événements programmés avant coup d'envoi, selon horodatage UTC interprété, sur **deux ligues et deux journées civiles**. Dernier instantané examiné : 7 rencontres futures, 5 événements live/passés écartés, sans score stocké. L'API gratuite peut tronquer à 3 matchs/date/ligue. Ce n'est pas une collecte exhaustive des matchs, ni des 62 paramètres.

## Confrontation avec les sous-contrats R8 L3 (GitHub, 17 octobre)

- `LEAGUE_BASE.GOALS_DISTRIBUTION_PRIOR` requiert notamment `completed_before_asof_fixture_set`, `analysis_asof_utc`, `first_available_at` et horizon de coupure : **non démontrés**.
- `TEAM_STRENGTH.ATTACK_OPPONENT_ADJUSTED` réclame `opponent_ids`, `eligible_past_matches`, domaines et moment de publication : **pas d'ajustement adverse validé**.
- `SCORING_HISTORY.REGULATION_SCORE_LINEAGE` réclame `historic_fixture_id`, `source_version_digest` et `original_publisher_issue_utc` : SHA-256 possible, mais pas la datation éditeur historique.
- `SHOT_CREATION.SHOT_VOLUME_EXPOSURE` : volumes tirs bruts repérés, mais provenance, exposition et comparaison pré-T non certifiées.

Références :
`Terminator364/ChatGPT-PC` branche `research/matrice-r8-g3-depth-audit-2026-10-14`,
`MATRICE/R8_G3_DEEP_20261014/L3_BATCH06_LEAGUE_STRENGTH_20261016/L3_BATCH06_CONTRACTS.json`,
`MATRICE/R8_G3_DEEP_20261014/L3_BATCH07_SCORING_SHOTS_20261017/L3_BATCH07_CONTRACTS.json`,
et feuille directrice `MATRICE/GOUVERNANCE/FEUILLE_DE_ROUTE_DIRECTRICE_MATRICE_ADN_2026_10_14_R8.md`.

## Corrections à programmer dans le collecteur (pas encore implémentées)

1. **Mapping vérifiable** `source_field → world_id.child_id → source_proof`, avec unité, définition, version, licence, `available_at` et conflit éventuel.
2. **Distinguer** fichiers d'issues post-match et **preuves d'entrée prématch**. Ne pas injecter xG du match cible, tirs ou son score dans sa propre prévision.
3. Index `fixture_id`, alias clubs, coup d'envoi UTC, source d'origine, photographie `asof` immuable (J−6, J−3, J−1, H−1).
4. Audit par famille et ligue : couverture réelle, trous, conflits, formats et changements de définition des fournisseurs.
5. Fournisseurs supplémentaires autorisés pour blessures, convocations, arbitres, météo prévisionnelle historique, compositions et données événementielles; rien n'est déclaré utilisable sans preuve.
6. Tester les features sur fenêtres rétrospectives sans fuite et hors échantillon avant toute promotion scientifique.

## Localisation preuve
`C:\Users\Lenovo\Documents\COLLECTEUR_AUTONOME_MULTISOURCES\06_AUDITS\CONFORMITE_DONNEES_MATRICE_R8.json` : tableau détaillé par colonne et par famille; script de l'audit `audit_conformite_donnees.py`. Ces éléments sont distincts des journaux d'exécution du collecteur.

**Décision** : le pipeline possède une base documentaire prometteuse, mais n'est **pas conforme de bout en bout aux contrats de toutes les familles de MATRICE R8**. Exécuter les corrections comme un lot d'ingénierie futur, sans modifier le moteur officiel automatiquement.
