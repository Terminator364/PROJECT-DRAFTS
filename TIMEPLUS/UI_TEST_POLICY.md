# TimePlus — Visual release gate

Avant toute livraison d'une mise à jour :
1. compiler debug + release non signé ;
2. installer le debug dans un émulateur Android GitHub Actions ;
3. capturer au minimum l'écran principal en mode Maintenant, le mode Heure de départ et Paramètres ;
4. contrôler qu'aucun texte, bouton ou carte n'est tronqué ou superposé ;
5. seulement après validation visuelle, signer le release avec la clé permanente TimePlus ;
6. incrémenter versionCode et publier l'APK signé dans Drive/TimePlus/Installé.

Version 1.2.0 ajoute :
- mode Maintenant ;
- mode Heure de départ saisissable en HH:mm + TimePicker ;
- stepper +/- et SeekBar de durée ;
- raccourcis +10/+30/+1h/+2h ;
- écran Paramètres ;
- layout compact pour écran étroit.
