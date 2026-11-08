# PCRC V2 — banc public isolé (2026-11-08)

Ce dossier est un **banc public de tests contractuels**, pas une copie de `Terminator364/ChatGPT-PC`.

## Frontière de sécurité
- Ne jamais publier : sources privées, endpoints, noms d'hôte privés, secrets, certificats, clés, fichiers SQLite, journaux de production, captures ou états du HP.
- Les seules entrées de CI sont les fichiers publics de ce dossier et la bibliothèque standard Python.
- Aucun accès au dépôt privé, à l'ordinateur HP, à ChatGPT Sites ou aux secrets GitHub.
- `GITHUB_TOKEN` en lecture seule; aucune action tierce, aucun artifact à téléverser.
- Toute synchronisation future des tests depuis le dépôt privé exige un **audit de déclassification** manuel avant publication.
- Résultat vert = conformité du **modèle contractuel public**, jamais certification du Core V2 réel.

## Contrainte mémoire
La cible est de **maintenir les commandes légères et le journal durable** sous pression mémoire (y compris lorsque l'indicateur Windows atteint 99 %), pas de garantir une opération lourde nécessitant de la RAM inexistante. Les tests publics vérifient la logique de découpage et de mise en attente sans allocation massive; les essais réels de Windows/HP restent séparés et supervisés.

## CI et quotas
Standard GitHub-hosted runners sur dépôt public : utilisation gratuite selon GitHub, soumise aux limites d'usage et d'abus; runners plus grands facturables. Ce banc n'utilise que `ubuntu-latest` et `windows-latest`. La politique historique du dépôt (0 minute) est remplacée **pour ce périmètre public explicite seulement** par l'instruction du propriétaire du 8 novembre 2026. Les quotas privés restent protégés. Pas de déclenchement `schedule`; filtres de branche et de chemins.

## Phases
1. CI publique autonome (ce lot) — ne déploie rien.
2. Intégration de cas de test déclassifiés avec rapport de correspondance contre la source privée.
3. Qualification locale Windows/HP et vérification cryptographique indépendante.
4. Canary V2 réel avec rollback et arrêt des opérations risquées en cas d'incohérence.

## Première validation
Le workflow est limité à la branche expérimentale publique. Son résultat doit être observé dans GitHub Actions avant toute affirmation de réussite.
