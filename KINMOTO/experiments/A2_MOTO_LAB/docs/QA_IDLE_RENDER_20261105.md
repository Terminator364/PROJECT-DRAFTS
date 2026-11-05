# KINMOTO A2 — Réduction du rendu inutile en menu/pause
Date : 2026-11-05. Périmètre : branche expérimentale dérivée de la PR #35, **pas de release**.

## Défaut reproductible
La boucle `requestAnimationFrame` appelait `Renderer.render` en permanence y compris sur les pages menu, pause et garage. Elle continuait à émettre ~1 400 appels simulés de dessin par tranche de 1,2 seconde alors que la moto et le trafic n'évoluaient pas. Sur un appareil mobile, ce travail de préparation GPU est susceptible de gaspiller du temps CPU/GPU et de la batterie, mais la consommation électrique réelle n'a **pas** été mesurée.

## Correctif
- `IdleFrameGate` pur, testable depuis Node, dans `src/adaptive_resolution.js` : plein débit uniquement en jeu actif et premier plan ; un rendu toutes les 120 ms au maximum dans le menu / pause ; aucun dessin en arrière-plan.
- `src/main.js` garde le cycle RAF et le pas fixe de simulation, mais filtre la fréquence de dessin seulement quand le jeu est inactif. Reprise immédiate dès le retour en jeu.
- `src/render.js` exclut les échantillons de menu et pause de l'adaptation dynamique de résolution et du compteur FPS, afin de ne pas interpréter volontairement 8 FPS comme une saturation GPU.
- Les deux builders existants contiennent déjà le module `adaptive_resolution.js` ; aucun nouveau module à référencer dans Python, PowerShell ni dans le cache PWA.

## Preuves indépendantes exécutées sur la candidate HTML locale
- `node --check` sur JS autonome patché : PASS.
- `node --test gate_test.cjs` : **9/9 PASS** sur la classe pure (cadence, premier dessin, reprise, arrière-plan, horloge, invalides). 10e test de câblage enregistré dans la branche GitHub.
- Chromium Playwright à 393 × 852, **GPU WebGL simulé**, deux répétitions de 1,2 seconde par état :

| État | Version initiale (appels dessin moyens) | Correctif (appels dessin moyens) | Différence |
|---|---:|---:|---|
| Menu | 1368 | 171 | -87,5 % |
| Pause | 1470 | 210 | -85,7 % |
| Jeu actif | 1482,5 | 1452,5 | -2,0 % |
| Reprise, 850 ms | 1040 | 1040 | Pas de régression observée |

- Deux parcours Chromium additionnels (1280 × 800 et 393 × 852) : bouton Jouer, accélération clavier/tactile, Pause, Reprise, HUD et boucle d'appels WebGL **simulés** fonctionnels. Upload géométrique instrumenté ~5,97 Mo, aucune matrice NaN, aucune exception JS.
- La seconde passe avec la classe autonome (plutôt qu'une condition inline) a de nouveau respecté les seuils de réduction.
- Le navigateur de test n'expose **pas de véritable WebGL** : ni vitesse GPU, ni batteries, ni graphismes réels ne sont validés. Ne pas interpréter les compteurs FPS du moteur factice comme des FPS matériels.

## Gate release
Ne pas déclarer un gain de batterie sur Android avant essai de 15 minutes sur le Galaxy A21s. Ne pas fusionner dans main ni déployer en public. Exécuter `npm run check && npm test && python build.py` sur la branche GitHub et sur la branche d'intégration actualisée avant promotion.

Tests manquants : HP Windows réel, Galaxy A21s, iPhone, WebGL physique, vrai GLB texturé ; tous **NOT_TESTED**.
