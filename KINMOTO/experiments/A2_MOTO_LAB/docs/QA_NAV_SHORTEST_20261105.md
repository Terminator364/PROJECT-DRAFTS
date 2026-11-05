# QA A2 — GPS sans détour inutile (2026-11-05)

## Reproduction du défaut dans le build A2 v0.5.5 fourni

Le fichier autonome joint `KINMOTO_A2_V055_JOUER_LOCAL_PC.html` a été exécuté dans un banc Node VM sans lancer `boot()`. L'ancien `findRoute` force le déplacement par une intersection, même lorsque source et destination appartiennent au même segment :

| Cas | Distance correcte | Ancienne distance |
|---|---:|---:|
| (0,10) → (0,20) | 10 m | 30 m |
| (0,13) → (0,23) | 10 m | 36 m |
| (20,0) → (40,0) | 20 m | 60 m |
| (20,120) → (40,120) | 20 m | 60 m |

Ce comportement rend la flèche GPS mensongère et peut ordonner de revenir à un carrefour inutilement.

## Correction

Le graphe conserve les 9 carrefours mais insère 2 ancres temporaires sur les tronçons pertinents, puis relie les noeuds dans l'ordre géométrique. Dijkstra calcule alors un trajet sur les rues, y compris une arête directe si les deux ancres sont sur le même tronçon. La fonction reste indépendante du moteur 3D et du réseau. Les débuts/fins hors de l'axe routier peuvent avoir un raccord perpendiculaire jusqu'à la rue proche (client devant une boutique, par exemple).

Aucune expansion de ville, aucun changement de physique, aucun nouvel asset ni aucune API.

## Preuves de QA de ce lot

- `node --test /mnt/data/kinmoto_lab_work/graph_src/tests/*.test.mjs` : **15/15 PASS** sur Node v22.16.0, à partir d'une extraction du bundle A2 et du module remplacé.
- 1 500 couples pseudo-aléatoires : distances finies, symétrie, déterminisme et longueur jamais inférieure à la distance euclidienne.
- 81 couples de destinations de la liste KIN MOTO : routes finies.
- 250 routes vérifiées sur les segments intérieurs : pas de diagonale traversant les pâtés de maisons.
- `node --check /mnt/data/kinmoto_lab_work/bundle.js` : **PASS** sur HTML assemblé avec la modification GPS et la correction FPS de la PR #30.
- Validation visuelle WebGL du nouveau bundle : **BLOCKED** dans l'environnement isolé (navigateur refuse l'accès WebGL, aucune capture 3D certifiée).
- Suite officielle 85 tests du dépôt / téléphones Galaxy A21s et iPhone / HP Windows réel : **NOT_TESTED** dans ce lot. Ne pas confondre les tests additionnels avec un passage de toute la suite.

## Indépendance des correctifs

Ce patch GPS est isolé de la PR #30 (temps de frame), et ni l'un ni l'autre ne doit être fusionné en STABLE sans vérification indépendante. Le HTML expérimental combine les deux uniquement pour une recette locale à venir.

## Prochaine validation

Récupérer la branche sur un environnement de tests complet, lancer `npm run check && npm test && python build.py`, puis filmer un trajet de 10 m et un parcours avec virage sur HP/Galaxy A21s. Mesurer les FPS et RAM réels. Aucun déploiement public, runner hébergé, achat ou appel Remote Desktop n'est requis pour la QA logique.
