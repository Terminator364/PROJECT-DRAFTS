# KIN MOTO — V1.0.1 Optimized Review / contre-audit final
**2026-11-05 — BUILD JOUABLE PRIVE — publication STABLE : NO-GO.**

## Base conservée
Cette branche est une fille directe de la PR #46, la V1 « Les Premières Courses ». Elle ne remplace pas son fichier HTML livré, la carrière antérieure ni `main`. Le gameplay de quatre activités (taxi, colis, VIP, défi sept portes), la circulation, le garage et les sauvegardes sont conservés.

## Défauts reproduits et correctifs vérifiés
1. **Carrière polluée par le mode défi.** Le kilométrage, la rotation des roues, les statistiques de collisions et la position sauvegardée devenaient ceux de la piste du défi. `restoreChallengeCareer` restaure maintenant le checkpoint original et `snapshot()` écrit les coordonnées de carrière même lorsqu'un défi est en cours. Nouveau contrôle des paiements de record.
2. **Projection 3D recalculée pour chaque `resize()` appelé.** Cache de matrice, invalidation sur redimensionnement réel et changement de ratio/résolution. Microbench CPU 60 000 invocations, médianes environ **15,07 ms → 7,14 ms** (ancien → corrigé), une matrice recalculée au lieu de 60 000. **Ne prouve pas de gain FPS sur téléphone**.
3. **WebGL : attributs réactivés pour chaque objet.** Désormais une seule activation par attribut lors de la création du renderer ; mêmes buffers/draw calls et rendu.
4. **Mini-carte :** routes/points d'intérêt peints une fois dans un canvas standard (pas besoin d'OffscreenCanvas), puis seul l'itinéraire et la moto sont actualisés. Compteur `minimapBackgroundBuilds` exposé en diagnostic.
5. **Compatibilité appareil :** suppression des appels `Array.at(-1)`; avertissement quand localStorage n'est pas disponible ; export fichier de sauvegarde compatible `navigator.share/canShare` si pris en charge, sinon téléchargement local ; bouton pour réessayer WebGL en qualité Éco **3D**, pas de bascule cachée en 2D ; défi ne dessine plus le passager de la carrière.
6. **Écran de résultat :** les commandes clavier ne peuvent plus redémarrer la physique derrière une victoire ; Rejouer restaure l'isolation du mode Défi.

## Preuves reproduites sur code livré
- `npm run check` PASS.
- `npm test` **213/213 PASS** (200 précédents + 13 tests de compatibilité/régression).
- `python -m unittest discover -s tests -p 'test_*.py'` **26/26 PASS**.
- `python build.py` PASS — 13 modules, HTML `dist/index.html` 125 400 octets, HTML file:// totalement autonome **126 461 octets**, SHA256 **`3c7cf6d1001d5a71c5b3955446a767e2233c57ccd25c3f9f0ce5c8af772324d8`**.
- `python tools/test_local_delivery.py` PASS : HTTP local, 5 ressources, aucune publication.
- Autopilote sans téléportation : **7/7 portes en 19,633s virtuelles**, 0 collision, 3 étoiles.
- **Vrai WebGL2 logiciel** Chromium+Xvfb+ANGLE SwiftShader : bureau 1280×800 et mobile émulé 393×852, démarrage carrière, déplacement, pause/reprise, défi : PASS, **0 erreur JS**. FPS 1–5 sont logiciels, non représentatifs du HP, d'Android ou d'iOS.
- WebGL1 logiciel forcé sur fichier autonome : PASS lors de l'essai précédent, zéro requête externe.
- UI responsive 320×568, 393×852, 852×393 et 1366×768 : PASS dans **renderer MOCK seulement**.
- Quatre scénarios navigateur renderer simulé : partage fichier natif, stockage privé indisponible/export local, restauration exacte d'une carrière, protection clavier écran victoire : PASS.
- Deux simulations de 25 minutes **virtuelles** chacune sous trafic/défis : aucune erreur d'état. Ce ne sont PAS 25 minutes humaines ni un test de température, mémoire GPU, autonomie.
- Connecteur Opera : l'ancienne URL `kin-moto-taxi-rush-demo.vercel.app` a été retrouvée, mais la lecture de son onglet a expiré. **Aucun test V1 réel sur Opera du PC n'est revendiqué**.

## Livrable à partir d'une extraction réellement vierge
Fichier indépendant `KIN_MOTO_V1_1_0_1_OPTIMISE_PC_ANDROID_IOS.html` : 126 461 octets. Archive privée `KINMOTO_V1_1_0_1_OPTIMISE_COMPLETE_QA_20261105.zip` : **2 591 726 octets**, **144 entrées**, SHA256 **`b7653875f68ee29f87918cbaf32b38bb654e5f5547e270905b185254af186d04`**.
- ZIP CRC PASS, **143/143 empreintes de manifeste PASS**.
- Extraction vierge : **213/213 Node, 26/26 Python, check, build, HTTP PASS**, HTML reconstruit **strictement identique octet à octet** au livrable individuel.
- Contient `SOURCE_V1_1_0_1/`, `SITE_PWA_OPTIONNEL_HTTPS/`, captures et preuve QA, `LIRE_AVANT_JOUER.txt`.
- L'archive n'est pas commitée comme un blob binaire GitHub ; les sources sont synchronisées sur cette branche.

## Modes de partage
- **Windows** : télécharger HTML, puis l'ouvrir avec Edge, Chrome ou Opera ; NE PAS cliquer sur son aperçu dans ChatGPT.
- **Android** : télécharger HTML puis l'ouvrir dans Chrome ou un autre navigateur autorisant les fichiers locaux.
- **iOS** : le navigateur Safari/Chrome peut afficher du HTML, mais l'aperçu Quick Look/Telegram peut bloquer JavaScript. **L'iPhone réel reste NOT_TESTED**. Le site HTTPS séparé est une option si le partage fichier ne marche pas ; ce lot n'en déploie aucun.
- ZIP : extraire puis lancer le HTML ; le ZIP n'est pas un exécutable.

## Gates selon la charte FACTORY V3
G1 logiciel PASS. G2 appréciation visuelle et ressenti humain PENDING. G3 FPS/RAM/chauffe réels HP et Galaxy A21s NOT_TESTED. G4 session 15–20 min HP/Android/iPhone NOT_TESTED. Choix final A1-D, audit juridique des ressources héritées et autorisation publication du propriétaire PENDING.

**Décision : V1 fonctionnelle livrée en candidate de travail, mais STABLE / déploiement public : NO-GO.** Aucun merge `main`, aucun Actions hébergées, aucune dépense, aucun appel Remote Desktop.
