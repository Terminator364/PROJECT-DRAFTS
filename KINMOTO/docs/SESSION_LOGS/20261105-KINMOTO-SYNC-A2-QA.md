# KINMOTO — Session de reprise indépendante — 2026-11-05

Code de reprise : **KINMOTO|SYNC**. Type : audit + correctifs de laboratoire, **aucune release officielle**.

## État de départ vérifié

Dépôt : `Terminator364/PROJECT-DRAFTS`, sous-répertoire `KINMOTO/`.
HEAD `main` au départ : `d5d6796ceabef8de853883925f41d0861d679948`.
Laboratoire A2 réel sur main : `v0.5.5` (85 tests Node + 7 tests Python **selon le rapport précédent**, non relancés intégralement ici).
Source HTML personnel disponible dans cette session : `KINMOTO_A2_V055_JOUER_LOCAL_PC.html` (91 629 octets).

## Correctifs isolés et traçables

| PR | Sujet | Fichiers du jeu | QA locale de cette session | Fusion |
|---|---|---|---|---|
| [#30](https://github.com/Terminator364/PROJECT-DRAFTS/pull/30) | FPS réel vs delta physique, adaptation des chutes soutenues à 2–6 FPS | main.js, adaptive_resolution.js, tests, rapport | 11 tests ciblés de dynamique + JS syntaxe | Brouillon, non fusionné |
| [#32](https://github.com/Terminator364/PROJECT-DRAFTS/pull/32) | Plus court chemin sur un segment et proximité du point de prise en charge | navigation.js, tests, rapport | 17 tests de GPS/guide, dont 1 500 paires aléatoires | Brouillon, non fusionné |
| [#33](https://github.com/Terminator364/PROJECT-DRAFTS/pull/33) | SW du dossier source, pré-cache 12 modules + isolation du cache | sw.js, tests, rapport | 4 tests simulés, 17 fichiers de cache inspectés | Brouillon, non fusionné |

**Total des contrôles ciblés exécutés hors hébergement : 32/32 PASS.** Ils ne doivent pas être additionnés aux 85 anciens tests comme s'il s'agissait d'une suite complète réexécutée.

## Intégration expérimentale hors dépôt STABLE

Un HTML local temporaire combine les correctifs de PR #30 et #32 depuis le fichier HTML v0.5.5 donné par le propriétaire. `node --check` PASS.

Simulation Node VM : 72 000 pas de logique (20 minutes **virtuelles**, pas 20 min de jeu humain), 600 calculs de route sans erreurs, `validate(game)=[]`; parcours de mission : 3500→6050 FC, 1 seule course payée, tentative immédiate suivante n'a pas versé de double rémunération. Environ 10 s de CPU conteneur, delta de heap Node environ +822 Ko après GC : **aucune extrapolation FPS/CPU/RAM sur Android**.

Archive de recette locale : `KINMOTO_A2_V056_QA_LOCAL_20261105.zip`, SHA-256 `829e76d0ab37aaa817d689a560c3bc416903177e86a7c9644fbd7cd6da989f50`, créée localement dans la conversation du 05/11. **Cette archive n'est pas un build public ni une V1.** Les fichiers de conversation ne deviennent pas automatiquement des fichiers GitHub/Drive.

## Contre-audit et limites

- Nouveau défaut GPS d'abord détecté : même rue (0,10)→(0,20) = 30m sur base v0.5.5 au lieu de 10m. Corrigé par insertion d'ancres.
- Correctif GPS contre-audité : destination à 1m sur un trottoir pouvait encore indiquer ~27m ; corrigé par route directe sous 16m.
- Nouveau défaut GPU : delta de rendu plafonné à 100ms et filtre qui ignorait les frames >120ms ; corrigé. Contre-audit ensuite étendu aux chutes de 2-3FPS et pauses isolées.
- Source PWA : 6 modules sur 12 préchargés et PNG absents du dépôt source. Corrigé sans toucher au `dist/sw.js` généré.
- Essai Chromium avec Playwright dans environnement isolé : **WebGL indisponible**. G2 visuel **BLOCKED** ici ; aucune capture 3D valide revendiquée.
- HP Windows réel v0.5.6, Samsung Galaxy A21s, iPhone, hors ligne matériel, RAM/FPS/thermique 15min : **NOT_TESTED**.
- Modèle moto GLB CC0 : site source vérifié ; **binaire non acquis**, licence et compatibilité du fichier exact non contrôlées localement. Aucun asset importé.
- Aucun nouvel hébergement, aucune GitHub Actions hébergée, aucun Remote Desktop, aucune dépense.

## NEXT_ACTION précis

1. Examiner indépendamment les PR #30, #32 et #33, chacune sans toucher à `main` avant vérifications.
2. Sur le dépôt complet : `npm run check && npm test && python build.py && python -m unittest discover -s tests -p 'test_*.py'`. Cette suite reste NOT_TESTED pour ces branches combinées.
3. Comparer l'HTML généré Python/PowerShell ; vérifier activation du SW sur vrai navigateur et reprise mode avion.
4. Benchmark matériel HP/Galaxy A21s : parcours S1-S5, contact roues/sol, GPU, RAM, FPS/15min, chaleur, confort HUD. Noter le navigateur exact.
5. Acquérir et auditer un modèle moto CC0 réel (hash, triangles, pivot, licence, textures) ; intégrer seulement après choix de loader et benchmark mémoire.
6. Conserver le gel de toutes URLs publiques et le veto utilisateur sur STABLE/V1. Ne pas présenter 0.5.6 comme publiée.

**Session consignée — statuts PASS/FAIL/BLOCKED/NOT_TESTED explicites, aucun travail après fin de tour promis.**

## Annexe de contre-audit : modèles 3D et coût géométrique

- [PR #34](https://github.com/Terminator364/PROJECT-DRAFTS/pull/34) **brouillon, non fusionnée** : durcissement `tools/audit_glb.py` (indices négatifs, limites de bufferViews, taille au début, tableaux/structures internes invalides). Prototype local Python : **17/17 tests synthétiques PASS** (7 historiques répliqués + 10 adverses). **La suite exacte GitHub et un vrai GLB externe sont NOT_TESTED.**
- Analyse sur l'HTML autonome v0.5.5 : `makeWorld()` crée **139 296 sommets / 46 432 triangles**, soit environ **5 014 656 octets de tampon Float32 GPU** pour le monde seul (sans textures, buffers supplémentaires, navigateur ou GPU driver). Moto sans passager : 3 116 triangles ; avec passager : 3 608 triangles. Ce sont des volumes géométriques calculés, **pas** une mesure de RAM Android.
- Microbenchmark GPS rectifié : le premier comparatif mélangeait moteur VM et module natif et a été rejeté. Reprise identique des deux versions via Node VM, 15 000 paires : ancien **1 733,89 ms** (115,59 µs/appel), nouveau **396,95 ms** (26,46 µs/appel). Valeurs uniquement Node/CPU, pas FPS ou latence tactile.
- Archive ZIP de recette locale initiale vérifiée avec `ZipFile.testzip()`, ses 6 SHA-256 internes et contrôle de syntaxe JavaScript. SHA-256 archive inchangé : `829e76d0ab37aaa817d689a560c3bc416903177e86a7c9644fbd7cd6da989f50`.
- Une évaluation A/B d'un vrai GLB texturé reste indispensable. Le candidat Road Sportbike annoncé 5 156 triangles sur sa page n'a pas été téléchargé ; 8 matériaux et rotations de roues peuvent accroître les draw calls. **Ne pas le promouvoir automatiquement au rang de modèle accepté.**

## Reprise assemblée en branche d'intégration (05/11)

**Branche source candidate sans promotion STABLE :** `kinmoto/integration-a2-v056-review-20261105`. Parent de référence `main` : `d5d6796ceabef8de853883925f41d0861d679948`. Git tree agrégée : `840cff6f7f1f211d38d6be2a3f29f0ac24f95e5d`. Commit initial d'intégration : `c387ac64c657b302ba677019599ebb1bd579fa43`.

Les **16 fichiers** concernés (code, tests et documentation des PR #30–34) ont été comparés aux SHA de blobs Git des branches sources. **16/16 concordances PASS**. Aucune donnée étrangère à `KINMOTO/` intégrée.

`PROJECT_STATE.json` sur cette seule branche enregistre `DRAFT_INTEGRATION_NOT_RELEASED` et `qa_full_repo=NOT_TESTED` ; `NEXT_ACTION.md` spécifie la suite locale Node/Python/WebGL. La branche `main` conserve l'ancienne V0.5.5 canonique et le gel du déploiement. Ce checkpoint est vérifiable même sans l'artefact ZIP du chat.

**Ne pas confondre égalité de blobs, QA Node isolée et recette Android réelle.**
