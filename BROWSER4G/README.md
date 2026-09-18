# BROWSER4G — P0 minimal instrumenté

État : **SOURCE_READY / BUILD_UNVERIFIED / FIELD_UNVERIFIED**

Ce P0 est volontairement petit. Son but n’est pas encore de livrer le navigateur complet, mais de vérifier sur le PC réel que le socle choisi tient avant d’ajouter les onglets et la gouvernance HOT/WARM/COLD/PROTECTED.

## Inclus dans P0

- Win32 / C++17 / x64.
- Un seul WebView2 actif : **SLOT A**.
- WebView2 SDK stable épinglé : `Microsoft.Web.WebView2 1.0.4191.47`.
- User Data Folder explicite sous `%LOCALAPPDATA%\BROWSER4G\P0\UserData`.
- Runtime Health Guard :
  - lecture de la version WebView2 réellement disponible ;
  - comparaison avec le dernier runtime ayant passé le probe ;
  - micro-probe local sans réseau au premier lancement ou après changement du runtime ;
  - test DOM + JavaScript via `NavigateToString` puis `ExecuteScript`;
  - aucun downgrade automatique ;
  - navigation externe bloquée si le probe échoue.
- Télémétrie toutes les 15 secondes :
  - Working Set du processus ;
  - Private Usage ;
  - charge RAM système ;
  - RAM physique disponible ;
  - commit total / limite / pourcentage.
- Barre d’adresse minimale après validation du runtime.
- Aucun workflow GitHub Actions.

## Build local

Pré-requis : Windows 10/11 x64 et Visual Studio 2022 Build Tools avec **Desktop development with C++**.

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1 -Configuration Release
```

Le script :
1. télécharge `nuget.exe` uniquement s’il manque ;
2. restaure le SDK WebView2 épinglé ;
3. trouve MSBuild via `vswhere`;
4. compile en x64 avec un seul worker MSBuild (`/m:1`) pour limiter les pics RAM ;
5. affiche le SHA-256 de l’EXE.

Sortie attendue :

`out\Release\BROWSER4G-P0.exe`

## Journaux et état runtime

- `%LOCALAPPDATA%\BROWSER4G\P0\logs\p0.log`
- `%LOCALAPPDATA%\BROWSER4G\P0\state\last_seen_runtime.txt`
- `%LOCALAPPDATA%\BROWSER4G\P0\state\last_good_runtime.txt`

## Ce que P0 ne fait volontairement pas encore

- pas d’onglets multiples ;
- pas de COLD discard ;
- pas de restauration DOM/session-history garantie ;
- pas encore de SQLite historique/favoris/recovery ;
- pas de gouverneur mémoire adaptatif actif ;
- pas de BITS/download manager custom ;
- pas de CI distante.

Ces éléments ne seront ajoutés qu’après preuve terrain du socle P0.
