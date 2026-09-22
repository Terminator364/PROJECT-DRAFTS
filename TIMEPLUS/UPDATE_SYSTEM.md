# TimePlus — système de mise à jour Android

## Identité immuable
- applicationId : `com.terminator364.timeplus`
- certificat de distribution SHA-256 : `0B:6B:F4:59:81:75:11:EB:8E:FB:EC:13:F8:FA:AA:34:84:F6:59:05:53:BA:BB:4B:20:49:ED:20:F8:C4:31:C1`
- la clé privée de signature n'est jamais stockée dans ce dépôt public.

## Règles obligatoires pour chaque mise à jour
1. conserver exactement le même `applicationId` ;
2. augmenter `versionCode` ;
3. compiler debug + release non signé ;
4. exécuter le gate visuel Android Emulator (Maintenant, Heure de départ, Paramètres) ;
5. corriger tout clipping, chevauchement ou rendu anormal avant livraison ;
6. signer avec la clé permanente TimePlus ;
7. vérifier signatures APK et empreinte du certificat ;
8. publier l'APK signé dans Drive `TimePlus/Installé`.

## Version courante
- versionName : `1.2.0`
- versionCode : `3`
- prochain versionCode minimum : `4`
- APK : `TimePlus-v1.2.0-FINAL.apk`
- visual gate : PASS, Android API 34, 720x1600
- mise à jour directe depuis C3 : compatible (même package + même certificat + versionCode supérieur)

## Fonctionnalités 1.2.0
- mode `Maintenant` : lit l'heure courante automatiquement ;
- mode `Heure de départ` : saisie HH:mm ou sélecteur horaire ;
- calcul propre avec passage au jour suivant ;
- durées rapides +10 min, +30 min, +1 h ;
- durée personnalisée avec boutons -/+, slider et saisie numérique ;
- écran Paramètres ;
- notification, son, vibration et alarmes Android.

## Transition historique v1.0.0
La v1.0.0 debug utilisait une clé éphémère. C3 a établi la clé permanente.
À partir de C3 (versionCode 2), les mises à jour signées par cette clé s'installent par-dessus.


## État v1.2.1
- versionName : `1.2.1`
- versionCode : `4`
- prochain versionCode minimum : `5`
- SHA-256 APK : `e4821866b434128f35aa26ba8462693c5d08dcb9b82a53b9f7b35fd0b6a21436`
- gate logique : 270720 cas PASS
- gate visuel : 16 captures émulateur PASS
- certificat de signature : inchangé, clé permanente TimePlus.
