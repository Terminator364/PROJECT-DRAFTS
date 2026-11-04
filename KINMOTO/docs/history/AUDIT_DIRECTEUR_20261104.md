# KIN MOTO — AUDIT DIRECTEUR, FEASIBILITY ET PRODUCTION EN TROIS VERSIONS

**Édition :** 2.0 — 4 novembre 2026  
**Statut :** préproduction validable ; **aucun code du jeu en production modifié**.  
**Commanditaire :** utilisateur ; **développeur principal prévu :** ChatGPT avec outils locaux, Git et outils de déploiement accessibles.  
**Budget d'argent neuf :** 0 franc congolais obligatoire (abonnement Plus existant exclu des nouvelles dépenses ; Internet et électricité ne sont pas réellement gratuits).  
**Cibles obligatoires :** navigateur Android, navigateur iPhone, navigateur PC ; même code source et mêmes règles de jeu ; profil graphique adapté.

> **Règle supérieure :** trois versions majeures — **V1 jouable**, **V2 enrichie**, **V3 ambitieuse**. Les correctifs critiques peuvent exister comme patchs, mais ne deviennent pas de nouvelles versions de contenu. La série de prototypes précédente (V2 envoyée à la testeuse et v0.4 expérimentale) n'est pas cette nouvelle série.

## 1. Verdict stratégique

Le concept est faisable comme jeu web statique hors ligne après mise en cache, **à condition** de réduire le monde chargé et la complexité de simulation visible simultanément. Il n'est pas raisonnable de promettre sur les matériels modestes : photoréalisme, milliers d'agents 3D actifs, 60 FPS garantis, exactitude cadastrale de Kinshasa et IA générative locale sophistiquée. Les mêmes sensations fondamentales doivent exister sur chaque appareil ; la **distance visuelle**, le **niveau des textures**, les **effets** peuvent varier, pas les règles de conduite, collisions ou le résultat des missions.

Les objectifs de performance, de taille et de mémoire ci-dessous sont des **hypothèses conditionnelles**, non des résultats déjà mesurés. Un iPhone réel devra confirmer la compatibilité ; une simulation « iPhone » ne suffit pas.

## 2. Preuves auditées, ce que nous savons réellement

1. Fichier du prototype v0.4 : `KIN_MOTO_V04_JOUER.html`, environ **649 lignes** HTML/CSS/JS. Gameplay, collision, rendu et persistance encore largement dans un même fichier. Route surtout rectiligne et trafic initial de **24 voitures** ; pas de véritable graphe urbain.
2. Rapport `KIN_MOTO_V04_PACKAGE/RESULTATS_TESTS.json` : **42 contrôles réussis**. Point essentiel : la propriété `graphical mode initialized` des profils `android_mobile`, `iphone_simulated` et `desktop` vaut dans les trois cas **`2d`**. Les essais ont validé des règles de logique et le mode de secours, **pas le rendu 3D réel sur ces appareils**.
3. Les captures envoyées par l'utilisateur révèlent une dégradation qualitative dans un profil graphique par rapport à la meilleure référence. « Fonctionne » ne signifie donc pas « acceptable visuellement ».
4. L'ancien code effectue des comparaisons entre véhicules dans des boucles imbriquées ; le coût peut croître comme O(N²). À 24 véhicules, au plus 552 paires ordonnées ; à 120, 14 280 ; à 1 000, 999 000. À remplacer à grande échelle par une grille spatiale et un trafic limité en agents actifs.
5. Le meilleur rendu précédent et les commandes valides constituent des références **de qualité**, pas des preuves que le code actuel doit être conservé tel quel.
6. L'iPhone de la testeuse n'a pas encore de fiche matérielle complète, et son comportement GPU réel n'a pas été vérifié par une instrumentation native. Ne pas lui attribuer une mémoire ou une performance supposée.

### Corrections d'exigences

| Ancienne formulation | Problème | Nouvelle formulation | 
|---|---|---|
| « 200 Mio de RAM et 60 FPS » | Mémoire Safari/WebGL difficile à mesurer et niveau irréaliste sur bas de gamme | Profilage par postes, FPS minimum pratique 24–30 selon appareil ; 60 FPS seulement si marge |
| « Toute la ville et milliers de voitures » | Incompatibilité avec la performance et le temps de production | V1 micro-zone cohérente ; V2 quelques zones ; V3 macroflux + objets détaillés proches |
| « IA intelligente » | Terme vague | Automates, graphes, heuristiques, règles de priorité, comportements mesurés |
| « Reproduction exacte de Kinshasa » | Données et travail artistique disproportionnés | Localités identifiables et stylisation explicite ; fidélité augmentée par itérations |
| « Même densité graphique partout » | Inefficace matériellement | Même mécanique/données proche du joueur, LOD visuel et far-traffic statistique |
| « 1000 tests réussis » | Nombre sans pertinence si rendus absents des tests | Matrice 4 certifications : logique, vrai rendu 3D, performances, matériel réel |
| « Version = toute nouvelle idée » | Dérive et régressions | Contrat de contenu fermé pour V1 ; modifications de scope uniquement par arbitrage explicite |

## 3. Contrainte financière et implications

**Zéro nouvelle dépense obligatoire** : code libre, assets originaux/CC0 ou licences compatibles, hébergement statique à offre gratuite, dépôt Git gratuit, pas de base de données serveur, API commerciale, abonnement cloud, Apple Developer Program, Play Store ou compte joueur payant. La disponibilité future des offres gratuites n'est pas garantie. Conserver le code et un build exportable ; ne pas s'enfermer dans Vercel/Cloudflare.

**Attention juridique** : Vercel Hobby est réservé aux usages non commerciaux selon ses conditions ; avant une commercialisation éventuelle, vérifier un hébergeur compatible. Cloudflare Pages Free publie des sites statiques et prévoit des limites de build/fichier ; la compatibilité finale reste soumise à ses conditions. Les musiques non libres, enseignes protégées et assets non autorisés sont exclus. OSM : données sous ODbL, attribution et obligations afférentes si utilisées.

**Plus** : l'abonnement ChatGPT Plus existant facilite la conception/code, et Codex y est accessible sous limites d'usage ; il ne fournit pas un serveur gratuit illimité ni un processus autonome permanent entre les conversations. Écrire des livrables traçables à chaque session est impératif.

## 4. Produit défini, sans surcharge

**Genre :** simulation arcade/semi-réaliste de moto-taxi à Kinshasa. **Promesse joueur :** « Je conduis une moto, j'effectue de vraies courses dans une ville vivante et je progresse. »

**Boucle courte :** choix mission → trajet vers client → prise en charge → navigation vers destination → interactions avec circulation → livraison → paiement → réparation/amélioration → nouvelle course.

**Le plaisir décisif** : diriger naturellement une moto, lire la route, éviter et anticiper les voitures, accomplir des missions variées ; pas une barre de progression automatique.

**Identité locale :** taxis, mini-bus, moto-taxis, marché, kiosques, parcelles, panneaux et commerces fictifs, sons et couleurs inspirés de Kinshasa. Éviter une caricature de pauvreté, de violence ou d'indiscipline. Des références visuelles crédibles valent mieux qu'une infinité de bâtiments génériques.

## 5. Grille de la décision en trois versions

| Domaine | V1 — Les premières courses | V2 — Kinshasa vivante | V3 — Ville et carrière |
|---|---|---|---|
| Géographie | Une micro-zone stylisée de Kinshasa, plusieurs rues reliées, 6–8 intersections | 2–3 zones connectées ou sélectionnables et plus de repères | Plusieurs secteurs, streaming et densités différenciées |
| Véhicules | Une moto principale, trois familles de voitures visibles, trafic régulé | Motos concurrentes, minibus, intersections riches, comportement contextuel | Flotte urbaine macro-simulée, plus de diversité |
| Conduite | Arcade semi-réaliste, accélération/freinage/virage, caméra stable | Usure plus profonde, surface humide, comportement avancé | Personnalisation des styles et perfectionnement physiques selon tests |
| Collisions | Choc, freinage, dégâts et séparation, pas de téléportation visible | Réactions IA, collisions différenciées, route humide | Propagation dans le trafic et situations émergentes |
| Missions | 4 familles, 6–8 destinations, 1 tutoriel | Multi-arrêts, livraison, météo, personnages récurrents | Contrats complexes, activités et événements reliés |
| Économie | Paiement, coût réparation, 2 améliorations | Entretien, réputation, plus de garage | Carrière approfondie, petite flotte hors ligne |
| Environnement | Cycle visuel simple, quartier vivant mais statique par endroit | Pluie et densité horaire simulées | Événements interconnectés et nouveaux types d'activités |
| Narration | Dialogues courts, 2–3 personnages d'identité | Relations récurrentes et mini-arcs | Arcs plus développés et radios originales |
| Technique | PWA statique, offline, export sauvegarde, 3D de base | Chargement différé, optimisation LOD, transitions | Simulation multiniveau, streaming élargi, optimisation continue |
| Fonctionnalités exclues | Multiplayer, serveur, IA générative, monde immense, combat armé, foule simulée | Serveur permanent, centaines de quêtes uniques, photoréalisme | Même exclusions si coût ou incompatibilité |

Le mode de jeu unique V1 est la **carrière** ; la **conduite libre** est un accès à la même carte, pas un moteur de jeu distinct. La météo dynamique, les centaines d'objets et les systèmes d'entreprise sont reportés. Les « combats », poursuites et chasse ne sont pas le cœur du jeu ; des défis de suivi ou d'évitement non violents pourront être évalués en V3.

## 6. Contrat précis de V1 : ce que nous allons effectivement fabriquer

### 6.1 Zone
- **Quartier composite stylisé inspiré de Victoire/Matonge**, avec dénomination honnête « inspiré de » ; pas de promesse de fidélité cadastrale.
- **Enveloppe de conception initiale :** environ 400 × 400 à 600 × 500 mètres à confirmer selon rendu ; **6–8 intersections**, routes bifurquées, boucles et sens de circulation définis. Cette plage est une décision de cadrage, pas une mesure GPS.
- **6–8 destinations** : marché, école, garage, arrêt, restaurant fictif, quartier résidentiel, petit bureau, station-service fictive. Chacune dispose d'un marqueur de prise en charge, d'une zone d'arrêt et d'un chemin accessible.
- **Décor** : 10–15 modèles de bâtiments modulaires, 5–8 éléments urbains réutilisés, 1–2 atlas partagés, végétation par instances. Seulement quelques personnages visibles près des points d'intérêt, pas de foules navigantes.

### 6.2 Pilotage
- Une moto principale avec accélérateur, frein, direction graduelle, marche lente, arrêt, inclinaison cosmétique cohérente et résistance aux changements brusques. Limiter le risque de perte de contrôle involontaire en mode arcade.
- Caméra principale derrière le conducteur, décalage minimal. Une seconde distance de caméra peut exister si elle n'allonge pas excessivement les tests. Pas de caméra cockpit obligatoire en V1.
- **Invariance d'entrée** : flèche gauche = déplacement visuel gauche dans la caméra principale ; droite = droite ; gaz + direction simultanés sur tactile ; clavier flèches, WASD et ZQSD selon mapping, au besoin personnalisable.
- Timestep de simulation fixe, rendu interpolé, compteur de vitesse indépendant de FPS. Après mise en arrière-plan, pas de « bond » physique au retour.

### 6.3 Trafic et accidents
- **Initial :** 8–16 véhicules actifs autour du joueur, chiffre soumis à benchmark. Trois types : voiture particulière, taxi, minibus ; variations de couleurs.
- Voitures sur le graphe routier, freinent si obstacle, s'arrêtent aux carrefours selon règles simplifiées, ne changent pas soudainement de position à proximité visible.
- Collisions entre moto et véhicules : distance/volume adapté, résolution de pénétration, impulsion simplifiée, perte de vitesse et dommages ; délai anti-répétition après choc ; pas de chute longue en animation V1.
- Les piétons sont avant tout des décors animés ou des passagers immobiles au point de prise en charge ; évitement et simulation de foule reportés.

### 6.4 Missions et progression
- Quatre familles : (1) course normale, (2) transport pressé mais sécurisé, (3) petite livraison, (4) trajet avec contrainte de confort. **Pas quatre moteurs différents** : une seule machine à états de mission avec paramètres.
- Tutoriel guidé ; au moins 6–8 clients/destinations combinables, dont 2–3 personnages mémorables ; dialogues courts affichés, audio vocal non obligatoire.
- Récompenses en FC fictifs équilibrés : base + distance + qualité plafonnée ; pas de prime incitant à conduite dangereuse. Une course doit être annulable et récupérable après pause.
- Garage V1 : réparation, 2 améliorations simples (freinage/accélération ou maniabilité), solde persistant, coût cohérent. Pas d'inventaire de centaines de pièces.

### 6.5 Visuel et son
- Même **vraie scène 3D** à trois niveaux de qualité. Eco baisse résolution interne, portée, ombres/particules, jamais l'orientation, l'identité des lieux ou les interactions.
- Modèles low-poly soignés, silhouettes lisibles, quelques points de repère locaux, motos et véhicules clairement reconnaissables. Pas de moteur photo-réaliste ni d'ombres dynamiques nombreuses.
- Audio minimal original/CC0 : moteur, frein/choc, klaxon, validation mission et ambiance limitée. Démarrage audio sur geste utilisateur pour respecter iOS.
- Interface adaptable aux safe areas iPhone, visibilité des commandes, mode pause, volume et qualité ; HUD non intrusif.

### 6.6 Sauvegarde et hébergement
- HTTPS, manifest, service worker statique, cache du shell et du pack V1 essentiel, message « disponible hors connexion » seulement après vérification effective. iOS peut évincer les données : exporter/importer la sauvegarde.
- IndexedDB pour la progression locale ; version de schéma et migration. Un navigateur/appareil distinct ne synchronise pas automatiquement avec les autres sans serveur ; import/export de fichier JSON.
- Garder l'ancienne démo sur l'URL actuelle pendant le développement. Déployer V1 sur une URL de test, remplacer le lien public seulement après validation de l'utilisateur.

### 6.7 Expérience de référence V1 (simulation d'une session)
1. Lancement via lien HTTPS dans Chrome Android, Safari/Chrome iPhone, Opera/Chrome PC ; sélection automatique du profil prudent, option d'ajustement manuel.
2. Menu lisible → tutoriel commande gauche/droite, frein, gaz en moins de deux minutes de jeu.
3. Joueur démarre au garage, voit un véhicule passer, roule jusqu'au point de prise en charge.
4. Une voiture ralentit au carrefour : le joueur freine et passe ensuite. S'il la touche, le choc ralentit la moto et réduit son état de santé.
5. Client monte ; la navigation indique une destination différente, accessible par au moins deux chemins.
6. Le joueur arrive, ralentit et dépose. L'argent augmente une seule fois, la mission passe à l'état « terminée ».
7. Passage au garage : réparation, achat d'une amélioration ; nouveau solde correctement calculé.
8. Fermeture de l'onglet, réouverture : la progression et les achats restent cohérents ; s'il a activé le mode hors ligne, le jeu reste accessible sans réseau après préchargement.
9. Export de sauvegarde et import sur un autre appareil (transfert manuel) : progression identique.

Si l'une des étapes échoue, V1 ne peut pas être déclarée livrée.

## 7. Architecture recommandée V1 (sans sur-ingénierie)

**Stack conditionnelle :** TypeScript + Vite + Three.js WebGL2 + HTML/CSS HUD + IndexedDB + service worker + tests Node/Playwright. Versions de dépendances figées au début. **WebGL2 obligatoire pour les versions récentes de Three.js** ; ne pas tenter de garantir les appareils sans WebGL2 avec un simple changement de user-agent. Afficher un diagnostic explicite si indisponible, envisager une solution de compatibilité séparée seulement si les tests montrent un besoin réel.

**Pourquoi ne pas recréer 20 moteurs internes ?** V1 a besoin de modules fonctionnels testables, mais pas nécessairement de dizaines de packages. Cinq ensembles suffisent au départ :
1. `core/` : temps fixe, PRNG seed, état et events ;
2. `sim/` : moto, graphe, trafic, collision, missions, économie ;
3. `view/` : scène Three.js, géométrie, caméra, UI, son ;
4. `data/` : carte, mission templates, paramètres ;
5. `platform/` + `tests/` : input, stockage, PWA, diagnostic, QA.

**Invariants d'architecture :**
- La simulation ne dépend pas des objets Three.js.
- Le rendu lit l'état de simulation et n'effectue aucun calcul économique.
- `steer=-1` correspond à gauche dans le repère joueur ; test supplémentaire de sens à l'écran après transformation caméra.
- La mise à jour `updateFixed(dt)` ne dépend pas du temps d'image.
- Trafic et collisions sont déterministes à seed/inputs identiques dans les tests.
- Un agent proche est unique ; sa représentation graphique peut changer de LOD sans changer ses collisions.
- Aucun créateur de voitures ou de textures dans la boucle par image, réutiliser buffers et pools.
- Pas de `localStorage` comme unique lieu de sauvegarde critique.
- Aucune API payante ni clé d'API dans le client.

**Algorithmique V1 :** moto en modèle cinématique simplifié ; grille spatiale élémentaire pour voisins ; freinage sur distance et time-to-collision ; A* sur petit graphe de rues ; volumes simples pour collision. Pas de moteur de rigid bodies complet ni de pathfinding général pour toutes les personnes.

## 8. Budget de performance : devis de ressources, pas déclaration de réussite

**Cible A21s (Eco)** : 24 FPS pratiques comme seuil minimal provisoire ; objectif 30 FPS soutenus dans une scène V1 représentative. **HP et Android puissant** : 30 FPS ou mieux. **iPhone** : niveau fixé après test réel, sans présupposer son modèle. 60 FPS = bonus des appareils suffisamment puissants.

**Hypothèses de chargement V1 :** première charge compressée ~3–12 Mio ciblés ; pack de base complet et hors-ligne idéalement sous 20 Mio. Ce n'est pas un seuil garanti, à mesurer après production des assets. Aucun seul asset ne doit dépasser la limite du fournisseur choisi.

**Comptabilité mémoire** : enregistrer nombre de textures, dimensions, taille CPU des buffers, mesh count, draw calls, JS heap lorsque mesurable et RSS navigateur par outils externes. La mémoire GPU exacte est rarement observable de façon portable ; la mesurer par approximation et les outils locaux, pas par un chiffre JavaScript fictif. Une texture RGBA 1024² non compressée utilise 4 Mio avant mipmaps (~5,3 Mio avec chaîne complète), alors que 2048² utilise 16 Mio avant mipmaps. Stockage disque compressé et mémoire GPU sont des métriques différentes.

**Budget provisoire rendu économique V1** (à réviser dès les benchmarks) : 8–16 véhicules actifs ; 6–8 carrefours ; une à deux textures atlas 1024 ; affichage initial de 80–150 mètres ; résolution 3D interne adaptative, d'abord 0,65–0,85 de la résolution du canvas CSS × pixel ratio plafonné ; 30 FPS si matériel le permet. Les budgets ne peuvent jamais être augmentés pour passer un test sans afficher le nouveau coût.

**Mesures V1** : distribution du temps entre `update`, `render`, `UI` ; FPS médian + p95 frame time ; mémoire du processus sur PC ; monitoring externe Android/iOS si disponible ; absence de tendance mémoire croissante anormale sur 20 minutes ; latence de démarrage ; volume téléchargé. Un benchmark sans vrai rendu 3D est invalidé.

**Optimisations** : InstancedMesh, atlases, réutilisation de géométrie, chargement différé, textures raisonnables, réutilisation des arrays, brouillard pour masquer distance, style low-poly, pause sur arrière-plan. V2 introduit du streaming réel après que V1 ait prouvé la qualité de base.

## 9. Simulation de construction V1, du début à la sortie

**Cycle 0 — Conservation** : sauvegarder archives et captures du jeu V2, v0.4 ; enregistrer dix images d'une scène de référence, les commandes et les bugs connus. Pas de modification de la version partagée.

**Cycle 1 — Banc matériel** : micro-scène 3D web de 10 objets + compteur FPS + diagnostic WebGL2 sur HP, Android, iPhone ; vérifier la vraie 3D, la réaction au tactile, la latence et le comportement après perte d'onglet. *Décision technique avant grande modélisation*.

**Cycle 2 — Dépôt de développement** : squelette TS, build Vite, modules, tests, versionnement, pipeline de preview. Construire une page ouverte sur les trois plateformes sans jeu.

**Cycle 3 — Moto seule** : circuit de base ; gaz, frein, direction, joystick/boutons ; vérifier position et orientation à chaque tick. Test sur 30/60/120 FPS simulés pour égalité des distances à delta identique.

**Cycle 4 — Caméra et écran** : moto 3D détaillée proportionnellement, vue arrière, HUD minimal. Tests direction visuelle gauche et droite avec caméras différentes ; pas de renversement.

**Cycle 5 — Carte compacte** : route et intersections ; véhicule suit le graphe ; navigation A* ; collision avec trottoir. Ne pas décorater avant la stabilité de la géométrie.

**Cycle 6 — Trafic de base** : génération de véhicules, stops/ralentissements, trajectoires, suppression hors champ, pooling et barrières pour ne pas téléporter devant la caméra.

**Cycle 7 — Collisions** : choc moto-car, dégât et vitesse réduite ; test sans répétition/collision fantôme ; non-pénétration ; pas de variation quand FPS baisse.

**Cycle 8 — Direction artistique** : ajouter parcelles et lieux, véhicules distincts, végétation, couleurs, textures ; même scene de comparaison et revue explicite par rapport au meilleur prototype.

**Cycle 9 — Passagers et missions** : états `available→to_pickup→boarding→to_dropoff→completed/failed` ; quatre templates, données de carte, validation des destinations ; pas de paiement double.

**Cycle 10 — Garage** : argent, réparations, deux améliorations, équilibrage simple ; test de progression sur plusieurs courses et achats.

**Cycle 11 — Sauvegarde** : snapshot local transactionnel, export/import, redémarrage en mission, changement de version de schéma.

**Cycle 12 — Hors ligne** : distribution statique HTTPS, installation PWA quand prise en charge, téléchargement complet vérifié, service worker, mode avion, update après mission, récupération après stockage effacé via export.

**Cycle 13 — Finissions** : sons basiques, confort des commandes, interface safe-area, guide de démarrage, messages d'erreur utiles.

**Cycle 14 — Épreuve de vérité** : quinze à vingt minutes de gameplay sur chaque classe d'appareil réel, défauts et performance enregistrés. Toute dégradation visuelle non approuvée = refus de release.

**Cycle 15 — Publication** : signer version V1, ZIP/source, date, manifest checksums, notes de version, URL stable, archivage. Pas de remplacement du lien actuel si le gate est refusé.

> **Ordre impératif :** ne pas générer des kilomètres de carte avant le test de moteur ; ne pas produire des centaines de personnages avant la première mission terminée ; ne pas publier en partant d'un test uniquement en fallback 2D.

## 10. Injections de pannes : simulation des situations critiques

| Événement | Comportement attendu | Test de refus |
|---|---|---|
| Direction semble inversée | Conversion claire du repère joueur au repère écran ; test visuel de mouvement | 10 pressions gauche/droite par caméra ; tout échec bloque |
| Chute de FPS 60→20 | Moto parcourt la même distance pour le même temps de simulation ; rendu ralenti mais pas physique | Replay seedée à FPS différents |
| Voiture bloque carrefour | Freinage/arrêt ; itinéraire d'agent valide ; pas de véhicule qui apparaît au milieu | Scénario trafic saturé pendant 3 min |
| Gros choc répété | Une réponse de collision et cooldown, dommages plafonnés, pas de téléportation | Impact suivi de 10 frames de contact |
| iOS ouvre fichier HTML local | Le jeu distribué par HTTPS, non par aperçu de pièce jointe | Ouvrir URL dans Safari et Chrome iOS |
| WebGL2 absent/perdu | Message précis, essai de récupération; pas de fallback 2D silencieux comme faux succès | Désactivation GPU / perte de contexte simulée |
| Onglet suspendu 5 minutes | Pause et horloge remise en état au retour ; pas de saut de moto | `visibilitychange` puis reprise |
| Réseau coupé | Si les assets sont mis en cache, démarrage et missions sans requêtes externes | Mode avion après confirmation cache |
| Cache effacé | Explication et re-téléchargement nécessaire ; sauvegarde récupérable si exportée | Suppression données site, import JSON |
| Mise à jour au milieu d'une course | Le jeu reste sur ancienne version jusqu'à mission terminée ; sauvegarde compatible | Swap service-worker simulé |
| Smartphone chauffe | Réduire résolution et distance graphique, pas les règles de simulation | Profil basse consommation, longue session |
| Changement PC→Android | Export/import manuel car absence de serveur | Même solde/missions après import |
| Modèle 3D trop lourd | Remplacement par LOD ou instancing, avant sacrifice de conduite | Test frame-time + compteurs draw calls |
| Source externe disparaît | Build reproductible avec dépendances verrouillées et assets détenus/licenciés | Build à partir du dépôt + lockfile sans URL dynamique |

## 11. Gouvernance IA : maîtriser le développement entre conversations

### Références canoniques
- **Repo Git** du projet source avec `/docs/DECISIONS.md`, `/docs/MASTER_PLAN.md`, `/docs/ACCEPTANCE_V1.md`, `/docs/CHANGELOG.md`, `/docs/KNOWN_ISSUES.md`, `/qa/results/`.
- Versions immuables (tags `legacy-v2-reference`, `legacy-v04-lab`, `v1.0.0`, `v2.0.0`, `v3.0.0`), pas de remplacement invisible ; sauvegardes de sécurité.
- Un **cahier mère** d'une page à chaque fin de session : état du dépôt, dernier build, modules acceptés, tests passés/non faits, risque ouvert, prochaine tâche exacte.
- Chaque nouvelle conversation reprend le dépôt et son état ; n'accorde pas à la mémoire conversationnelle le statut de preuve de compilations ou tests.

### Règle d'autonomie
ChatGPT peut concevoir, coder, tester dans les environnements auxquels il a effectivement accès, rédiger, préparer les branches et demander les essais matériels utiles. Il ne doit pas prétendre tester physiquement un iPhone si seul un navigateur émulé a été utilisé, ni promettre un développement autonome illimité entre les conversations.

### Définition de terminé (DoD) pour toute fonctionnalité
Code modulaire, lint/compilation, tests unitaires pertinents, integration, comparaison de visuel si elle influence le rendu, mesure de performance si elle influence boucle/rendu, documentation de changement, sauvegarde persistante si format modifié, et absence de régression majeure. Si élément manquant : **en attente**, jamais « fini ».

### Politique de publication
Canal **DEV** → **PREVIEW** → **STABLE** ; la V2 déjà envoyée reste intacte comme référence. Pas de mise à jour publique quotidienne ; seulement V1/V2/V3, à l'exception de correctifs critiques approuvés. La publication en stable nécessite un résultat de QA et l'approbation de l'utilisateur.

## 12. Critères d'acceptation de la V1 : 20 portes objectivables

1. V1 s'ouvre par URL HTTPS depuis Android, iPhone et PC réels, sur navigateurs compatibles connus.
2. Sur chaque appareil, **vraie 3D** observée (preuve d'une image, diagnostic WebGL2, pas de mode 2D).
3. Aucun bouton essentiel hors écran, y compris zones safe-area iPhone.
4. Gauche/droite cohérents à l'écran à au moins 10 pressions successives dans chaque sens.
5. Gaz simultané avec direction et frein fonctionnant en multitouch.
6. Vitesse et position cohérentes à FPS variables.
7. Moto n'avance pas toute seule après perte de focus.
8. Au moins 6 intersections et 2 itinéraires alternatifs entre certaines destinations.
9. Aucune mission ne place une destination inaccessible dans le graphe.
10. Les voitures gardent la bonne voie et freinent devant un obstacle.
11. Un choc réduit la vitesse et cause un dommage unique contrôlé.
12. Pas de véhicule qui apparaît brusquement devant le joueur.
13. Au moins 4 familles de missions jouables, non uniquement affichées.
14. La prise en charge et la dépose modifient correctement l'état de mission.
15. L'argent est crédité une fois et les achats de garage sont déduits exactement.
16. La sauvegarde persiste après fermeture et réouverture.
17. Export/import de sauvegarde vérifié sur deux appareils.
18. Jeu offline après mise en cache complète, confirmé par test en mode avion.
19. Session de 15–20 minutes sans crash ; FPS/mémoire réels mesurés et consignés.
20. Comparaison visuelle de scènes de référence : pas de régression non approuvée.

**Important** : les résultats sont `PASS`, `FAIL`, `BLOCKED`, `NOT_TESTED`, jamais une réussite inventée. En cas de matériel inaccessible : « V1 non certifiée sur cette cible » jusqu'au vrai essai.

## 13. V2 — cahier d'extension, verrouillé après la V1

- Intégration de deux nouveaux secteurs de ville ou de deux quartiers virtuels connectés ; transitions douces et carte enrichie.
- IA trafic : minibus qui s'arrêtent à certains points, taxis qui ralentissent, changements de voie contrôlés, priorité d'intersection ; densité conditionnée par horaires simulés.
- Météo pluie réduisant grip/visibilité et introduisant des itinéraires difficiles, sans prétention de données temps réel.
- Missions multi-arrêts, livraisons fragiles, contraintes d'horaire et profils clients.
- Relations simples avec des passagers récurrents et réputation différenciée ; plus de vocabulaire français/lingala relu.
- Garage avec état des composants simplifié et budgets de réparation ; achats uniquement avec monnaie fictive de jeu.
- Streaming des secteurs et variations visuelles permettant d'étendre la carte sans mémoire proportionnelle.
- Critère de sortie : V1 fonctionne toujours ; nouvelles zones jouables en 3D sur tous les appareils compatibles ; zéro perte de progression, tests de ressources et 30 minutes de jeu par plateforme.

## 14. V3 — cahier d'ambition, avec limites explicites

- Plusieurs zones de Kinshasa reliées par itinéraires avec streaming ; nombre de secteurs décidé par performance/rendu, non par une promesse arbitraire.
- Trafic multiniveau : agents proches précis, flux agrégés éloignés ; éviter milliers d'agents 3D actifs.
- Événements émergents : pluie + chantier + déplacement d'un client + panne = alternatives rationnelles ; système contrôlé pour éviter missions impossibles.
- Carrière : réputation, contrats, développement de micro-entreprise et petite flotte simulée localement.
- Narration : scénarios, voix facultatives originales, univers culturels et diversité des quartiers.
- Nouvelles activités non obligatoires : défis de maîtrise, transport spécialisé, progression de personnage, parcours d'exploration.
- La V3 ne signifie pas « jeu AAA » : pas de promesse de rendu 4K, de multijoueur massif, de simulation de tout Kinshasa, ni de milliers de collisions calculées à chaque frame.
- Critère de sortie : stabilité multi-plateformes, framerate réellement mesuré, hors-ligne, 0 dépense neuve obligatoire, compatibilité des sauvegardes et identité de ville convaincante.

## 15. Matrice des risques et décisions de réduction

| Risque | Gravité | Probabilité initiale | Réduction | Action si échec |
|---|---|---|---|---|
| WebGL2 indisponible/instable sur iPhone ciblé | Critique | Indéterminée sans modèle réel | Prototype de rendu à faire d'abord | Ne pas déclarer compatible ; explorer autre renderer ou support ciblé |
| Rendu dégradé pour gagner FPS | Haute | Forte si optimisation tardive | Profil graphique dès prototype + comparaisons référence | Refuser release ; diminuer ombres/résolution, pas identité |
| Temps de création des assets sous-estimé | Haute | Haute | Kits modulaires + procedural + modèles libres audités | Réduire variété visible, pas cohérence de scène |
| Scope V1 devenu énorme | Critique | Haute | V1 limité par contrat ; backlog futures versions | Reporter nouveauté V2, garder V1 jouable |
| Simulations de tests faussement rassurantes | Critique | Constatée dans v0.4 | Distinguer QA logique/rendu/physique/performance | Résultat NON CERTIFIÉ, pas annonce de succès |
| Panne de stockage/cache sur iOS | Haute | Variable | Offline verified, sauvegarde exportable | Réinstaller cache et restaurer fichier exporté |
| Performances faibles Galaxy A21s | Haute | À mesurer | Dynamic resolution, culling, instancing, densité active bornée | Profil Eco; si encore insuffisant, réduire taille scène en accord utilisateur |
| AI perd le contexte entre conversations | Haute | Forte sans dépôt | Git source de vérité + résumés de session | Reprise depuis dernier tag et état QA |
| Gratuité/fair use hébergeur change | Moyenne | Variable | Serveur statique découplé, export | Migration hébergement statique alternatif |
| Assets ou données sous licence incompatible | Haute | Variable | Catalogue licences + créations propres | Remplacer l'asset, bloquer release publique |

## 16. Audit des dépendances et estimation de complexité relative

Un backlog de **35 unités** est fourni dans le fichier JSON compagnon. Il contient pour chaque unité : version, nom, dépendances, estimation de complexité **relative** et critère de sortie. Un contrôle automatique a vérifié l'absence de cycle et interdit toute dépendance de V1 vers V2/V3.

- V1 : **19 chantiers**, **104 points relatifs** ; comprend la plupart des fondations techniques.
- V2 : **9 chantiers**, **74 points relatifs** ; ajoute systèmes et zones.
- V3 : **7 chantiers**, **80 points relatifs** ; plus petit nombre de chantiers mais systèmes plus profonds.
- Ces points ne correspondent pas à des heures, à des jours ou à des coûts financiers. Ils mesurent uniquement la **complexité de réalisation comparative**. Une tâche peut être subdivisée en plusieurs conversations de code et QA.

La chaîne de dépendances la plus sensible avant sortie V1 concerne la fondation → la physique → le trafic → les collisions → les missions → la sauvegarde → le hors-ligne → les tests matériels → la publication. Le développement graphique et de la carte peut avancer en parallèle mais ne peut être accepté sans liaison stable avec la simulation.

**Avertissement d'organisation :** V1 concentre environ 40 % des points totaux. Cela prouve qu'une V1 de qualité n'est pas « deux heures de décoration » ; le bon arbitrage est d'éviter la grande carte et la multitude de missions, sans retirer les fondations qui éviteraient de tout refaire dans V2.

## 17. Les décisions fermes et les inconnues suivies

### Fermes
1. Trois grandes versions V1/V2/V3 ; publication incrémentale contrôlée.
2. Zéro dépense additionnelle obligatoire, pas d'API facturée, pas de serveur temps réel.
3. Une web app/PWA statique, un seul code commun, vraie 3D si compatible ; accès HTTPS pour iPhone.
4. Développement par ChatGPT sur modules testables, dépôt et cahier mère comme sources de vérité.
5. V1 limitée à une zone, 8–16 voitures environ, 4 familles de missions, progression/garage élémentaires.
6. Les 42 tests de v0.4 ne certifient pas le rendu WebGL 3D ; ne pas les réutiliser comme preuve de compatibilité.

### À déterminer par mesure, sans bloquer le cadrage
- Modèle exact et version iOS de l'iPhone ; capacités WebGL2 physiques.
- FPS/temps de chargement/consommation mémoire observés sur A21s, PC et iPhone.
- Localisation exacte du premier quartier composite et son niveau de fidélité graphique souhaité.
- Possibilité de produire rapidement les assets nécessaires sous licences propres.
- Limites effectives de l'hébergement choisi à l'heure de publication.

## 18. Protocole d'entrée en production V1

**Code de reprise recommandé :** `KINMOTO|V1|GO`.

Quand l'utilisateur autorise la programmation, ne pas commencer par une ville énorme. Commencer par : (1) archivage et base Git ; (2) banc d'essai WebGL2 sur vrai matériel ; (3) squelette TypeScript / Vite / Three.js ; (4) petite scène 3D + moto + direction ; (5) preuve de performance et comparaison à la référence. Une fois ce socle accepté, ajouter carte, circulation, collisions, missions, économie et PWA selon les dépendances. À chaque session : travail fini et résultats vérifiables, pas d'annonce de travail futur exécuté en arrière-plan.

**Aucune publication de V1 ni remplacement de la version existante n'est autorisé par ce document seul.**

## 19. Sources de vérification

- MDN, WebGL best practices : https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices
- Three.js WebGLRenderer (WebGL2, WebGL1 non pris en charge depuis r163) : https://threejs.org/docs/pages/WebGLRenderer
- Three.js InstancedMesh : https://threejs.org/docs/pages/InstancedMesh.html
- Vite, support navigateurs/targets : https://vite.dev/guide/build
- Playwright, nature de l'émulation : https://playwright.dev/docs/emulation
- MDN, quotas stockage/éviction : https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria
- WebKit storage policy : https://webkit.org/blog/14403/updates-to-storage-policy/
- Cloudflare Pages pricing : https://developers.cloudflare.com/pages/functions/pricing/
- Cloudflare Pages limits : https://developers.cloudflare.com/pages/platform/limits/
- OpenAI Codex et ChatGPT plans : https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan
- OpenStreetMap copyright / ODbL : https://www.openstreetmap.org/copyright

---
**Conclusion :** construire d'abord un petit jeu 3D cohérent et agréable, avec missions réelles, circulation et persistance, puis étendre son univers. Ne pas promettre des performances non testées ni utiliser l'émulation iPhone comme certificat matériel. Le projet peut rester à zéro coût obligatoire, mais son temps de production et ses limites matérielles doivent rester explicitement mesurés et gouvernés.
