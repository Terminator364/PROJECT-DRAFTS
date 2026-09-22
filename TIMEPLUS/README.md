# TimePlus ⏱️

TimePlus calcule immédiatement l'heure obtenue après ajout d'une durée à l'heure actuelle.

## C3 — 1.1.0
- vraie icône launcher TimePlus intégrée ;
- versionCode 2 / versionName 1.1.0-c3 ;
- +10 min, +30 min, +1 h et durée personnalisée ;
- notification, son et vibration configurables ;
- alarme exacte quand Android l'autorise ;
- fonctionnement local, sans Internet, sans publicité.

## Mise à jour Android
Le package reste `com.terminator364.timeplus`. Les futures versions incrémentent `versionCode`.
La chaîne C3 introduit une clé de signature permanente hors du dépôt public afin de permettre l'installation des futures versions directement par-dessus la version C3 signée.

## Construction
Le workflow GitHub compile un APK debug et un APK release non signé. La signature de distribution est appliquée hors du dépôt public avec la clé TimePlus permanente.
