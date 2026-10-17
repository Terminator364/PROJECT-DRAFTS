# Index unique — Bibliothèque historique et entraînement exploratoire

**17 octobre 2026 • Projet indépendant** `COLLECTEUR_AUTONOME_MULTISOURCES` • Compétitions favorites pilotes : Premier League et Serie A.

## Une seule racine, deux couches complémentaires

Le dossier maître reste `C:\Users\Lenovo\Documents\COLLECTEUR_AUTONOME_MULTISOURCES`. Les deux sous-dossiers de `05_JOURNEES` ne sont **pas deux programmes** :

1. **INDEX HISTORIQUE CANONIQUE** `HISTORIQUE_J1_ACTUEL` : journées J1–J6, 120 matchs historiques, score et provenance, index de recherche, six horizons théoriques par match (J−6, J−4, J−3, J−1, H−1, H0). Serie A J7 avec match non résolu reste explicitement sans résultat. C'est le point d'entrée qui doit être actualisé en priorité.
2. **COUCHE DÉTAIL ET CONTRÔLE** `HISTORIQUE_J1_J6` : 120 fiches JSON **une par match**, 12 synthèses de journée, 12 grilles `COUVERTURE_62_ET_L3.json`, et bilan général. Reconstitution déterministe depuis les CSV historiques sauvegardés, sans connexion ni deuxième worker. Chaque fiche conserve tous les champs source et sépare `H0_ASOF_BEFORE_KICKOFF` (encore inconnu) et `AFTER_MATCH_ARCHIVE` (observations post-match), plus une esquisse de features fondées seulement sur matches précédents à date strictement antérieure.

## Périmètre validé

- 2 ligues, 6 journées complètes chacune, 10 matchs par journée = **120 matchs**.
- Scores : **100 accords** Football-Data et OpenFootball, **20 résultats** provenant seulement de Football-Data dans les snapshots consultés (octobre). Le recoupement TheSportsDB concerne séparément seulement un petit échantillon historique.
- Correspondance documentaire : **62 familles gelées** MATRICE R8, **109 sous-paramètres L3 documentés sur 20 familles**. Les 42 autres familles **n'ont pas de contrats L3 vérifiés dans ces lots consultés**; ne pas en inventer.
- 12 × 62 = **744 entrées de couverture**; 12 × 109 = **1308 références d'enfants L3** dans la couche de contrôle.
- **720 horizon-fiches** = 120 matchs × 6 horizons théoriques (squelettes non certifiés PIT).
- Tests hors ligne : **5/5** contre-tests indépendants sur la couche de détail; **11/11** tests documentés sur la couche canonique et le module historique, soit **16/16** dans deux commandes distinctes.
- **Zéro famille nouvellement certifiée opérationnelle pour l'IC**. Les résultats historiques sont des labels et corpus d'apprentissage; les données de matchs antérieurs ne deviennent des features J−n qu'avec preuves de disponibilité à cet horizon.

## Historique H0 versus post-match

**H0 avant coup d'envoi** : peut comprendre l'heure, l'équipe, les absents confirmés, la composition officielle si publiée, arbitre, prévision météo datée. Le pilote n'a **pas reconstitué** ces preuves historiques à H0. Le statut est **UNKNOWN / NOT_RECONSTRUCTED**.

**Après le match** : résultat, buts, tirs, xG, cartons et autres statistiques sont des observations de la rencontre; elles doivent servir de **labels** et de connaissances historiques pour entraîner les lois et mesurer les effets sans fuite sur le match cible.

Le modèle d'anticipation devra apprendre à partir de couples (snapshot disponible à J−6...H0, issue survenue plus tard), une fois les vrais horodatages de publication acquis. **La date du match n'est pas la date de publication du fournisseur.** Les six horizons générés restent donc **plans de recherche**, pas replays certifiés.

## Exécution unique

Le contrôle maître `standalone_controller.py` est le seul programme persistant. `historical_matchdays.py`, `build_historical_horizons.py`, `historical_provider_backfill.py` sont des modules / exécutions ponctuelles, non des travailleurs parallèles. Pour actualiser les données, le maître devra effectuer les collectes historiques limitées selon le fournisseur, sans mélanger les résultats live et futurs dans l'historique. Les preuves sont sous `07_EXECUTION`, `09_JOURNAUX`, `03_FOURNISSEURS`.

**Décision :** conserver les deux couches dans le même dossier maître avec ce repère explicite. Ne pas supprimer un artefact existant avant rapprochement des manifestes et contrôle de références.
