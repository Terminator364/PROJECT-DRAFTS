# COLLECTEUR AUTONOME MULTISOURCES — lancement indépendant vérifié

**17 octobre 2026, 18:05:47 UTC / 19:05:47 Kinshasa**.

## Identité
- Dossier maître PC : `C:\Users\Lenovo\Documents\COLLECTEUR_AUTONOME_MULTISOURCES`.
- Projet autonome distinct de MATRICE (aucun commit ni coefficient modifié dans le dépôt MATRICE).
- Dépôt brouillon : `Terminator364/PROJECT-DRAFTS`, branche `experiment/bcp-autonomous-data-run-2026-10-17`, sous-dossier indépendant `independent-multisource-collector/`.
- Deux dossiers sources archivés **par copie**, non déplacés : le workspace R8 (215 fichiers) et le dossier BCP 2026-10-17 (125 fichiers) ont été consolidés sous la racine maîtresse. Les originaux demeurent.
- Charte maîtresse locale : `00_GOUVERNANCE\CAHIER_MAITRE_COLLECTEUR.md`.

## Fonctionnement actif
- Contrôleur : `standalone_controller.py` lancé sur MBMPC via `pythonw.exe`.
- PID confirmé à la vérification : **5364**, `MASTER_PROCESS_ALIVE=True`.
- Run ID : `MASTER-20261017T180234Z` (état initial créé pendant le smoke test et réutilisé par le run actif).
- Programme indépendant de la conversation et borné à **24 heures à compter du lancement vers 18:05 UTC**.
- Cadence : heartbeat toutes les **60 secondes**; audit / rapprochement des archives **toutes les 300 secondes**.
- Source réseau ouverte : seulement les **deux fichiers de calendrier de OpenFootball**, avec délai minimal **86400 secondes** entre cycles réseau (24h). La source est publique/CC0; les fichiers Football-Data et TheSportsDB sont relus en cache uniquement, **sans réseau répété**.
- Retour initial du réseau : **2/2 fichiers OpenFootball validés**, **380 rencontres par ligue**, empreintes enregistrées. Aucun échec observé au lancement.
- Test `python standalone_controller.py --once --offline` : **exit code 0**.
- Premier rapport indépendant : **60/60 matchs déjà terminés rapprochés par ligue** et **15/15 accords trois sources par ligue** sur l'échantillon gratuit limité. Aucun conflit triple constaté.
- Source code préservé GitHub, logs sur PC. Les fichiers de rapport ne sont pas des preuves de calibration d'IC.

## Localisation de la preuve
- `07_EXECUTION\MASTER_STATE.json` : état et échéance
- `07_EXECUTION\LAST_RECEIPT.json` : reçu de la dernière fin; celui existant au lancement est celui du **smoke test**, pas une clôture de la mission de 24h
- `09_JOURNAUX\master_events.jsonl` : événements de lancement, rafraîchissement et heartbeat
- `08_RAPPORTS\LATEST_TWO_LEAGUES.json` : dernier rapport
- `05_JOURNEES\E0_JOURNEES.json` et `I1_JOURNEES.json` : données rapprochées par journée
- `03_FOURNISSEURS\OPENFOOTBALL_SHA256` : objets JSON bruts et versionnés par empreinte

## Garde-fous
- Ce n'est **pas** une seconde instance intelligente de ChatGPT qui raisonne spontanément : programme codé autonome spécialisé.
- Référence au registre des 62 familles R8 sans promotion de paramètres à l'IC.
- Données sportives historiques pas certifiées PIT : les horodatages de publication/availability avant chaque match restent à reconstituer.
- S'il y a coupure de courant/redémarrage Windows, le processus s'arrête; checkpoint conservé mais **pas de démarrage automatique à l'ouverture de session** configuré à ce stade.
- Une future clôture réelle de la session de 24 heures doit être vérifiée sur le PC et documentée séparément; ne pas la présumer.

## Reprise
Code de continuité : `COLLECTEUR/CONTINUE`. Toujours reprendre par état de `MASTER_STATE.json` et la charte maîtresse, puis les rapports et journaux.
