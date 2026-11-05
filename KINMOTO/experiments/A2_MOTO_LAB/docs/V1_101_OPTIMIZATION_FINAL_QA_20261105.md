# KIN MOTO V1.0.1 — Audit et optimisation multiplateforme (05-11-2026)

**Statut : V1 jouable pour tests privés, mais NON STABLE.** Branche `kinmoto/v1-optimized-crossplatform-r1-20261105`, dérivée de PR #46. Aucun site existant modifié et aucune fusion dans `main`.

## Modifications, toutes issues de la V1 existante

1. **Intégrité de carrière / défi.** Une partie du défi n'incrémente plus définitivement les mètres de la carrière, le compteur d'incidents ni la rotation des roues. `snapshot(game)` enregistre les coordonnées et mètres de la carrière, même si le jeu se ferme durant le défi. Nouveau meilleur record/reward conservé.
2. **Écran de résultat bloquant.** La partie ne peut pas reprendre derrière un écran de victoire ; `Rejouer` recrée une tentative, `Retour à la carrière` restaure la position originale.
3. **Performance sans régression.** Attributs WebGL activés une fois à l'initialisation ; projection recalculée seulement si taille de rendu/viewport change ; fond de mini-carte (chaussées et points d'intérêt) en cache 2D, route et position toujours dynamiques.
4. **Compatibilité iOS/Android.** Suppression de `Array.at(-1)` dans les statistiques ; aucun `OffscreenCanvas` nécessaire. Partage natif de sauvegarde JSON sur navigateur autorisé via `navigator.share`+`navigator.canShare`, sinon téléchargement local. Stockage persistant non disponible signalé explicitement. Bouton réessai 3D Éco si WebGL est inaccessible, pas de remplacement 2D silencieux.
5. **Rendu métier.** Le défi temporaire n'affiche plus un passager de carrière sur la moto.

## Preuves exécutées, résultats reproductibles

| Vérification | Verdict |
|---|---|
| `npm run check` | PASS |
| `npm test` sur source 1.0.1 | **213/213 PASS** |
| `python -m unittest discover -s tests -p 'test_*.py'` | **26/26 PASS** |
| `python build.py` | **PASS, 13 modules** |
| `python tools/test_local_delivery.py` | **PASS, 5 ressources HTTP locales** |
| Autopilote : 7 portes sans téléportation | **PASS, 19,6333s virtuelles, 0 collision** |
| Stress (2 parcours de 90 000 pas / 25 min chacun) | **PASS, aucun état invalide**, pas un test humain |
| UI 320×568, 393×852, 852×393, 1366×768 | **PASS avec rendu mock**, touches, pause, défi, sauvegarde |
| WebGL2 **réel logiciel** Chromium/Xvfb antérieur | **PASS bureau/mobile émulé**, 0 JS exception |
| WebGL1 **réel logiciel** sur HTML autonome antérieur | **PASS**, 0 requête HTTP externe |
| Nouvelle tentative WebGL2 logiciel | **TIMEOUT/INCONCLUSIVE** (non comptée PASS) |
| Navigateur Opera via connecteur | Onglet ancien site V0.4 retrouvé ; lecture détaillée **TIMEOUT**, aucune validation du nouveau fichier dans Opera |
| WebKit/Safari iOS physique, Galaxy A21s, HP Windows réel | **NOT_TESTED** |

Sur un micro-benchmark de 60 000 appels de projection, la médiane Node locale a diminué de 15,07ms à 7,14ms ; c'est une optimisation mathématique isolée, **pas** un FPS GPU garanti.

## Contrôle totalement indépendant du ZIP final

- HTML autonome : `KIN_MOTO_V1_1_0_1_OPTIMISEE_PC_ANDROID_IOS.html`, **126 461 octets**, SHA-256 `3c7cf6d1001d5a71c5b3955446a767e2233c57ccd25c3f9f0ce5c8af772324d8`.
- ZIP : `KIN_MOTO_V1_1_0_1_OPTIMISEE_SOURCES_QA_20261105.zip`, **2 322 619 octets**, SHA-256 `e97f7a1b4e62a92490c5b96e42b495d16e7b9b98f5d35e252c6e60573d4196d4`, 120 entrées, **118/118 empreintes SHA-256 du manifeste validées** et CRC ZIP validé.
- ZIP extrait dans `KINMOTO_V1_101_COLD_RETEST_20261105` : 213/213 Node PASS, 26/26 Python PASS, build et HTTP PASS, autopilote PASS. SHA-256 du fichier `dist/KIN_MOTO_V1_FICHIER_UNIQUE.html` reconstruite égale au HTML fourni, **égalité octet pour octet**.
- Gate `python tools/a4_release_gate.py --strict` retournant **exit 2 intentionnel : NO_GO STABLE**, G1 fonctionnel PASS mais G2 visuel, G3 HP/A21s, G4 humains, benchmark A1-D, droits complets et accord propriétaire encore non prouvés.

## Livraison et restrictions

- PC : HTML direct depuis Edge, Opera, Chrome, **hors aperçu ChatGPT**.
- Android : HTML téléchargé puis navigateur qui autorise `file://`/JavaScript/WebGL ; varier l'application d'ouverture si nécessaire.
- iPhone : HTML local transmis comme document est **une possibilité**, mais Fichiers/Telegram/Quick Look peuvent bloquer JS ; **la méthode fiable à valider est un HTTPS de prévisualisation pour le dossier PWA**, sans altérer l'ancien site. Aucun déploiement entrepris ici.
- Aucune action Remote Desktop, aucun GitHub Actions hébergée, aucun nouveau coût, aucun merge `main` ni STABLE, aucune substitution de la V1 originale.

**Prochaine QA matérielle** : une session 15–20 minutes sur HP, Galaxy A21s et iPhone, profil Éco, rapport local téléchargé (FPS et heures d'échantillonnage), batteries et chaleur notées manuellement, qualité graphique + plaisir de jeu notés par un testeur. Ne pas annoncer un PASS multi-appareils sans ces preuves.
