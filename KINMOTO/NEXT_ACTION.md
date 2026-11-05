# CHECKPOINT A2 v0.5.6 RIDE + VRAI WEBGL2 LOGICIEL — 05/11/2026

**Reprise prioritaire : [PR #37 — Real wheel travel + WebGL2 software QA](https://github.com/Terminator364/PROJECT-DRAFTS/pull/37)**, branche `kinmoto/a2-real-wheel-travel-20261105` dérivée de PR #36. **AUCUNE sortie V1/STABLE, pas de fusion dans main.**

## Acquis du nouveau cycle
1. Nouveau défaut physique authentique reproduit : moto immobilisée sur une bordure (0,01 m de trajet), mais pneus tournant comme pour 11,04 m ; HUD indiquait ~8 km/h. Corrigé après contre-audit (pas de baisse artificielle de la vitesse du moteur qui empêcherait le glissement longitudinal).
2. `src/sim.js` synchronise maintenant les rotations des roues et la vitesse au sol sur le vrai trajet après contraintes; `src/main.js` affiche la vitesse mesurée ; `bike_physics.js` expose le rayon. **4 tests nouveaux**.
3. `npm run check` et `npm test` : **127/127 PASS** ; `python -m unittest discover -s tests -p 'test_*.py'` : **22/22 PASS** ; `python build.py` : **94 880 octets** ; test HTTP localhost **PASS**.
4. **WebGL 2.0 réel exécuté en logiciel** : Chromium + Xvfb + ANGLE/Vulkan SwiftShader, bureau 1280×800 et mobile émulé 393×852. Démarrage, moto en mouvement, pause/reprise, shaders et scène visibles, 0 exceptions JS ; captures en artefacts de conversation. Script facultatif `tools/qa_software_webgl.py` reproductible hors réseau. **Ne pas confondre SwiftShader avec GPU réel Android** : le FPS logiciel ~5–10 est non transposable.
5. Simulation 72 000 pas (20min virtuelles) sous trafic : erreur de cohérence roue-odometre max 2,34×10⁻¹¹ m ; aucun état invalide. Collisions fréquentes sous commande artificiellement agressive : pas une preuve d'équilibrage du trafic. Ne pas annoncer une session humaine de 20min.
6. Archive conversation `KINMOTO_A2_V056_RIDE_WEBGL2_QA_20261105.zip` **638 266 octets**, 71 fichiers ; SHA-256 `40838a24affb3efac681e259de3916e66db6166f9dd2991a6de9c7dbeb380d28`. Après extraction neuve, 127 Node/22 Python PASS, compilation HTML SHA-256 inchangé `513c39659c8c8144a71ff7f90af373d5338b649d0e426cc04169fd48cd3a6421`.
7. Rapport complet : `experiments/A2_MOTO_LAB/docs/QA_GROUND_TRAVEL_SWIFT_WEBGL2_20261105.md`.

## Portes encore fermées — action à faire, pas à présumer

- **G2 matériel :** scène sur HP Windows réel, qualité de la moto, roues/sol/perspective, FPS, consommation mémoire, entrées clavier, états menu/pause. WebGL2 software PASS n'est PAS un test matériel.
- **G3/G4 :** Galaxy A21s (15min, 5 exercices S1–S5), écran tactile réel, chauffe/RAM, batterie, Android offline ; iOS/Chrome puis Safari sur iPhone réel (les navigateurs iOS ne sont pas vérifiés par le Chrome desktop émulé).
- **Qualité perçue :** captures SwiftShader montrent un style low-poly, véhicules/bâtiments peu détaillés ; qualité V1 **NON VALIDÉE**, ne pas qualifier de jeu fini.
- **Asset moto :** source Road Sportbike CC0 candidate; GLB binaire exact non acquis, hash/animations/matériaux/licence exacte non auditables. Ne pas importer sans audit et benchmark A/B. 
- **A1-D** comparaison dynamique avec références libres Neon/Costa : toujours PENDING.
- **Règles intangibles :** aucune publication STABLE, aucune nouvelle URL publique, aucune GitHub Action hébergée, aucun quota Remote ni coût sans accord explicite.

Reprise par `KINMOTO|SYNC`; poursuivre au niveau du source de PR #37, lire `PROJECT_STATE.json` et le rapport. Éviter de répéter les QA déjà passées hors changement de source.

---

# CHECKPOINT A2 0.5.6 POWER — RECETTE LOGICIELLE COMPLÈTE — 05/11/2026

**Reprise canonique du lot expérimental :** [PR #36](https://github.com/Terminator364/PROJECT-DRAFTS/pull/36), branche `kinmoto/a2-idle-render-gate-20261105`. Cette branche repose sur [PR #35](https://github.com/Terminator364/PROJECT-DRAFTS/pull/35), non fusionnée, et **ne représente pas STABLE/V1**.

## Acquis vérifiés avec le paquet source réel
- Source A2 v0.5.5 ZIP récupérée depuis Drive et vérifiée ; patchs GitHub A2 v0.5.6 appliqués dans une copie isolée.
- `npm run check` PASS ; `npm test` **123/123 PASS** ; `python -m unittest discover -s tests -p 'test_*.py'` **22/22 PASS**.
- `python build.py` PASS, HTML **94 499 octets**. `node --check` sur JS compilé PASS. `python tools/test_local_delivery.py` PASS (5 ressources).
- Paquet ZIP privé de conversation `KINMOTO_A2_V056_POWER_REVIEW_20261105.zip` **268 968 octets**, SHA-256 `334439ee2a0c00f2cf93e8e92c608a667ee78d09133f29af1b4e0a15d07ea8bc` ; archive réextraite, tests réussis, HTML reconstruit à SHA identique.
- HTML SHA-256 `ddc10f12239d00d28b8174821a2253311ffdae92cd46583f8264cc8fe4346ab4`.
- Fake WebGL Chromium mobile/bureau : UI et logique PASS, **réduction d'appels de dessin pendant menu/pause** (pas une mesure GPU/power réelle).
- Correctifs annexes : test adaptatif ancien mis à jour, appel de rendu gate testé, GLB validation BIN padding 0–3 octets, fixtures Python réparées.
- Rapport détaillé `experiments/A2_MOTO_LAB/docs/QA_FULL_INTEGRATION_POWER_20261105.md`.
- Tests GLB de résistance complémentaires : `tests/test_glb_fuzz.py` (**3 000 cas déterministes**, aucune exception non gérée). Paquet de recette actualisé `KINMOTO_A2_V056_POWER_QA22_20261105.zip`, SHA-256 `f21b85535ee682486dca9beeab991e2a42a81b0005b6066fb46e44f38600a2ad` (65 entrées, 270 288 octets). Re-test après extraction fraîche : 123 Node + 22 Python + HTTP PASS.


## Prochaine mission autonome — qualité perceptuelle et test matériel
1. **G2** : obtenir une vraie capture WebGL, vérifier matériaux/roues/sol/camera/occlusion sans GPU factice. Ne pas étiqueter PASS si contexte WebGL bloqué.
2. **G3/G4** : benchmark 15 min sur HP réel et Galaxy A21s (à réseau local, sans coût/Remote tant que possible). Répéter S1 ligne droite, S2 slalom, S3 freinage, S4 bosse/virage, S5 frôlement/choc. FPS, consommation RAM, surchauffe/batterie, input latency, interruption/reprise. iPhone ensuite.
3. **A1-D / Assets** : comparer aux vrais contrôleurs de Neon/Costa, acquérir le **GLB moto exact** sous licence démontrée avec hash et capacités textures/animation ; aucun modèle non validé dans le jeu.
4. Ne fusionner ni déployer vers `main`, V1, STABLE, Vercel ou autre sans accord explicite. Les PR demeurent des brouillons ; pas de runners hébergés ni quota Remote.

**État : G1 logique PASS ; G2 vraie 3D NOT_TESTED ; G3 performance matérielle NOT_TESTED ; G4 Android/iOS NOT_TESTED ; G5 licence modèle externe PENDING.** Autonomie pour corrections réversibles, mais aucune promesse de travail en arrière-plan après la réponse.

---

# CHECKPOINT EXPÉRIMENTAL A2 v0.5.6 — 05 novembre 2026

**Dépôt / branche de reprise pour la recette :** [kinmoto/integration-a2-v056-review-20261105](https://github.com/Terminator364/PROJECT-DRAFTS/tree/kinmoto/integration-a2-v056-review-20261105).

**IMPORTANT :** ceci est une branche d'intégration non-STABLE, constituée depuis le code A2 v0.5.5 et les PR brouillon #30 à #34. Aucune modification de la branche main, aucune publication. Les 16 fichiers originaux intégrés ont été vérifiés par leurs SHA de blobs Git (16/16). L'archive HTML v0.5.6 de QA existe seulement comme artefact de conversation, pas comme déploiement public.

**Résultats effectivement observés en laboratoire isolé :** 17 tests navigation, 11 tests de résolution adaptative, 4 tests SW simulé (=32/32 ciblés) ; prototype d'audit GLB 17/17 tests synthétiques ; `node --check` du HTML combiné PASS ; 72 000 pas CPU / 20 minutes simulées avec 600 routes valides ; simulation de paiement unique valide. Les microbenchmarks Node CPU ne sont pas FPS Android.

**NON VALIDÉ :** suite intégrale officielle Node/Python après fusion des sources sur cette branche, import du vrai GLB, capture vraie 3D dans cet environnement, essais 15 min PC/Android et iPhone. **Ne pas appeler v0.5.6 une nouvelle V1.**

## Mission suivante UNIQUE — QA d'intégration avant décision de fusion

1. Dans un environnement qui peut récupérer cette branche, exécuter `npm run check && npm test && python build.py` depuis `KINMOTO/experiments/A2_MOTO_LAB/`.
2. Exécuter `python -m unittest discover -s tests -p 'test_*.py'`, puis comparer les deux builders Python/PowerShell ; préserver le `sw.js` généré dans `dist/`.
3. Si G1 passe, recueillir une capture WebGL réelle et le compteur GPU/FPS ; benchmark HP + Galaxy A21s, 15 min, qualité Eco, RAM et chauffe, tests hors ligne, sans utiliser de quota Remote tant que non nécessaire.
4. Reprendre le benchmark A1-D des bases libres Neon/Costa et la vérification juridique du **binaire GLB exact** avant sélection de moteur/asset ; jamais importer en silence les modèles non audités.
5. Si G2/G3/G4/G5 ne passent pas, garder toutes les PR brouillon. Aucun déploiement Vercel/Cloudflare/Pages, aucune GitHub Actions hébergée, aucun achat, aucune suppression historique.

**Code de continuité :** KINMOTO|SYNC. L'utilisateur donne autonomie technique pour rechercher, décider des corrections réversibles et enchaîner tests/contre-tests ; les gates publics et financiers restent soumis à veto.

---

# CHECKPOINT CUMULATIF A2 v0.5.5 — 4 novembre 2026

PR [#28](https://github.com/Terminator364/PROJECT-DRAFTS/pull/28) (GPS routes et confort) et [#29](https://github.com/Terminator364/PROJECT-DRAFTS/pull/29) (rendu adaptatif, intégrité des deux builders, WebGL visual QA et audit GLB) **fusionnées**. Commit principal d'intégration : `0ebb6cf219689c0d8c989e860affaa3b49f2d7d4`.

**Livrable** : `KINMOTO_A2_V055_CUMULATIF_ANDROID_PC_SOURCES_QA_20261104.zip`, SHA-256 `c329f5a92658b1f78b7a0a2d4acc7a827106ae47bcbf42ff19e86b2e3a985076`, archivé sur Drive id `1kzvupTC0y3ubV20JSLseBv0H4BKYCRDC` (à ne pas recopier dans GitHub public).
**QA** : Node 85/85 ; Python asset tests 7/7 ; HTML autonome de 12 modules (91 629 octets) ; vrai WebGL2 dans Chromium logiciel + format mobile simulé 393×852, client ramassé et GPS + confort affichés ; 20 min CPU simulées / 72 000 pas sans état invalide. **PAS de test matériel Galaxy A21s ni HP sur cette version**, et pas d'essai du vrai GLB moto.

**Anomalie majeure corrigée** : l'HTML autonome cumulait plusieurs `const clamp` et ne démarrait pas ; le constructeur PowerShell avait une liste de modules divergente et sans `collision.js`. Contrôles Node VM + parité des sources ajoutés.

**Limite graphique** : la 3D reste stylisée ; la moto CC0 3DAssets.dev est annoncée 254,7 Ko, 5 156 triangles et clips d'animation, mais le binaire n'est PAS obtenu. Le script `tools/audit_glb.py` fournit un contrôle offline strict sans prétendre approuver la licence du fichier absent.

**Opération suivante — sans arrêt entre checkpoints** : recherche/acquisition d'un modèle moto CC0 réel libre (avec hash), audit technique, chargement glTF texturé léger, optimisation 3D et sensations sur piste étalon. Ensuite regroupement de la validation matérielle HP+Android, sans dépenser le quota Remote avant ce jalon.

**Interdits toujours actifs :** 0 appel Remote Desktop Commander, 0 déploiement Vercel/Cloudflare/Pages, 0 action GitHub hébergée, pas de nouvelle V1 publique. `KINMOTO|SYNC` reprend depuis ce fichier et `PROJECT_STATE.json`.

---

# CHECKPOINT A2 v0.5.2 CLOUD-FIRST — 4 novembre 2026

**PR #27 fusionnée** : https://github.com/Terminator364/PROJECT-DRAFTS/pull/27 ; commit `756843efd4eec5f86829eef76c1b4fc25ae75bb8`. Laboratoire expérimental A2, pas une nouvelle V1.

**Réalisé hors PC** : collision moto/disque vs voiture/bus/rectangle orienté, correction des faux chocs pendant les dépassements, séparation selon normale de contact, impact d'un véhicule sur moto arrêtée et tampon de calcul réutilisable. 64/64 tests Node PASS (incluant six minutes simulées), `npm run check` PASS, `python build.py` PASS, HTML 83 895 octets, serveur Python local PASS. L'essai navigateur Chromium headless ne dispose pas de WebGL dans ce conteneur : rendu 3D `NOT_TESTED` pour cette version.

**Protection des quotas** : capture utilisateur = 6 049/10 000 appels Remote consommés, 3 951 restants au moment de la capture, renouvellement indiqué le 1er décembre ; **0 appel Remote pendant ce lot**, 0 Vercel, 0 GitHub Actions hébergées. Ne pas consulter Remote juste pour actualiser le quota. Règles détaillées : `docs/REMOTE_QUOTA_POLICY_20261104.md`.

**Prochaine action autonome** : investiguer/acquérir un modèle de moto CC0 réellement léger, construire un petit test d'import/performance dans l'environnement isolé, vérifier ses droits et l'animation des deux roues. Comparer les sensations et le rendu sans toucher au PC. Le vrai benchmark Android/HP sera regroupé à la fin du jalon, uniquement lorsqu'une candidate est assez aboutie. `A1-D` reste ouvert, `A2` pas certifié, `A3` non commencé.

**Publications :** aucun nouveau site ni changement de V1 ; la politique de gel Vercel reste en vigueur.

---

# ✅ CHECKPOINT LOCAL 0.5.1 (sans Vercel)

PR #26 fusionnée : [outil local Windows/Python et correction collision façades](https://github.com/Terminator364/PROJECT-DRAFTS/pull/26), commit `ee2902e625136f0af97352e56e0ae65844012bfd`.

Faits : **54/54 tests** sur Node, **compilation Python + PowerShell** (Windows HP, HTML 81 006 octets), **serveurs localhost Python et PowerShell** testés (HTTP 200, 3D chargée dans Opera), aucune connexion ou déploiement Vercel. Le serveur temporaire sur HP a été arrêté après QA (port 8789 fermé). Le bundle ZIP est `KINMOTO_A2_LOCAL_QA_V051_ANDROID_PC_SOURCES_20261104.zip`, SHA-256 `00899a4406bda755d9f393fdf11acb713fe568491acb27ccbdb9ef1d56b388f5`.

Amélioration concrète : limite moto à **8,1 m** du centre de rue et caméra à **7,5 m**, contre l'ancien dérapage jusqu'à 14,5 m dans les façades. Cette correction est vérifiée numériquement et visuellement au démarrage, mais une partie longue et un Android réel sont **NOT_TESTED**.

**Prochaine action :** rester en local, benchmark A1-D + amélioration qualité A2 ; évaluation utilisateur sur HP et Galaxy A21s ; **ne pas déployer** sans nouveau GO.

---

# PRIORITÉ IMMÉDIATE — MODE LOCAL / QUOTA HÉBERGEMENT GELÉ

Décision propriétaire 2026-11-04 : **interdiction de tout nouveau déploiement Vercel**, et aucune publication alternative automatiquement, jusqu'à demande explicite. Développer et tester en local, sauvegarder dans GitHub. L'hébergement sera arbitré au moment d'une vraie release candidate. Quota Vercel Hobby : **100 déploiements / 24 h et 32 builds / heure** d'après https://vercel.com/docs/limits ; consommation réelle du compte inconnue. Ne pas inventer de solde. Aucun changement des anciennes URLs.

Voir `docs/NO_DEPLOY_DEV_POLICY.md` et `experiments/A2_MOTO_LAB/tools/` après fusion de la branche d'outillage. La prochaine démonstration se fait sur `http://localhost:8789/` (PC), **pas sur Vercel**.

---

# Prochaine action — KINMOTO A1-D (benchmark dynamique)

**État :** A0 achevé, statut public de GitHub confirmé, A1 sources et licences statiques achevés. **Aucune base 3D sélectionnée**.

Lire successivement :
1. `PROJECT_STATE.json`
2. `docs/A1_STATIC_SOURCE_AUDIT_20261104.md`
3. `docs/A1_SCORECARD_20261104.json`
4. `tasks/A1-D-BENCHMARK-RUNTIME.md`
5. `docs/CI_POLICY.md`

**Action unique :** comparer les **sensations réelles de la moto**, le rendu et les performances sur HP Windows et Galaxy A21s, sans télécharger de gros assets non nécessaires ni facturer GitHub Actions. Le HP a déjà démarré le HUD de Neon Mayhem dans Opera ; la moto n'a pas été évaluée.

**Choix d'architecture :** à décider seulement après essais. Hypothèse technique : conduite Rapier issue d'un sous-ensemble Costa Vista, interface tactile de Neon Mayhem, 3D CC0 Kenney. Ne jamais importer toute une archive externe ni les assets de Costa Vista non vérifiés.

**Arrêt sûr :** déposer preuves/mesures, créer `docs/A1_RUNTIME_REPORT.md` et revoir le tableau /100. A2 et A3 attendent le verdict, aucune URL STABLE modifiée.

## Préparation A2 sans travaux de jeu
L'interface technique moto et les dix conditions de réussite sont préparées dans `tasks/A2-MOTO-PHYSICS-DESIGN-PRELIMINARY.md`. C'est un cahier, pas un moteur choisi ou codé ; A2 ne peut démarrer qu'après A1-D.

## Relevé matériel HP (A1)
Le 04/11/2026, 8 190 240 KiB visibles, 1 157 568 KiB libres après fermeture de la démo ; Intel UHD 620. Ce relevé n'est pas un benchmark de consommation du jeu. Préférer un test de module léger à 270 Mo d'assets sur ce PC tant que la mémoire reste sous pression.

## Réalisation expérimentale intermédiaire (sans lever A1-D)

Un **laboratoire moto A2 indépendant** est disponible : [source](https://github.com/Terminator364/PROJECT-DRAFTS/tree/main/KINMOTO/experiments/A2_MOTO_LAB) et [preview](https://kin-moto-a2-moto-lab.vercel.app/). Commit de fusion PR #24 : `553b6ecd6e1678b2ebfd8832470ecb7b98526a74`.

Preuves : 38/38 tests de logique, rendu WebGL réellement observé dans Opera sur HP (50–60 FPS instantanés), scénarios direction droite/gauche avec x de signe opposé. Le **jugement qualité du joueur**, l'Android physique, les tests 15 minutes et la simulation complète de suspension n'ont **pas** été validés ; il serait faux d'appeler cela une nouvelle V1 ou de considérer A2 terminée. Le ZIP complet est sauvegardé sur Drive (fichier `1euNCtOxZqXcLNr0PLAw781pWp5ARuvL0`).

Prochaine opération : benchmark A1-D + test de cette piste sur Galaxy A21s et HP, puis décision de réemploi Costa/Neon/CC0. **Ni la V1 précédente ni son URL publique n'ont été remplacées.**
