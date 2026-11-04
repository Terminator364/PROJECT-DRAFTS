# KIN MOTO | CHARTE MAÎTRE DU PROJET

**Édition documentaire :** FACTORY 3.0 — 4 novembre 2026  
**Nature :** constitution du projet, attentes de qualité, organisation humaine/IA et règles de décision.  
**Statut :** PROPOSITION STRUCTURÉE À UTILISER COMME RÉFÉRENCE DE TRAVAIL ; les exigences explicites de l'utilisateur sont conservées, les choix nouveaux restent des propositions à arbitrer.  
**Dossier concerné :** JEU MOTO / KIN MOTO.  
**Destination :** sources du Projet ChatGPT, dépôt GitHub canonique à créer ou à désigner, archive documentaire Drive.  
**Portée :** gouvernance et conception. **Aucune modification du jeu, aucun déploiement, aucune fusion GitHub n'est effectuée par la création de ce document.**

> **Phrase directrice :** « Un vrai jeu de moto-taxi à Kinshasa : agréable à piloter, beau à regarder, cohérent à jouer, réellement compatible avec nos appareils, développé sans paiement supplémentaire obligatoire, et amélioré sans retour en arrière. »

## 0. Comment lire et utiliser ce document

### 0.1 Force des décisions

| Marque | Sens | Conséquence |
|---|---|---|
| **E** | Exigence exprimée et répétée par le commanditaire | Non négociable sans son arbitrage explicite |
| **C** | Constat vérifié sur un livrable ou une source | À conserver avec sa preuve et sa date |
| **P** | Proposition d'architecture ou de méthode | Peut être ajustée après benchmark/contre-audit |
| **H** | Hypothèse non démontrée | Ne jamais présenter comme performance obtenue |
| **N** | Non autorisé ou exclu du périmètre | Ne pas exécuter implicitement |

### 0.2 Hiérarchie des sources et arbitrage de conflit

1. Les décisions explicites et récentes de l'utilisateur priment sur les suggestions anciennes.
2. Les mesures sur les appareils physiques priment sur les simulations logicielles, pour la performance et le ressenti.
3. Pour le code : dépôt GitHub, commit et rapport QA liés au même commit priment sur le souvenir d'un chat.
4. Pour la gouvernance : cette charte, son journal des décisions approuvées et les procédures d'exécution.
5. Pour le contexte historique : cahier directeur du 4 novembre, ZIP des prototypes, rapports de recette, conversations.
6. Une information contradictoire est étiquetée **CONFLIT**, documentée puis soumise à arbitrage ; elle n'est pas silently résolue par l'assistant.

**IMPORTANT :** ce PDF n'est ni un dépôt de code ni une preuve de qualité du jeu. Les fichiers `.md`, `.json` et les commits portent les informations opérables. Toute copie destinée aux sources du Projet doit avoir un numéro d'édition et une date.

## 1. Vision du produit : ce que l'on construit réellement

**Genre :** jeu de moto-taxi 3D semi-réaliste, à la troisième personne, avec une conduite satisfaisante et une progression de carrière inspirée de Kinshasa. Une caméra alternative est possible après validation du pilotage central.

**Promesse joueur :** démarrer une moto, prendre une course, lire une vraie circulation, choisir un itinéraire, déposer un client, gagner des francs fictifs, améliorer sa moto et revenir jouer parce que le mouvement et la ville sont plaisants.

**Différenciation :** une expérience de mobilité kinoise crédible et respectueuse, et non un clone générique d'une autoroute infinie ou une démonstration de cubes 3D. Diversité urbaine, commerces, couleurs, bruits, quartiers, langues et situations quotidiennes ; ne pas réduire Kinshasa aux embouteillages, à la pauvreté ou à la violence.

**La qualité se mesure dans cet ordre :** (1) sensations de conduite, (2) lisibilité et cohérence des commandes, (3) représentation visuelle crédible et stable, (4) interactions de circulation, (5) missions significatives, (6) profondeur et étendue de contenu. Ajouter 50 missions à un mauvais pilotage ne constitue pas une amélioration.

**Boucle fondamentale :** liberté de déplacement → prise de mission → approche du client → interaction à l'arrêt → itinéraire et trafic → dépose → paiement → progression/garage → choix suivant.

## 2. Profil de collaboration : ce que le commanditaire aime et refuse

### 2.1 Ce qu'il veut explicitement [E]

- **Des résultats visibles et jouables**, pas une avalanche de rapports qui masquerait une mauvaise expérience.
- **Une progression en crescendo** : chaque version doit être qualitativement meilleure, ou rester expérimentale et non publiée.
- **De la profondeur et de l'autonomie** : rechercher, comparer, contre-auditer, anticiper les erreurs, résoudre ce qui est réellement accessible et avancer entre les sous-étapes sans demander confirmation à chaque détail technique.
- **Une vraie recherche des sources libres** : profiter de modèles 3D, mécaniques, bibliothèques, projets complets et outils open source existants, plutôt que réinventer tout le moteur.
- **Une conversation principale naturelle** : il parle de ses idées, de ses critiques et de ses objectifs ici ; l'organisation technique doit prendre en charge leur transformation en tâches.
- **Un rôle clair pour ChatGPT Work** : déléguer les opérations lourdes, intégrations, tests et audits de dépôts ; préserver le quota et assurer la continuité entre les sessions.
- **Un jeu utilisable par simple lien HTTPS**, sur Android et PC en priorité de test ; à terme iPhone également, à partir d'un code commun. L'installation PWA doit rester facultative.
- **Une consommation de RAM et de batterie raisonnable** pour appareils modestes ; mode graphique économique sans perte des mécaniques de jeu.
- **Zéro franc congolais de nouvelle dépense obligatoire de A à Z** : ni logiciel, serveur, achats d'assets, crédits API, facturation CI, domaine ou publication payante.
- **Trois versions majeures V1, V2, V3** pour le produit reconstruit ; pas de mini-versions publiques tous les jours.
- **Une documentation de reprise exhaustive** : projet compréhensible même lorsqu'une conversation se termine ou que Work atteint son quota.
- **L'interaction routière** : les voitures doivent réellement réagir, freiner, changer d'intention et subir les conséquences des collisions.
- **Une physique crédible** : contact visuel roue/sol, accélération/freinage, inertie calibrée, inclinaison cohérente, aucune impression que la moto « glisse sur l'eau ».
- **Des graphismes valorisants** : vrais véhicules et bâtiments convenablement modélisés, composition urbaine, textures, éclairage, animations et ambiance, pas uniquement des primitives géométriques.
- **Des commandes intuitives** : appuyer gauche fait partir à gauche à l'écran, droite à droite, y compris après changement de caméra.

### 2.2 Ce qu'il n'aime pas / ce qui constitue un échec [E/C]

- Les réponses précipitées, les promesses de résultat imminent et la déclaration de fin avant des preuves vérifiables.
- Les dégradations graphiques silencieuses : un rendu 2D de secours simpliste présenté comme l'équivalent du rendu 3D.
- Les jeux « techniques mais pas bons » : compteurs, fonctionnalités affichées, tests automatiques réussis alors que les sensations et visuels sont médiocres.
- La sensation de glissement, les virages inversés, les véhicules sans réaction et les missions artificiellement répétitives.
- Le recommencement dans une nouvelle conversation, l'oubli des décisions précédentes et la recréation d'un prototype inférieur.
- La délégation aveugle de tout le projet à un seul agent sans contrôle produit et sans validation utilisateur.
- Le fait de demander à l'utilisateur de programmer, gérer le dépôt ou répéter des informations déjà connues.
- Le recours automatique à des services payants, des abonnements, de la télémétrie superflue ou un serveur permanent.
- Le marketing verbal (« professionnel », « fini ») sans examen du produit par quelqu'un qui joue.
- Les envois d'archives identiques plusieurs fois et les mises en ligne non demandées pendant le cadrage.

### 2.3 Style de collaboration et pouvoir de décision [P, conforme aux échanges]

Le ton de l'assistant doit être **franc, technique, froid dans l'évaluation**, avec des observations mesurables. Il reconnaît les erreurs sans multiplier les excuses, propose des solutions plutôt que des plaintes et n'impose pas un choix entre deux versions jugées mauvaises. Une question n'est posée que si elle bloque réellement une décision réservée au commanditaire ; sinon, documenter une hypothèse et travailler dessus. Les états d'avancement doivent distinguer `FAIT`, `VÉRIFIÉ`, `NON VÉRIFIÉ`, `BLOQUÉ` et `REFUSÉ`.

## 3. Histoire et contre-audit : la vérité sur les versions déjà reçues

### 3.1 Registre historique minimal [C]

| Objet | État vérifié au 4 nov. 2026 | Limite critique |
|---|---|---|
| Premiers prototypes HTML et V2 partagée | Jeux web publiés ou envoyés ; une version ancienne disposait de meilleurs éléments perçus | Pas de qualité finale validée ; la V2 a été jugée insuffisante |
| Démo V0.4 | 42 contrôles annoncés réussis | Les profils automatisés utilisaient le rendu 2D, pas une certification 3D sur chaque appareil |
| « V1 Les Premières Courses » publiée | Archive source, déploiement web séparé, code modulaire JS, neuf carrefours, seize voitures, garage, quatre familles de missions | 17 tests Node + 3 tests cache ; UI mobile en émulation ; Android physique/offline non validés ; ressenti/visuels rejetés par l'utilisateur |
| Version actuelle de travail | **Aucune des anciennes V1/V2 n'est déclarée bonne base produit** | Réemploi possible de modules isolés seulement après audit comparatif |

### 3.2 Causes racines identifiées [C/P]

1. **Prototype fabriqué à partir de zéro** sans évaluer assez tôt les bases de jeux complètes et bibliothèques d'assets gratuites.
2. **Qualité graphique traitée comme quantité d'objets** plutôt que direction artistique, modèles, animation, textures et cohérence d'ensemble.
3. **Logique et rendu trop couplés** dans des versions précédentes : une correction peut dégrader la scène entière.
4. **Recettes fondées sur des assertions techniques** sans vrai test des sensations de conduite ni comparaison image à image de scènes canoniques.
5. **Émulation confondue avec appareil réel**, particulièrement pour GPU, mémoire, tactile et Safari.
6. **Livraison technique confondue avec approbation produit** ; un ZIP reçu et un HTTP 200 ne signifient pas que le jeu soit bon.
7. **Délégation mal cadrée** : des tâches trop vastes sont confiées à un environnement sans contrats de qualité et sans boucle de révision rapprochée.
8. **Contrôle des versions fragmenté** : documents, chats, ZIP et URLs sans référentiel unique immuable et statut clair.

### 3.3 Conséquence

**Interdiction de reconstruire immédiatement une troisième V1 à partir d'une page vide.** Première mission : benchmark comparatif des bases existantes et d'une référence maison. Un code existant n'est importé que si son avantage a été **démontré**, ses licences vérifiées et ses performances compatibles avec les objectifs.

## 4. Contraintes dures et arbitrages non négociables

| Dimension | Règle [E] | Traduction technique |
|---|---|---|
| Coût | 0 FC supplémentaires obligatoires | Infrastructure statique gratuite, dépendances libres, aucun achat in-app ni API requise |
| Diffusion | Un même jeu Android, iPhone, PC | Web/PWA et une source commune ; adapter seulement commandes/rendu selon appareil |
| Priorité | Android et PC d'abord | iPhone demeure cible officielle, ne pas lui attribuer une compatibilité non testée |
| Équipement modeste | Faible RAM/CPU/batterie | Profil Eco digne, streaming d'assets, LOD, budget mémoire benchmarké |
| Mode offline | Sans connexion après installation complète | Service worker vérifié sur appareil réel, sauvegarde locale exportable |
| Qualité | Aucune régression silencieuse | Diff image, comparaison jouée, blocage de publication si sensible |
| Versionnement | V1/V2/V3 majeures | DEV et PREVIEW illimitées en interne, STABLE seulement après décision |
| Confidentialité | Données et comptes protégés | Aucun jeton dans repo ; contrôles d'accès ; licences conservées |
| Volonté utilisateur | Pilotage conversationnel | Dialogue stratégique dans chat, actions lourdes en Work/Codex |

**Ne pas confondre « 0 FC » et absence de consommation Internet/électricité.** Le projet ne provoquera pas une facture logicielle obligatoire ; les données mobiles et l'alimentation restent des ressources réelles. Refuser toute solution techniquement intéressante dont l'usage exigerait finalement un paiement, sauf validation expresse d'une modification de cette contrainte.

## 5. Sensations de jeu : le contrat qualité, non seulement le contrat code

### 5.1 Les six piliers

| Pilier | Essai humain attendu | Garde-fou logiciel |
|---|---|---|
| Pilotage | « Je dirige une moto », pas un objet qui flotte | Test direction/trajectoire, vitesses physiques, suspension visuelle |
| Contact au sol | Roues alignées sur route, virages lisibles, aucune lévitation | Sonde contact, pente/hauteur, animation contrôlée par état |
| Circulation | Les voitures anticipent le joueur et les obstacles | Tests d'intersection, freinage, séparation et perception |
| Qualité visuelle | Silhouette moto, bâtiments, profondeur et ambiance crédibles | Captures de référence et revue d'assets sous même caméra |
| Mission | Trajet motivant avec client, destination et conséquence | Machine à états, paiements idempotents, validation de route |
| Fluidité | Session agréable, sans ralentissement notable | Benchmark FPS, RAM, 1% lows si mesurables, temps de chargement |

### 5.2 Protocole de « sensation moto » [P]

Avant de créer la ville : une piste de référence avec ligne droite, slalom, virage lent, virage rapide, freinage et obstacle mobile. Deux caméras : poursuite stable et caméra proche. Le moteur de moto doit posséder accélération longitudinale, direction dépendante de vitesse, légère inclinaison, friction de retour au centre, rotation des roues et ombre/contact cohérents. Les équations retenues sont jugées sur la sensation **et** la reproductibilité ; la physique rigide complète n'est pas obligatoire.

**Critère subjectif formalisé :** échelle joueur de 1 à 5 sur pilotage, contact au sol, caméra, trafic, graphismes, envie de rejouer. Toute note <=2 bloque le passage au jalon suivant ; aucune moyenne ne peut masquer un pilier fondamental raté. Seuils et protocole restent proposés, pas déjà approuvés.

### 5.3 Comparaison en crescendo

Pour chaque nouvelle candidate, reproduire **exactement les mêmes scènes** et mêmes contrôles sur le même appareil : démarrage, route principale, croisement, choc évité, collision légère, mission. Enregistrer captures/vidéos, FPS et conditions. Comparer au meilleur élément observé **dans chaque ancienne version**, sans qualifier globalement l'une des versions de « bonne ». Une amélioration n'est pas acceptée si elle gagne seulement du contenu tout en perdant l'essentiel.

## 6. Architecture humaine : une conversation pilote et des corps de métiers

### 6.1 La conversation principale [E/P]

**Une conversation ChatGPT du Projet = salle de pilotage.** L'utilisateur y parle librement, exprime idées et critiques. ChatGPT traduit les demandes en décisions et tickets, tient le registre des priorités, prépare des missions Work et reçoit les rapports. Il ne renvoie pas l'utilisateur systématiquement vers un autre chat pour chaque question. Il ne prétend pas recevoir automatiquement le résultat d'une autre session Work : il doit lire le dépôt et les artefacts disponibles.

**Corps spécialisés :** (1) Direction produit, (2) Architecture/intégration, (3) Physique et circulation, (4) 3D/animation/assets, (5) Monde et missions, (6) Performance et compatibilité, (7) QA et contre-audit, (8) Documentation, licences et release. Une même session Work peut traiter plusieurs corps, mais chaque ticket n'a qu'un propriétaire et un périmètre.

### 6.2 Rôles et autorisations

| Acteur | Peut faire sans re-demander | Doit demander autorisation |
|---|---|---|
| **Utilisateur (PRODUCT OWNER)** | Exprimer besoins, noter la qualité, définir priorités | Détient approbation STABLE, changement de budget et de périmètre majeur |
| **ChatGPT pilote** | Rechercher, analyser, planifier, classer bugs, réviser briefs, préparer tickets et rapports | Changer un choix produit explicite, déclarer une release approuvée sans aval |
| **Work / Codex opérateur** | Coder dans branche prévue, installer dépendances gratuites, exécuter tests, produire captures, créer PR | Pousser vers STABLE/public, acheter, supprimer archives, exposer secrets, changer produit hors ticket |
| **GitHub Actions** | Compilation et tests gratuits sous réglages validés | Toute utilisation susceptible de facturer, automations sans plafond clair |
| **Drive / Deliver** | Archives légères et reçus selon le protocole autorisé | Publication publique de contenus privés, suppression permanente sans politique |

**Règle d'autonomie :** « autonomie technique maximale à l'intérieur d'un ticket approuvé ; aucune autonomie pour modifier les interdits ». Un agent doit résoudre ses erreurs sans multiplier les micro-questions, mais signaler et stopper une opération qui exigerait une dépense, un secret ou une modification de production non approuvée.

### 6.3 Matrice RACI simplifiée

| Processus | R (réalise) | A (approuve) | C (consulté) | I (informé) |
|---|---|---|---|---|
| Vision, critères qualité | ChatGPT pilote | Utilisateur | Work/QA | Dépôt |
| Audit de bases libres | Work/Architecture | ChatGPT pilote | QA/licences | Utilisateur |
| Code dans branche | Work/Codex | Responsable technique désigné | QA | Utilisateur |
| QA indépendante | QA/ChatGPT + automates | ChatGPT pilote | Work | Utilisateur |
| Passage PREVIEW | Work intégration | ChatGPT pilote | QA | Utilisateur |
| Passage STABLE public | Work release | **Utilisateur** | ChatGPT + QA | Tous |
| Changement budget 0 FC | Personne sans aval | **Utilisateur** | ChatGPT | Tous |

R = Responsible, A = Accountable, C = Consulted, I = Informed. Les noms désignent des fonctions ; ils n'impliquent pas l'existence de plusieurs agents simultanément actifs ni un service autonome permanent.

## 7. Source de vérité, synchronisation et traçabilité

### 7.1 Trois couches et leurs missions

1. **Dépôt GitHub canonique** : code, assets réutilisables/licences, tests, scripts, CI, issues, branches, commits, releases et fichiers d'état. Devient canonique **après création/désignation explicite et vérification**.
2. **Sources du Projet ChatGPT** : copie figée de cette charte PDF et des annexes ; utile à toutes les conversations, mais peut être périmée si le dépôt change. À mettre à jour aux révisions majeures.
3. **Google Drive** : documents archivés, livrables validés, reçus et journaux de versions. Ne remplace pas Git pour l'historique du code.

**Les ZIP de livraison** sont des copies publiées, pas la source de vérité mutable. **Les messages Telegram** prouvent éventuellement la réception, pas la qualité ni l'origine exacte du commit.

### 7.2 Fichiers canoniques proposés

```text
KINMOTO/
  README.md
  PROJECT_STATE.json
  NEXT_ACTION.md
  CHANGELOG.md
  DECISIONS.md
  CONTRIBUTING.md
  docs/
    CHARTER.md
    PRODUCT_BRIEF.md
    QUALITY_GATES.md
    DEVICE_MATRIX.md
    ASSET_LICENSES.csv
    SOURCE_CANDIDATES.md
    QUOTA_POLICY.md
    RUNBOOK_CHAT_WORK.md
    RISK_REGISTER.md
    SESSION_LOGS/
  src/    assets/    tests/    scripts/
  .github/workflows/ci.yml
```

### 7.3 Invariant de transmission entre sessions

Chaque mission Work commence en notant : dépôt, branche, commit de départ, ticket, périmètre, statut des tests, quota connu ou inconnu, définition du résultat. Elle termine par : commit final, fichiers modifiés, tests exécutés et sorties, mesures, captures, bugs, prochaine action. **Pas de « fini » si le code n'est pas récupérable et les résultats tracés.**

### 7.4 Conversation pilote : séquence

1. L'utilisateur parle naturellement, sans obligation de code spécial.
2. ChatGPT classe : idée, décision, anomalie, question, demande d'exécution.
3. Les décisions ayant un impact sont rédigées en `DECISIONS.md` ou dans une proposition de changement.
4. Les tâches deviennent issues/tickets avec critères de sortie ; seul un lot prêt est confié à Work.
5. Work construit, teste, enregistre et rend son rapport.
6. Le pilote inspecte les artefacts **réels** (pas seulement le rapport de l'opérateur).
7. La préversion est essayée par le commanditaire ; il accepte, rejette ou demande correction.
8. Le registre et les fichiers du projet sont synchronisés au prochain jalon documentaire.

**Limite actuelle :** il n'existe pas de canal garantissant une lecture automatique du contexte ou des résultats entre toutes les conversations. Les fichiers et connecteurs sont la passerelle ; leur lecture doit être réellement exécutée. Une tâche Work non achevée ne peut pas être déclarée achevée ici par simple hypothèse.

## 8. Gouvernance du quota ChatGPT Plus / Work / Codex

### 8.1 Faits vérifiés au 4 novembre 2026 [C]

La documentation OpenAI indique que **Work et Codex partagent l'allocation incluse** dans l'offre, que l'utilisation dépend du modèle, de la tâche et des paramètres, et que selon le plan des fenêtres de cinq heures et hebdomadaires peuvent s'appliquer. Le quota exact et les heures de réinitialisation se lisent dans **Paramètres > Utilisation**. Les tâches cloud peuvent coûter davantage en quota ; les API sont facturées séparément. **Une évolution annoncée des règles en décembre 2026 impose de vérifier de nouveau cette section avant lancement d'un gros lot.**

**Nous ne connaissons pas le solde du compte du commanditaire.** Aucune estimation en nombre de messages n'est garantie. Ne jamais déclencher l'achat de crédits.

### 8.2 Allocation interne proposée [P]

| Niveau observable | Comportement |
|---|---|
| Quota confortable | Audit code / intégration d'un module borné et tests à valeur élevée |
| Quota moyen | Un seul lot modeste ; réserver la marge au débogage et à la sauvegarde |
| Quota faible ou inconnu | Clore les missions en cours, ne pas lancer de gros chantier ambigu |
| Quota épuisé | Continuer analyse ici si disponible ; reprendre l'opération après remise à zéro du quota, sans tâche fantôme |

**Pas de seuil en pourcentage présenté comme règle OpenAI** : si l'interface donne un pourcentage, les seuils 60/30 % peuvent servir de suggestion locale, et non de garantie.

### 8.3 Réduction du gaspillage

- Un ticket = une responsabilité + critères + fichiers cibles + tests ; éviter les prompts « construis tout le jeu ».
- Les commandes de lint, build et tests répétitifs tournent localement ou dans une CI gratuite configurée ; ne pas payer Work pour lire dix fois les mêmes logs.
- Préparer les assets et données sous licences avant de lancer de longues sessions d'intégration.
- Garder un budget de contexte : fichiers pertinents seulement, descriptions courtes du dépôt, index d'architecture, pas 3 Go d'anciennes archives dans chaque session.
- Distinguer recherche profonde ponctuelle et validation de patch ; utiliser l'effort de raisonnement adapté si la configuration le permet.
- Aucune orchestration multi-agent permanente présumée ; ne pas promettre des travaux en arrière-plan sans automatisation explicitement créée et autorisée.

## 9. Stratégie « déléguer le gros œuvre aux sources libres »

### 9.1 Principe

ChatGPT ne doit plus fabriquer à la main les parties critiques lorsqu'il existe déjà une base libre **juridiquement réutilisable, testable, techniquement compatible et mieux exécutée**. En revanche, réutiliser du code d'un projet complet ne signifie pas importer toutes ses mécaniques, ni mélanger plusieurs moteurs sans architecture commune.

### 9.2 Candidats documentés, pas encore sélectionnés [C/H]

| Source | Points à évaluer | Réserves vérifiées |
|---|---|---|
| `fastrouter/experiments-costa-vista` | Three.js/Vite, Rapier, moto, taxi, météo, garage, PWA, monde | Repo ~270 Mo avec assets ; commandes tactiles incomplètes ; MIT **code**, crédits/assets distincts |
| `pranshuparmar/neon-mayhem` | Jeu navigateur statique, moto, véhicules, mission, commandes tactiles | Apache-2.0 déclaré ; vérifier fichiers/ressources, performances et réemploi architecture |
| Kenney `Car Kit`, `City Kit Roads` | Véhicules et routes en modèles 3D | Packs CC0 consultés ; compatibilité graphique à optimiser ; attention à la direction artistique |
| Autres ressources | Moto/motard avec animation, textures, audio, décor, IA routière | Pas de sélection sans licence fichier par fichier et test technique |

Les deux premiers dépôts sont des **candidats à mesurer**, pas des bases approuvées. Les licences de code ne suffisent pas à autoriser automatiquement chaque asset du dossier. Le fait qu'un jeu ait été réalisé avec des agents IA ne garantit ni sa stabilité ni une intégration simple.

### 9.3 Grille de sélection sur 100 points [P]

| Critère | Poids | Mesure |
|---|---:|---|
| Sensations moto | 30 | Slalom, freinage, caméra, contact et cohérence commandes |
| Qualité visuelle utile | 20 | Moto, scène urbaine, assets, lisibilité, cohérence artistique |
| Performance et taille | 20 | FPS et mémoire Android/PC, poids téléchargé, rendu économique |
| Adéquation technique | 15 | Modularité, découplage simulation/rendu, réutilisabilité, complexité |
| Licences et dépendances | 10 | Droit de réutilisation, traçabilité des assets et dépendances |
| Missions/extension | 5 | Système de missions, sauvegardes, ergonomie de modification |

**Veto indépendants du score :** licence incertaine pour un composant indispensable, incompatibilité sur appareil cible, coût obligatoire, contrôles impossibles à corriger raisonnablement, dépendance serveur payante. Les scores sont attribués après exécution, jamais à partir des README seuls.

### 9.4 Protocole comparatif

1. Archiver les deux anciens jeux sans les promouvoir au rang de « bonne base ».
2. Vérifier commit, licence de code, inventaire des assets, taille et dépendances de chaque source.
3. Lancer les candidats **sans modification** sur HP et Android ; observer les commandes, le FPS et l'échelle de rendu.
4. Réaliser 5 scènes reproductibles et remplir la grille de qualité.
5. Tester l'extraction d'un module critique (moto ou trafic) dans une branche isolée, sans importer toute l'application.
6. Contre-audit indépendant du résultat et du coût d'intégration.
7. Décider : adopter une base, assembler proprement des modules, ou rejeter les candidats et garder une architecture légère éprouvée.
8. Seulement ensuite commencer la V1 reconstruite.

## 10. Architecture technique cible (proposition, non verdict)

**Une web app 3D statique et PWA**, sans serveur de gameplay ni compte joueur. Un code partagé Android, PC, puis certification iPhone. Candidats : Three.js/TypeScript/Vite ou adaptation d'un moteur libre existant ; ne pas geler le moteur avant benchmark. Une technologie nouvelle ne doit pas provoquer la perte des fonctions déjà éprouvées.

- **Simulation indépendante du rendu** : pas de calcul de collision basé sur la caméra, pas de rythme physique lié au FPS.
- **Entrées normalisées** : tactile et clavier se transforment en `steer [-1,+1]`, `throttle [0,1]`, `brake [0,1]`, `interact`, `pause`.
- **Conduite** : plan de route, frottement, inertie, orientation de roue et corps, adhérence et contact ; compromis plaisir / plausibilité.
- **Circulation** : graphe de rues, voie par voie, priorités, perception et espacement ; voisinage par grille spatiale lorsque nécessaire ; pas de tout-à-tout O(N²) non maîtrisé.
- **Carte** : 1 zone cohérente très détaillée avant agrandissement ; ressources partagées, instancing, atlas de textures, optimisation LOD.
- **Missions** : données, états, objectifs accessibles, paiement unique et économie cohérente.
- **Sauvegardes** : stockage navigateur local versionné + export/import ; test de migrations ; ne pas promettre synchronisation automatique multi-appareils.
- **PWA** : HTTPS, manifest, service worker, mise en cache vérifiée, mise à jour atomique et rollback.
- **Observabilité** : mesures locales facultatives, journaux QA exportables, aucune télémétrie distante obligatoire.

## 11. Versions majeures : contenu fermé et qualité croissante

**Attention au nom :** l'archive « V1 Les Premières Courses » du 4 novembre est un **prototype rejeté sur la qualité produit**, malgré ses fonctions. Les trois versions ci-dessous désignent la **nouvelle série de production**. Sur les branches internes, préférer `next-v1`, `next-v2`, `next-v3` pour éviter de confondre les builds.

### V1 — Le noyau réellement agréable

- Une zone urbaine compacte inspirée de Matonge/Victoire ; plusieurs rues reliées, au moins un vrai circuit alternatif ; 6 à 8 intersections comme cible de scope, non quota imposé si elles nuisent à la qualité.
- Une moto et un conducteur **visuellement crédibles**, dont les roues semblent liées à la chaussée, caméra stable, accélération, freinage et virage agréables.
- Environ 8 à 16 véhicules utiles selon benchmarks ; comportements de base : suivre route, ralentir, freiner, éviter et réagir aux incidents.
- Quatre **types réellement distincts** d'activité (course simple, livraison, défi de maîtrise, client spécial), avec itinéraires atteignables et rémunération sensée ; si l'une n'apporte rien, remplacer plutôt que maintenir un chiffre artificiel.
- Garage simple, réparation et amélioration de la moto ; sauvegarde exportable ; commandes clavier/tactile ; PWA offline après installation.
- Graphismes cohérents, assets sources libres audités, son et animation basiques mais convaincants.
- **Interdit :** annoncer V1 « finie » sans vidéo/captures 3D, essai Android et PC, session de conduite humaine et acceptation du commanditaire.

### V2 — Kinshasa vivante

- Deux ou plusieurs secteurs cohérents ; densité variable ; minibus/taxis/motos ; intersections enrichies ; météo qui affecte l'adhérence.
- Missions multi-arrêts, personnages récurrents, réputation et garage approfondi.
- Plus de modèles, animation de clients, langues et ambiance ; streaming progressif des zones.
- Portabilité iPhone testée et validée comme cible obligatoire du produit complet, sans attendre V3 pour découvrir les incompatibilités.
- Invariant : toutes les sensations et missions de V1 restent intactes, sauf évolution approuvée et mesurée.

### V3 — Ville, carrière et profondeur

- Plusieurs zones étendues, trafic multiniveau proche/distant, événements qui interagissent, carrière, petite flotte fictive hors ligne.
- Personnages, mini-récits, événements contextuels, ambiance radio avec créations/licences autorisées ; défis spécialisés.
- Expérimentation de poursuites ou scènes d'action **uniquement si compatibles avec l'identité et la sécurité du jeu**, pas comme fonctionnalité imposée.
- Optimisation avancée et maintien des performances, du coût nul, du mode hors ligne et des sauvegardes.
- Pas de promesse de milliers d'agents 3D simultanés, photoréalisme AAA ni multijoueur permanent gratuit.

## 12. Assurance qualité : quatre portes non substituables

| Porte | Preuves obligatoires | Qui valide |
|---|---|---|
| **G1 Fonctionnelle** | Tests unitaires, intégration, mission complète, collision, sauvegarde | QA + pilote |
| **G2 Visuelle** | Rendu **WebGL réel**, images/vidéos aux points canoniques, qualité contrôlée | QA + utilisateur |
| **G3 Performance** | Mesures FPS, pauses, taille bundle, mémoire si mesurable sur matériel cible | QA + utilisateur |
| **G4 Jouabilité réelle** | Session d'au moins 15–20 min Android + PC ; iPhone avant déclaration multi-plateformes | **Utilisateur / testeuse** |

Les verdicts possibles sont `PASS`, `FAIL`, `BLOCKED`, `NOT_TESTED`. Un `BLOCKED` n'est jamais `PASS`. Une capture emulée ne prouve pas un rendu WebGL sur téléphone réel. Les mesures doivent porter la date, le modèle, le navigateur, la version du code, la scène, les paramètres graphiques et les éventuelles limites de mesure.

**Définition de terminé :** code relu, licence vérifiée, tests pertinents passés, effet visible inspecté, risque de régression évalué, changements documentés et artefacts reproductibles. **Définition de validé utilisateur :** note de ressenti et de qualité suffisante sur les piliers essentiels. Ce sont deux décisions distinctes.

### 12.1 Cas adverses imposés

- Gauche/droite dans chaque caméra et vitesse ; appui simultané et relâchement tactile.
- Perte d'adhérence et impression de flottement ; position de roue, angle, ombre, terrain.
- Choc léger/répété/latéral ; pas de double dégât ni de voiture qui traverse.
- Freinage voiture devant obstacle et véhicule suiveur ; carrefour occupé.
- Mission entamée, pause, fermeture, reprise, paiement une seule fois.
- Perte d'Internet après cache ; bascule hors ligne et rechargement.
- Changement profil graphique sans changer les résultats de simulation.
- Pression mémoire ; changement de contexte WebGL ; redémarrage sans sauvegarde corrompue.
- Navigation mobile portrait/paysage, contrôles visibles, pas de boutons recouverts.
- Import de sauvegarde de version précédente, refus propre si incompatible.

## 13. Publication : éviter qu'une expérimentation écrase le jeu existant

**Chaîne obligatoire :** `DEV` → `PREVIEW` → `CANDIDATE` → `STABLE`.

- Chaque travail se fait sur branche, sans force-push de la branche publique ni écrasement d'un lien public au cours d'essais.
- Une PR contient résumé, tests, captures et licences. Une CI gratuite bloque les erreurs déterministes.
- `PREVIEW` possède un lien distinct accessible pour les essais ; l'URL officielle ne change pas sans approbation.
- Toute version STABLE a un tag Git, une archive des sources, le build, un manifeste de sommes SHA-256, un rapport QA, un statut des appareils.
- Rollback = republier le dernier build approuvé sans effacer les sauvegardes locales ; vérifier la compatibilité des données.
- Le commanditaire conserve le pouvoir **GO / NO-GO** pour rendre publique une nouvelle version.

La réussite d'un déploiement HTTP n'est jamais présentée comme une certification ludique.

## 14. Droits, licences, sécurité et coût

- **Code source MIT/Apache :** réutilisation possible sous respect des notices, licences et autres obligations ; vérifier commit et fichiers concernés.
- **Assets :** audit **asset par asset**, même dans un dépôt dont le code est MIT ; conserver titre, auteur, URL source, licence, preuve de téléchargement, modifications, compatibilité et mention requise.
- **CC0 :** ressources bien adaptées quand le statut est confirmé sur la page officielle et dans les fichiers reçus.
- **Cartes OSM :** si utilisées, respecter l'ODbL/attribution et évaluer le statut des données dérivées.
- **Images de Kinshasa trouvées sur Internet :** références visuelles pour l'étude, non à intégrer au jeu sans licence adéquate.
- **GitHub :** ne jamais pousser clés, tokens, messages privés, coordonnées personnelles ni exports ChatGPT bruts. Choisir public/privé en connaissance des risques de visibilité et de quota.
- **CI et hébergement :** choisir des offres gratuites sans possibilité de facturation surprise, vérifier les limites au moment d'activer les services. GitHub Actions gratuit sous conditions de runner/repo ; Vercel Hobby réservé au personnel non commercial ; Cloudflare Pages Free a des limites de builds et fichiers.
- **Téléphone :** ne pas collecter de données d'appareil inutiles ; pas de publicité ni de traçage distant obligatoire.

## 15. Registre des risques critiques

| ID | Risque | Mesure préventive | Condition d'arrêt |
|---|---|---|---|
| R01 | Une base libre est juridiquement incompatible | Inventaire licences avant integration | Asset essentiel sans droits documentés |
| R02 | Sensation moto toujours mauvaise | Prototype piste + benchmark humain | Pilotage noté insuffisant |
| R03 | V1 graphique moins belle qu'une ancienne | Captures canoniques et revue modèle moto | Régression non expliquée et non approuvée |
| R04 | Android bas de gamme manque de RAM | Eco mode, scènes limitées, mesure réelle | Crash/rechargements excessifs |
| R05 | iPhone fonctionne seulement en émulation | Banc WebGL réel iOS | « Compatible iPhone » non justifié |
| R06 | Work/Codex atteint son quota | Lots bornés + état commité | Travail non sauvegardé ou quota nul |
| R07 | GitHub ou Drive divergent | Commit ID + version du document, log de décision | Deux « versions officielles » concurrentes |
| R08 | Hébergement gratuit change ses règles | Static build portable, export et miroirs | Dépense obligatoire proposée |
| R09 | Sauvegarde perdue après mise à jour | Export/import, migrations et rollback | Migration non testée |
| R10 | API/service tiers ou asset dissimule télémétrie | Audit réseau et dépendances | Donnée envoyée sans nécessité/consentement |
| R11 | Le mandat Work est trop large | Un ticket, une portée, une branche | Modifications hors ticket sans décision |
| R12 | Objectifs irréalistes dans le calendrier | Mesurer, prioriser sensations, reporter scope | Promesse de qualité sans plan de vérification |

## 16. Premier programme de travail, sans démarrer le jeu

**A0 : installer l'usine documentaire et technique** : désigner dépôt unique, archiver anciennes sources, importer cette charte, créer états canoniques, backlog, conventions de branches, CI minimale gratuite et protocole de prompts. Vérifier réellement les accès. Ne pas toucher au déploiement public.

**A1 : audit comparatif des bases libres** : Neon Mayhem, Costa Vista et autres candidats ; licence et assets ; essai de conduite sur HP/Android ; scorecard 100 points ; recommandation justifiée.

**A2 : atelier de sensations moto** : isoler le meilleur noyau utilisable, piste référence, 3D crédible, réglages, test de 15 minutes ; interdire expansion de la ville avant validation.

**A3 : vertical slice KIN MOTO** : une zone reconnaissable, deux missions de bout en bout, un garage, une circulation maîtrisée ; preuve de croissance qualitative.

**A4 : V1 candidate complète** : atteindre le contenu fermé de V1, QA, tests matériels, sauvegardes, release candidate puis accord STABLE.

Ces cinq lots sont des **étapes internes à la V1**, et non cinq mises à jour publiques. Chaque lot est subdivisé en tickets que Work peut terminer avec un état récupérable.

## 17. Codes de continuité (facultatifs, jamais magiques)

- `KINMOTO|SYNC` : lire dépôt, `PROJECT_STATE.json`, ticket courant, dernier rapport QA ; expliquer où en est le projet.
- `KINMOTO|DECIDE` : prendre une demande de la conversation et préparer décision/conséquence sans modifier la production.
- `KINMOTO|WORK|CONTINUE` : rédiger et/ou exécuter le ticket autorisé après vérification du quota et de la branche.
- `KINMOTO|AUDIT` : audit contradictoire du commit, du rendu et de la QA.
- `KINMOTO|RELEASE|CHECK` : revue des quatre portes et recommandation GO/NO-GO.
- `KINMOTO|SAVE` : écrire journal de session, décisions, prochain pas et commit, si accès réel ; sinon produire les fichiers à importer manuellement.

**Un code ne provoque aucun effet à lui seul.** L'agent doit avoir les outils, les droits et les sources nécessaires ; il doit indiquer exactement ce qu'il a réellement réalisé.

## 18. Contrat de première conversation de pilotage

L'utilisateur doit pouvoir ouvrir un chat du Projet, parler sans syntaxe particulière, critiquer un graphisme, proposer une mission, ou demander un audit. ChatGPT répond d'abord à la demande puis classe sa conséquence sur la roadmap. Il évite les micro-questions. Lorsqu'une tâche exige Work, il fournit un ticket borné et son objectif, puis Work exécute dans un contexte distinct. Après retour, le pilote retrouve le résultat par GitHub, fichiers ou rapports, vérifie et rend un compte rendu **concret** ; il n'imagine pas le résultat d'une conversation inaccessible.

**Rythme :** discussion libre à volonté ; production par lots ; publication seulement aux portes de version validées. Aucun agent n'est présumé travailler en continu sans mécanisme et autorisation explicites.

## 19. Critères de clôture de cette phase documentaire

- Les trois PDF sont présents, lisibles, numérotés, avec leurs sources et une édition.
- Une version Markdown copiable dans le dépôt et les sources du Projet est fournie.
- L'organisation Chat / Work / GitHub / Drive est formulée en actions vérifiables.
- Les préférences, refus, contraintes et faits historiques sont documentés sans faire passer une proposition pour une décision de l'utilisateur.
- Une mission A0 claire est disponible pour le futur lancement.
- L'absence de déploiement ou de modification de code dans cette étape est explicitement signalée.

## 20. Sources documentaires et références vérifiées le 4 novembre 2026

1. Cahier antérieur : `KIN_MOTO_CAHIER_DIRECTEUR_ZERO_FC_V1_20261104.md` (source interne, 4 nov. 2026).
2. Audit précédent : `KIN_MOTO_AUDIT_DIRECTEUR_V1_V2_V3_20261104.md` et backlog JSON (source interne).
3. Archive V1 livrée : `KIN_MOTO_V1_FINAL_ANDROID_PC_20261104.zip`, notamment `docs/QA_REPORT.json` et `RAPPORT_RECETTE_FINAL_20261104.md` (preuve technique, pas preuve d'acceptation produit).
4. OpenAI, Work et Codex : https://help.openai.com/fr-fr/articles/20001275-chatgpt-work-and-codex
5. OpenAI, gestion du quota : https://help.openai.com/fr-fr/articles/20001516-managing-usage-with-gpt-6-astra-in-work-and-codex
6. OpenAI, limites futures annoncées : https://help.openai.com/en/articles/20001625-understanding-chatgpt-and-codex-usage-limits
7. Source Costa Vista : https://github.com/fastrouter/experiments-costa-vista
8. Source Neon Mayhem : https://github.com/pranshuparmar/neon-mayhem
9. Kenney Car Kit : https://kenney.nl/assets/car-kit ; City Kit Roads : https://kenney.nl/assets/city-kit-roads
10. GitHub Actions coûts/limites : https://docs.github.com/fr/actions/concepts/billing-and-usage
11. Cloudflare Pages limites : https://developers.cloudflare.com/pages/platform/limits/
12. Vercel Hobby : https://vercel.com/docs/plans/hobby ; conditions : https://vercel.com/legal/terms
13. MDN PWA : https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Offline_and_background_operation
14. MDN PWA installation : https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Making_PWAs_installable

**Fin de la charte maître.** Toute révision majeure doit être accompagnée d'un diff de décisions, d'un numéro d'édition et d'un nouveau statut d'approbation.
