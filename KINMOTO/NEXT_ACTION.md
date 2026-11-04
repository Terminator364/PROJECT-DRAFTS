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
