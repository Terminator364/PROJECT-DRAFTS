# LINK2HP Android 1.0

Application Android native Kotlin sans services cloud. Compatible API 26+ ; interface française. Utilisation : dans Opera/Chrome, sélectionner **Partager → LINK2HP**. Le téléphone conserve le lien localement (SQLite + Android Keystore) puis le transmet au HP dès qu'il peut le joindre. Un `JobScheduler` réessaie selon la politique réseau choisie.

## Appairage initial
1. Installer le logiciel Windows LINK2HP, ouvrir son interface et copier le code `L2H1|IP|PORT|JETON|EMPREINTE` indiqué.
2. Dans l'APK, coller/saisir ce code (une seule fois). Ne jamais publier ce code : c'est la clé d'accès à votre PC.
3. Connecter les deux appareils au même Wi-Fi. Par défaut, les réseaux mesurés sont bloqués. Si vous utilisez le point d'accès du téléphone, activer la case « Autoriser réseau mesuré / point d'accès mobile ».

Le certificat TLS de ce PC est **épinglé par SHA-256** et la connexion échoue si l'empreinte diffère ; HTTPS sans authentification ne suffit pas. Aucune télécommande/shell sur le HP, seulement des demandes de transfert filtrées.

## Compilation
Gradle 8.7, Android Gradle Plugin 8.6.1, Kotlin 2.0.21, JDK17, SDK Android 35. Dans `android/` : `gradle :app:assembleDebug`. Le fichier généré se trouve dans `app/build/outputs/apk/debug/app-debug.apk`. Le dépôt PROJECT-DRAFTS fournit un workflow de compilation isolé, ponctuel et explicitement ciblé.

L'APK debug est signée avec une clé de debug générée par le runner et est destinée à une première installation. Une clé de release persistante privée devra être mise en place pour les mises à jour ultérieures.
