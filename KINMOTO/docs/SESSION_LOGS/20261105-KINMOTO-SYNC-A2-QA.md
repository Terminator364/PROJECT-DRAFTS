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
