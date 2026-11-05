# KIN MOTO A2 0.5.6 POWER — QA d'intégration complète
Date : 2026-11-05. **LABORATOIRE UNIQUEMENT — NON STABLE, NON PUBLIÉ.**

## Provenance et environnement
Base réelle : ZIP canonique A2 v0.5.5 récupéré dans Google Drive (ID `1kzvupTC0y3ubV20JSLseBv0H4BKYCRDC`, 818 717 octets, 83 entrées). Recoupement des fichiers changés avec GitHub : PR #35 (intégration GPS/FPS/SW/GLB) et PR #36 (rendu ralenti en pause/menu). Node v22.16.0, Python 3, tests réalisés dans un environnement Linux isolé. Les données de l'utilisateur et la source sauvegardée n'ont pas été modifiées.

## Commandes et résultats réellement exécutés
Depuis `SOURCE_A2_V056` reconstitué à partir des sources :
- `npm run check` : **PASS** (syntaxe des modules contrôlés).
- `npm test` : **123/123 PASS**. Il s'agit des 85 tests originaux et des tests supplémentaires présents dans le dossier; deux tests historiques de FPS/câblage ont été adaptés à l'interface de rendu réellement modifiée.
- `python -m unittest discover -s tests -p 'test_*.py'` : **20/20 PASS** (7 scénarios originaux + 13 adverses, dont trois contrôles BIN glTF).
- `python build.py` : **PASS**, 12 modules, HTML autonome **94 499 octets**.
- `node --check` sur le JavaScript extrait du HTML autonome : **PASS**.
- `python tools/test_local_delivery.py` : **PASS**, 5 ressources servies sur 127.0.0.1, contrôle path traversal et cache, aucune publication.
- Simulation du moteur CPU 72 000 pas (20 minutes *virtuelles*), 600 itinéraires : PASS ; mission payée une fois. Ne pas présenter ceci comme 20 minutes de jeu physique.

## Vérification de rendu sur navigateur avec GPU factice
Chromium/Playwright, résolution bureau 1280×800 et mobile simulé 393×852. Démarrage, accélération clavier/tactile, HUD, pause/reprise, uploads de données de géométrie et matrices finies : PASS sur le **moteur de rendu instrumenté/factice**. Aucune preuve d'un contexte WebGL physique, aucun benchmark de FPS GPU réel.

Comparaison d'appels de dessin sur 1,2s (deux passages) : menu 1368→171 (-87,5%), pause 1470→210 (-85,7%), conduite 1482,5→1452,5 (-2,0%). La réduction du nombre d'appels en pause est observée, mais l'effet sur batterie ou chauffe Android reste **NOT_TESTED**.

## Contre-audits effectués en cours de chantier
1. La suite d'intégration échouait sur un ancien test exigeant d'ignorer **100 images à 300 ms** au premier plan, alors que le correctif doit traiter une chute persistante ~3 FPS. Corrigé : test des images masquées et suspensions >600 ms. Sources GitHub mises en cohérence sur branches #30, #35, #36.
2. Test de câblage de rendu obsolète : il attendait `renderer.render(game,frameSeconds)`; le code actuel emploie `renderer.render(game,active?frameSeconds:1/60,active)`. Assertion ajustée sur branche #36 ; 123 tests repassés.
3. Validateur glTF trop permissif pour BIN : requiert maintenant 0–3 octets de remplissage nul seulement et un premier buffer embarqué ; fixtures Python initialement incorrectes (144 octets `\\x00` au lieu de 36 octets nuls) réparées. Ajout de trois cas; 20/20 PASS, recopiés dans branches #34, #35, #36.
4. Première archive de distribution manquait son dossier `docs/` requis par `build.py`. Refaite et reconstruite **depuis un dossier neuf**; nouvel HTML strictement identique à l'original.

## Artefact de contrôle
Archive privée de conversation `KINMOTO_A2_V056_POWER_REVIEW_20261105.zip` :
- Taille **268 968 octets**, 64 fichiers, `ZipFile.testzip()=None`.
- SHA-256 ZIP : `334439ee2a0c00f2cf93e8e92c608a667ee78d09133f29af1b4e0a15d07ea8bc`.
- HTML `KINMOTO_A2_V056_POWER_TEST.html`, taille **94 499 octets**, SHA-256 `ddc10f12239d00d28b8174821a2253311ffdae92cd46583f8264cc8fe4346ab4`.
- Reconstruction après extraction fraîche : SHA256 HTML identique, suite Node **123/123**, Python **20/20**, test HTTP local **PASS**.
- Archive livrée à travers cette conversation; **aucune copie de cette archive n'est présumée présente sur GitHub ou Drive**.

## Portes encore fermées
- Vrai rendu WebGL2 et qualité graphique sur GPU : **NOT_TESTED** (l'environnement isole le contexte graphique).
- Galaxy A21s / HP Windows / iPhone physiques, 15 minutes de conduite humaine, FPS, mémoire, thermique, son, commandes iOS : **NOT_TESTED**.
- Modèle Road Sportbike CC0 réel : **NOT_ACQUIRED**. Les informations du catalogue ne suffisent pas à vérifier le fichier exact, les animations, les textures et les droits.
- Benchmark dynamique comparatif Neon/Costa : **PENDING**.
- Version V1 officielle/publication, déplacement des URLs STABLE, fusion main : **INTERDIT SANS ACCORD PROPRIÉTAIRE**.

## Succession
Reprendre depuis PR #36, branche `kinmoto/a2-idle-render-gate-20261105`, qui dérive de PR #35. Effectuer un test de bureau WebGL avec GPU réel, puis Galaxy A21s sur réseau local avant tout arbitrage qualité. Toute future publication exige validation de l'utilisateur; aucune GitHub Actions hébergée, Vercel, Remote Desktop ni dépense effectuée.

## Annexe QA22 — fuzzing déterministe et paquet republié dans le chat
Après le bilan initial 123 Node / 20 Python, un test de robustesse reproductible et **sans connexion réseau** a été ajouté sous `tests/test_glb_fuzz.py` : 1 500 mutations binaires aléatoires et 1 500 mutations structurelles JSON, graines fixes `20261105`. Un premier balayage ad hoc de 7 000 cas n'avait trouvé aucune exception non gérée ; les **3 000 cas** de la suite officielle sont maintenant rejouables à chaque build.

**Nouvelle suite officielle sur source locale : 123/123 Node + 22/22 Python PASS.** `npm run check`, `python build.py`, `python tools/test_local_delivery.py` PASS. Ce sont des tests de résistance du parseur, pas une preuve de conformité complète glTF ni la validation d'un modèle externe.

**Archive de contrôle suivante** (plus complète que le ZIP précédent) : `KINMOTO_A2_V056_POWER_QA22_20261105.zip`, **270 288 octets**, 65 entrées, SHA-256 `f21b85535ee682486dca9beeab991e2a42a81b0005b6066fb46e44f38600a2ad`. L'archive a été extraite à neuf ; manifeste SHA vérifié sur 64 fichiers ; tests **123/123 Node**, **22/22 Python**, serveur HTTP local PASS après extraction ; reconstruction HTML **94 499 octets**, SHA-256 **inchangé** `ddc10f12239d00d28b8174821a2253311ffdae92cd46583f8264cc8fe4346ab4`.

**Portes G2-G4 inchangées :** vrai GPU WebGL, Galaxy A21s, HP, iPhone et ressenti toujours NON TESTÉS. Aucun modèle CC0 binaire récupéré (DNS du serveur externe indisponible). Aucune mise en production ni déploiement public. L'archive demeure un artefact de conversation, non présumée présente sur Drive/GitHub.
