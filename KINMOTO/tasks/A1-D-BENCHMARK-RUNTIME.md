# A1-D — Protocole de benchmark d'exécution à zéro franc

**But :** vérifier quel réemploi est réellement supérieur aux anciennes versions KIN MOTO. **Ce n'est pas un mandat de reconstruire le jeu.**

## Priorités impératives
1. **Neon Mayhem** : démo officielle `https://pranshuparmar.github.io/neon-mayhem/`, sans installation ni téléchargement de ZIP au départ. Sur HP Opera, le chargement du titre, puis l'entrée au HUD de jeu ont été observés le 04/11/2026 après touche Enter (vérification via arbre d'accessibilité). La conduite moto réelle et les FPS/RAM sont **NON TESTÉS**.
2. **Costa Vista** : `https://github.com/fastrouter/experiments-costa-vista`. Ne **PAS** télécharger les ~270 Mo de ressources pour un premier diagnostic. Examiner `src/physics/vehicleController.ts`, `src/world/roadGraph.ts`, `src/systems/traffic.ts` à SHA fixé. Ensuite prototype **extrait** léger sur scène fictive ou build limité aux assets expressément approuvés, après préparation d'un outil Node 20+ gratuit si indispensable.
3. **Contraintes de qualité** : la moto doit porter ses roues sur le sol, avoir une accélération, un freinage, une inclinaison et une trajectoire crédibles ; aucune inversion gauche/droite. Les tests automatiques ne valident pas à eux seuls le ressenti.
4. **Artefacts libres** : Kenney Car Kit + City Kit Roads, CC0, télécharger uniquement ce qui sert à la piste étalon. Ne pas recopier la moto interne de Costa Vista dont la licence asset est à éclaircir.
5. **Aucun** site KIN MOTO public, URL STABLE, API, workflow GitHub Actions ni données privées n'est modifié.

## Scènes/tests canoniques, échantillon minimal
| Scène | Manoeuvre | Mesure | FAIL si |
|---|---|---|---|
| S1 | 100 m droit, accélération puis lâcher gaz | vitesse, roue/sol, caméra, FPS | glisse visuellement en permanence ; input retardé |
| S2 | Slalom lent 6 plots | direction gauche/droite, yaw/lean, collision | axe inversé, zigzags instables |
| S3 | Freinage de 50 km/h à 0 | distance, temps, animation roue, arrêt | compteur seul change ; moto continue à glisser |
| S4 | Virage serré + irrégularité chaussée | tenue de route, amortissement | s'envole, rebondit, tombe sans raison |
| S5 | Frôlement puis choc voiture | réaction véhicule, perte de vitesse, dégâts | traversées, collision fantôme, téléportation |

**Benchmark reproductible :** version du navigateur, profil machine, réglage, dimensions d'écran, build/commit, durée de session, scène, mesure et capture. Répéter sur deux navigateurs PC ; puis Galaxy A21s réel 15–20 minutes en mode économie.

**Plafonds à calibrer** : 24–30 FPS cible pour A21s, pas de crash, échauffement ni croissance mémoire continue, réactivité perçue acceptable. Ces valeurs restent cibles provisoires ; aucune mesure réelle encore enregistrée.

## QA et état d'arrêt
- `PASS` seulement si preuves graphiques + ressenti utilisateur + données techniques suffisantes ;
- `FAIL` pour problèmes reproduits ;
- `BLOCKED` si accès nécessaire manque ;
- `NOT_TESTED` si pas tenté.
- Dossier de rapport : `docs/A1_RUNTIME_REPORT.md`, avec captures et traces nommées, preuves de licences et scores sur 100.
- **A2 interdit** tant que le contrôleur moto cible n'est pas sélectionné par benchmark et que les droits de ses ressources ne sont pas acquis.

## Alternative de bibliothèque (à investiguer, non approuvée)
`AndyGura/gg-web-engine` code Apache-2.0 : composants Three.js/Rapier et commandes mobiles, mais architecture de jeu/moteur générique, pas un contrôleur de moto validé. Le registre de sources peut l'étudier comme **bibliothèque**, pas comme troisième jeu déjà testé.

**Sécurité des quotas** : priorité aux analyses statiques, aux démos déjà hébergées et aux tests locaux. Zéro GitHub-hosted runner, aucun achat.
