# KINMOTO A2 LAB 0.5 — audit mécanique et trafic

**Objectif :** réduire le flottement et les comportements de glissement constatés sur les prototypes ; aucune certification subjective.

## Changements
- Route profilée : géométrie et simulation utilisent le même `sampleRoadSurface`.
- Roues avant/arrière : centres placés sur la hauteur de route, malgré amortissement, pitch et lean.
- Châssis : ressort/amortisseur borné avec inertie ; angle de route et couple frein/accélération distincts.
- Trafic : sensing des véhicules proches, freinage, priorités à l'intersection, aucune nouvelle dépendance.

## Vérifications locales
- `npm test` : **46/46 PASS**, y compris 5 tests spécialisés contact-route, 3 interactions de trafic.
- `npm run check` : PASS.
- `python build.py` : PASS, un HTML PWA autonome (environ 79 Ko).
- Simulation 10 min (36 000 pas) : exécution CPU locale avec validation sans NaN. Ce n'est ni FPS GPU ni RAM de navigateur.

## Limites et conditions de sortie
- Sol de référence déterministe + petites bosses : **pas de raycasts Rapier**, suspension simplifiée, pas de relief général.
- Le trafic ne bénéficie pas d'une simulation physique rigide automobile ; priorité et freinage règles.
- Test physique sur vrai Android, 15 min sur HP, ressenti du joueur, comparaison visuelle et chauffe : **NOT_TESTED**.
- L'ancien jeu ne doit pas être remplacé. Toute nouvelle URL demeure un laboratoire isolé.
