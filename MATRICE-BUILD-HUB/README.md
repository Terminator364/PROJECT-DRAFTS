# MATRICE BUILD HUB — V0.1

Usine centrale de build pour Terminator364.

Objectif utilisateur: signaler un bug dans la conversation du projet, laisser ChatGPT corriger le dépôt, puis obtenir une nouvelle bêta sans apprendre Gradle, Android SDK, SSH ou GitHub Actions.

Flux: ChatGPT -> GitHub -> MATRICE BUILD HUB -> GitHub Codespaces -> APK/EXE/bundle -> GitHub prerelease -> lien.

Règles: GitHub Actions reste à 0 minute par défaut; pas de Codespaces prebuild; plus petite machine disponible; arrêt/suppression après build; aucune clé de signature committée.

Fichiers: hub.ps1, hub.cmd, projects.json, adapters/.

La première installation PC demande GitHub CLI et une authentification GitHub. Après cela, hub.cmd doit devenir le point d’entrée unique.
