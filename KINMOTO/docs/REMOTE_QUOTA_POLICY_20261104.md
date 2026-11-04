# KIN MOTO FACTORY — Politique de préservation Remote Desktop Commander

**Date :** 4 novembre 2026. **Décision propriétaire :** travailler essentiellement en ligne et ne toucher au PC qu'en dernier recours. Cette politique complète le gel Vercel du 04/11/2026.

## Contexte quantifié (capture utilisateur)

La capture fournie par le propriétaire indique **6 049 appels consommés sur 10 000** (60,49 %), soit **3 951 appels disponibles au moment de la capture**, avec remise à zéro indiquée pour le **1er décembre 2026**. C'est un instantané d'interface et **non un relevé actualisé par l'API**. Le reste peut changer ; aucun appel Remote ne doit être utilisé pour actualiser ce chiffre sauf nécessité explicitement justifiée.

## Priorités des moyens d'exécution

1. **GitHub connecté :** rechercher, lire, versionner et relire le dépôt ; gérer issues/PR et revues. Ne pas utiliser des runners hébergés par défaut, selon `CI_POLICY.md`.
2. **Environnement d'exécution isolé côté assistant :** tester Node/Python, assembler builds, créer ZIP, vérifier licences et hashes ; zéro charge CPU/RAM sur le PC utilisateur.
3. **Sources publiques directement via GitHub / documentation officielle :** vérifier modèles, licences et dimensions avant acquisition. Ne pas demander un navigateur PC pour une page accessible sans lui.
4. **PC utilisateur — dernier recours seulement :** essai de saisie réelle, comparaison de FPS/RAM sur l'Intel UHD 620, comportement Windows/Opera, ou bug matériel impossible à reproduire en conteneur. Grouper les vérifications en une intervention courte et planifiée après les gates de logique.
5. **Android réel :** ne pas affirmer sa compatibilité tant que l'essai matériel n'existe pas. Préparer des packages installables hors connexion ou tests LAN sur réseau privé ; ne pas forcer l'installation de services payants.

## Barrières et règles strictes

- **Budget Remote opérationnel par défaut : 0 appel par lot de développement.** Il n'est pas nécessaire de bloquer absolument une intervention critique ; elle doit comporter une justification, un objectif mesurable et ne pas répéter un contrôle déjà possible côté cloud.
- **Aucun appel Remote pour** simples listings, lectures de repo, téléchargements de projets GitHub, compilation, tests unitaires, édition de fichiers, hashing ou copies de documents.
- Un audit du PC est regroupé en un seul créneau à la validation technique d'une candidate, pas à chaque module.
- Conserver des notes d'environnement après l'unique mesure matérielle afin de ne pas relire les mêmes données à chaque conversation.
- **Vercel : gel confirmé ;** aucune nouvelle publication/alias/build via outil Vercel jusqu'au GO explicite du propriétaire. Hébergement gratuit ne signifie pas quotas illimités.
- **GitHub Actions : 0 minute hébergée par défaut.** Préférer les tests locaux de l'environnement isolé.
- **Pas d'API payante, pas d'abonnement, pas de facture, zéro FC supplémentaire.**

## Checkpoint et reprise

Chaque lot doit enregistrer un commit/PR, une version, une suite QA avec FAIL/NOT_TESTED explicites, `PROJECT_STATE.json` et `NEXT_ACTION.md`. Les anciens sites et jeux restent intacts jusqu'à validation de la release candidate par le propriétaire.

**Codes :** `KINMOTO|SYNC` relit l'état ; `KINMOTO|WORK|CONTINUE` exécute le prochain lot hors Remote ; `KINMOTO|AUDIT` contrôle la validité des preuves et quotas. Ces codes ne font pas de synchronisation automatique.
