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
