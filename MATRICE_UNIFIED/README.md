# MATRICE — Consolidation documentaire et technique (incubation)

Cette branche publique contient exclusivement des **contrats de migration et d'audit génériques**. Elle ne contient ni corpus bruts, ni modèles propriétaires, ni performances détaillées, ni identifiants privés Google Drive.

## Périmètre et doctrine

- Famille de produits : Matrice historique, Matrice ISI, MAXV, recherches et évaluations.
- Une racine de projet sur chaque espace de stockage, avec sous-dossiers fonctionnels.
- Les états scientifiques, registres, identifiants et sauvegardes réels sont **privés** et restent dans le Drive connecté.
- Inventaire et contrôle des dépendances d'abord; réorganisation réversible ensuite.
- Les versions distinctes sont conservées, même si elles sont anciennes.
- Les doublons exacts ne peuvent être supprimés qu'après comparaison cryptographique et preuve d'un exemplaire survivant récupérable.
- Aucune fusion scientifique ou modèle promu dans la phase de migration documentaire.
- Aucun système d'engagement automatique de mises.

## Gates

1. Inventaire complet et paginé : source, ID, parent, propriétaire, taille, rôle, hash lorsque disponible.
2. Provenance et dépendances : pointeurs actifs et anciennes références identifiées.
3. Readback : chaque déplacement vérifié avec le même identifiant de fichier/dossier.
4. Déduplication : uniquement après preuve SHA-256 et absence de dépendances.
5. Audit comparatif reproductible : modèles, corpus et protocoles réellement comparables.
6. GO humain avant toute fusion, déploiement, édition live ou publication de données.

## Politique technique

- Projet hébergé dans un dépôt **public** d'incubation : zéro information privée dans Git, même dans les manifests.
- Respect impératif de `AGENTS.md` et `CI_BUDGET_POLICY.json` à la racine.
- **Zéro workflow GitHub Actions automatique** et aucun runner pour le ménage ordinaire.
- Un dépôt permanent privé peut être envisagé après inventaire et validation.

Ce document ne constitue ni une certification de prédiction sportive ni une garantie de rentabilité.
