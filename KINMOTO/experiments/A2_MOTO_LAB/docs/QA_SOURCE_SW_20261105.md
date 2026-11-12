# QA A2 — Cache offline du dossier source (2026-11-05)

**Périmètre strict** : `experiments/A2_MOTO_LAB/sw.js` du dossier source. Le `dist/sw.js` produit par `build.py` est un autre fichier généré (avec cache hashé) et n'a pas été modifié.

## Défauts statiques vérifiés dans le dépôt

L'ancien SW source utilisait le nom de cache `kin-moto-v1-1.0.0`, ne précachait que 6 modules JS sur 12, et référençait des PNG absents du dépôt source. Les PNG ne sont présents que sous `.png.base64` dans `assets/` et sont générés lors d'un vrai build. Conformément à Cache.addAll (MDN), un seul fichier introuvable peut rejeter l'installation du worker entier.

De plus, l'ancienne activation supprimait **tous** les caches autres que son nom, y compris ceux d'autres applications partageant l'origine. Risque opérationnel de destruction de caches non liés.

## Modification

- Nom de cache dédié au laboratoire *source* et nettoyage limité à son préfixe.
- Liste de pré-cache de 12 modules, CSS, HTML, manifest et SVG existants, sans exiger les PNG qui seront créés dans `dist/`.
- Récupération réseau prioritaire lorsque disponible et repli en cache pour HTML et modules ; pas d'interception des méthodes non GET ni d'origines externes.
- Pas de `skipWaiting()` forcé pendant une mission.
- Aucune collecte de données ou requête API ajoutée.

## Contre-tests

`node --test /mnt/data/kinmoto_lab_work/sw_source_test.mjs`: **4/4 PASS**, Node 22.16, avec simulation de `CacheStorage` et du réseau. Pré-cache = 17 entrées, absence d'effacement de `other-app` ou d'un cache distinct du jeu ; navigation/modules servis hors réseau après cache.

**NOT_TESTED :** installation du SW source sur vrai navigateur, fermeture/reprise Android, offline 15 min, migration de versions et quotas de stockage. `dist/sw.js` a déjà ses propres tests et n'a pas été changé dans ce lot.

Source technique : https://developer.mozilla.org/en-US/docs/Web/API/Cache/addAll et https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API/Using_Service_Workers

**Gate :** ne pas convertir ce contrôle simulé en certification PWA Android/iPhone ; tester sur matériel avant sortie. Zéro hébergement/Actions/Remote/frais.
