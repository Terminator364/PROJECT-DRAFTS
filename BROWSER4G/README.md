# BROWSER4G — P0 minimal instrumenté

État : **P0.1_SOURCE_READY / BUILD_UNVERIFIED / FIELD_UNVERIFIED**

Ce P0 est volontairement petit. Son but n’est pas encore de livrer le navigateur complet, mais de vérifier sur le PC réel que le socle choisi tient avant d’ajouter les onglets et la gouvernance HOT/WARM/COLD/PROTECTED.

## Inclus dans P0

- Win32 / C++17 / x64.
- WebView2Loader lié statiquement : artefact P0 = **un seul EXE**.
- Un seul WebView2 actif : **SLOT A**.
- WebView2 SDK stable épinglé : `Microsoft.Web.WebView2 1.0.4191.47`.
- User Data Folder explicite sous `%LOCALAPPDATA%\BROWSER4G\P0\UserData`.
- Runtime Health Guard :
  - lecture de la version WebView2 réellement disponible ;
  - comparaison avec la dernière signature de santé validée (`build + SDK + runtime`) ;
  - micro-probe local sans réseau au premier lancement ou après changement du build, du SDK ou du runtime ;
  - test DOM + JavaScript via `NavigateToString` puis `ExecuteScript`;
  - aucun downgrade automatique ;
  - navigation externe bloquée si le probe échoue.
- Télémétrie toutes les 15 secondes :
  - Working Set + Private Usage du processus hôte ;
  - liste des processus WebView2 du même User Data Folder via `ICoreWebView2Environment8::GetProcessInfos` (hors crashpad, conformément au contrat de l’API) ;
  - Working Set + Private Usage agrégés WebView2 ;
  - totaux hôte + WebView2 ;
  - charge RAM système ;
  - RAM physique disponible ;
  - commit total / limite / pourcentage.
- Barre d’adresse minimale après validation du runtime.
- Aucun workflow GitHub Actions.

## Build local

Pré-requis : Windows 10/11 x64. Si MSVC C++ Build Tools manque, le script tente de le provisionner via `winget` ; aucune licence payante n’est requise.

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1 -Configuration Release
```

Le script :
1. vérifie/provisionne conditionnellement MSVC C++ Build Tools ;
2. télécharge **NuGet 7.9.0 figé** uniquement s’il manque et vérifie son SHA-256 ;
3. restaure WebView2 1.0.4191.47 uniquement depuis nuget.org ;
4. trouve MSBuild/MSVC x64 via `vswhere`;
5. compile en x64 avec un seul worker MSBuild (`/m:1`) pour limiter les pics RAM ;
6. affiche le SHA-256 de l’EXE.

Sortie attendue :

`out\Release\BROWSER4G-P0.exe`

## Journaux et état runtime

- `%LOCALAPPDATA%\BROWSER4G\P0\logs\p0.log`
- `%LOCALAPPDATA%\BROWSER4G\P0\state\last_seen_runtime.txt`
- `%LOCALAPPDATA%\BROWSER4G\P0\state\last_good_health.txt` (signature build + SDK + runtime)

## Ce que P0 ne fait volontairement pas encore

- pas d’onglets multiples ;
- pas de COLD discard ;
- pas de restauration DOM/session-history garantie ;
- pas encore de SQLite historique/favoris/recovery ;
- pas de gouverneur mémoire adaptatif actif ;
- pas de BITS/download manager custom ;
- pas de CI distante ;
- pas encore d’installation/réparation automatique du WebView2 Evergreen Runtime si celui-ci est absent.

Ces éléments ne seront ajoutés qu’après preuve terrain du socle P0.
