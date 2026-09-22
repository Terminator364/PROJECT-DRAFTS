# TimePlus ⏱️

TimePlus est une calculatrice temporelle Android locale : elle part d'une heure de référence et applique une durée, ou calcule la durée entre deux heures.

## V2 — 2.0.0

### Calcul temporel
- référence = Maintenant ou Heure choisie ;
- opération + Ajouter ou − Soustraire ;
- presets 1, 2, 3, 5, 10, 15, 20, 30, 45 et 60 minutes ;
- saisie directe en minutes ;
- sélecteur de durée par roues heures/minutes ;
- passage automatique à Hier / Aujourd’hui / Demain et aux jours suivants.

### Différence entre deux heures
- départ + arrivée ;
- option de passage à minuit ;
- durée calculée en heures/minutes.

### Fonctions connexes
- historique local des calculs ;
- réutilisation d'un résultat comme nouvelle référence ;
- copie du résultat ;
- programmation d'une alerte ;
- son et vibration ;
- reprise d'une alerte future après redémarrage ;
- paramètres et état réel des permissions.

## Architecture
- applicationId: com.terminator364.timeplus
- Jetpack Compose + Material 3
- fonctionnement hors ligne, aucune permission Internet
- clé de signature permanente conservée hors du dépôt public
- mises à jour installables par-dessus la chaîne signée C3+

## Release gate V2
La version 2.0.0 est livrée après :
- 5 561 287 cas déterministes du moteur temporel ;
- compilation debug + release ;
- Android Emulator API 35 ;
- 36 captures sur 3 classes d'écran et 2 tailles de police ;
- états Calcul, TimePicker, roulettes, Différence, Paramètres et bas de Paramètres ;
- assertions UI géométriques/tactiles ;
- 500 événements Monkey de crash-smoke.

Le workflow GitHub produit les APK de build. La distribution finale est signée hors du dépôt public avec la clé permanente TimePlus.
