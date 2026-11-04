# KIN MOTO — A2 / Conduite moto : cahier technique préliminaire

**Statut : READY_FOR_REVIEW_AFTER_A1_D.** Ceci prépare le développement sans sélectionner prématurément le moteur, importer d'assets ni publier de nouvelle V1.

## 1. Défaut historique à éliminer
Les prototypes précédents donnaient une sensation de glissement sur l'eau, une inversion gauche/droite, des roues déconnectées de la chaussée et des collisions non crédibles. A2 doit valider la sensation physique sur appareil réel, pas simplement le passage de tests unitaires.

## 2. Interface indépendante de la base choisie
**BikeInput :** throttle 0..1, frontBrake 0..1, rearBrake 0..1, steer -1..1.
**BikeTelemetry :** vitesse m/s ; yawRate rad/s ; lean rad ; contact roue avant/arrière ; spin roue avant/arrière ; slip latéral ; impulsion collision ; état des dégâts.
**BikeSimulation :** reset(seed), step(fixedDt, BikeInput), telemetry(), saveState(), restoreState(), dispose().
Définir une convention absolue des axes et du signe de direction. La caméra ne doit pas inverser la commande du pilote. Clavier et tactile passent par le même contrat de conduite.

## 3. Physique à développer ou adapter
- Contact roue/sol robuste : rayon, suspension, position visuelle du châssis et collision indépendantes du compteur de vitesse.
- Accélération progressive : transmettre le couple à la roue motrice, éviter le déplacement latéral forcé.
- Direction amortie : virages lents contrôlables, courbes rapides cohérentes, pas de pivot instantané.
- Inclinaison : liée à l'accélération latérale et à la courbure, cible indicative atan(v²*kappa/g), limité/filtré ; pas d'oscillation purement cosmétique.
- Freinage : vitesse et déplacement réellement réduits, animations de roue et d'assiette crédibles ; test sec versus humide.
- Suspension : bosses, petits chocs, amortissement sans rebond infini, absence de flottement.
- Passager : poids supplémentaire maîtrisé, position visuelle, réponse à l'accélération/freinage.
- Collision : séparation, perte d'énergie, réaction du trafic, dégâts déclenchés une fois par impact.

## 4. Réemploi proposé, non approuvé
**Costa Vista** : étudier vehicleController.ts (ressorts, raycasts, adhérence, Rapier, roll), mais ses quatre points d'appui virtuels stabilisent un deux-roues ; ce n'est pas une simulation complète et doit être testé. Ne pas importer son modèle 3D de moto : son droit asset n'est pas établi par MIT.
**Neon Mayhem** : comparer le modèle cinématique de vehicles.js et l'ergonomie de touch.js ; extraire uniquement les idées/modules après tests car le code dépend de l'objet global GAME.
**Art** : la moto Poly Pizza par AliceCassie (CC0 sur page source https://poly.pizza/m/j20srJUjpB) est candidate pour la géométrie. Fichier exact non acquis ; licence et dimensions à confirmer avant intégration.

## 5. Coûts et temps de calcul
Simulation à pas fixe (cible 60 Hz à valider), rendu indépendant à 24–30 FPS selon mobile ; interpoler les positions, plafonner le temps de rattrapage. Éviter allocations par frame et appels GPU inutiles. Optimisation RAM par répétition des ressources ; pas de fallback 2D qui change les règles de conduite.

## 6. Dix critères de sortie A2
1. Gauche à gauche / droite à droite, avec 3 caméras et commandes clavier/tactile.
2. Contact permanent des roues avec la route sans lévitation inexpliquée.
3. Trajet droit à vitesse progressive, accélération crédible.
4. Slalom de 6 plots sans oscillations ou patinage continu.
5. Freinage depuis 50 km/h avec arrêt réellement mesuré.
6. Virages lents/rapides, inclinaison stable et proportionnelle.
7. Bosse/chaussée irrégulière : suspension et roue/sol crédibles.
8. Choc voiture : séparation, dégâts, freinage, aucune collision fantôme.
9. Cinématique indépendante des FPS, comparaison 30/60.
10. Essai de 15 minutes sur HP et Android modeste : sensation jugée satisfaisante par le joueur.

**Stop :** ne pas commencer les modifications A2 avant la conclusion du benchmark A1-D et la vérification des licences. Ne toucher à aucune URL STABLE.
