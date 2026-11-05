# KINMOTO A2 — Horloge physique indépendante des FPS graphiques
Date : 05 novembre 2026. **LABORATOIRE / PR fille de #38. AUCUNE RELEASE.**

## 1. Défaut réel et reproduction sur A2 FastFPS

Avant le correctif, `src/main.js` utilisait `delta=Math.min(.1,frameSeconds)` et seulement **six pas de 1/60 s par image**. Quand la 3D tombait sous 10 FPS, la simulation ne pouvait donc pas suivre le temps réel.

Simulation du code d'origine depuis le ZIP `KINMOTO_A2_V056_RIDE_FASTFPS_WEBGL2_QA_20261105.zip`, entrée accélérateur constante pendant **5 secondes de temps réel synthétique**, sans trafic :

| Images/s | Horloge du jeu avant | Ratio réel |
|---:|---:|---:|
| 60 | 5.0 s | 100 % |
| 30 | 5.0 s | 100 % |
| 10 | 5.0 s | 100 % |
| 5 | 2.5 s | 50 % |
| 3 | 1.5 s | 30 % |
| 2 | 1.0 s | 20 % |

En conséquence, commandes de conduite, trafic et pénalités chronométrées étaient ralentis alors que la personne voyait les vraies secondes passer.

## 2. Correction

**Aucune fréquence de simulation variable : pas fixe de 1/60 seconde conservé.**

- Nouvelle classe pure et testable `FixedStepScheduler` dans le module déjà embarqué `src/adaptive_resolution.js` (pas de nouveau module, de lib ou de CDN).
- `src/main.js` transmet la **durée réelle de l'image** au scheduler, qui exécute jusqu'à 30 pas de physique par rendu (plafond temporel 0,5 s), au lieu des 6 pas anciens.
- Pause, menu et onglet caché => zéro tick et réinitialisation du reliquat ; démarrage/reprise appellent également `reset()`.
- Sauts/suspensions supérieurs à 0,5 s => temps excédentaire volontairement abandonné, avec compteur `droppedSeconds` diagnostic. Un GPU à 1 FPS ne peut pas devenir jouable par rattrapage infini.
- Compteurs UI/QA/sauvegarde intègrent le delta réel plafonné à 0,5s. Résolution adaptative et qualité GPU continuent de recevoir `frameSeconds` brut, pas le delta des pas physiques.
- `KINMOTO_DIAGNOSTIC().physics` expose le nombre de ticks, le temps écarté et la limite de rattrapage.
- Les changements sont limités aux ressources internes du laboratoire : aucun déploiement, aucune facturation et aucune publication V1/STABLE.

## 3. Preuves exécutées

**14 tests nouveaux** dans `tests/low_fps_simulation_clock.test.mjs` : six cadences 2–60 FPS, limite d'un long stall, suspension de 5s, saturation à 1FPS, invalides, câblage du navigateur, déterminisme du trafic réel entre 2/5/60FPS et jitter synthétique.

| 5 secondes réelles synthétiques | Avant | Après |
|---|---:|---:|
| 5 FPS | 2,5 s de jeu | 5,0 s de jeu |
| 3 FPS | 1,5 s | 5,0 s |
| 2 FPS | 1,0 s | 5,0 s |
| 1 FPS | 0,5 s | 2,5 s (limite CPU intentionnelle) |

Avec le trafic et les collisions, les états complets `player`, 16 `cars`, `clock`, `save.health` et `collisions` après 5 secondes sont **strictement identiques** à 2, 5 et 60FPS dans le test deterministe.

Suite sur les **sources réellement présentes dans le paquet QA22+FastFPS et les patches exacts GitHub** :
- `npm run check` : PASS.
- `npm test` : **145/145 PASS**.
- `python -m unittest discover -s tests -p 'test_*.py'` : **22/22 PASS**.
- `python build.py` : PASS, 12 modules, HTML **97 194 octets**, SHA-256 `86801e5562854bc09b16ee46471050246edb677f746dbacd1a302f90960db047`.
- `python tools/test_local_delivery.py` : PASS (cinq ressources localhost).
- Comparaison des empreintes **SHA Git Blob : 4/4 identiques** entre fichiers locaux testés et fichiers commités sur cette branche.

## 4. Test WebGL2 logiciel réel : verdict nuancé

`xvfb-run -a python tools/qa_software_webgl.py` sur l'HTML patché : PASS en 1280×800 et mobile émulé 393×852. Chromium WebGL2 **ANGLE/Vulkan SwiftShader** (logiciel), moto avancée ~4,396 m et ~4,165 m pendant la fenêtre de touche, pause/reprise PASS, aucune exception JavaScript, 139 296 sommets de monde.

Deuxième banc browser instrumenté de 4,2 s en GPU logiciel, sans accélérateur :
- Desktop : 4,321 s de durée mesurée, **2,400 s de simulation** (~55,5 %), pilote ~1 FPS selon indicateur et `droppedSeconds=.867`.
- Mobile émulé : 4,212 s mesurées, **2,883 s simulées** (~68,5 %), ~4 FPS logiciels, `droppedSeconds=2.374`.

Ce second banc montre clairement **que l'environnement SwiftShader était parfois sous la limite de 2 FPS** et que le mécanisme a volontairement abandonné du temps au lieu de lancer un rattrapage illimité. Les fenêtres de mesure restent petites et les FPS logiciel instables. **Ne pas prétendre que ces valeurs constituent une amélioration FPS mesurée ou une validation du GPU HP/Android.**

## 5. Portes qui restent fermées

- Vrai rendu matériel HP Windows et Galaxy A21s, 15 min, FPS/RAM/thermique, touche Android : **NOT_TESTED**.
- iPhone Chrome/Safari réel, ouverture depuis Telegram, fichier hors ligne et SW : **NOT_TESTED**.
- Qualité graphique/tactile V1 : **NOT_APPROVED**. Rendu actuel low-poly confirmé par les captures logicielles.
- GLB Road Sportbike binaire et licence fichier exact : **NOT_ACQUIRED**.
- A1-D benchmark comparatif sources libres : **PENDING**.
- Ne pas utiliser GitHub Actions hébergées, Vercel/Pages publics ni Remote. Maintenir toutes les PR en brouillon, aucun merge de main/STABLE sans accord.
