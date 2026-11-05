# KIN MOTO — V1 « Les Premières Courses » — checkpoint de livraison

**Date : 2026-11-05. Statut : V1 jouable, candidate de revue privée, NON STABLE.**
Branche : `kinmoto/v1-les-premieres-courses-review-20261105`. Branche parente : `kinmoto/a4-traffic-corner-detour-20261105`. Conservation de l'ancienne version publique : obligatoire.

## Ce qui est dans cette V1

- Carrière moto-taxi dans Kinshasa : quartier Bandal, Victoire, Matonge, 16 véhicules, itinéraires, 3D WebGL1/2 procédurale, caméra troisième personne, tactile et clavier.
- **4 activités de jeu distinctes** : taxi « Maman Chantal », livraison de colis, course spéciale VIP « Docteur Alain » avec bonus de confort/ponctualité, défi de maîtrise 7 portes et 90 secondes. Garage, réparations, moteur/freins et progression conservés.
- Le mode Défi ne modifie pas les missions ni les pénalités de la carrière ; récompense de record payée une seule fois pour un score amélioré.
- Aucun CDN, font distant ou asset GLB tiers ajouté. HTML autonome indépendant du réseau ; PWA via hébergement HTTPS éventuel et Service Worker versionné, **non déployé ici**.
- Source 13 modules, `src/challenge.js` ajouté, et `build.py` génère `dist/KIN_MOTO_V1_FICHIER_UNIQUE.html`.

## Archive source de référence — à ne pas réinventer

Fichier **déjà livré dans la conversation** :
`KIN_MOTO_V1_LES_PREMIERES_COURSES_SOURCES_QA_20261105.zip`
- Taille : **2 400 000+ octets** ; empreinte exacte SHA-256 **`f6832afd35998025ebe21224fbc6297d8d778699532c3d5c183dc2c1a5de30f7`**.
- **133 entrées**, **132/132 hashes de manifeste validés**, CRC du ZIP PASS.
- HTML autonome `KIN_MOTO_V1_LES_PREMIERES_COURSES_JOUER.html`, **123154 octets**, SHA-256 `8306cd52d66868f36a0fc72a1e56404cbedaa9bdf4a672770d9fa01ae7781b83`.
- Sources, illustrations, captures navigateur, tests, rapports de QA et PWA dans l'archive. Archive **pas importée comme binaire sur GitHub** ; la branche contient les fichiers texte d'intégration.

## Test indépendant exécuté de l'archive après extraction vierge

```sh
cd SOURCE_V1
npm run check
python build.py
npm test
python -m unittest discover -s tests -p 'test_*.py'
python tools/test_local_delivery.py
node tools/v1_autopilot_qa.mjs
node tools/v1_s1_s5_qa.mjs
python tools/a4_release_gate.py --strict
```

Résultats : **200/200 Node PASS**, **26/26 Python PASS**, HTTP local 5 ressources PASS, build 13 modules PASS ; fichier HTML reconstruit **byte-identique** au standalone livré. Défi 7/7 en **19,633 secondes virtuelles** par pilote numérique, sans téléportation ni collision. Gate strict retourne **exit 2 = NO_GO STABLE**, par conception et preuve insuffisante.

Navigateur :
- Vrai WebGL2 logiciel Chromium/Xvfb/ANGLE SwiftShader : bureau 1280×800 et mobile émulé 393×852, carrière, accélération, pause/reprise et défi PASS, 0 exception JS.
- WebGL1 logiciel forcé sur **le fichier autonome** : PASS, zéro requête HTTP externe, pause PASS.
- Responsiveness 320×568, 393×852, 852×393, 1366×768 : UI pass avec **renderer simulé**, pas preuve de FPS mobile réel.
- Écran victoire et bouton Rejouer testés sous WebGL2 logiciel ; événement de victoire atteint par contrôles de test, non un conducteur humain.
- Véritables matériels HP Windows, Galaxy A21s et iPhone/Safari, FPS/RAM/batterie, 15–20 minutes humaines : **NOT_TESTED**.

## Gates du cahier FACTORY V3

- **G1 fonctionnel : PASS logiciel**.
- **G2 qualitatif visuel : en attente d'approbation humaine**.
- **G3 performances réelles HP/Galaxy A21s : NOT_TESTED**.
- **G4 jouabilité 15–20min sur appareils réels : NOT_TESTED**.
- **A1-D choix comparatif définitif : PENDING**.
- **Droits complets sur les ressources héritées : PARTIAL**.
- **Publication `main` / V1 STABLE : NO_GO**, pas de GO propriétaire.

**Important :** V1 existe et est livrable pour tests privés. Ne pas publier comme version commerciale/officialisée avant les gates ci-dessus. Ne pas écraser l'ancien site, ni déclencher GitHub Actions hébergées, Vercel ou Remote.
