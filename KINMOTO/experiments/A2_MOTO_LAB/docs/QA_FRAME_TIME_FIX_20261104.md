# KIN MOTO A2 — contre-audit du temps graphique (branche expérimentale)

Date documentaire : 2026-11-04. Ticket parent : #20 (A2). Mode : **cloud-first, zéro publication**.

## Problème reproduit dans le code

La boucle de `src/main.js` transmettait au moteur graphique `delta = min(0.1, elapsed)`, qui est une **protection de la simulation**, pas une mesure du temps réel entre les images. Pour une image observée toutes les 166,7 ms (6 FPS), le moteur graphique recevait 100 ms (10 FPS fictifs). Cette sous-estimation peut rendre les compteurs FPS trompeurs.

En parallèle, `AdaptiveResolution.observe()` rejetait tout intervalle supérieur à 120 ms. Ce garde-fou était largement masqué en production par le plafonnement en amont ; une correction isolée du régulateur n'aurait donc **pas** résolu le problème complet.

## Correction isolée

- `src/main.js` transmet `frameSeconds` réel au rendu, tandis que la simulation conserve son delta plafonné et sa boucle fixe 60 Hz.
- `src/adaptive_resolution.js` accepte les images visibles jusqu'à 250 ms ; les pauses plus longues sont toujours filtrées pour éviter une baisse brutale de qualité sur un réveil de navigateur.
- Deux tests de comportement ajoutés : 6 FPS visibles soutenus et pause isolée de 400 ms.
- Un test supplémentaire vérifie le contrat d'appel : temps réel envoyé au rendu et pas de modification du pas fixe de simulation.

## Preuves / limitations

- Banc de tests ciblés du régulateur, répliqué dans un dossier d'essai isolé : **8/8 PASS** avec Node.js 22.
- Après écriture dans GitHub : **PASS** des quatre contrôles de structure du code (appel du rendu, pas fixe, seuil 250 ms, présence des tests). Ce n'est pas l'exécution de l'ensemble du dépôt.
- Suite officielle Node (85 anciens + nouveaux tests), build Python/PowerShell, WebGL réel, perf GPU, Android Galaxy A21s, HP et iPhone sur cette branche : **NOT_TESTED** dans cette reprise.
- La diminution de la résolution n'améliorera pas nécessairement un appareil limité par le CPU ; aucun gain FPS matériel n'est revendiqué.
- Aucun nouveau modèle GLB intégré ni aucune licence d'asset modifiée.

## Garde-fous

Aucune modification de `main`, `STABLE`, URL Vercel, GitHub Actions, quotas Remote Desktop ou clé privée. Branch/PR de revue uniquement. Ne pas fusionner avant exécution de `npm run check && npm test && python build.py`, contre-test manuel Android/PC et accord sur une éventuelle release.

## Prochain contrôle précis

Lancer le jeu localement depuis ce commit, relever via `KINMOTO_DIAGNOSTIC()` : FPS, qualité, `adaptiveScale`, `adaptiveSteps` après 10 minutes de parcours identique. Comparer à `d5d6796` en profils Eco/Balanced ; noter aussi chaleur, RAM, erreurs WebGL. **Ne pas déclarer PASS matériel sans appareil physique.**
