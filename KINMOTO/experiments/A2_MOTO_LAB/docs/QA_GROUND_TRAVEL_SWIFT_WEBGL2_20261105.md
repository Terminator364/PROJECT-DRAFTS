# KIN MOTO — Contre-audit de la motricité et vrai rendu WebGL2 logiciel
Date : 05 novembre 2026. **Branche de laboratoire uniquement.** Source parente : PR #36 A2 v0.5.6 POWER / QA22.

## Bug physique nouveau reproduit sur le code QA22, avant correction

Scénario : moto sans trafic placée en x=8,09, z=45, yaw=+π/2, face à la bordure (axe routier x=0). Accélérateur maintenu 300 pas fixes à 60 Hz, soit 5 secondes de simulation.

| Grandeur | Code QA22 AVANT correctif |
|---|---:|
| Déplacement réel de la moto | 0,01 m |
| Distance artificielle représentée par les rotations de roue (×0,49m) | 11,04 m |
| Vitesse HUD basée sur la vitesse moteur | 2,2 m/s (~8 km/h) |
| Validateur historique `validate(game)` | 0 anomalie |

Cause vérifiée : `advanceBike` incrémente `wheelSpin` sur le déplacement libre `dx,dz`, puis `step` annule une partie du déplacement par `keepOverStreet`. L'odometre est mis à jour **après** la contrainte, pas la roue. Conséquence visuelle : moto bloquée dont les roues tournent sans avancer, et vitesse affichée non représentative du terrain.

## Correction retenue, après contre-test

- `BIKE_WHEEL_RADIUS` exporté par `src/bike_physics.js` ; `createBikeTelemetry` intègre un `groundSpeed` distinct de la vitesse du modèle longitudinal.
- `src/sim.js` mémorise `wheelSpinBefore`, applique la physique et les collisions aux bordures, puis calcule `roadTravel=hypot(player.x-oldX,player.z-oldZ)`. Les roues tournent désormais selon `roadTravel/BIKE_WHEEL_RADIUS` ; `p.meters` utilise déjà cette distance.
- Vitesse réelle au sol `groundSpeed=roadTravel/dt` ; `src/main.js` l'utilise pour l'affichage HUD, sans modifier l'accélération moteur, l'adhérence ou la suspension.
- Contre-proposition **rejetée après test** : réduire la vitesse dynamique du modèle en fonction de `roadTravel/dt`. Cela causait une régression grave : glissement tangentiel le long de la bordure réduit de >1m à ~0,49m en 5s. La version finalement conservée n'écrase donc pas la vitesse physique.

## Tests effectivement réexécutés

1. Nouveau fichier `tests/wheel_ground_travel.test.mjs` : **4/4 PASS**, dont moto bloquée, glissement longitudinal tangent à la bordure, moto libre en ligne droite et câblage HUD.
2. Suite Node **127/127 PASS** (123 précédents + 4 tests).
3. Suite Python `python -m unittest discover -s tests -p 'test_*.py'` : **22/22 PASS**.
4. `npm run check`, `python build.py` PASS (12 modules; HTML autonome reconstitué **94 880 octets**).
5. `python tools/test_local_delivery.py` : **PASS** (5 ressources HTTP locales, aucun hébergement).
6. `validate(game)` après le scénario contre bordure : aucune erreur, mais le nouveau test vérifie les comportements que le validateur ne détectait pas.

## Premier rendu véritable WebGL2 dans cet environnement

**Méthode :** Chromium Linux avec Xvfb + ANGLE, pilote *logiciel* Vulkan SwiftShader ; Playwright utilise `about:blank` puis `page.set_content` avec le HTML autonome. La navigation `file://` et HTTP était bloquée par politique du navigateur automatisé ; ce test n'évalue donc pas l'installation du Service Worker ni l'ouverture du jeu depuis Telegram. Cette méthode ne remplace pas les essais physiques.

**Commande reproductible facultative** (nécessite Chromium dans /usr/bin et Playwright installé) :
`xvfb-run -a python tools/qa_software_webgl.py`

Deux parcours effectivement réussis :
- Desktop 1280 × 800 : `canvas.getContext('webgl2')` **non-null**, pilote `ANGLE ... SwiftShader Device (Subzero)`, moteur `webgl2`, 139 296 sommets pour la ville, jeu démarré et accélération clavier ; ~1,307 m de déplacement mesuré durant la fenêtre de test ; pause/reprise PASS ; **0 erreur JavaScript**.
- Mobile émulé 393 × 852 avec vrai rendu logiciel (pas de GPU mobile) : WebGL2, moto/ville/voitures/repères visibles, commande tactile accélérateur ; ~2,192 m parcourus ; pause/reprise PASS ; **0 erreur JavaScript**.
- Captures de rendu réel **logiciel** conservées en artefacts de cette conversation : `DESKTOP_real_software_webgl.png`, `MOBILE_real_software_webgl.png`, et résultats JSON `qa_local_swiftshader/REPORT.json`. Les images sont des preuves de rendu, pas de qualité acceptable pour une version commerciale.
- FPS logiciel fluctuants ~5–10 selon l'essai et la taille de fenêtre : **NON transposables** au HP Windows, au Galaxy A21s ou à l'iPhone. Aucune affirmation d'autonomie, CPU, batterie ou stabilité 15min sur appareil réel.

## Contre-audit visuel

Sur les images, la 3D et l'interface sont réellement visibles : route, voitures, moto à troisième personne, panneaux de mission, bâtiments, HUD, manettes tactiles, profondeur/caméra. Le style demeure low-poly et les formes des véhicules/bâtiments restent élémentaires. La porte de qualité esthétique **n'est pas levée**, même si le moteur dessine maintenant en WebGL2 logiciel.

## Gate récapitulatif

- **G1 logique / recette : PASS 127 Node / 22 Python / build / HTTP.**
- **G2 rendu WebGL2 logiciel avec vraie API GL : PASS**, mais rendu GPU matériel : **NOT_TESTED**.
- **G3 HP Windows FPS/RAM/thermique/ressenti : NOT_TESTED.**
- **G4 Galaxy A21s/iPhone réels, tactile long, offline : NOT_TESTED.**
- **G5 modèle GLB Road Sportbike binaire/licence/animations : NOT_ACQUIRED.**
- Aucun merge main, déploiement public, Actions hébergées, Remote, coût ou changement STABLE.
