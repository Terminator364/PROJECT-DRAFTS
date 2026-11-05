# KINMOTO A2 — Rapport technique local, exportable en un clic
Date : 05 novembre 2026. **Laboratoire uniquement, sans publication V1/STABLE.**

## Problème à résoudre
Les tests Node 156/156, Python 22/22 et les parcours WebGL2 logiciels ont passé sur la candidate Clock + Save de PR #40. Mais un rendu SwiftShader Linux ne permet pas de mesurer les performances du **PC HP Windows** ni du **Samsung Galaxy A21s** : FPS, charge GPU réelle, occupation mémoire du navigateur et ralentissements physiques sur 15min restaient NOT_TESTED. Il faut un protocole local que le joueur puisse exécuter lui-même sans serveur.

## Implémentation dans la présente branche
- `src/adaptive_resolution.js` : `DevicePerformanceRecorder`, enregistre **au plus une mesure par seconde pendant le jeu actif visible**, sans timer indépendant; jusqu'à **900 mesures** (15 minutes à 1Hz), anneau borné, pas d'accumulation infinie.
- Mesures JSON : `fps`, `renderScale`, `renderPixels`, `simSeconds`, `droppedSeconds`, `jsHeapBytes` (si fourni par le navigateur). Résumé : moyenne, minimum, P10, maximum FPS, résolution minimale, durée de fenêtre mesurée, secondes de simulation volontairement ignorées.
- `src/main.js` : appelle la collecte à la cadence prévue, puis sur clic crée un objet Blob JSON et le télécharge localement avec `URL.createObjectURL`. Aucun `fetch`, requête réseau, backend, Analytics ou nouvelle dépendance.
- `index.html` : nouveau bouton **« ↓ RAPPORT DE PERFORMANCE (LOCAL) »** dans le menu Pause, près de l'export de sauvegarde. Le téléchargement n'est lancé **que sur action du joueur**.
- `tests/local_device_diagnostics.test.mjs` : **9 tests** couvrant intervalle, pause, limite900, statistiques, métriques invalides, absence de données de partie, copies non mutables, budgets invalides et câblage UI.
- Version identifiée comme `A2-LAB-0.5.6-DIAGNOSTIC-DRAFT` ; ne pas confondre avec une version commerciale.

## Confidentialité et limites
Le rapport **ne comprend pas** : nom du joueur, position GPS, mission/client, trajet, argent, adresse, téléphone, identifiant de compte ni navigateur envoyé vers Internet. Il contient l'échelle de rendu, les FPS, la résolution écran, le profil qualité, les dimensions et éventuellement l'utilisation mémoire JavaScript, selon la disponibilité de `performance.memory`. Les informations restent sur l'appareil à moins que le propriétaire ne partage volontairement le fichier.

`jsHeapBytes` peut être `null` sur Android et iOS ; cela ne signifie pas zéro mémoire. Le navigateur peut ralentir en arrière-plan : les échantillons ne sont recueillis que lorsque la partie est visible et non en pause. Les FPS pendant la pause ne polluent pas les statistiques.

## QA exécutée sur la source complète
- `npm run check` **PASS**.
- `npm test` **165/165 PASS** (156 existants + 9 rapports locaux).
- `python -m unittest discover -s tests -p 'test_*.py'` **22/22 PASS**.
- `python build.py` **PASS**, 12 modules, HTML autonome **103 029 octets**, SHA-256 `fef699cd212c86989c55fbb8b09fa301f2d7757cca6af70d4f0c8c4f94bfa368`.
- `python tools/test_local_delivery.py` PASS, vérification HTTP localhost.
- GitHub : six fichiers nouvellement changés comparés à leur Git blob SHA local par une récupération indépendante.
- Navigateur **Chromium WebGL2 logiciel SwiftShader**, mobile émulé **393×852** : ouverture du menu Pause, clic Export, téléchargement JSON réel intercepté. Résultat : `schema=1`, `samples=4`, `avgFps=7.3`, `minRenderScale=1`, **0 erreur JavaScript**. Une courte session de démonstration **n'est pas** la validation physique de 15min, et le FPS logiciel n'est pas extrapolable à l'Android réel.

## Protocole matériel HP / Galaxy A21s (15 minutes)
1. Ouvrir le fichier HTML autonome depuis le navigateur de l'appareil, démarrer une partie et choisir ECO.
2. Réaliser des trajets libres et des missions pendant **15 minutes réelles**, avec les commandes clavier/tactile appropriées. Maintenir l'écran actif et le jeu visible.
3. Ouvrir Pause, cliquer **« Rapport de performance (local) »**, conserver le JSON téléchargé. Exporter la sauvegarde séparément seulement si souhaité ; ne pas envoyer de données de partie pour l'audit matériel.
4. Vérifier `summary.samples`, `summary.sampleWindowSeconds`, `summary.avgFps`, `p10Fps`, `minRenderScale`, `droppedSimSeconds` et la présence éventuelle de `jsHeapBytes`. Si la fenêtre est courte (petit nombre de mesures), ne pas déclarer un test de 15 minutes.
5. Enregistrer séparément, si possible, chaleur ressentie, pourcentage batterie avant/après et erreurs de contrôle, car le navigateur peut ne pas exposer ces mesures. Comparer les résultats sur HP et Galaxy sans supposer un matériel équivalent.

## Gates
**Le bouton lui-même est validé sur Chromium logiciel.** Collecte de 15min réelle sur HP, Galaxy A21s et iPhone : **NOT_TESTED**. GPU natif et qualité V1 : **NOT_APPROVED**. Binaire/licence GLB externe : **NOT_ACQUIRED**. Aucun déploiement public, GitHub Actions hébergée, Remote Desktop, dépense, merge main ni modification d'URL STABLE.
