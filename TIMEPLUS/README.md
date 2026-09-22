# TimePlus ⏱️

TimePlus est une petite application Android qui répond à une question simple : **« si j’ajoute X minutes à maintenant, quelle heure sera-t-il ? »**

## Fonctions
- heure actuelle mise à jour chaque seconde ;
- raccourcis **+10 min**, **+30 min**, **+1 h** ;
- durée personnalisée de 1 à 9999 minutes ;
- affichage clair de l’heure cible et du jour si elle dépasse minuit ;
- alerte Android optionnelle ;
- son et vibration activables séparément ;
- annulation de l’alerte programmée ;
- fonctionnement local, sans compte, sans Internet, sans publicité.

## Projet Android
- package : `com.terminator364.timeplus`
- minSdk : 23
- targetSdk / compileSdk : 35
- langage : Java
- UI : composants Android natifs, sans dépendance UI tierce

## Construire
Ouvrir le dossier `TIMEPLUS` dans Android Studio, laisser Gradle synchroniser puis lancer **Build > Build APK(s)**.

Le dépôt PROJECT-DRAFTS impose zéro minute GitHub Actions par défaut ; aucun workflow automatique n’est ajouté ou exécuté.

## Exactitude des alertes
Sur Android 12+, le système peut demander l’autorisation spéciale **Alarmes et rappels** pour garantir une alarme exacte. Sans cette autorisation, TimePlus programme une alerte de secours que le système peut légèrement décaler pour économiser la batterie.
