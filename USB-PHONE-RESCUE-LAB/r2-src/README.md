# BCP USB Rescue R2 — Android + Windows

**ÉTAT : CODE SOURCE + TESTS INTÉGRATION VALIDÉS HORS ANDROID ; APK NON CONSTRUIT, USB RÉEL NON TESTÉ.**

Ce n'est pas une application ChatGPT officielle ni un équivalent complet de Desktop Commander. Elle fournit un **canal de diagnostic et de fichiers borné** du téléphone vers un agent Windows via un réseau privé, notamment le partage Internet USB Android.

## Ce qui existe

- **android/** : vraie application Android Java (package `com.blessing.rescuebridge`, Android 8.0+), écran d'appairage, signatures HMAC, clés chiffrées Android Keystore, diagnostics, audit, consultation et écriture après confirmation dans un seul espace autorisé.
- **windows/bridge_agent.py** : serveur Python 3.10+ autonome, bind explicite IP USB, anti-rejeu persistant SQLite, écritures atomiques, sauvegardes, sélecteur limité d'actions.
- **windows/guardian.ps1** : superviseur de session Windows qui attend l'interface USB RNDIS/NCM et relance l'agent ; sans élévation, sans règle pare-feu automatique.
- **windows/install_startup.ps1** : autorise volontairement un raccourci pour relancer le gardien **à l'ouverture de session utilisateur**. Ce n'est pas un service pré-login.
- **windows/REMOVE.cmd** : retire la tâche planifiée, en conservant volontairement les données.
- **tests/** : tests de sécurité, serveur HTTP réel sur loopback, interopérabilité Java-Python, vérification de syntaxe Java.
- **.github/workflows/build-android-rescue.yml** : recette GitHub Actions avec `workflow_dispatch` uniquement. Ne s'exécute pas toute seule et ne consomme pas de minutes sans déclenchement manuel.

## Installer et utiliser : après compilation de l'APK

1. Sur Windows, installer Python 3.10+, extraire ce package, double-cliquer sur `windows/INSTALLER.cmd`, activer le partage de connexion USB sur le téléphone, puis lancer `%LOCALAPPDATA%\BCP-USB-Rescue\windows\Start-Bridge.ps1`. **Le mode MTP/transfert de fichiers seul ne suffit pas.**
2. Sur le PC, trouver l'IP de l'interface `USB RNDIS/NCM` avec `ipconfig`. L'agent attend le réseau USB; les pare-feux peuvent nécessiter une autorisation locale spécifique. **Ne jamais ouvrir le port sur Internet.**
3. Démarrer l'agent; la clé est générée dans `%LOCALAPPDATA%\BCP-USB-Rescue\private-state\pairing-key.txt`. Copier les 64 caractères hexadécimaux dans l'application Android, puis les enregistrer (Android Keystore).
4. Saisir l'IP Windows du réseau USB et le port `8766`, lancer `Tester l'état du PC`.
5. Pour activer le superviseur après ouverture de session à chaque redémarrage, exécuter `INSTALLER.cmd` une fois, dans PowerShell, avec autorisation de l'utilisateur. Les réglages sont réversibles par `REMOVE.cmd`.
6. Les écritures s'effectuent seulement dans `%LOCALAPPDATA%\BCP-USB-Rescue\workspace`, après confirmation visible sur le téléphone. Ne pas y mettre de données sensibles tant que TLS n'est pas implémenté.

## Compiler une APK

Avec Android SDK 35, Build Tools 35 et Gradle 8.9 sous JDK 17 :

```bash
cd android
gradle :app:assembleDebug
```

L'APK résultante est : `android/app/build/outputs/apk/debug/app-debug.apk` **uniquement lorsque le build réussit**. Un fichier de ce nom n'est PAS livré dans ce package source.

Sur GitHub, le workflow manuel propose de compiler et conserver l'APK comme artefact, sans déclencheur `push`, `pull_request` ni `schedule`.

## Importer une mission depuis ChatGPT (R2)

La nouvelle interface Android contient « Importer mission JSON » et « Partager dernier résultat ».
Lorsqu'une mission est proposée dans cette conversation, tu peux télécharger le JSON sur Android,
l'importer avec le sélecteur de fichiers, puis lire ou partager le résultat pour qu'il soit analysé ici.
C'est un **transfert manuel de fichier**, et **pas un connecteur ChatGPT ni une télécommande autonome**.
Les missions ont une expiration maximale de 24 heures après émission.
Une mission d'écriture affiche une confirmation sur le téléphone; les autorisations transportées dans le fichier sont ignorées.

Exemple de structure d'une mission de lecture seule :

```json
{"schema":"bcp-rescue-mission/1","action":"diagnostics","expires_unix_seconds":0,"payload":{}}
```

Ce **gabarit n'est pas exécutable** : sa date d'expiration égale à 0 provoque volontairement son refus.
Il faut générer un vrai horodatage d'expiration dans les 24 heures lorsque la mission est créée.

## Vérifications réelles obtenues

- Tests Python serveur sur HTTP loopback : OK.
- Signature Java sur JVM compatible avec validation HMAC Python : OK.
- Analyse syntaxique des quatre sources Java Android : OK.
- Émulateur Android/AUT réel : **NON EXÉCUTÉ**.
- APK construite et installée : **NON EXÉCUTÉ**.
- USB Android ↔ MBMPC : **NON EXÉCUTÉ**.
- ChatGPT connecté directement à l'app : **NON IMPLÉMENTÉ**. Ce module ne crée pas de connecteur MCP ChatGPT.
- Prise de contrôle visuelle / shell arbitraire : **NON IMPLÉMENTÉ** par sécurité et périmètre.

## Risques et garde-fous

Le tunnel actuel utilise **HTTP + HMAC** : il authentifie les messages et les réponses mais **ne chiffre pas le contenu en transit**. À employer uniquement sur un réseau USB privé de test, jamais sur un LAN hostile ou Internet. Avant une sortie de type production, ajouter TLS 1.3 avec épinglage du certificat, séparation des autorisations, révocation, règles Windows minimales, limitation des requêtes, validation sur l'appareil réel et tests UI Android.

Les tests locaux certifient seulement les propriétés exécutées, pas la disponibilité de ton PC lorsqu'il est éteint, ni la fiabilité d'une liaison USB jamais testée sur MBMPC.

## Compilation GitHub R2, sans déclencheur automatique

Les fichiers Java, Gradle, Windows et tests sont aussi déposés dans
`Terminator364/PROJECT-DRAFTS`, branche `work/usb-phone-rescue-lab-2026-10-12`,
sous `USB-PHONE-RESCUE-LAB/r2-src/`.

Workflow GitHub Actions **manuel uniquement** sur la branche principale :
`https://github.com/Terminator364/PROJECT-DRAFTS/actions/workflows/usb-rescue-r2-manual-apk.yml`

Ouvrir ce lien, choisir `Run workflow` (workflow sur `main`). Le job vérifie l'archive,
compare les dix fichiers Android lisibles, lance la suite Python/JVM, compile
avec JDK 17 / SDK 35 / Gradle 8.9, puis sauvegarde le fichier `app-debug.apk`
sous l'artefact `BCP-USB-Rescue-R2-debug-APK` en cas de succès. Il faut
**constater un run réussi et télécharger cet artefact** avant d'affirmer
qu'un APK existe. L'application ne dispose pas encore de signature stable pour
une distribution pérenne ; les APK de débogage ne constituent pas une version de production.

Ne pas activer de déclencheur CI automatique ni contourner la politique `AGENTS.md`.