# MATRICE R8 — Pilote de collecte multi-source, deux favoris (17 octobre 2026)

**Dépôt expérimental :** `Terminator364/PROJECT-DRAFTS`, branche `experiment/bcp-autonomous-data-run-2026-10-17`.

**Source des favoris :** `Terminator364/ChatGPT-PC`, `MATRICE/GOUVERNANCE/FAVORIS_COMPETITIONS_CAPTURE_CANDIDATS_R7.md`, branche `research/matrice-r8-g3-depth-audit-2026-10-14`. Le registre précise que la transcription est indicative et partielle. Deux compétitions effectivement mentionnées : **Premier League** (E0) et **Serie A** (I1). Ce pilote ne prétend pas couvrir l'ensemble des favoris.

## Trajet chronologique

- Date de recherche et cutoff exclusif des résultats historiques : **2026-10-17**.
- Saison cible : **2026/27** ; parcours **matchday 7 → 1** pour chaque compétition.
- **14 dossiers de journées**, 10 fixtures chacun, 140 rencontres en calendrier.
- J1–J5 : **100 matchs avec scores identiques** dans deux bases distinctes.
- J6 (10–12 octobre) : **20 scores vérifiés dans Football-Data en cache**, mais manquants dans les fichiers OpenFootball consultés, soit un retard de cette source.
- J7 : 10 rencontres anglaises datées du 17–19 octobre (résultats volontairement exclus), 10 italiennes dont Frosinone–Sassuolo du 16 octobre. Ce résultat 4–2 est consigné **dans une pièce post-match officielle distincte**, non utilisé comme feature pré-match du match concerné.

## Couches de sources

1. **Football-Data** (https://www.football-data.co.uk/downloadm.php) : archives CSV 2026/27 des deux championnats **déjà téléchargées lors du test précédent** et conservées sur MBMPC avec SHA-256, sans nouveau téléchargement de ce fournisseur pendant ce pilote. Conditions de fair use : au plus deux téléchargements automatisés par semaine. Ne pas recopier ici les CSV bruts.
2. **OpenFootball / football.json** (https://github.com/openfootball/football.json) : `2026-27/en.1.json` et `2026-27/it.1.json`, téléchargés une fois chacun et sauvegardés avec empreinte; données publiées en domaine public. Le dépôt signale que son pipeline JSON peut s'exécuter quotidiennement **sans garantir** la fraîcheur des sources Football.TXT en amont.
3. **Autorités officielles** : Premier League, https://www.premierleague.com/en/matches/premier-league/2026-27/matchweek-7 ; Lega Serie A, https://en.legaseriea.it/serie-a/fixtures-results. Pour les désignations d'arbitres : https://www.premierleague.com/en/news/4731949/match-officials-for-matchweek-7 (publié le 16 octobre selon page consultée), https://en.legaseriea.it/serie-a/news/the-referees-for-the-7th-round-x8311 (annoncé le 14 octobre). **12 affirmations sourcées** associées aux fixtures (2 Premier League et 10 Serie A). Il ne s'agit pas de 20 désignations complètes pour les deux ligues.

## Résultats reproductibles

- `reports/ROUNDWISE_MANIFEST.json` : audit des deux sources structurées et état par journée.
- `reports/E0_matchday_01.json` ... `E0_matchday_07.json` et les homologues `I1` : **14 fixtures snapshots**. Les journées 6 et 7 conservent les divergences/métadonnées explicites.
- `reports/OFFICIAL_ENRICHMENT_REPORT.json` : couverture des faits officiels.
- `reports/E0_RESEARCH_FEATURES.json` et `I1_RESEARCH_FEATURES.json` : **70 lignes chacune**, dérivés candidats : régime de buts, moyennes d'équipe (domicile/extérieur), cinq derniers résultats, intervalle en jours depuis match précédent. Les calculs utilisent **uniquement les résultats datés strictement avant chaque rencontre**. Pour les fixtures J7, les statistiques sont construites sur 60 matchs antérieurs par ligue et la dernière date source est le 12 octobre 2026.
- `collect_roundwise.py`, `enrich_official.py`, `build_research_features.py`, `test_roundwise.py`, `test_features.py` : code et validation. Depuis le dossier `v3_favorites`, exécuter `python -m unittest -v test_roundwise test_features` (**8/8 réussis sur MBMPC**).

**PC de travail :** `C:\Users\Lenovo\BCP_AUTONOMOUS_TEST_20261017\v2\v3_favorites`, sorties locales dans `outputs/`. Dans un clone du dépôt, les tests et dérivés utiliseront automatiquement `reports/` si `outputs/` n'existe pas. Pour réexécuter le téléchargement OpenFootball, `collect_roundwise.py` nécessite les CSV existants du test V2 dans son dossier d'intégration; ne pas relancer de téléchargement Football-Data.

## Frontières de preuve — primordiales

- **RESEARCH_ONLY, OBSERVATION_ONLY, aucun IC, aucun effet activé.** Les 62 familles de MATRICE ne sont pas collectées ou opérationnelles. Les requêtes historiques ne documentent pas encore les heures `published_at` et `available_at`; sans ces preuves, les replay J−6/J−3/J−1/H−1 restent **non certifiés PIT**.
- Pour les données de matchday 7 à la date de coupure, scores du 17 octobre ou futurs sont exclus. Le score italien du 16 octobre observé après événement n'est pas ajouté à la feature de son propre match.
- Les données officielles de referee sont gardées comme **preuve documentaire horodatée au jour**, l'heure de publication restant non vérifiée. Elles ne sont pas un coefficient de probabilité Over 1,5.
- Les identifiants d'équipe sont réconciliés par **40 alias explicites**; aucune association automatique d'homonymes sur la base d'un score.
- Aucun scraping minute-par-minute, aucun contournement de blocage ni API payante imposée. Ce pilote est une **exécution ponctuelle**, pas un agent IA autonome qui continue à rechercher sans outils.
- Cette expérience **ne modifie pas** la feuille directrice R8, la branche MATRICE principale ni le moteur historique 2.0/2.5. Fusion et promotion seulement après audit scientifique.

## Suite logique

Compléter les **contrats par sous-paramètre** des 62 familles (source, droits, identité, instant de publication, hétérogénéité des ligues, coût, confiance, scénarios); brancher ensuite des producteurs complémentaires (statistiques événementielles autorisées, effectifs/communiqués clubs, arbitres, météo prévisionnelle datée), conserver les contradictions et tester la valeur incrémentale des features contre les baselines, avant toute modification d'IC.
