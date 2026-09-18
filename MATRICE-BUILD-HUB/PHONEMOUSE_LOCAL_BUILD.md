# PhoneMouse — build local sans GitHub Actions

Ce circuit sert quand GitHub Actions est indisponible ou lorsqu'on veut éviter toute minute de runner.

## Point d'entrée

Double-cliquer:

`MATRICE-BUILD-HUB/local-phonemouse.cmd`

Le premier lancement peut installer/télécharger automatiquement Git, GitHub CLI, Python, JDK 17 portable, Android SDK et Gradle dans les caches locaux. Les lancements suivants réutilisent ces outils.

## Ce que fait le script

1. Authentifie GitHub si nécessaire.
2. Clone/met à jour `Terminator364/PhoneMouse` sur `beta11-visual-20260918`.
3. Exige `beta11-overrides/BUILD_READY.json`.
4. Reconstruit PhoneMouse de BETA01 à BETA11 depuis les patches canoniques.
5. Lance `tools/beta11_preflight.py`.
6. Récupère l'artifact de signature canonique PhoneMouse via l'API GitHub, sans lancer de workflow.
7. Compile en profil faible RAM: Gradle sans daemon, un worker, heap plafonné.
8. Vérifie certificat, package, version, label et SHA-256.
9. Dépose l'APK dans `Téléchargements/PhoneMouse-Builds/...`.

## Publication optionnelle sans Actions

Depuis un terminal:

`local-phonemouse.cmd -PublishRelease`

Cela publie l'APK comme GitHub prerelease via `gh release`, sans GitHub Actions.

## Contrainte mémoire

Le build Android est plus lourd que l'exécution de PhoneMouse. Sur un PC 4 Go déjà très chargé, fermer les applications lourdes avant le build. Le script utilise volontairement un worker unique et un heap conservateur afin de limiter la pression mémoire.

## Signature

Ne jamais resignER PhoneMouse avec une nouvelle clé pour une mise à jour normale. Le script récupère la clé canonique existante afin que l'APK puisse s'installer par-dessus les versions déjà installées.
