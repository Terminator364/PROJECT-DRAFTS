# Contrat de transfert RIZ-112 → MATRICE

Ce laboratoire est **un banc d'essai pour la méthode**, et non un changement de métier ou de finalité du moteur sportif.

## Critères obligatoires avant transposition

1. Données JSON pré-T₀ typées (observation, hypothèse, action annoncée, règle de contrôle, sortie ciblée). Chaque valeur a une source, un instant de disponibilité et un niveau de vérification indépendant.
2. Chaque monde/case porte **sa propre formulation mathématique** lorsque pertinente. Un champ inventorié mais non consommé n'est pas compté comme « actif ».
3. Un graphe de dépendances prouve quelles entrées ont modifié quelles sorties ; analyses contrefactuelles quantifient les effets conjoints et signalent redondances.
4. Aucune preuve de disponibilité rétrospective fabriquée ; aucun résultat d'un match déjà joué ne rentre dans l'analyse pré-match.
5. Une prédiction IC n'est fournie que si sa chaîne complète est numériquement active, son domaine valide, son apprentissage et sa calibration réels, et son audit hors-échantillon réussis. Une baseline est étiquetée BASELINE_ONLY, jamais MOTOR_FULL.
6. L'incertitude jointe et les données UNKNOWN doivent être représentées ; les variables de garde, sorties et indicateurs composites ne deviennent pas des bonus indépendants.
7. Pas de paramètre live : horodatage de gel avant le coup d'envoi ; cible sportive = **Over 1,5 buts réglementaires 90 minutes**, pas prolongation/penalty.

## Critère anti-régression des quatre matchs du 16 octobre

Le pilote conservé dans `mb1/pilots/20261016_four_matches` avait **0 observations mondes et 0 mécanisme transversal calculé**. Il serait techniquement interdit de présenter son unique Poisson de ligue comme IC construit depuis les 62 mondes. L'expérience RIZ-112 doit servir à construire un test qui rejette explicitement cette erreur de couverture et de traçabilité, sans prétendre que toute case est obligatoirement un prédicteur indépendant.

## Interface de reprise souhaitée

- `input_snapshot.json`: données pré-T₀ avec hash, horodatages et schéma.
- `mechanism_graph_trace.json`: graphe et lignée des calculs actifs, unités, intervalles et contraintes.
- `label_protocol.json`: définition pré-enregistrée de l'événement observé, **pas disponible pendant l'inférence**.
- `model_card.json`: données d'apprentissage, sélection, calibration, hors-échantillon et limites.
- `prediction.json`: IC calibré ou abstention expliquée, nombre de mondes effectivement utilisés et preuves.

Le transfert n'est pas exécuté dans MATRICE à ce stade ; il devra être autorisé par une revue d'interface et suivi dans la feuille de route MATRICE, sans effacer ses propres checkpoints.

## Leçon opérationnelle de l'étape 6 — anti-faux « tous mondes intégrés »

Adapter le contrat 112 à MATRICE en remplaçant la grille par les **62 mondes canoniques**, chaque monde portant : `ROLE`, `SOURCE/PIT`, `FORMULE_EFFECTIVEMENT_EVALUÉE`, `CONTRIBUTION_DIRECTE_OU_DEPENDANCE`, `OBSERVATION_CONNUE/UNKNOWN`, `SORTIE_SEULEMENT`, `COEFFICIENT_CALIBRÉ_OU_NON`, `ÉTAT_FILTRE`. Une preuve de 62/62 rôles validés est distincte de 62/62 contributions quantitatives. Les mondes de gouvernance et les sorties doivent participer à l'admissibilité ou à la définition de la tâche, **jamais comme des bonus de buts ou des observations futures**.

**Condition de non-régression** : rejeter tout rapport présentant un IC Over 1,5 issu du seul prior Poisson comme si les 62 mondes avaient contribué. L'absence d'une formule pertinente se rapporte comme `NOT_MODELED` / `ABSTAIN` et non une valeur zéro déguisée.

### Rapport de transfert — Étape 7
La recherche de chemins et l'audit DAG sont **réutilisables conceptuellement** pour MATRICE. Il faut interdire tout arc partant d'une variable post-coup d'envoi vers les features pré-match, distinguer héritage de source/corrélation/causalité, et publier les mondes encore **non reliés** au calcul de l'IC. Ne jamais compter un contrôle de faisabilité (qualité de source, présence d'une donnée, validation de cohérence) comme bonus sportif ; ne jamais corriger artificiellement un graphe en ajoutant une dépendance sans justification.

## Résultat étape 9 — point d'attention pour MATRICE
Un IC numérique peut être calculé par simulation Monte-Carlo si les hypothèses et la cible proxy sont spécifiées ; mais **un IC numérique n'est pas automatiquement un IC fiable**. Le laboratoire RIZ112 V9 propose `IC_DEMO` sur `Q*_DEMO`; les chiffres ne doivent pas devenir un score sportif. La fonction de validation doit distinguer `CALCULATED_ASSUMPTION_DEMO` de `CALIBRATED_REAL_OUTCOME`, garder les origines temporelles PIT, séparer les observables futures et évaluer par validation chronologique et ablation. La couche 112 rôles évite les cases silencieusement omises, sans inventer une influence quantitative.


### Apprentissage RIZ-112 V12 → MATRICE (2026-10-17)

- Pour chaque match réel, distinguer **données observables pré-match** / **variables calculées** / **plan ou événement probable** / **conditions de veto** / **résultat cible** ; ne pas dire « 62 mondes indépendants » par le seul nombre de fiches.
- Un générateur de situations doit conserver la même cible et garantir les données strictement pré-match. Les paires contrôlées (une variable à la fois) démontrent quelles variables modifient les mécanismes ou les gardes.
- Un nom de catégorie (p. ex. matériau de marmite) sans propriété mesurée est comme un nom de compétition/joueur sans collecte d'effet : ne jamais fabriquer le coefficient correspondant.
- Une baseline ou un IC simulé n'est pas un IC empirique, et sa stabilité doit être mesurée sous changements de données + contraintes.
- Les variables servant à définir le résultat futur ne peuvent pas alimenter le calcul pré-match, même pour rendre « 112/112 » plus vendeur.

## D025 — sous-paramètres imbriqués et anticipations (2026-10-17)
Transférer **la grammaire du modèle**, pas ses valeurs : paramètre 62 mondes → sous-paramètres numériques/catégoriels/qualitatifs → sous-sous-paramètres → anticipations et scénarios pré-match → graphe de calcul / interactions / incertitude → IC conditionnel de la rencontre. Tester la perturbation d'un sous-paramètre et mesurer le changement dans le graphe et, si pertinent, l'IC. Cas sans effet local possibles (goulot d'étranglement/saturation). Les futurs résultats sportifs (buts, tirs du match) sont des **cibles** et ne sont jamais introduits comme caractéristiques pré-match. Aucun coefficient thermique du riz, aucun seuil fictif Q*, aucun « 112/112 » documentaire ne vaut validation sportive.

### D026/D027 — Pont anticipations avant l'événement

Le sous-modèle `step13/prospective_branches.py` compare une trajectoire prospective sans correction à une trajectoire conditionnée par **une politique déclarée avant T₀**. Le déclenchement est dérivé d'états **simulés** et jamais de données postérieures au match ou à la cuisson. La probabilité hypothétique d'exécution et les stocks font partie de la provenance de l'IC. MATRICE doit adopter cette *discipline temporelle* sans copier les modèles physiques, valeurs ou pourcentages du riz.


## H3 — Règles de transfert (2026-10-17)
Les 112 rubriques RIZ sont hiérarchiques, mais leurs sous-paramètres ne sont pas des points d IC à sommer. H3 ajoute quatre chemins numériques **supposés** : alimentation, régulation, ambiance, géométrie grain; les tests de contre-factuels incluent les interactions et empêchent de modifier les valeurs des rubriques parentes en écrivant leurs sous-paramètres. **MATRICE** doit réutiliser cette discipline de propagation/pré-match/anticipations/préservation de données, sans copier les équations physiques, constantes ou Q* hypothétique du riz. 22 cases restent encore sans nouvelle loi numérique dans les 26 lacunes identifiées à H1, aucun effet empirique validé.


## D030 — Réutilisation du contexte par MOTEUR|CONTINUE
Le registre conversationnel RIZ-112 et les décisions D001–D030 sont une **source méthodologique** pour la feuille de route sportive; ils ne changent pas le moteur de production, n'autorisent aucune promotion scientifique et ne remplacent ni les 62 mondes ni les données PIT. À la reprise parent, lire `MOTEUR-BLESSING/labs/RIZ112/CONTEXTE_CONVERSATIONS.md` et `CHECKPOINT.json`.


## D052 — Logique des chemins vers 2 buts AVANT les données (23 octobre 2026)

Ce point **ne crée pas de nouvelle doctrine** : il est déjà dans l'addendum ADN R8 « logique d'abord, mesures ensuite » du 15 octobre 2026, que la Direction vient de réaffirmer (CTX-0073). Le transfert du riz à MATRICE commence par l'**inventaire raisonné des mécanismes** : accès et progression, pressing et pertes, transitions, occasion/tir, qualité, gardien et conversion, phases arrêtées, penalties, état du score et réaction tactique. Les deux côtés peuvent marquer (1–1), ou un seul deux fois (2–0). Les futurs résultats d'une rencontre ciblée sont des scénarios à anticiper, pas des données pré-match.

La nouvelle synthèse est `logical_first/LOGIQUE_DES_BUTS_OVER15_20261023.md` et `logical_first/MECANISMES_CONDITIONNELS_OVER15_20261023.json`, tous deux rattachés aux mondes du catalogue R8 existant. Les **11 chemins** ne sont ni 11 paramètres nouveaux, ni 11 lois quantitatives vérifiées. Maintenir les **62 mondes historiques canoniques**, leur hiérarchie, le gel avant le match, la gestion des inconnus, l'interdiction des coefficients imaginaires et le contrôle des régressions contre la baseline. Les sources historiques et le modèle G4 doivent valider les relations numériques **après la conception logique**, non les déterminer prématurément. Aucune feuille de route R8 modifiée ici ; aucune G3/G4/G5 promue ; **nouvel IC sportif = 0**. À `Moteur/continue` ou `MATRICE|CONTINUE`, lire D052 avant de discuter entraînement et pourcentages.


## D053 — Prototype logique effectif, 14 sous-paramètres L3 actifs (2026-10-23)

Prototype MOTEUR-BLESSING/labs/MATRICE_LOGIC_FIRST_V01/ : sous-paramètres L3 R8 réels, 14/355 enfants issus de 14/62 mondes, 7 règles logiques bilatérales, 22/22 tests unitaires locaux rejoués PASS, 3 scénarios synthétiques et 183 modifications conditionnelles testées. Il est INEXACT de présenter les 62/62 mondes L3 documentés comme un moteur numérique actif complet ; 341 candidats ne sont pas encore reliés. Absence de score futur observé comme entrée, inconnus signalés, aucun bonus IC arbitraire, IC_over15_percent = null ; MATRICE 2.0 gelée inchangée, G3 ouvert, G4/G5 non promues. ZIP vérifié : MATRICE_R8_MOTEUR_LOGIQUE_V0_1_20261023.zip SHA256 f392715cf3996aa23130ac43b3593ee1e73b7ad4f24052c342f189e189cd4c2c. Suite : règles pour les autres rôles, tests de causalité contradictoire, intégration de valeurs PIT observées, puis calibration sur matchs indépendants.
