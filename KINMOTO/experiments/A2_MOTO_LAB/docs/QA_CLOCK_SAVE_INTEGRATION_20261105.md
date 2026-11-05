# KINMOTO — QA A2 0.5.6 CLOCK + SAVE — 05/11/2026

**Statut : laboratoire de revue, jamais V1/STABLE.** Référence : branches GitHub PR #39 (horloge physique), PR #40 (restauration robuste).

## Départ

Source extraite du ZIP vérifié `KINMOTO_A2_V056_RIDE_FASTFPS_WEBGL2_QA_20261105.zip`, puis recoupée avec les fichiers du dépôt GitHub. Les écarts textuels initiaux (commentaires dans `sim.js`, échappement Unicode dans `package.json`) ont été rectifiés pour assurer une égalité des Git blob SHA des sources testées.

## Correction 1 : physique à 60 Hz indépendante du rendu

Avant : `frame()` plafonnait `delta` à 100ms et n'autorisait que 6 ticks par image : en 5s de vraie durée synthétique, le jeu ne progressait que 2,5s à 5 FPS, 1,5s à 3 FPS, 1s à 2 FPS.

Après : `FixedStepScheduler` accepte jusqu'à 0,5s par image, 30 ticks à 1/60s, réinitialisation des accumulations en pause/arrière-plan. Les tests déterministes à 60, 30, 10, 5, 3, 2 FPS avancent tous de 5s virtuelles en 5s réelles synthétiques ; 1FPS est volontairement plafonné à 2,5s pour ne pas saturer le processeur. Avec le trafic réel simulé, l'état de la moto et des 16 voitures après 5s est **identique** aux trois cadences testées (2, 5, 60 FPS). Tests de cadence irrégulière et de reprise de pause inclus. Le compteur de temps rejeté est exposé dans le diagnostic du navigateur.

## Correction 2 : protection des sauvegardes

Avant : `makeGame(snapshot)` acceptait `save.stars='BUG'` et `mission.reward='oops'` sans erreur du validateur ; `stars.toFixed` provoquait une erreur d'interface ; `health=-200`, étape de mission inconnue, compteurs incohérents et `bike={}` incomplet pouvaient passer le filtrage ou corrompre la physique. Une ancienne donnée `readSave` non numérique pouvait même produire `stars=NaN`.

Après : `readSave()` garde le solde valide et normalise les champs optionnels ; `validate()` vérifie types, bornes, compteurs, niveau d'amélioration, télémétrie moto et intégrité de mission ; le démarrage refuse un snapshot local corrompu et restaure une carrière locale valide ; l'import manuel refuse un fichier incohérent avant de remplacer la partie. Sauvegardes valides du schéma 1 compatibles. Version de laboratoire affichée : `A2-LAB-0.5.6-CLOCK-SAVE-DRAFT`.

## Commandes exécutées après patch complet

- `npm run check` : **PASS**.
- `npm test` : **156/156 tests Node PASS** (131 existants +14 horloge +11 sauvegarde).
- `python -m unittest discover -s tests -p 'test_*.py'` : **22/22 tests Python PASS**.
- `python build.py` : **PASS**, 12 modules, HTML autonome **99 372 octets**, SHA-256 `49d0eb4fe5586a8d9b3830604b8a57c27fd1dd647df9e6b8c43cb5918aacba98`.
- `python tools/test_local_delivery.py` : **PASS**, 5 ressources locales, zéro déploiement.
- `xvfb-run -a python tools/qa_software_webgl.py` : **PASS** sur Chromium/Xvfb/ANGLE Vulkan SwiftShader WebGL2, ordinateur 1280×800 et mobile émulé 393×852 : moto en mouvement, pause/reprise, HUD et scène 3D visibles ; **0 erreur JS**. Déplacements mesurés dans les fenêtres de commandes : 7,368m (bureau), 4,755m (mobile émulé), au cours d'essais non strictement identiques en durée effective.
- Banc Playwright avec `localStorage` injecté : sauvegarde locale corrompue → carrière de secours à 9000 FC sans erreur ; import JSON invalide → refus avec toast, 9000 FC conservés ; import valide → reprise à 12345 FC, état en pause et **0 erreur JS**.

## Limite matérielle importante

Le rendu WebGL2 est réel au sens API/shaders, mais le matériel est **SwiftShader logiciel**. Les FPS (~5 bureau, ~10 mobile simulé dans un essai) et les observations de rattrapage **ne sont pas une mesure sur le GPU HP ni Samsung**. Un autre test software-WebGL de 4,2s avec cadences 1–4 FPS indiquait ~55–69% de temps simulé, conformément au plafonnement volontaire sous 2 FPS. Une cadence si basse ne permet pas une expérience acceptable même avec une horloge corrigée.

**Non réalisé :** Galaxy A21s/HP/iPhone physiques, GPS réel, batterie/chauffe/15min, ouverture depuis Telegram sur iPhone, licence du vrai modèle GLB (non acquis), qualification de la qualité esthétique et fusion STABLE. Aucune GitHub Actions hébergée, aucun Remote ni coût déclenchés.
