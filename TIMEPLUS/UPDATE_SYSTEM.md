# TimePlus — système de mise à jour Android

## Identité immuable
- applicationId : `com.terminator364.timeplus`
- certificat de distribution SHA-256 : `0B:6B:F4:59:81:75:11:EB:8E:FB:EC:13:F8:FA:AA:34:84:F6:59:05:53:BA:BB:4B:20:49:ED:20:F8:C4:31:C1`
- la clé privée de signature n'est jamais stockée dans ce dépôt public.

## Règles obligatoires pour chaque mise à jour
1. conserver exactement le même `applicationId` ;
2. augmenter `versionCode` à chaque version ;
3. compiler un APK release non signé ;
4. signer l'APK avec la clé permanente TimePlus ;
5. vérifier les signatures APK v1 + v2 + v3 et l'empreinte du certificat ;
6. déposer seulement l'APK signé dans le dossier Drive `TimePlus/Installé`.

## État C3
- versionName : `1.1.0-c3`
- versionCode : `2`
- prochain versionCode minimum : `3`
- APK C3 : signé avec la clé permanente.

## Transition depuis la première v1.0.0 debug
La première v1.0.0 avait été signée automatiquement par une clé debug éphémère d'un runner GitHub.
Son certificat SHA-256 était :
`2D:80:61:0B:F6:F9:F6:1B:5B:AA:92:FF:B7:C6:0F:E0:2A:D3:AB:0A:4A:2F:30:1C:48:F5:DB:D0:EF:41:41:0D`.

Cette clé privée n'existe plus sur le runner. Android ne peut donc pas accepter C3 par-dessus une v1.0.0 déjà installée.
Si v1.0.0 a été installée, C3 est l'unique transition nécessitant désinstallation/réinstallation.
À partir de C3, les mises à jour suivantes doivent s'installer directement par-dessus.
