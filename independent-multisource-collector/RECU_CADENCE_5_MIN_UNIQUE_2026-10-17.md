# COLLECTEUR — réconciliation de la cadence, un seul processus

Date : 17 octobre 2026, initialisation 18:15:20 UTC (19:15:20 Kinshasa).

## Demande utilisateur interprétée strictement
- **Un seul programme actif**, dans `C:\Users\Lenovo\Documents\COLLECTEUR_AUTONOME_MULTISOURCES`.
- **Une vraie collecte depuis Internet toutes les cinq minutes**, et pas uniquement une relecture des fichiers existants.
- Méthode par source respectant ses limites. Première source à cadence 5 minutes : TheSportsDB gratuite, Premier League + Serie A, aujourd'hui et demain.
- OpenFootball publie une compilation quotidienne : consultation réseau du fichier complet au plus toutes les 24 heures.
- Football-Data ne permet pas de collecte répétitive intensive : réutilisation du cache seulement.

## Opérations réalisées (preuves PC)
1. Arrêt propre de l'ancien contrôleur PID 5364 par `07_EXECUTION\STOP`; lecture de l'état `stopped_by_user`.
2. Modification du contrôleur unique `standalone_controller.py` pour inclure un module `five_minute_provider.py` exécuté toutes les 300 secondes; ce module n'est **pas** un second programme exécuté en permanence.
3. Quatre tests de sécurité exécutés sur MBMPC : **4/4 OK** (exclusion scores/live, exclusion événements anciens sous statut NS, aucune sauvegarde de résultat live, absence d'heure).
4. Retrait du drapeau STOP puis démarrage **d'un seul** processus `pythonw.exe` de PID **13876**. Contrôle `Win32_Process` : **ACTIVE_PROJECT_PROCESS_COUNT=1**.
5. Première collecte vérifiée : `network_request_count=4`, **4 requêtes HTTP** vers TheSportsDB V1 `eventsday`, 2 compétitions × 2 dates, **7 fixtures futures conservées, 5 événements live/past éliminés, aucune erreur**.
6. Fichier de preuve : `03_FOURNISSEURS\THESPORTSDB_PREMATCH\LATEST_PREMATCH.json`, horodatage `2026-10-17T18:15:20+00:00`, `no_scores_or_live_features: true`.
7. État : `07_EXECUTION\MASTER_STATE.json` `status=running`, `heartbeat` une fois par minute, `last_five_minute_fetch_epoch` activé; rapports inter-sources toutes les 5 minutes.
8. Maintien des 2 ligues prioritaires (favoris SofiaScore transcrits) et du registre des 62 familles pour usage futur, sans déclarer de couverture opérationnelle.

## Limitations non négociables
- **Il n'y a pas un téléchargement complet et indépendant de toutes les données de MATRICE toutes les 5 minutes**. La source TheSportsDB gratuite limite sa réponse `eventsday` à 3 rencontres/date/ligue ; les 4 requêtes donnent au plus 12 événements bruts par cycle. Le filtre rejette les statuts live et terminés.
- On conserve des **informations de calendrier prématch**, pas des xG, données de blessures, compositions historiques PIT certifiées, ni un modèle IA autonome qui raisonne.
- Les premiers résultats montrent qu'un téléchargement a été exécuté au démarrage ; il faudra vérifier un **deuxième cycle après au moins 300 secondes** pour prouver la répétition réelle.
- TheSportsDB API V1 gratuite : https://www.thesportsdb.com/docs/api (30 requêtes/minute; `eventsday` 3 items gratuits); arrêt temporaire une heure si HTTP 429; OpenFootball : https://github.com/openfootball/football.json (mise à jour automatique quotidienne, sources TXT manuelles).
- Aucun modèle/coefficients IC MATRICE modifié.
