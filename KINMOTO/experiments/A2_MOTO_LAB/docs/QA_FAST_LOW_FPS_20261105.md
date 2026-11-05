# KIN MOTO A2 0.5.6 — Récupération rapide des FPS faibles
Date 2026-11-05. **Correctif expérimental sur la branche fille de PR #37, aucun déploiement.**

## Défaut observé en vrai WebGL2 logiciel
Le moteur de rendu utilise `AdaptiveResolution.observe(dt)` avec la durée réelle des images. Le premier correctif protégeait les images longues mais attendait 45 échantillons pour déclencher la première baisse de résolution lorsqu'une image mettait 100–250ms. Cela représente jusqu'à 4,5–11,25 secondes à 4–10 FPS, même sans compter les suspensions plus longues.

**Reproduction concrète :** Chromium Linux sous Xvfb + WebGL2 ANGLE/Vulkan SwiftShader, scène A2 v0.5.6. Mesures successives à 0, 3, 6, 9, 12, 15 secondes demandées : le diagnostic indiquait 1–5 FPS logiciels et `adaptiveScale=1`, `adaptiveSteps=0` sur toute la fenêtre de 15 secondes. Pas de remplacement WebGL par un mock; pas de GPU matériel.

## Correctif
- Si six images visibles consécutives ont chacune pris au moins 1/12 s (~12FPS ou moins), basculer vers un seuil d'évaluation accéléré de 6 échantillons, sans réduire la fenêtre temporelle minimale de 1,6 seconde.
- Autoriser des ralentissements visibles jusqu'à 2 secondes, mais exiger au moins trois ralentissements consécutifs au-delà de 250ms pour les distinguer d'une pause isolée.
- Une page cachée réinitialise le filtre, l'EMA et les compteurs temporels **sans remettre brutalement la qualité à 100 %**. Les changements de cadence après retour d'onglet ne contaminent plus le calcul.
- Suspensions extrêmes >2 secondes : toujours écartées comme pauses possibles du navigateur/système.
- Le pas fixe de simulation 60 Hz et la politique de rendu idle de PR #36 ne changent pas ; aucune modification aux shaders, assets ou FPS de la physique.

## QA reproductible
`node --test tests/adaptive_resolution.test.mjs` : **19/19 PASS**, dont quatre scénarios nouveaux et deux anciens adaptés. Nouveaux : 5 FPS soutenus -> baisse de résolution en <3 secondes virtuelles, 1,4 FPS prolongé, une pause isolée <2 secondes non pénalisante, retour de l'arrière-plan sans dégradation fictive.

`npm test` sur source A2 corrigée : **131/131 PASS** (127 précédents + 4 nouveaux).
`python -m unittest discover -s tests -p 'test_*.py'` : **22/22 PASS**.
`npm run check`, `python build.py` : **PASS**, 12 modules, HTML autonome **95 612 octets**.

Fichiers `src/adaptive_resolution.js` et `tests/adaptive_resolution.test.mjs` du banc local ont les **mêmes empreintes Git blob** que les deux fichiers GitHub du patch au moment de la QA.

## Contre-épreuve WebGL2 logiciel réelle
Test de la même ville dans Chromium/Xvfb SwiftShader après correction : un des parcours a fini avec `adaptiveScale=0.84`, `adaptiveSteps=2` au point de mesure demandé à 15 secondes, vs 1.00 et 0 dans l'essai de référence. **Limites :** l'environnement logiciel sature et le parcours de test n'a pas toujours terminé proprement (timeout lors de la fermeture automatisée du navigateur). Ne pas appeler cela un benchmark A/B statistiquement significatif ni un gain confirmé sur Android. Les résultats Node ci-dessus sont les tests de non-régression déterministes et reproductibles.

## Portes non franchies
- Aucun FPS ni autonomie/chauffe sur HP Windows ou Samsung Galaxy A21s mesuré.
- iPhone/Safari / offline après Telegram : NOT_TESTED.
- Qualité visuelle reste à améliorer, modèle GLB Road Sportbike extérieur non acquis.
- Ne pas fusionner main, publier, déployer, exécuter Actions hébergées ou utiliser Remote sans accord.
