# BCP USB Rescue R3 — qualification et limites au 12 octobre 2026

## Obtenu
- Code Android Java R3 : interface utilisateur orientée accueil, 4 onglets, assistance de diagnostic, appairage dans Réglages, icône adaptative et versionCode=2 ; même applicationId `com.blessing.rescuebridge` que R2.
- Agent Windows R2 réutilisé sans réécriture, isolation du dossier de test, authentification HMAC, anti-rejeu et superviseur de liaison USB.
- 42 tests par cycle, 3 cycles réussis dans l'environnement d'exécution fourni : 126 tests au total. Protocole JVM/Python éprouvé en loopback. Java sans Android (quatre classes cœur) compilé par `javac`.
- Sources R3 stockées individuellement dans `Terminator364/PROJECT-DRAFTS/USB-PHONE-RESCUE-LAB/r3-src` sur branche de travail.
- Workflow GitHub Actions R3 exclusivement `workflow_dispatch`, sans runners lancés de notre côté.

## NON accompli — bloquants réels
- **AUCUN APK R3 COMPILÉ** : Android SDK 35 et Gradle absents localement, pas de possibilité de télécharger les outils depuis cet environnement.
- **AUCUNE validation Android Emulator ou Samsung SM-G990E Android 16** : pas de preuve de responsive UI sur le matériel.
- **MBMPC non accessible** via Desktop Commander lors de la vérification; pas de test USB réel, d'installation Windows ni de redémarrage terrain.
- R3 conserve HTTP + HMAC uniquement (intégrité, pas confidentialité). Ne pas utiliser avec données sensibles, ni sur réseau partagé.
- Aucune connexion directe à ChatGPT, aucun contrôle GUI/shell général, aucune découverte automatique fiable de l'IP Windows. Le mode suivi ne tourne qu'au premier plan.
- L'APK de débogage construite par GitHub Actions aurait une signature variable selon le runner. Aucune mise à jour par-dessus une APK existante n'est garantie avant la fixation d'une identité de signature.
- Windows nécessite Python 3.10+ installé. Les scripts de démarrage Windows n'ont pas été exécutés sur Windows réel.

## Prochaine chaîne de certification
1. Compiler R3 via `usb-rescue-r3-manual-apk.yml`, lire les logs et les SHA-256, vérifier `apksigner` et l'applicationId.
2. Doter les builds diffusables d'une identité de signature permanente, conservée en coffre protégé et non commitée au dépôt.
3. Tester AVD tailles/zoom de polices et téléphone Samsung réel; résoudre toute anomalie.
4. Installer l'agent dans la session Windows, tester le câble USB RNDIS/NCM, permissions, pare-feu, reconnexion et veille avec reçus.
5. Ajouter un canal chiffré de bout en bout et un chemin d'instructions ChatGPT explicitement supporté avant d'élargir les capacités.