# MATRICE BUILD HUB — V0.2 HARDENED

Usine centrale de production pour les projets Terminator364.

## Mission utilisateur

Le flux normal doit rester simple:

**bug/amélioration dans ChatGPT → source GitHub corrigée → MATRICE BUILD HUB → build cloud → vérifications locales → prerelease GitHub → lien utilisable.**

L'utilisateur n'a pas à apprendre Gradle, Android SDK, SSH, Codespaces ou GitHub Actions.

## Architecture active

- GitHub est la source canonique.
- Les GitHub Actions hébergées restent **manual-only / exceptionnelles**; BuildHub ne les déclenche pas pour une production normale.
- GitHub Codespaces est le compilateur distant principal tant que le quota inclus est disponible.
- La plus petite machine adaptée est choisie en priorité.
- Les Codespaces prebuilds sont refusés.
- Chaque branche de production possède sa recette `.matrix-build/build.sh`; les adaptateurs centraux ne sont que des fallbacks.
- Le build est figé sur un SHA source exact avant la création du builder.
- Les APK Android sont produits **non signés dans le cloud**.
- Les clés Android ne quittent pas Windows: vault local protégé par DPAPI CurrentUser.
- La signature, le package ID, la version et le certificat sont vérifiés localement.
- Une sauvegarde catastrophe chiffrée doit être exportée et **restaurée/testée fonctionnellement** avant toute production Android signée.
- Les artefacts publiés sont revalidés contre le digest SHA-256 renvoyé par GitHub.
- Les scripts shell sont forcés en LF pour éviter les pannes Windows→Linux.
- Le Codespace est stoppé puis supprimé après le job.
- Un ledger local estime la consommation de core-hours et bloque au plafond interne.

## Projets enregistrés

- PhoneMouse
- P2PCR95
- ChatGPT-PC

Voir `projects.json` pour les branches de production et les contrats de build.

## Gates AX15

Un PASS statique n'est pas un PASS terrain. BuildHub reste non opérationnel tant que les preuves réelles Windows/Codespaces/Android ne sont pas observées.

Gates principaux: `STATIC_AUDIT_PASS`, `ZERO_AUTO_ACTIONS_ACTIVE_BRANCHES`, `LOCAL_BOOTSTRAP_PASS`, `LOCAL_SIGNING_VAULT_PASS`, `DISASTER_RECOVERY_EXPORT_PASS`, `DISASTER_RECOVERY_RESTORE_TEST_PASS`, `CLOUD_SMOKE_PASS`, `ANDROID_CLOUD_BUILD_PASS`, `LOCAL_SIGNATURE_PASS`, `RELEASE_ASSET_DIGESTS_PASS`, `UPDATE_OVER_EXISTING_APP_PASS`, `SECOND_INDEPENDENT_BUILD_PASS`.

## Point d'entrée

Après l'installation unique, utiliser simplement:

`hub.cmd`

Le launcher exécute le self-test avant toute construction et bloque en cas d'incohérence.

## Statut

V0.2 hardening. Ne pas déclarer **OPERATIONAL** avant les campagnes réelles prévues dans `CONTINUATION_BUILDHUB_AX15.md`.
