# CAHIER MÈRE — RIZ-112 → MATRICE

**Référence unique de continuité de l'expérience pédagogique RIZ-112.**

- **Code de reprise** : `RIZ112|CONTINUE` (alias `RIZ/CONTINUE`).
- **Identité** : laboratoire conceptuel et technique de construction du moteur mathématique de **MATRICE ADN R8**. **Ce n'est pas un moteur qui conseille des recettes**.
- **Source canonique et append-only** : `Terminator364/PROJECT-DRAFTS`, dossier `MOTEUR-BLESSING/labs/RIZ112/` sur `main`. `CAHIER_MERE.md` donne l'état consolidé ; `JOURNAL_EVENEMENTS.jsonl` conserve les entrées factuelles horodatées ; `DECISIONS.md` conserve les décisions, révisions et objections ; `CHECKPOINT.json` pointe vers code, preuves et statut.
- **Date de naissance du cahier** : 2026-10-16. Tout élément antérieur reconstitué est signalé comme **RECONSTRUIT** à partir de propos disponibles ; ceci **n'est pas une transcription exhaustive de tous les anciens échanges**.
- **Dernière version du laboratoire avant étape 5** : [Étape 4](https://github.com/Terminator364/PROJECT-DRAFTS/blob/main/MOTEUR-BLESSING/labs/RIZ112/STEP4_CHECKPOINT_20261016.json), 112 cases au catalogue, **15 cases réellement exécutées**, 22/22 tests sur Python dans ChatGPT, **IC = null** faute de données de qualité calibrées.

## 0. Mandat utilisateur, en ses propres termes

> « Nous ne construirons pas en fait un moteur qui nous dit comment préparer les riz. [...] à partir des données initiales [...] certaines données devant [...] être analysées en JSON [...] nous donnera un IC des préparations de riz [...] tout ça c'est pour la matrice. » (16/10/2026 ; extraits de la présente conversation)

> « Créer un cahier mère, dans lequel tu écrit toutes les réflexions, processus ou hypothèse, tu les enregistre tes actions, mes réponses, feedback ou autres de maniere continue pour oe projet, c'est bien synchroniser pour chaque conversation et ça aidera lorsque l'on passera à la matrice [...] » (16/10/2026 ; message déclencheur)

**Interprétation opérationnelle** : construire un système prédictif exclusivement **avant T₀** qui ingère des dossiers JSON sourcés, exécute des formules propres aux mondes/cases et des interactions conditionnelles, propage incertitude et dépendances, puis, **seulement après apprentissage et calibration réelle**, retourne `IC = 100 × P(Q ≥ 85 | X_{T₀})` pour la qualité du riz. Les caractéristiques mesurées après T₀ restent les **étiquettes de validation** et n'entrent jamais dans les entrées prévisionnelles.

## 1. Objectif stable

- Cas pilote : **2 portions de riz blanc moelleux avec grains séparés**. Exemple de départ **160 g de riz** et **300 mL d'eau** ; ce ne sont **pas** des quantités idéales universelles.
- `Q` : qualité finale, mesurable selon un protocole **à définir et figer avant expériences**. `Q ≥ 85/100` définit le succès **après** observation ; `IC` désigne la probabilité **avant** préparation de cet événement.
- Le seuil **85/100** ne prouve ni la validité de l'échelle Q ni celle de la probabilité. Aucun IC ne doit être fabriqué en l'absence de données et de calibration.
- Les **112 cases** couvrent entrées, variables dérivées, conditions, actions prévues, interactions, contrôles et sorties. Elles ne sont ni 112 facteurs indépendants ni 112 coefficients à additionner.

## 2. Évolution conceptuelle et révisions

### 15 octobre 2026 — contexte historique reconstitué

À partir des échanges antérieurs retrouvés : l'utilisateur exige un exemple exhaustif A à Z (riz, eau, quantités, température, casserole, couvercle, matériel, ordre), **en contexte prématch/précuisson uniquement** ; règles physiques qui s'adaptent aux quantités et conditions réelles, calculs des plages et dépendances, non une recette figée. Les **112 cases** de l'analogie préparent le raisonnement sur **62 mondes** de MATRICE. Interactions, compensations, incompatibilités et ordre sont essentiels ; un simple total de bonus/malus est contraire à la conception. Source : contexte de conversations précédentes, synthétisé, non verbatim complet.

### 16 octobre — décision utilisateur, étape 1

Le résultat choisi explicitement : **riz moelleux avec grains séparés**, deux portions ; la réussite vise le seuil Q = 85/100. Première proposition d'une architecture avec données initiales, formules, interactions, scénarios et sortie de confiance. Critique anticipée : un moteur de recettes serait une mauvaise finalité.

### Étape 2 — catalogue des 112 cases

Catalogue organisé à titre didactique : `01–48` conditions initiales, `49–85` opérations, `86–98` corrections conditionnelles, `99–112` sorties/contrôles. **Rectification** : cette disposition par phases de cuisine n'implique pas que le moteur prédictif doive voir les opérations et observations futures. Les règles annoncées avant T₀ peuvent être des entrées ; les actions futures effectivement réalisées et le Q constaté sont hors de l'espace des prédicteurs.

### Étape 3 — recadrage majeur du mandat

L'utilisateur corrige explicitement : **pas de recette**, mais un **moteur d'IC depuis données initiales JSON**. Adoption d'un contrat de temps strict `available_at <= freeze < start`; UNKNOWN ≠ ZERO ; mécanismes en graphe sans pénalisation double ; causalité et propagation d'incertitudes. L'exemple A/B/C ne représente aucune vraie expérience. `IC = null` en absence de calibration.

### Étape 4 — premier noyau exécutable

ZIP d'origine : `RIZ112_ETAPE4_Noyau_Mathematique_2026-10-16.zip` ; SHA-256 `5e28c684e0cd2743db8e95c7ced0625bbfd05d8fd02fc559e4663424e7c52764`, **29 039 octets, 18 fichiers**, CRC conforme. Calculs pilotes du bilan d'eau, chaleur, évaporation, hydratation et indice d'amidon de surface (**pas une mesure de texture**). 15 cases reliées aux 16 nœuds du graphe ; 16 entrées, dont certaines **hypothèses** non observées. 22/22 tests réussis (ChatGPT container), pas de validation externe. Bilan massique contrôlé ; cas D d'information manquante rejeté. **Les constantes sont simplifiées et non calibrées**.

**Exemples V4** : A couvercle ajusté : évap. ~63,65 g, hydrat. possible ~216 g ; B couvercle fuyant : évap. ~139,60 g, hydrat. ~168,40 g ; C chauffe faible : évap. ~16,78 g, hydrat. ~94,67 g. Même objet de prédiction ; les différences ne sont pas des IC. Cet exercice enseigne des relations contre-intuitives : moins d'évaporation peut coexister avec une hydratation insuffisante si le temps chaud manque.

### Étape 5 — ouverte par demande « crée un cahier mère ; puis continue »

Création du cahier consolidé, du journal structuré append-only, des règles de synchronisation et d'un protocole de mesure/vérification avant tout entraînement. **Aucune échelle de qualité pondérée n'est encore approuvée par l'utilisateur**, et aucun jeu de préparations réelles n'existe. Le statut scientifique reste `NOT_CALIBRATED`.

## 3. Architecture mathématique non négociable

`INPUT_JSON (pré-T₀ + provenance)` → `VALIDATION/QUALITÉ/PIT` → `FONCTIONS DE SOUS-PARAMÈTRES` → `GRAPHE DE MÉCANISMES` → `INTERACTIONS/CONTRAINTES/SCÉNARIOS JOINTS` → `FEATURES AVEC LIGNÉE` → `MODÈLE APPRIS SUR OBSERVATIONS INDÉPENDANTES` → `CALIBRATION/TEST CHRONOLOGIQUE` → `IC OU ABSTENTION + EXPLICATION/PROVENANCE`.

Ne jamais remplacer cette chaîne par une baseline de fréquence ou une moyenne « habillée » en analyse multimonde. Émettre un **reçu de traçabilité** : cases déclarées/exécutées, équations et entrées effectivement consommées, chemins de dépendances, données inconnues, mécanismes inactifs, historique du modèle, état de preuve, statut de calibration. Des filtres de gouvernance ne sont pas des contributions causales additionnelles.

## 4. Inventaire des hypothèses, risques et objections

| ID | Hypothèse/proposition | Statut | Ce qui manque |
|---|---|---|---|
| H01 | Bilan hydrique comme mécanisme de premier ordre | TESTÉ LOGICIEL / NON VALIDÉ PHYSIQUEMENT | Mesures réelles eau évaporée/absorbée, pertes, cuissons |
| H02 | Approximation d'énergie et de temps chaud | DIDACTIQUE | Énergie réellement transmise et rendement par équipement |
| H03 | Progression hydratation linéaire `min(1, T_hot/T_need)` | DIDACTIQUE | Cinétique réelle, variété, température, validation |
| H04 | Multiplicateur de couvercle et taux d'évaporation | DIDACTIQUE | Mesures observées et distribution d'incertitude |
| H05 | Amidon de surface comme variable utile à la séparation | NON ÉTABLI | Loi empirique indépendante, interaction avec variété |
| H06 | Qualité Q/100 mesurable reproductiblement | EN CONCEPTION | Définitions, protocole, accord évaluateurs, seuils, approbation |
| H07 | Les 112 cases ont un effet indépendant | **REJETÉE** | Plusieurs sont observables, contrôles ou sorties ; dépendances/duplications |
| H08 | Un IC chiffré est admissible avant vraies préparations calibrées | **REJETÉE** | Dataset pré-T₀ / post-T₀, validation temporelle |
| H09 | Date déclarée dans JSON prouve publication PIT | **REJETÉE** | Archivage tiers vérifiable, empreinte et capture source |
| H10 | Effets locaux additifs des cases | **REJETÉE** | Graphe causal/fonctionnel avec interactions et compensations |
| H11 | Modèle transférable tel quel au football | **REJETÉE** | Transférer *contrats et architecture*, non les équations culinaires |

## 5. Transposition contrôlée vers MATRICE

| Laboratoire RIZ-112 | MATRICE ADN R8 |
|---|---|
| `T₀` début de préparation | Coup d'envoi (gel pré-match) |
| Dossier initial JSON | Dossier fixture JSON/PIT |
| 112 cases de différentes natures | 62 mondes canoniques, 372 propositions de sous-paramètres, plusieurs rôles |
| Hydratation, transfert de chaleur, bilan d'eau | Processus propres aux mondes (forme, calendrier, effectifs, météo, etc.) |
| Fuite couvercle → eau → texture | Absence joueur → minutes/rotation/structure → intensité de buts, **sans compter trois fois** |
| Q≥85 | Over 1,5 buts pendant les 90 minutes réglementaires |
| IC sur 100 | IC Over 1,5/100 pré-match |
| Cuisons réelles & qualité observée | Matchs réels & score final strictement hors entrées |

**Transfert autorisé** : type des données, schémas, lignée, test de fuite, graphe, incertitudes jointes, audit contradictoire, métriques, abstention ; **interdit** de copier des coefficients numériques ou relations culinaires vers les équipes. Le moteur sportif actuel est distinct et reste `EXPERIMENTAL_NOT_APPROVED` ; le précédent pilote 4 matchs n'a exploité **aucune des entrées numériques des 62 mondes** et a seulement calculé des baselines de ligue. Ce contre-exemple guide nos tests anti-régression.

## 6. Synchronisation et méthode de travail entre conversations

1. Avant `RIZ112|CONTINUE`, lire dans cet ordre : `CHECKPOINT.json` → `CAHIER_MERE.md` → fin de `JOURNAL_EVENEMENTS.jsonl` → `DECISIONS.md` → plus récent audit/test.
2. **À chaque avancée vérifiée**, ajouter au journal : UTC, acteur, événement, décision ou hypothèse, dossier/chemin, preuve hash et statut. Signaler explicitement ce qui n'a PAS été observé. Ne jamais effacer l'ancienne ligne pour réécrire l'histoire ; les rectifications sont des événements supplémentaires reliés par `supersedes`.
3. Écrire dans GitHub l'état de référence et les scripts **avec tests**, sauvegarder les archives/checkpoints sur Drive et/ou Bibliothèque ChatGPT ; ajouter le reçu et l'empreinte. Windows est un miroir **seulement après vérification de lecture**, jamais une preuve supposée.
4. Les modifications de projet dans une conversation ne deviennent pas automatiquement des synchronisations dans toutes les conversations futures. La continuité repose sur la **relecture de ce dossier canonique** au prochain déclenchement, suivie d'une nouvelle écriture lors de la séance active. Aucun agent de fond permanent n'est prétendu.
5. Appliquer chaque fois construction → audit → contre-audit → correction → ré-audit ; séparer tests logiciels, preuves physiques et validation de prédiction.
6. Ne pas changer l'objectif, ni approuver silencieusement la métrique Q, ni injecter la fin de la préparation dans ses entrées.

## 7. État scientifique exact

- **112 cases** : inventaire conceptuel, **15 cases** exécutées en étape 4, pas 112 calculs calibrés.
- **Nombre de préparations réelles instrumentées** : **0**.
- **Barème Q approuvé et reproductible** : **NON**.
- **Jeu d'apprentissage/validation réel** : **NON**.
- **Probabilité calibrée** : `null` / **ABSTAIN**.
- **Étape active** : **5 — schéma qualité et contrat de preuve**, puis collecte et calibration avec contrôles chronologiques.

## 8. Questions de conception ouvertes, à poser quand elles deviennent bloquantes

- Comment mesurer séparément « moelleux » et « grains séparés » ? Mesure instrumentale ou protocole d'observateurs ?
- Quels critères constituent des **veto** indépendamment de la qualité moyenne (riz brûlé, sécurité, grains collés) ?
- Comment convertir ces mesures en Q/100 *sans pondérations arbitraires* ? Une étude d'accord inter-évaluateurs et une validation externe sont souhaitables.
- Quel protocole de préparation est effectivement connu avant T₀, sans présumer des réactions futures de l'opérateur ?
- Comment attester la capture des entrées au temps T₀ de façon indépendante ?

**Fin du cahier initial — les entrées futures seront ajoutées comme journal et décisions, et le checkpoint indiquera la version courante.**

## 9. Nouvelle directive et Étape 6 — 16 octobre 2026

**[DIRECTIVE UTILISATEUR]** « Ouo veille à la synchronisation. Continue les travaux, j'insiste notamment sur les faits que réellement les 112 contribue et non seulement 15 ». La priorité ne se réduit plus à inventorier les fiches : garantir une **exécution traçable pour chaque identifiant** et rendre visible la part **réellement reliée aux équations physiques**.

**[CONSTRUCTION TESTÉE]** `step6/engine112.py` exécute le contrat de 112 cases : **44 déclarations pré-T₀, 4 événements calculés/projetés, 37 plans d'actions, 13 politiques conditionnelles et 14 contrats de résultat futurs**. Il rejette une case absente, une date post-gel, une variable `UNKNOWN` faussement utilisée comme calculée, des unités/types incohérents, des contradictions pratiques et une qualité finale injectée comme prédicteur. Chaque cas produit un reçu d'exécution. Trois scénarios JSON indépendants A/B/C sont enregistrés.

**[AUDIT CONTRADICTOIRE]** 112/112 **contrats traités**, mais seulement **15 cases dans le noyau physique d'origine**. Les cas 043 (temps théorique de montée en température) et 048 (bilan hydrique prévisionnel) sont désormais des **dérivations mathématiques explicitement rattachées aux mécanismes existants**, sans constituer deux nouvelles influences indépendantes. La case 044 (stabilité du frémissement) reste **non quantifiée** ; la case 046 (fuite vapeur) est un **proxy non validé**. Les autres valeurs peuvent changer les contraintes, la disponibilité, la branche prévue ou la définition du résultat — **pas l'IC sans mesures et calibration**. Dans les exemples, 20 des 44 entrées pré-T₀ restent explicitement inconnues.

**[TESTS]** 42/42 nouveaux tests V6 (dont suppressions systématiques de 108 entrées externes, correction de driver UNKNOWN et types), anciens 22 +31 +10 tests = **105/105 PASS**, logiciel ChatGPT Python 3.13. Pas de tests Windows dans cette séance ; le laboratoire ne modifie pas le code sportif MATRICE.

**[CONCLUSION SCIENTIFIQUE]** L'exigence de **traçabilité des 112** est maintenant satisfaite **dans la couche de contrat de rôle**. L'exigence « 112 facteurs contribuent mathématiquement à une probabilité prédictive validée » **n'est pas satisfaite** : elle exigerait des définitions observables, des lois pertinentes et des données indépendantes, et serait de toute manière mal posée pour les 14 cibles futures qui ne peuvent pas être des prédicteurs. IC reste `null`.

**[PROCHAINE PRIORITÉ]** augmenter la couverture *des mécanismes légitimes* plutôt que distribuer arbitrairement 97 coefficients, mesurer Q avec un protocole pré-enregistré et produire des évaluations indépendantes. Voir `step6/README_ETAPE6.md` et `step6/AUDIT_CINQ_CYCLES_ETAPE6.md`. Le code de reprise et les journaux restent canoniques sur GitHub ; aucun travail de fond n'est exécuté entre conversations.

---

## Étape 7 (2026-10-16) — Contre-audit du graphe et premières contraintes calculables

**Déclencheur utilisateur :** « Continue » après l'étape 6, dans le mandat conservé d'une contribution **réelle** des 112 cases (ne pas se contenter de compter des clés JSON).

**Découverte majeure :** les dépendances V6 ont des orientations et fonctions hétérogènes : certaines représentent la causalité candidate, d'autres des conditions préalables, et d'autres des références croisées à des résultats futurs. Un seul DAG prédictif ne peut donc pas les réutiliser sans correction. Le nouvel audit montre **169 arcs au total, dont 17 références rétrogrades à des labels poststart et deux dépendances circulaires 054→055/056**. Ces 19 arcs sont séparés/refusés ; les **150 arcs structurels candidats** restants forment un DAG sur les 112 cases. Cette correction préserve la source historique intacte et documente les suppressions ; elle n'implique pas que les 150 arcs soient des lois causales établies.

**État réel de l'influence :** 112/112 traitées comme rôles ; 17 chemins numériques simplifiés (dont deux sorties dérivées) ; 50 cases dotées d'un chemin hypothétique jusqu'à Q112, **62 sans chemin**. Les cases 014 (ajustement du couvercle), 037 (température initiale eau), 038 (température initiale riz), 043 (moment d'ébullition) ont une valeur dans le noyau ou comme dérivé mais ne sont pas reliées au label dans le graphe déclaratif. Cela ne prouve pas leur inutilité physique : cela démontre une lacune de *documentation du graphe*.

**Nouvelles équations/contraintes de faisabilité, sans coefficients fictifs :** ressources hydriques suffisantes pour l'eau prévue (conversion simplificatrice 1 g ≈ 1 mL) ; volume d'eau seul inférieur à la capacité du récipient (condition nécessaire, NON suffisante pour inclure le riz et la marge de sécurité) ; cohérence présence matériel ↔ actions projetées (couvercle, balance, doseur, passoire, ustensile, service, puissance réglable) ; énergie requise si démarrage de chauffe prévu. Dix vérifications, états `CONSISTENT`, `INCONSISTENT`, `UNRESOLVED` ou `CONSISTENT_NECESSARY_ONLY`. Ces vérifications modifient **l'admissibilité et les risques d'exécution déclarée**, pas un score de texture ni l'IC : leur effet quantitatif sur Q n'est pas identifié.

**Réévaluation des 112 fiches :** `step7/GAPS_112_V7.json` contient chaque case et son statut de lien numérique/structurel, ses manques et la prochaine exigence de preuve. Le nombre de cases sans lien Q reste visible, sans flèches artificielles pour atteindre artificiellement « 112 chemins ».

**Revalidation de tous les tests : 141/141 PASS** en environnement Python 3.13/Linux (22 historiques étape 4 sous leur arborescence originale ; 31 étape 5 ; 10 journal ; 42 étape 6 ; 36 nouveaux tests étape 7). La première tentative de lancer les tests historiques depuis le mauvais répertoire avait généré des erreurs d'import/chemin ; la méthode reproductible correcte utilise l'archive originale étape 4 et les 22 tests passent sans modification de leurs sources.

**Aucune expérience réelle, aucun barème Q approuvé, aucun entraînement, aucun IC légitime.** Projet sportif MATRICE inchangé. La transposition devra employer la même détection de dépendances rétrogrades, cycles, faisabilité et chemin réellement calculé avant de revendiquer une couverture des 62 mondes.


## 11. Correction utilisateur sur les « paliers » — 16 octobre 2026

**[DIRECTIVE DE L'UTILISATEUR, formulation conservée dans le journal]** : « Donc tu n'as toujours pas fini de me... je n'était pas, c'est si compliqué que ça pour les faire. Parce que là on y va par paliers. Et d'ailleurs faudrait écrire dans le caim. » L'expression « caim » est interprétée comme **Cahier mère** dans ce projet ; cette interprétation n'est pas présentée comme une citation reformulée.

**[RECONNAISSANCE DU MANQUEMENT]** : la structure des 112 cases était construite, mais les réponses répétaient des annonces de progrès en confondant l'inventaire, la validation de contrat et la contribution démontrée. En étape 7, seules 50 cases sur 112 possédaient un chemin *déclaratif* jusqu'à Q112, alors que 62 n'avaient pas ce chemin, dont 4 avec un calcul numérique isolé. Même ces 50 chemins ne prouvent aucun effet empirique. La frustration de l'utilisateur est donc liée à un écart de livraison réel, pas à une simple incompréhension.

**[DÉCISION RÉVISÉE D014]** : les paliers sont des **moyens de contrôle** et non des livrables autosuffisants. Leur répétition ne doit pas devenir une justification pour éviter de finir le moteur fonctionnel. À la reprise, priorité à un **lot de raccordement complet des 62 cas** et à l'audit des 50 autres selon leurs rôles réels, pas à un nouveau palier décoratif. Chaque cas aura une observation ou action initiale, une route mathématique/conditionnelle/contrôle ou un contrat de cible, une sortie observable et un test de mutation ; chaque chemin non démontré sera identifié. Interdiction d'ajouter une flèche causale fictive ou un malus arbitraire pour remplir un tableau.

**[DÉFINITION DE « TERMINÉ » — deux portes séparées]** :
- **Fin du moteur fonctionnel de laboratoire** : les 112 cases possèdent des effets de traitement réellement exécutés, adaptés à leur rôle (y compris les 14 critères-cibles sans fuite temporelle), et des essais de mutation prouvent leurs conséquences de traitement pertinentes. Une action facultative peut rester inactive dans un dossier : son branchement doit être testé lorsqu'elle est applicable.
- **Fin du moteur prédictif fiable** : barème de qualité Q approuvé, données de préparations réelles appariées avant/après cuisson, équations identifiées ou modèle statistique entraîné, validation hors-échantillon et calibration de P(Q≥85). Aucun IC légitime avant cette seconde porte.

**[ÉTAT À NE PAS MASQUER]** : 112/112 contrats de rôle traités, 17 chemins numériques simplifiés (15 moteurs initiaux + 2 dérivés), 62 absences de chemin Q (25 préalables, 26 actions, 11 corrections), 14 résultats comme cibles et non entrées, 141/141 tests logiciels antérieurs, zéro effet scientifique validé, IC `null`. Cette directive a été enregistrée, mais **le travail de raccordement des 62 n'est pas affirmé terminé dans cette entrée**.

**[TRANSFERT MATRICE]** : cette distinction est impérative : 62 mondes répertoriés ne garantissent pas qu'un match a été analysé à travers eux. L'IC Over 1,5 doit être issu uniquement des mécanismes réellement calculés, admissibles en pré-match, et validés ; les gardes et les définitions de résultat ne deviennent pas des prédicteurs par décret.

## §13 — Reprise après D014 : raccordements fonctionnels, étape 8 (2026-10-16)

**Instruction utilisateur (par reconnaissance vocale ambiguë) :** une formulation comporte les mots « accord », « synchronisation » et « cahier mère ». Interprétation opératoire à confirmer si nécessaire : poursuivre les travaux tout en conservant le Cahier mère synchronisé. Les mots incertains ne sont pas traités comme une citation exacte.

**Travail exécuté :** `step8/functional_routes.py` applique 62 routes nommées aux 62 lacunes du registre D014 : 22 données/ressources pré-T0, 3 prévisions, 26 actions planifiées et 11 politiques conditionnelles. En particulier :
- les ressources et instruments disponibles sont confrontés aux opérations annoncées ; un manque produit `CONTRADICTED` ou `UNKNOWN`, sans pénalité IC arbitraire ;
- l'eau disponible, la capacité de la casserole, la surface de casserole supposée circulaire et la masse sèche sur base humide supposée donnent des calculs diagnostiques dimensionnés ; aucun n'est considéré calibré pour la qualité Q ;
- les actions prévues sont distinguées de leur réalisation future ; la succession des actions n'est pas imposée comme vérité universelle ;
- onze politiques peuvent être sélectionnées par événement hypothétique explicitement déclaré, jamais par événement post-T0 déjà observé ;
- la prévision 044 « stabilité du frémissement » ne possède pas de loi justifiée et conserve `NO_FORMULA`. Les prévisions 043 et 046 sont de simples proxies du modèle simplifié.

**Contre-audit :** une quantité d'eau de rinçage changeait sans modifier sa trace positive ; corrigé pour reporter la quantité. Une dépendance de séquence facultative ne doit pas devenir un conflit dur ; corrigé en hypothèse de plan. Les origines de la date doivent rester compatibles avec T0 ; le contrat V6-V7 est réutilisé.

**Résultat / frontière :** les 62 dossiers ont maintenant des traitements *opérationnels et vérifiables* dans un moteur d'admissibilité/scénarios. **Ce n'est PAS 62 effets sur la qualité Q, ni une clôture du véritable IC**. Les 62 chemins scientifiquement mesurés vers Q restent non prouvés ; 044 reste non modélisé. D014 demeure actif pour la preuve de contribution prédictive et pour la calibration réelle. La distinction entre couverture contractuelle, causalité et science est conservée pour MATRICE.

**Synchronisation effective V8 (constat) :** sources et journal V8 diffusés sous `MOTEUR-BLESSING/labs/RIZ112/` sur GitHub ; copie de travail complète et archive sous `/RIZ112_LAB/CAHIER_MERE_STAGE8_2026-10-16/` dans la Bibliothèque ChatGPT. Le connecteur Google Drive a refusé ce nouveau ZIP car il demande un fichier exporté depuis la conversation, pas un identifiant de fichier Library ; **la version V8 n'est donc pas confirmée sur Drive**. Le dernier ZIP privé de Drive reste D014. Le PC MBMPC est hors ligne ; pas de tests Windows V8. Ne jamais annoncer la synchronisation totale des quatre miroirs dans ce cas.

**Correction de synchronisation V8, événement E045 :** la référence de fichier exportée par la conversation a permis un second envoi réussi sur Google Drive, taille lue en retour 206876 octets, dossier privé confirmé. La précédente mention de blocage Drive (E044) reste conservée comme historique et est supplantée par E045. MBMPC reste hors ligne. Aucune confirmation SHA des octets côté Drive n'est disponible : on conserve l'empreinte source et la vérification de la taille/du parent.

## §14 — Directive utilisateur « finissons et produisons un IC » — Étape 9 (2026-10-16)

**Instruction reçue (sens) :** achever enfin un moteur RIZ-112 capable de produire des IC, sans s'arrêter aux versions purement architecturales. Ceci demeure un exercice transférable méthodologiquement à MATRICE. Conserver D014 (112 rôles réels, pas 112 coefficients).

**Action exécutée :** `step9/ic_simulation_v1.py` appelle les 112 contrôles puis les 62 routes D014, refuse les contradictions bloquantes et simule 3 000 scénarios de l'ancien graphe physique. Chaque scénario contient une incertitude explicitement déclarée (huit paramètres). Une substitution de qualité fictive, `Q*_DEMO`, est calculée avec quatre métriques normalisées et un agrégateur `minimum`, sans somme de points. Le contrat, la graine, les distributions et les échelles sont dans `step9/DEMONSTRATION_CONTRACT.json`. **Ce n'est pas un modèle entraîné de réussite réelle.**

**Résultats reproductibles de démonstration uniquement :** A 62,40 % ; B 36,83 % ; C 0,10 %. La préparation A perd 60 g d'eau prévue → 44,87 %. En changeant seulement une échelle fictive de Q*, A passe à 38,20 %. Cette sensibilité rappelle que ces chiffres n'ont PAS le sens d'IC scientifiques; aucun essai réel disponible.

**Test global :** 160 suites antérieures + 25 nouvelles = **185/185 PASS**, Python sur environnement ChatGPT. Les tests originaux étape 4 ont été lancés depuis l'archive d'origine (sinon leur résolution de chemins échoue). Aucun résultat post-T0 utilisé. Pas de tests Windows dans ce cycle tant que l'accès PC n'est pas confirmé.

**État d'intégrité des 112 :** tous les rôles pré-T0/cibles/gardes sont parcourus et traçables ; seules quatre dimensions fictives alimentent Q* ; les dix autres sous-critères finaux ne sont pas simulés, et la majorité des rôles ne sont pas associés à des paramètres de lois physiques vérifiés. **Une chaîne logicielle fonctionnelle de démonstration n'est pas le modèle intégral scientifiquement validé** demandé à terme. Le mandat D014 reste une contrainte active de transparence ; ne pas prétendre qu'un effet de chaque case sur le résultat réel a été appris.

**Pour MATRICE :** transférer les règles de contrôle T0, de lignage, de simulation incertaine et de séparation `REFERENCE / DEMO / SCIENTIFIQUEMENT CALIBRÉ` ; ne transférer **aucun coefficient, aucune distribution, aucun pourcentage alimentaire**. La validation OOS prématch reste impérative pour les vrais IC Over 1,5.

## §15 — Étape 10 : épreuve contradictoire des **112 contributions réelles** — 17 octobre 2026

Suite au contrôle demandé implicitement par le signal « 👀 », vérification directe du code V9 : il utilisait quatre seules dimensions fictives de qualité, malgré l'exécution contractuelle de 112 rôles. **Une nouvelle démonstration chiffrée n'est pas une preuve d'intégration de tous les paramètres.**

**Expérience :** intervention unitaire sur les 112 cases du JSON A, 3 000 tirages chacun avec graine fixe. **11** cas changent le pourcentage de démonstration ; **5** entraînent un refus ; **92** ne changent pas la valeur finale ; **4** variables sont calculées, donc non mutables directement. Les 112 interventions ont été réalisées sans erreur technique. Voir `step10/INTERVENTIONS_112_STAGE9.json`.

**Anomalie critique :** en V9, modifier chacune des 14 définitions de qualité future laissait l'IC démonstratif inchangé. Un score qui ne dépend pas du contrat-cible ne peut être présenté comme une probabilité de ce contrat. Correction V10 : liaison par empreinte SHA256 des 14 cibles, **abstention** dès qu'une seule change ou devient indéfinie. Pour une modification approuvée, une nouvelle version explicite de cible et sa validation seront requises. Cela ne valide pas le barème lui-même.

**État après correction :** 185 tests antérieurs + 20 tests V10 = **205/205 PASS** dans l'environnement ChatGPT ; résultats fictifs A/B/C conservés lorsque le contrat de démonstration ne change pas. L'IC scientifique reste `null`, qualité réelle observée n=0, les actions et politiques n'ont pas encore une influence numérique empirique établie sur Q.

**Transfert à MATRICE :** une analyse doit exposer **le nombre de variables réellement influentes sur l'IC dans ce match particulier**, celles qui provoquent abstention, celles sans effet dans les conditions du match, et la provenance de la cible. Ne jamais présenter la totalité du catalogue comme « consommée par le calcul » sans ce contre-test.


## §16 — Directive « générer aléatoirement des situations A, B, C » — 17 octobre 2026

**[DEMANDE DIRECTE]** L'utilisateur explique : « situation A qui génère aléatoirement les 119 conditions ... situation B ... chaque condition influe sur les résultats », avec exemples de matériau de la marmite, absence de couvercle, quantité de riz et d'eau. **Attention au nombre** : le catalogue canonique contient actuellement 112 cases. Le chiffre 119 est conservé comme point à clarifier ; 7 nouvelles cases ne sont pas créées silencieusement.

**[DÉCISION D020]** L'objectif architectural est un générateur de scénarios pré-T0 reproductible, un moteur mathématique/conditionnel et une analyse de sensibilité pour chaque condition applicable. Toute variation doit avoir une conséquence explicite parmi calcul, changement de contraintes, passage de branche, changement d'incertitude, ou aucun effet connu avec lacune tracée. Cela ne justifie PAS de forcer chaque case à modifier numériquement IC. Les 14 définitions de qualité restent constantes pour comparer A et B ; les 4 dérivées sont recalculées et ne sont pas échantillonnées. Le test contre-factuel doit distinguer contexte non quantifié et vraie influence IC.

**[DÉCISION D021]** La matière « marmite en bois non homologuée pour chauffage direct » est **ABSTAIN_UNSUPPORTED_VESSEL** (pas de faux rendement thermique) ; métal et céramique homologuée peuvent être simulés seulement sous hypothèses explicitement fournies. La simple étiquette de matériau ne reçoit pas de coefficient inventé. Un changement de matériel sans variation des paramètres physiques identifiés peut donc conserver exactement le même IC fictif ; il ne prouve pas équivalence physique.

**[EXÉCUTION ET CONTRE-AUDIT]** `step11/scenario_factory.py` réutilise l'entrée complète de 112 cases et le gate V10. Il génère des dossiers synthétiques déterministes depuis `seed`, anime ressources, matériel, couvercle, eau, puissance, masse de riz, durée, plans et politiques, conserve la cible gelée. Sur 60 scénarios avec 300 tirages chacun : 18 IC_DEMO calculés, 27 abstentions de contradiction, 15 abstentions matériau non homologué. Sur 18 cas calculables, 6 IC_DEMO sont strictement positifs. Pour deux cas choisis, le recalcul 3 000 tirages donne 11,27 % et 28,97 %. Tous ces IC concernent Q*_DEMO fictif, pas une qualité réelle.

**[TEST ET LIMITE]** Treize nouveaux tests passent : déterminisme, structure 112, cohérence des champs redondants, gel des 14 cibles, interdiction de fuite temporelle, changement d'eau provoquant changement d'IC démo, matériau non modélisé provoquant abstention, absence de nouveau bonus matériau arbitraire. Les anciennes suites exécutées depuis leurs emplacements d'origine passent ; le total est 218/218 (22+31+10+42+36+19+25+20+13). Aucune expérience de riz réelle : `scientific_ic_percent=null`. **La demande de 112 chemins prédictifs démontrés n'est pas encore satisfaite**, et l'étape 11 est une preuve de génération/scénarios, pas la clôture du mandat D014.

**[TRANSFERT MATRICE]** Lors de la génération de matchs A/B aléatoires ou de scénarios pré-match, l'IC ne doit répondre qu'aux variables dont le calcul/lien vers le résultat est identifié et testé ; les autres doivent être explicitement diagnostiquées. Gardes et définitions d'Over1,5 sur 90 minutes ne sont pas des poids prédictifs arbitraires. Ne pas reprendre les distributions alimentaires hypothétiques.


## 2026-10-17 — Étape 12, décisions D022–D024 : 100 situations réellement variées

L'utilisateur a confirmé que 100 situations A/B/C, décrites par 112 cases, doivent être comparées au travers d'un moteur où les conditions ont des conséquences explicables. **La V11 ne variait directement qu'une partie des champs, et il ne faut pas annoncer 112 effets numériques.**

Construction V12 : 100 dossiers JSON intégraux ; 44 données/conditions directement randomisables réellement diversifiées, 37 actions prévues et 13 politiques également diversifiées ; 4 sorties dérivées et 14 critères finaux fixes par définition. 500 simulations de la qualité fictive Q* par dossier admissible. Sur 100 : 30 IC de démonstration, 47 refus de marmites non prises en charge, 23 incohérences.

Tests de confrontation : 112 cases × deux situations A/B = 224 contre-interventions (avec 100 tirages chacune). 12 perturbations changent l'IC fictif, 52 modifient un contrôle opérationnel, 4 changent l'admissibilité, 26 ne montrent aucun effet dans ces tests ; 4 sorties calculées et 14 critères de réussite n'ont pas vocation à être mutés librement. **241/241 tests réussis**. Liste détaillée des 26 cas : `step12/GAPS_26_UNRESOLVED.json`. Rapports : `step12/RAPPORT_100_112_V12.json`, `step12/COUNTERFACTUAL_112_V12.json`, fichiers JSONL de 100 situations.

Démonstration contradictoire essentielle : métal vs céramique sans propriété thermique ajustée → même IC fictif ; modification explicite du rendement thermique de 0,45 à 0,75 → 44,60% contre 68,77% sur A, **mais cela ne prouve pas l'effet du matériau**. Les coefficients du modèle Q* restent des hypothèses, aucun modèle sportif MATRICE modifié, aucune préparation réelle ni calibrage.


## §18 — D025 : hiérarchie des 112 rubriques et anticipations (17 octobre 2026)

**Retour utilisateur confirmé sans ambiguïté :** une rubrique peut avoir plusieurs sous-paramètres et sous-sous-paramètres, avec des anticipations. Les rubriques ne sont pas 112 coefficients indépendants; chaque situation est soumise à des sous-modèles imbriqués et des interactions; une variation conditionnelle peut, mais ne doit pas obligatoirement, changer l'IC.

**Exécution H1 :** `step13/hierarchical_engine.py`, `H1_HIERARCHIE_112.json` et `H1_SCENARIOS.json` contiennent un premier registre imbriqué de 112 cas (schéma initial, non 112 lois) et le couplage numérique `matériau + diamètre + épaisseur + interface → résistance de conduction → rendement thermique effectif → ancien graphe eau/chaleur → Q*_DEMO`. Le couvercle absent provoque une anticipation de plan et de vapeur, au lieu d'une abstention de catégorie. Le bois direct non homologué reste marqué **NON SÛR** ; un insert métallique hypothétique est un montage différent.

**Preuves :** 20 tests supplémentaires H1 réussis + 23 de V12 relancés, scènes comparables 500 tirages. Les coefficients d'interface et les quatre dimensions de Q*_DEMO sont des hypothèses non calibrées. Les 112 sous-arbres présents ne signifient pas 112 effets validés. **Aucun résultat de sécurité/cuisson réel ni probabilité scientifique validée.** Sources techniques approximatives et audit disponibles dans `step13/README_HIERARCHIE.md`.

**Pont vers MATRICE :** transposer uniquement la structure paramètre→sous-paramètre→anticipation→mécanisme→IC, jamais les constantes de riz, les conventions fictives, ni une conversion artificielle des sorties/contraintes en prédicteurs.

## §19 — D026/D027 : sous-paramètres et anticipations prospectives calculées (17 octobre 2026)

Après la confirmation D025 (« un paramètre peut avoir plusieurs sous-paramètres et des anticipations »), poursuite effective plutôt qu'ajout d'un catalogue : le lot `step13/prospective_branches.py` prend la chaîne thermique hiérarchique H1, y ajoute les sous-paramètres 030/033/034/054 du riz et une branche conditionnelle 087 pour une correction en eau *pré-déclarée avant T₀*. Deux trajectoires sont calculées sur les mêmes tirages d'incertitude (avec et sans politique), la ressource 002 bornant l'action : une correction anticipée ne doit pas être confondue avec une observation future.

Expérience A purement **synthétique** : eau 180 g, politique seuil de déficit 5 g, dose 65 g et probabilité d'exécution supposée 0,75, 1000 tirages → 0,40 % sans politique, 44,00 % avec politique sur Q*_DEMO. Ni effet causal réel mesuré ni probabilité réelle de bon riz. **100 dossiers hiérarchiques distincts** ont aussi été exécutés (120 tirages chacun) : 22 scénarios changent l'IC fictif avec politique, 78 restent inchangés. La neutralité locale de plusieurs variables, les effets de seuil et la saturation sont des résultats possibles ; il ne faut pas injecter un malus arbitraire pour forcer des différences.

**Contre-audit D027** : séparation du générateur aléatoire de l'exécution de politique de celui des variables physiques pour garantir une comparaison équitable ; correction de l'inventaire `44+37+13+14+4=112`. **282/282 tests PASS** dans cet environnement Python/Linux (22 originaux + 260 suites ultérieures). Le statut reste `DEMONSTRATION_ASSUMPTIONS_ONLY_NOT_REAL_Q`, scientifique `null`, expérimentation réelle `n=0`, et pas de modification du moteur sportif. Voir `step13/README_H2_ANTICIPATIONS.md`, `step13/AUDIT_H2.md`, `step13/H2_100_RESULTS.jsonl`.
