# KINMOTO FACTORY V3 — A4 TRAFFIC REVIEW / 05 novembre 2026

**Version :** `A2A3-A4-0.5.7-TRAFFIC-REVIEW`. Laboratoire privé, pas V1/STABLE. Parent : PR #45 (A4) ← #44 (A3) ← #43 (A2). Le choix du moteur A1-D reste en cours (#42).

## Défauts reproduits et contre-audit

Sur le code parent de PR #45, une conduite synthétique sur **72 000 pas (20min virtuelles)** produisait **67 collisions, 31 518 corrections de contact et 31 113 images en chevauchement** avec une voiture. L'épisode le plus long durait **18 173 pas d'affilée** (~303s virtuelles). L'IA freine mais ne dépasse jamais une moto immobilisée devant elle. Une première contre-solution **recul automatique** a empiré les contacts à ~58 200 images : **rejetée, non fusionnée**.

Anomalie supplémentaire dans les itinéraires : les coins de route en diagonale passaient à **9,60m des axes routiers**, pour une demi-largeur d'asphalte de **9m**. Les voitures traversaient donc des coins de blocs visuellement bâtis. Les nouvelles trajectoires arrondies passent à **6,10m maximum** de l'axe routier sur les quatre boucles.

## Correctifs

- Détection d'une moto lente en avant, projection sur l'axe de circulation. Le véhicule choisit un décalage latéral de **2,9m opposé au pilote**, seulement si la position candidate demeure sur l'asphalte et qu'aucune autre voiture ne se trouve à moins de 5m dans la voie adjacente.
- Déplacement latéral plafonné à **3,1m/s** en coordonnées mondiales : aucun téléportage lorsque l'itinéraire change de segment. Maintien temporaire de 3,5s puis retour progressif à la trajectoire normale.
- Lors de l'évitement, la représentation de la voiture peut pivoter d'au plus **0,30 rad** vers sa direction de déplacement réelle ; le collider suit le `yaw` de la route d'origine. Les impacts à grande vitesse et le plafond de pénétration de 0,32m/tick de PR #43 restent actifs.
- Quatre boucles redessinées avec 20 points de contrôle (au lieu de 16), sans couper les coins de bâtiments.
- `sampleTrafficRoute` met en cache le segment de route par voiture au lieu de rechercher les 20 segments à chaque pas. Sur le banc Node après échauffement, **médianes de cinq runs : ~551ms ancien vs ~554ms nouveau pour 72 000 pas** ; variance du CPU conteneur importante. Ce ne sont PAS des performances A21s.

## Comparaison conservée en recette

| Scénario | Parent PR #45 | Nouveau |
|---|---:|---:|
| 20s derrière une moto arrêtée : distance voiture sur itinéraire | 5,00m | 153,29m |
| Vitesse voiture finale | ~0m/s | 8,00m/s |
| Mouvement voiture max par pas | 0,0696m | 0,1423m |
| Virage : distance max de l'axe routier | 9,60m | 6,10m |
| Conduite synthétique 72 000 pas : corrections de contacts | 31 518 | 0 |
| Conduite synthétique 72 000 pas : collisions | 67 | 0 |
| Conduite synthétique 72 000 pas : trajet moto | 992,69m | 280,13m |

**Interprétation rigoureuse :** les chiffres des trajectoires moto changent car les deux moteurs réagissent différemment à la même commande irréaliste contre une bordure. La diminution des collisions est vérifiée, mais ne constitue **ni une preuve de meilleure jouabilité ni une comparaison humaine de même trajet**. Un choc forcé à 12m/s continue de produire une vraie pénalité.

## QA reproductible

- **11 nouveaux tests** `tests/a4_traffic_detour.test.mjs` : dépassement et retour, absence d'évitement à distance, interdiction si voie voisine occupée, choc physique conservé, déterminisme, deux stress de **72 000 pas**, routes toujours sur chaussée, cache exact (y compris rebouclage), angle visuel et non-sortie de chaussée.
- **184/184 tests Node PASS** (173 précédents + 11) ; **26/26 tests Python PASS** ; `npm run check`, build 12 modules et contrôle HTTP local cinq ressources PASS.
- **Banc A1-D S1–S5** sur le moteur actuel : **5/5 scènes logiques PASS**. Aucun cône physique, navigateur, test tactile ni notation de plaisir n'est impliqué.
- Trois stress complémentaires de **90 000 pas chacun, 25 minutes virtuelles** : moto stationnée, conduite agressive et périodique ; **0 collision/chevauchement aux points échantillonnés, 0 état invalide**, maximum 6,10m de l'axe routier. Mesures mémoire heap Node après GC : +0,51MB lors du premier cycle de chauffe, puis +0,05MB et +0,04MB dans les deux suivants. **Pas des mesures de mémoire Android ni de batterie.**
- Vrai WebGL2 via **Chromium/Xvfb/ANGLE/Vulkan SwiftShader logiciel**, format bureau 1280×800 et mobile émulé 393×852 : démarrage, accélération, pause, reprise PASS, 0 erreur JS ; FPS logiciels indicatifs 4/11 non généralisables au GPU cible.

## Source, droit et gouvernance

Les quatre fichiers de code/test locaux `src/sim.js`, `src/render.js`, `package.json`, `tests/a4_traffic_detour.test.mjs` ont leurs **SHA Git blob comparés aux commits de cette PR** avant qualification. Aucun code Neon/Costa ni asset tiers n'a été copié dans le runtime ; principes de gestion de flux seulement.

Le gate A4 `tools/a4_release_gate.py --strict` conserve sa sortie **NO_GO (exit 2)** : G1 fonctionnelle PASS ; G2 visuel, G3 performances HP/A21s, G4 sessions humaines, décision moteur A1-D, licences finales et **GO propriétaire** tous BLOCKED. La circulation reste un jeu simplifié de voies, sans planification globale de carrefours/PNJ. Aucun merge main/STABLE, nouveau site public, GH Actions hébergées, Remote ou coût.
