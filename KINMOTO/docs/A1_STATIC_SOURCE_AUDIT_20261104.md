# KIN MOTO — A1 / Contre-audit des bases libres — 2026-11-04

**Étape :** A1 phase S (sourcing + code statique) ; **QA :** `PARTIAL_PASS` ; **sélection finale :** `NOT_SELECTED`.  
**Préconditions :** dépôt `PROJECT-DRAFTS` PUBLIC volontairement (décision propriétaire 2026-11-04) ; conserver la politique GitHub Actions **0 min par défaut**, sans workflow auto.  
**Contrainte :** 0 FC ; Android modeste et HP Windows prioritaires ; iPhone ensuite ; vraie 3D, faible RAM et sensation moto convaincante.

## 1. Sources épinglées et vérifiées

| Base | Commit examiné | Repo GitHub rapporté (taille indicative, non téléchargement du jeu) | Langage / structure | Licence code |
|---|---|---:|---|---|
| Neon Mayhem | `cd19f934d9088392d1f10374c3b64a1b7eb683cf` (2026-11-03) | 18 287 KiB | JS scripts globaux, Three.js r128 vendored, exécution statique sans Node | Apache 2.0 ; Three.js MIT |
| Costa Vista | `23e87108a281ac827e2ea23691aa7bf4b544146e` (2026-07-17) | 254 654 KiB | TypeScript, Three.js ^0.184, Rapier ^0.19.3, Vite ^8, tests Vitest et Playwright | MIT **pour le code uniquement** |

Taille dépôt GitHub `size` : métrique de métadonnées, pas un benchmark de transfert, de cache, de RAM ni de taille du build. README Costa Vista indique ~270 MB de ressources committed. Il serait imprudent de copier toute l'archive pour le joueur.

## 2. Analyse des mécanismes — extraits vérifiés dans le code

**Neon Mayhem**
- `js/vehicles.js` (160 852 octets) : `motorcycle`, `superbike` avec paramètres `maxSpeed, accel, grip, turn` ; `buildBikeMesh()` construit un modèle procédural de moto ; gestion position `car.pos += velocity*dt`, vitesse latérale `car.lat`, `tyreLean()` et roulement visuel interpolé. **Ce n'est pas la preuve d'un véritable deux-roues avec contact de pneus à la chaussée et suspension dynamique**. Les sensations de "glissement" nécessitent essais réels.
- `js/touch.js` (25 147 octets) : joystick virtuel basé sur `touchstart/touchmove`, identifiant de doigt, boutons GAS/BRAKE, gestion changements de taille/orientation ; bon **candidat d'idée** pour ergonomie tactile.
- `js/controls.js` (16 571 octets) : clavier et gamepad. `js/city.js` (~175 KiB), `js/missions.js` (~168 KiB), `js/player.js` (~77 KiB) ; sous-systèmes importants avec dépendances globales `GAME`, donc extraction difficile sans adaptateur.
- `test/smoke.js` (13 875 octets) et `test/regressions.js` (902 264 octets) : suite de régression revendiquée et fichiers présents ; **aucun test n'a été exécuté dans A1 S**, ne pas confondre présence et réussite.
- `index.html` et racine : pas d'enregistrement service worker identifié ; ne pas traiter sa promesse d'« offline » comme certification de **PWA installable hors réseau**. `js/analytics.js` charge un compteur externe sur site public : **ne pas importer** cette télémétrie dans KIN MOTO.

**Costa Vista**
- `src/physics/vehicleController.ts` (29 247 octets) : corps dynamique Rapier, raycasts de suspensions, forces ressort/amortisseur `suspensionForceN()`, adhérence latérale et coefficient de sol mouillé `wetSurfaceMultipliers()` ; `visualRoll` d'inclinaison. Bonne **piste de mécanique**.
- **Limite à mesurer :** `src/physics/vehicleSpec.ts` précise que les deux-roues emploient **quatre points d'appui virtuels** pour stabilisation, et `vehicleController.ts` applique ressort/couple anti-basculement. Cela favorise la jouabilité, mais **ne constitue pas une simulation complète de moto réelle** et peut produire une sensation artificielle.
- `src/systems/traffic.ts` : limite déclarée de ≤20 voitures cinématiques autour du joueur (+ véhicules enregistrés), itinéraires et inclinaison ; `src/world/roadGraph.ts` contient `routeBetween()` et A*. Pertinent pour réseau urbain compact.
- `src/core/save.ts` : `localStorage` ; `public/sw.js` et `manifest.webmanifest` existent ; PWA à **tester physiquement**.
- `package.json` : Node >=20, TypeScript/Vite/Rapier/Three et commandes `check`, `test`, `test:e2e` ; non exécutées lors de cette phase statique.
- `ATTRIBUTION.md` : certains modèles Kenney/Quaternius/poly.pizza/ambientCG sont crédités CC0 ; **les modèles créés dans le projet, dont la moto actuelle, incluent du matériel réalisé avec des outils 3D sous licences payantes**. `LICENSE` indique que `public/assets` n'est PAS couvert par MIT. **NE PAS importer les modèles internes de Costa Vista tant que leurs droits de réutilisation ne sont pas prouvés.**

## 3. Contrôle visuel et appareil

- **HP / Opera :** `https://pranshuparmar.github.io/neon-mayhem/` chargé, titre et menu "PRESS ENTER" présents via l'arbre d'accessibilité ; après envoi réel de la touche **Enter** depuis le HP, le menu disparaît et un **HUD de jeu** apparaît (heure, argent, district, prompt de véhicule) sur le même onglet. Ceci vérifie le **démarrage fonctionnel en navigateur**, mais PAS la maniabilité moto, le rendu 3D capturé, ni les FPS/RAM.
- **Screenshot Opera :** demande bloquée/timeout ; aucune capture de gameplay enregistrée.
- **HP, jeu initialisé via Enter :** `PASS_BOOT`. **Moto, FPS/RAM, collision, temps de chargement :** `NOT_TESTED`.
- **Android physique Galaxy A21s :** `NOT_TESTED`.
- **iPhone physique :** `NOT_TESTED`.
- **Costa Vista :** non installé ni exécuté ; pas de téléchargement massif sur le PC (respect réseau, RAM, quota).
- **Aucune mesure artificielle ne remplace le benchmark.**

## 4. Matrice 100 points — ne pas inventer des scores

| Critère | Pondération | Neon Mayhem | Costa Vista |
|---|---:|---|---|
| Sensations moto / contact route | 30 | NOT_TESTED ; physique cinématique | NOT_TESTED ; Rapier + suspension virtuelle |
| Graphismes / animation vraie 3D | 20 | NOT_TESTED in-game ; modèles procéduraux | NOT_TESTED ; assets mixtes |
| FPS / RAM / poids du premier chargement | 20 | NOT_TESTED ; dépôt plus petit | NOT_TESTED ; dépôt lourd |
| Modularité / extraction | 15 | Audit partiel : scripts globaux | Audit partiel : TS structuré, dépendances |
| Licences / coût | 10 | Code Apache 2 + Three MIT ; autres éléments à inventorier | Code MIT ; sous-ensemble assets CC0 ; projet-créés non validés |
| Missions / sauvegarde | 5 | Code présent, pas de validation | Code présent, pas de validation |

**Aucun total /100 officiel tant que les cinq essais physiques/visuels et les ressources utilisées ne sont pas vérifiés.** Un score élevé ne supprime pas un veto légal, coût ou compatibilité.

## 5. Décisions provisoires (sans sélectionner prématurément)

1. **Ne pas remplacer KIN MOTO par une copie complète de Neon Mayhem ou Costa Vista.** Les fonctions de combat, police, arsenal, etc. ne sont pas nécessaires à un moto-taxi et alourdiraient le projet.
2. **Piste principale à tester :** noyau PWA 3D compact + module de conduite issu/porté du modèle Rapier Costa Vista + ergonomie tactile inspirée de Neon Mayhem + assets directement vérifiés CC0 auprès de Kenney.
3. **Interdit immédiat :** importer `public/assets` complet de Costa Vista, sa moto créée sous outils payants ou toute télémétrie Neon Mayhem.
4. **Ne pas importer de code sans conserver les licences requises** (MIT/Apache 2.0 et notices de modification, selon fichiers).
5. **Vrai choix du moteur après benchmark A1 phase D sur HP et Android physique.** La sensation moto (30/100) a priorité. Si aucun candidat ne passe, extraire des idées/modules plutôt que prendre un jeu entier.

## 6. Prochain protocole A1 D — dossier reproductible

**HP Windows / Opera** (plus Chrome ou Edge) : scène à caméra constante ; démarrer, 5 s ligne droite, slalom, freinage, virage serré, collision ; enregistrer 5 captures avant/après, FPS sur 10 min, mémoire système navigateur avec protocole répétable, crash graphique. Le PC ne dispose pas actuellement de `node` ni `python` sur PATH selon audit terminal ; **ne pas lancer Costa Vista sans environnement gratuit correctement préparé**.

**Android Galaxy A21s** : même parcours 15 min, touches, rotation, reprise après mise en arrière-plan, batterie, chauffe, offline après cache et temps de chargement. Aucune prétention de test Android avant observation réelle.

**Hébergement/test** : utiliser PREVIEW distinct ; aucune URL STABLE modifiée ; pas de GitHub Actions automatiques, aucune dépense, pas de collecte de données.

## 7. Autre bibliothèque observée (non sélectionnée)

- [GG Web Engine](https://github.com/AndyGura/gg-web-engine) : source Apache 2.0 et modules Three.js/Rapier/contrôles mobiles documentés. **Ce n'est pas un jeu de moto** ; à étudier pour composants éventuels après tests, pas une raison pour ajouter un moteur supplémentaire à V1.

## 8. Ressources CC0 directement vérifiées

- https://kenney.nl/assets/car-kit — modèles de voitures, CC0.
- https://kenney.nl/assets/city-kit-roads — routes/intersections, CC0.
- Toute ressource importée doit recevoir une entrée fichier par fichier dans `docs/ASSET_LICENSES.csv`.

**A1 statut final de cette étape : PARTIAL_PASS / STATIC_COMPLETE / DYNAMIC_PENDING.**  
**Pas de choix définitif ; A2 et A3 restent non lancés.**

## 9. Observation réelle de ressources système HP (après fermeture du jeu de test)

Relevé Windows via Remote Desktop Commander sur `HP-840G6-MBM` le 2026-11-04 : `Win32_OperatingSystem.TotalVisibleMemorySize=8190240 KiB`, `FreePhysicalMemory=1157568 KiB` (environ **7,81 GiB installés, 1,10 GiB libres au moment du relevé**). Carte graphique `Intel(R) UHD Graphics 620`, `AdapterRAM` déclaré 1 GiB par Windows. **Attention :** c'est une capture ponctuelle du système, PAS la RAM utilisée par Neon Mayhem ou Costa Vista, ni nécessairement la VRAM dédiée réelle (GPU intégré à mémoire partagée).

Conséquence : ne pas charger sans nécessité les ~270 Mo d'assets Costa Vista sur cet HP sous forte pression mémoire. Comparer d'abord des modules isolés, sous-ensembles d'assets et scènes courtes, puis exécuter le vrai benchmark après vérification de la mémoire disponible et de l'absence de logiciels critiques à fermer.
