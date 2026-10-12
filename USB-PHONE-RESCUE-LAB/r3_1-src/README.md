# BCP USB Rescue R3.1 — Android + Windows (prototype de validation)

**ÉTAT : SOURCES ET TESTS LOGICIELS VALIDÉS. APK NON CONSTRUIT. USB SAMSUNG ↔ MBMPC NON PROUVÉ.**

Objectif : un canal de secours pour consulter l'état de Windows et lire/écrire **uniquement** un espace de test, lorsque Desktop Commander Remote est indisponible. Un câble USB en mode « transfert de fichiers » **ne suffit pas**. La solution R3.1 nécessite le **partage de connexion USB** (réseau local IP) et un agent indépendant préinstallé dans la session Windows.

## Utilisation prévue

1. Installer une seule fois le composant Windows : sur **son propre PC**, avec Python **3.10 ou supérieur**, extraire ce ZIP et lancer `INSTALLER-PC.cmd` ; l'agent reste en attente du téléphone par le superviseur après ouverture de session.
2. Connecter le Samsung au PC avec un câble USB de données. Activer **Paramètres Android → Partage de connexion → Partage USB** (nom exact suivant version Android).
3. Lancer `DIAGNOSTIC-PC.cmd` depuis le ZIP ou `windows/DIAGNOSTIC.cmd`. Celui-ci lit l'interface RNDIS/NCM, l'écoute du service, la tâche de démarrage et la présence d'une règle de pare-feu ciblée.
4. Si l'agent ne répond pas à cause d'un filtrage Windows **éventuel**, utiliser **sur décision de l'utilisateur uniquement** `windows/FIX-USB-FIREWALL.cmd`. L'outil demande les privilèges Windows UAC, cible un **seul adaptateur USB reconnu**, TCP 8766, `LocalSubnet`, n'altère pas le profil réseau. `windows/REMOVE-USB-FIREWALL.cmd` permet d'annuler cette règle.
5. Lancer `windows/START-NOW.cmd` si l'agent n'est pas encore présent, récupérer la clé locale par `windows/SHOW-PAIRING-KEY.cmd` et l'ajouter sur le téléphone dans « Réglages ». **Ne jamais publier cette clé dans une conversation.**
6. Quand une APK aura été réellement compilée puis vérifiée, elle présentera les onglets **Accueil / Missions / Fichiers / Réglages**, le bouton « Diagnostiquer maintenant » et le partage manuel des résultats.

**Important :** ce projet ne possède pas de canal natif ChatGPT→USB→Windows. Le fichier de mission JSON doit être importé explicitement par l'utilisateur. Il n'y a ni shell Windows arbitraire, ni accès graphique au bureau.

## Construction Android (après obtention du SDK)

Application Android Java, package **`com.blessing.rescuebridge`**, `versionCode 3`, `versionName 0.3.1-usb-readiness`, SDK Android 35, JDK 17, Gradle 8.9, Android Gradle Plugin 8.7.3.

À la racine du projet : `python run_qa.py` puis `cd android && gradle --no-daemon :app:assembleDebug`. Un APK ne peut être nommé « installable » qu'après **vérification de l'existence du fichier**, de la signature avec `apksigner`, du package avec `aapt`, et de l'empreinte SHA-256. Le workflow fourni dans `.github/workflows/build-android-rescue.yml` est un exemple **manuel uniquement** pour un dépôt standalone. Le dépôt `PROJECT-DRAFTS` utilise son propre workflow à chemins explicites.

Une APK signée avec la clé de debug d'un runner temporaire **ne garantit pas** la mise à jour par-dessus une application précédente. Une identité de signature durable doit être mise en place pour un vrai produit, selon les principes PhoneMouse.

## Sécurité et limitations

- Le prototype utilise **HTTP + HMAC** : authentification/intégrité des messages mais **aucun chiffrement du contenu**. Interdit pour informations sensibles, Wi-Fi public ou exposition Internet.
- La clé d'appairage est conservée localement, avec Android Keystore côté application et ACL réduites côté Windows.
- Le serveur Python accepte un ensemble fermé de commandes : état, diagnostic, liste des fichiers de test, lecture et écriture (avec confirmation), audit. Il refuse le shell arbitraire.
- Une confirmation d'écriture côté téléphone n'est pas une capacité d'administration illimitée.
- Le superviseur Windows démarre à **l'ouverture de session**, pas avant démarrage ni sur PC éteint. Le pare-feu est configuré séparément sur approbation.
- Les scripts PowerShell n'ont pas encore été exécutés sur Windows réel ; les tests Linux relisent leurs contrats sans prouver leur comportement matériel.
- Ce projet est distinct des packages/signatures de PhoneMouse, P2PCR95, et BCP B-Edge. Ne pas reprendre leurs identités de signature.

## Preuves de tests

Exécuter `python run_qa.py` (JDK requis). Le rapport machine se trouve dans `reports/qa_cycles.json`. Les tests couvrent le serveur Python sur boucle locale HTTP, Java non Android via JVM, requêtes signées et rejouées, chemins, autorisations, modes panne, UX source et scripts Windows statiques. **Aucune preuve Android Emulator / APK / USB réel** n'est attribuée à ces tests.

Voir `RELEASE_STATUS.md` et `UX_AUDIT_R3.md` pour l'historique et les limites. Un rapport positif sur une simulation ne doit pas être interprété comme « prêt à installer ». 