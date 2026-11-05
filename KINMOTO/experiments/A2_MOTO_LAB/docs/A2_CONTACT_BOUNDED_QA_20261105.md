# A2 — Collision S5 / correction plafonnée / laboratoire
Date : 2026-11-05. Base : branche `kinmoto/a2-local-perf-diagnostics-20261105`.

## Défaut A1-D reproduit
État initial artificiel mais possible après import/spawn : centre moto dans une voiture, vitesse 12m/s, premier pas 1/60s. Le moteur précédent corrigeait **toute la profondeur** dans une seule image : ~1,56m de déplacement écran, mais odomètre ~0,20m. L'absence de cohérence peut être perçue comme téléportation.

## Correctif minimal
`src/sim.js` limite chaque résolution de pénétration à `Math.min(contact.overlap,.32)` m par pas fixe ; la séparation restante se résout sur les pas suivants. La correction n'est pas ajoutée à l'odometre et ne fait pas tourner les pneus. `peakContactCorrection` et `contactCorrections` donnent un diagnostic purement interne. La pénalité et le cooldown de 1,3s demeurent inchangés.

## Preuves
- **3 tests nouveaux** `tests/a2_swept_contact_gate.test.mjs` : pas de déplacement >0,55m au premier tick même avec propulsion, résolution progressive de chevauchement et pénalité unique, exclusion de l'odomètre à l'arrêt.
- Suite sur source exactement dérivée du ZIP A1-D : **168/168 tests Node PASS** (165 initiaux +3), Python historique 22/22.
- **Limite** : il ne s'agit pas encore d'un solveur de collision continue ni de swept SAT complet. Le nom du ticket est historique. Test humain à haute vitesse et angle vif requis avant validation subjective A2.
- **Statut** : A2 code-review PASS pour ce bug, **A2 humain / 15min NOT_TESTED**.

Aucun merge main, STABLE, hébergement ou coût. Notre moteur n'est pas officiellement élu par A1-D.
