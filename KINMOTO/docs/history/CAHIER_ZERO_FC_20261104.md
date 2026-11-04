# KIN MOTO — CAHIER DIRECTEUR ZERO FRANC — VERSION CONCEPTION 1.0
Date : 4 novembre 2026
Statut : PLAN UNIQUEMENT. Aucune modification/deploiement du jeu n'est autorisee par ce document.
Cible : PWA 3D offline-first, code unique Android/iPhone/PC, 0 FC de frais obligatoires.
Version de comparaison envoyee a la testeuse : V2. Prototypes ulterieurs conserves comme archives techniques, non comme references definitives de qualite.

## 0. Principes inviolables
C0 : zero paiement impose au developpement, a la distribution, au serveur, aux SDK, aux ressources, aux notifications, aux API. Internet et electricite physiques non gratuits ; minimiser les transferts.
C1 : meme gameplay et monde sur Android, iPhone, Windows ; seuls controles, resolution, distance d'affichage, particules et densites VISUELLES peuvent varier.
C2 : hors ligne apres premier telechargement complet avec service worker / cache ; retour en ligne non requis pour jouer ; stockage navigateur possiblement efface => export de sauvegarde.
C3 : ergonomie : gauche va a gauche de l'ecran, droite a droite, sur toute camera ; controles multi-touch ; clavier ; aide visuelle.
C4 : jamais publier une regression de rendu, commandes, sauvegarde ou comportement, sauf exception approuvee.
C5 : graphismes 3D dans tous les profils pris en charge ; pas de bascule silencieuse en 2D inferieure.
C6 : proposer des mecanismes emergents mais les deployer uniquement avec tests de performance.
C7 : fonction sans compte, publicite, collecte personnelle, GPS permanent, microphone, paiement, ou serveur de jeu.

## 1. Faits acquis — materiels et prototype
PC principal recent : HP EliteBook 840 G6, Intel i5-8365U, 8 Go RAM, Intel UHD 620, Windows 11. RAM disponible tres variable avec Opera, ChatGPT et autres processus ; ne pas compter 8 Go libres.
Telephone Android de basse gamme : Galaxy A21s 4 Go RAM / Exynos 850. Autre telephone principal : S21 FE environ 8 Go RAM. iPhone de la testeuse : modele inconnu -> test physique indispensable.
Audit V0.4 : HTML/CSS/JS monolithique ~650 lignes ; WebGL1 artisanal ; trafic initial de 24 voitures ; route et missions essentiellement le long d'un seul axe ; repli Canvas 2D ; sauvegarde locale ; boucle trafic potentiellement O(N^2) par comparaisons de vehicules.
La correction graphique ne doit pas etre confondue avec une refonte architecturale. La V2 et ses captures servent de reference d'experience ; les versions plus recentes sont des essais techniques.

## 2. Produit et vision
Genre : simulation de moto-taxi urbaine semi-realiste dans Kinshasa, avec conduite plaisante, vie quotidienne, personnages memorables, trafic reactif, missions et carriere.
Promesse : 'Une moto, une ville vivante, une histoire qui emerge de chaque trajet.'
3 boucles : 20 secondes (plaisir de conduire et lire le trafic), 3 minutes (une course complete), 20 minutes (progression, garage et nouvelles relations).
Modes prevus : course libre, carriere, defis ; pas de mode multijoueur serveur en phase zero-franc.
Modes de physique : Arcade assiste et Simulation accessible avec parametres limitant les risques de sortie de route.

## 3. Feuille de choix technologiques
Architecture prescriptive a tester : TypeScript (build Vite) + Three.js WebGL2 pour les objets 3D + simulation maison 2D/2.5D kinematique + HTML/CSS pour HUD. Bibliotheques libres et dependances verrouillees. Pas de React/Next/Electron requis a l'execution. Le poids runtime doit etre mesure avant choix final ; si Three.js depasse le budget, comparer renderer WebGL custom modulaire ou Babylon.js en sous-ensemble minimal. Eviter une simulation de physique rigide complete en continu tant qu'un prototype ne prouve pas sa valeur.
Godot Web : challenger dans un banc d'essai identique, pas retenu a priori pour mobile sous contrainte RAM, les documentations signalant des contraintes propres a WebGL2/Safari et au navigateur.
Protocoles de detection : capabilities WebGL2, shaders compilables, resolution utile, latence de rendu mesuree. Ne pas baser les decisions uniquement sur user-agent ou navigator.deviceMemory (non universel). Eviter WebGPU obligatoire.
Livraison : application statique HTTPS, sous-domaine gratuit, manifest, service worker, Cache Storage, IndexedDB et sauvegarde exportable. Aucune fonction serveur. Source en Git ; releases immuables.
Hebergement : prototype Vercel Hobby personnel, non commercial uniquement ; cible Cloudflare Pages Free pour distribution statique selon conditions au moment du deploiement. Tranche par fichiers sous 25 MiB chacun. Aucune garantie absolue de gratuite future du fournisseur ; sauvegarder et prevoir migration.

## 4. Schema modules
/src/core : horloge fixe, PRNG graine, bus d'evenements, scenes, version ;
/src/input : bouton tactile, souris, clavier, remappage, multitouch, haptique facultative ;
/src/vehicle : etat moto, direction, acceleration, freinage, grip, masse passager, usure ;
/src/roads : graphe de routes, voies, intersections, carrefours, signalisation ;
/src/traffic : suivi de voie, gestion de priorites, distance securite, obstacle, spawn, agents par LOD ;
/src/collision : volumes, requetes spatiales, sweep, penetration, dommages ;
/src/world : tuiles/secteurs, proceduraux, reperes, batiments, cycle jour/nuit ;
/src/renderer : rendu webgl, instanciation, LOD, materiaux, textures, lumieres ;
/src/characters : passagers, comportements, animations, dialogues ;
/src/mission : generateur, etapes, verification, recompenses ;
/src/economy : prix du trajet, garage, usure, carburant virtuel, reputation ;
/src/audio : sons originaux, streaming, melange, extinction en pause ;
/src/persistence : IndexedDB, snapshots, migrations, import/export, recovery ;
/src/pwa : precache, mise a jour atomique, hors ligne ;
/src/ui : HUD, garage, menus, clavier/tactile, aides ;
/src/qa : tests unitaires, integration, e2e, enregistrement/rejeu, benchmarks.
Contrats typees entre modules ; dependances unidirectionnelles. Aucun calcul de monde dans la couche graphique.

## 5. Boucle de simulation
Physique de la moto : timestep fixe p.ex. 1/60s, variable entree. Rendu 30-60 FPS selon budget, interpolation entre etats ; trafic a 5-15 Hz selon proximite ; contrats et demande de courses a 1 Hz ou moins. Ajustements a mesurer.
Ne pas lier vitesse du joueur au nombre d'images par seconde. Pause sur visibilitychange/pagehide, sauvegarde, retour doux sans teleportation.
Unite en metres/secondes ; vitesse UI km/h. Graphique d'etat de la moto (position, cap, vitesse, inclinaison, freinage, adherence, dommage) independent du mesh rendu.
Physique couteuse remplacee par modele cinematique de moto + approximation inclination/acceleration laterale, amortissement suspensions predefini, usure cumulative. Collisions simples mais robustes avec boites orientees (OBB) et sweep pour grande vitesse ; tests de penetration et resolution conservative ; contact voiture => freinage/dommages/animation/effet sonore sans teleportation arbitraire.

## 6. Geometrie, carte et streaming
World cell prototype de 64x64 m (parametre non fige), 3x3 ou anneaux proches actifs ; secteur central avec rues et intersections reelles ; rayon selon appareil. Road graph independant du rendu.
1 zone verticale slice proposee : Victoire/Matonge, validee par references locales ; later Bandal/Kintambo, Limete, Gombe, Masina et autres. Distinguer elements verifies, stylisation et fiction.
Blocs de batiments modulaires avec variation proceduree (hauteur, toit, enseigne fictive, couleur, facade) ; 1 atlas texture partage ; objets repetes en instancing ; panneaux generes a partir de composants ; faible nombre de materiaux.
Eviter de photographier/copier sans autorisation les enseignes et marques reelles ; demander usage ou inventer noms.
OSM pour sources routieres possibles, respect ODbL, attribution, conditions de partage ; telecharger des donnees permises, ne pas dependre de tuiles en ligne.

## 7. Trafic multi-niveaux — economiser le CPU
Niveau 0 global : segments routiers avec flux agreges (pas d'objets 3D, p.ex. debits par heure). Niveau 1 lointain : tokens de trafic sur graphe, 0.5-2 Hz ; niveau 2 moyen : agents alloues, comportement simple 5-10Hz ; niveau 3 proche : volumes de collision et virages detailles 20-60Hz.
Requetes de voisins via grille de cellules/spatial hash, pas double boucle sur toutes voitures. Par agent, limiter nombre de voisins evalues.
Comportements : suivre voie, ralentir, ceder priorite, chercher itineraire, contourner obstacle autorise, s'arreter au terminus, depose de passager, sortie de parking, moto qui se faufile; detecter TTC (time-to-collision) pour eviter collisions artificielles.
Des milliers d'agents 'existants' dans la ville ne signifient jamais des milliers de voitures 3D ou 1000 trajectoires recalculées toutes les 16 ms.

## 8. Visuels : qualite satisfaisante, MEME en Eco
Direction artistique : semi-realiste stylisee, couleurs/ambiance locales, pas photorealisme agressif. Qualite artistique = silhouette, proportions, composition, lumieres, palettes, references ; pas uniquement densite de polygones.
Matieres : vertex colors + atlases 512/1024 selon profil ; mipmaps pour textures 3D ; compressions KTX2/Basis en option et benchmark transcodage. Eviter textures 4K ; 2048^2 RGBA=16MiB avant mipmaps, jusqu'a 21.3MiB avec mipmaps complets.
Rendu Eco : distance 100-180m selon perf, 3D complete, vegetation instanciee, ombres bakees/sol, lumiere principale, brume legere, resolution interne dynamique p.ex. 0.6-0.85. Equilibre et Eleve ajoutent distance, ombres, densite de decors, reflets legers, resolution.
Budget assets au premier chargement cible <= 8-15 Mio, total pack essentiel <= 30-50 Mio, quartiers facultatifs telecharges a la demande ; objectifs hypotheses, non performances promises.
Audio original/CC0 : moteur, klaxon, ambiance de marche, pluies, bruits de garage, dialogues optionnels ; priorite aux sons compresses courts et banque partagee. Cacher les logos commerciaux non autorises.

## 9. Regles de budget memoire (hypotheses de travail)
Eco : cible 30FPS stable et jeu incremental vise <=200 MiB sur appareils modestes, hors surcout du navigateur/systeme difficile a mesurer. Equilibre <=300 Mio et 30-45 FPS ; Avance <=450 Mio et 60 FPS. A invalider ou confirmer sur les appareils cibles.
Sous budgets Eco : moteur JS 45 Mio, textures GPU 40 Mio, meshes/buffers 25 Mio, framebuffers 30 Mio, audio/autres 20 Mio, reserve 40 Mio. Attention double comptage/runtimes ; utiliser compteurs de ressources propres et profils systeme (Windows task manager, Android dev profiler, Safari Web Inspector via appareils disponibles).
Assurer 95% frames sous la cible choisie; absence de freeze >250 ms pendant mission normale; mesure scene densite minimale et apres 20 min de jeu. La RAM n'est pas lisible de facon comparable via JavaScript sur Safari, ne pas annoncer des seuils verifies sans instrumentation externe.

## 10. Gameplay emergent et progression
Boucle : accepter course -> localiser client -> route -> conduite & incidents -> depot -> satisfaction -> paiement -> cout et reputation -> garage -> nouvelles missions.
Familles : transport ordinaire, multi-arrets, livraison, pluie, nuit, panne, urgence non medicale, contrat hebdomadaire, passager a besoins particuliers, quartier festival, trajet etudiant, parcours technique.
Parametres mission : point A/B sur graphe, fenetre horaire, profil du passager, charge, meteo, capacite route, etat moto ; generateur avec regles de compatibilite => milliers de variations sans ecrire 1000 scripts.
Satisfaction = fonction respect de conduite, duree raisonnable, absence de choc, itineraire, etat de moto ; bonus plafonnes, pas d'incitation a des vitesses dangereuses. Pas de microtransactions.
Progres : 3 etapes conducteur/contrats/flotte. Gestion flotte simulée hors ligne ; pas de paiement reel, blockchain, crypto ou comptes.
Chasses/poursuites : des scenarios de recherche, livraison urgente ou suivi non violents peuvent etre etudies sans en faire le coeur du jeu ; combats armes non prioritaires car ils augmenteraient contenu, animation, violence et cout technique.

## 11. Kinshasa vivante
Vie urbaine : marches, etudiants, ateliers, vendeurs, bus, taxis, motocyclistes, musique originale, phrases francaise/lingala revisees par locuteurs. Heures de pointe simulées, pas pretendues temps reel. Pluie, flaques, nids de poule, chantiers, routes alternatives ; temps de trajet change selon facteurs coherents.
Personnages persistent localement : clients fideles, commercants, mecaniciens, passagers avec arcs narratifs ; dialogues courts avec archetypes et variations, pas besoin de LLM online.
Representation digne et variee : moderne, residentielle, populaire, festive, laborieuse ; eviter une caricature de violence et de delabrement.

## 12. Controles, HUD et accessibilite
Tactile multi-doigts acceleration+direction ; gauche toujours a gauche visuelle, droite a droite, y compris si camera bouge ; bouton frein plus large et accessible ; profil gaucher/droitier. PC : clavier fleches/ZQSD/WASD selon mapping et option de personnalisation ; souris facultative.
Modes camera derriere moto proche/eloigne, laterale legere et casque en option ; jamais inverser commandes en changeant la camera.
HUD : minicarte orientable, vitesse, carburant virtuel, moto/degats, prochain objectif, temps de mission ; UI adaptative encoche iPhone et barres d'OS ; textes lisibles sur petits ecrans. Mode contraste renforce.
Assistance au demarrage : tutoriel 60-90 secondes sans quitter la route ; mission de niveau 0 facile.

## 13. PWA, offline et sauvegardes
HTTPS + manifest + icones + service-worker avec precache du shell et core assets. Installer hors ligne uniquement apres verification explicite que les packs essentiels ont ete caches ; progression de telechargement, pause/reprise, ne pas charger tout Kinshasa.
Jeu statique sans backend : IndexedDB pour progression (transaction, schema version, checksum/snapshot), export JSON documente et import avec migration ; sauvegarde auto par evenement et periodique en mission, sans ecritures a chaque frame. Service workers / caches gérés par version ; mise a jour disponible uniquement dans menu ; en pleine mission garder ancienne version jusqu'a fin ou pause ; rollback apres migration si possible.
Sur iOS, eviction possible sous pression stockage ; sauvegarde exportable indispensable. Pas de synchronisation automatique entre PC/iPhone/Android sans serveur : transfert manuel du fichier de sauvegarde.

## 14. Securite et droit
Pas de recueil de GPS, ni suivi perso, ni authentification, ni publicites, ni paiement ; logs diagnostics exportes uniquement sur action volontaire. CSP et dependances verrouillees ; pas de scripts tiers inutiles.
Assets originaux ou CC0 (Kenney pack individuel et Poly Haven), archive attribution/licence ; Blender libre ; aucune musique commerciale copiée. Utilisation donnees OSM sous ODbL avec attribution et obligations de partage de la base derivee le cas echeant.
Un site de demo Vercel Hobby doit rester non commercial. Pour produit commercial, examiner conditions d'un autre hebergeur statique avant lancement.

## 15. Bancs de tests
A) Unitaires : equations de freinage, virage et unite, impact, mission, argent, sauvegarde, progression ; seed fixe.
B) Propriete : aucune voiture ne traverse un obstacle solide, pas de collision fantome, pas de trajet dans sens interdit si scenario normal, taux de spawn bornes.
C) Simulation intensive : 1000 missions generees offline, 1000 changements de quartier, sauvegarde re-ouverte et migrations, test fuite memoire 20 puis 60 min.
D) End-to-end : souris/clavier desktop, multitouch Android, Safari iPhone reel ; 30 min sur chaque, coupure Wi-Fi, perte de contexte WebGL, changement d'onglet, appel entrant, ecran verrouille, batterie faible, extinction brutale ; retour au jeu sans perte critique.
E) Performance : FPS median, p95 frametime, 1% lows, CPU, RAM native, GPU estimé, temperature et batterie, temps premier chargement, taille pack. Aucune declaration de compatibilite iOS sans test reel.
F) Comparaison visuelle automatique : captures figees par seed, camera, heure et qualite a chaque release; seuils de difference, revue humaine pour changements intentionnels.
G) Telemetrie zero cloud : diagnostics telechargeables par le joueur si volontaire.

## 16. Livraison, versioning, controle budget
Branches /release-stable, /dev, /features ; chaque jalon a contenu gelé, replay, captures, rapports ; pas de mise a jour quotidienne non validee ; une unique adresse stabile pour public.
Moteur de mise a jour : manifest versionne et hash de chaque pack, atomique, pas de changement mid-mission, retention d'une sauvegarde ancienne, rollback si pb.
Ledger des depenses : 0 FC sur licences, hebergement, cloud, sons, textures, moteur, outils et distribution. Si une fonctionnalite impose depense, elle est rejetee ou repensee. Le temps humain, energie et data existantes ne sont pas 'gratuits' physiquement.

## 17. Jalons de production et portes de sortie
M0 - CADRAGE (ce document) : vision, contraintes, 3 niveaux quality, choix du quartier test et acceptance.
M1 - BENCHMARK TECHNIQUE : meme scene 3D sur Android A21s/S21 FE, PC HP, iPhone reel ; renderer choisi selon taille, FPS, RAM, stabilité.
M2 - PROTOTYPE CONDUITE : vrai virage, frein, collision, marche lente et scenario de carrefour ; aucune regression visuelle.
M3 - VERTICAL SLICE : quartier ~petit mais cohérent, 10 destinations, 3 familles de missions, passagers, trafic et garage ; 15-20min de jeu intéressant.
M4 - ALPHA SYSTEMES : pluie, horaire, trafic multicouches, plusieurs quartiers, contrats, personnages et economies.
M5 - BETA : campagne de tests, performances, corrections, audit de licences, stockage/offline.
M6 - 1.0 : PWA stable, une URL, plusieurs profils graphiques, assistances, mises a jour fiables.
La duree n'est pas estimable sans ressources humaines, benchmarks et qualite de la tranche verticale. Aucun jalon ne depend d'un service payant.

## 18. Risques, arbitrages
R1 iPhone non identifie -> observer reels iOS version, FPS, crash. Echec WebGL2 => analyser compatibilite ; eviter downgrade 2D silencieux.
R2 surcharge RAM -> réduire resolution, distance, textures et LOD sans retirer missions ni ville.
R3 hebergeur free modifie regles -> source, builds statiques et sauvegardes exportables, migration de sous-domaine (liens publics a communiquer).
R4 trop de missions -> generateur parametre par 10 templates bien joués plutot que 1000 bugs.
R5 'realisme' cher -> stylisation forte et details localement reconnaissables, economies sur shaders et IA.
R6 echec apres mise a jour -> version stable conservee, migration de save testee et rollback.
R7 peu de testeurs -> le joueur, l'utilisatrice iPhone et deux Android + HP; tickets traces avec captures et video + conditions.

## 19. Decision a prendre plus tard, PAS maintenant
(A) Moteur final apres benchmark Three.js vs petit renderer ; (B) quartier central ; (C) mode de physique dominant Arcade vs Simulation ; (D) niveau de narration ; (E) politique multijoueur (deferree) ; (F) license final assets et donnees ; (G) strategie de stockage par packs.
Le projet reste en preproduction. La V2 partagee par l'utilisateur reste inchangée.

## 20. Sources techniques controlees le 04/11/2026
- MDN PWA install: https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Making_PWAs_installable
- MDN offline SW: https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Offline_and_background_operation
- MDN WebGL best practices: https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices
- Three.js instancing: https://threejs.org/docs/pages/InstancedMesh.html
- WebKit storage policies: https://webkit.org/blog/14403/updates-to-storage-policy/
- Cloudflare static asset pricing: https://developers.cloudflare.com/pages/functions/pricing/
- Cloudflare Pages limits: https://developers.cloudflare.com/pages/platform/limits/
- Vercel Hobby terms: https://vercel.com/legal/terms
- Godot web export cautions: https://docs.godotengine.org/fr/4.x/tutorials/export/exporting_for_web.html
- Vite statics: https://vite.dev/guide/static-deploy
- OSM license: https://www.openstreetmap.org/copyright
- Poly Haven: https://polyhaven.com/license
- Kenney CC0: https://kenney.nl/support
- MDN navigator.deviceMemory caveats: https://developer.mozilla.org/en-US/docs/Web/API/Navigator/deviceMemory
