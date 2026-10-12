# BCP USB Rescue R3.1 — statut non certifié

## Améliorations vérifiées localement
- Correction non destructive ciblant le pare-feu Windows sur interface RNDIS/NCM USB uniquement (UAC explicite ; aucun lancement automatique).
- Diagnostic read-only des interfaces réseau USB, de la tâche de surveillance, de l’écoute TCP et de la règle de pare-feu.
- Possibilité de supprimer la règle créée, par contrôle utilisateur.
- Assistance utilisateur Java avec orientation en cas de connexion refusée et d’adresse mal saisie.
- Préservation applicationId `com.blessing.rescuebridge`; versionCode 3 (`0.3.1-usb-readiness`).

## Invariants non prouvés
- **Aucun APK réellement compilé, aucune installation sur le Samsung, aucun test USB sur MBMPC.**
- Scripts PowerShell contrôlés statiquement, non exécutés sur Windows.
- HTTP+HMAC sans confidentialité ; uniquement pour un banc USB privé sans données sensibles.
- Aucune intégration ChatGPT directe et aucun contrôle visuel/shell arbitraire.
- Windows nécessite Python 3.10+ et des autorisations explicites pour toute règle pare-feu.
- Signature d’APK stable non configurée. Éviter d’installer des builds debug temporaires sur une version durable.

## Build manuel
Workflow standalone `.github/workflows/build-android-rescue.yml` corrigé pour compiler `android/` depuis la racine du projet. Dans PROJECT-DRAFTS, la recette `usb-rescue-r3-manual-apk.yml` doit cibler le sous-dossier R3.1. Aucun déclenchement automatique ni exécution distante effectués.