# AUDIT → CONTRE-AUDIT → AMÉLIORATION — D079 vers MOTEUR BLESSING V1

## Énoncé de vérification

**Objectif utilisateur :** 62 familles, 355 sous-paramètres, 710 décisions pour UN match, recherche et anticipation des manques AVANT IC, intégration causale conditionnelle, traçabilité, paquet conversationnel réutilisable. Un résultat testable doit distinguer branchement numérique, qualité des preuves et validité prédictive.

### Audit A — éléments vraiment présents dans D079

- 355 IDs du catalogue, 710 lignes unique HOME/AWAY.
- 686 lignes participant à une équation et 24 lignes N/A (coupe et sélection) avec motifs.
- 46 lignes étiquetées `FAIT_PREMATCH_PLUS_INFERENCE`, 640 `INFERENCE_CONDITIONNELLE`; toutes nécessitent une inférence numérique, dont 640 une valeur partagée depuis les familles.
- 62 facteurs familiaux manuellement signés (sources officielles partielles), 12 interactions spécifiques Gamba–Kyoto, baseline GF/GA 11+11 matchs antérieurs.
- IC D079 témoin **82,609048 %** hypothétique, non calibré; environ 1 000 simulations de sensibilité, tests et ablations.

### Contre-audit B — objections retenues et preuves de code

| Priorité | Critique documentée | Localisation dans D079 | Pourquoi cela compte |
|---|---|---|---|
| Critique | **Marquage « direct » à partir d'une liste d'IDs** | `DIRECT_IDS` et `make_cells`, variable `direct` | On ne peut pas déduire qu'un enfant a sa propre mesure parce qu'une source générale mentionne sa famille. |
| Critique | **640 inférences par famille partagée + 2 liens de mots-clés au maximum** | `child_score` et `TOKENS` | 640 cases ne sont pas 640 observations ni des mécanismes individuels vérifiés. Certaines proximités lexicales peuvent être trompeuses. |
| Critique | **12 règles codées en dur pour un seul match** | `INTERACTIONS` et `compute` | Copier ces règles sur un autre match induirait prémisses fausses et mauvaise attribution des équipes. |
| Critique | **I10 est inversée** | `I10` cible HOME mais prend `GK_DEFENSE` HOME et `SHOT_CONVERSION` AWAY | La règle voulait **gardien Kyoto × finition Gamba**; c'est l'inverse de l'opérateur original. |
| Importante | **Avantage du terrain potentiellement compté deux fois** | `baseline(): *1.035/*0.965`, puis famille `NEUTRAL_VENUE` | Un même facteur intervient dans le prior et dans le raisonnement contextuel. |
| Importante | **37 conflits potentiels de rôle source vs famille** | `role_for` famille et contrats source; fichier `AUDIT_CONFLITS_ROLES_355.json` | Des rôles CONTEXT/FRICTION/TEMPO peuvent être ramenés à un simple effet d'attaque, sans révision mécanique individuelle. |
| Importante | **Sources dynamiques non archivées** | `sources_asof.json` S7/S8; pages live S4/S5/S6 | Une URL actuelle n'est pas une preuve suffisante de son contenu exact à T−1; garder la nuance. |
| Importante | **Gates utilisés comme atténuation continue, pas comme refus systématique** | `compute`, `reliab` de 0,70 à 0,96 | L'identité du match erronée doit bloquer en amont; un multiplicateur de qualité ne suffit pas. |
| Importante | **Répartition familiale de poids uniforme** | `SIZE[fam]/FAM_COUNTS[fam]` | Garantit une influence non nulle de chaque case, mais pourrait affecter trop de poids à des enfants périphériques. |
| Importante | **Crédibilité des pourcentages** | `probo15` et `simulate` | Baseline, dispersion et corrélations sont hypothétiques, pas probabilités calibrées. |
| Domaine | **24 N/A non réactivables numériquement en l'état** | `INAPPLICABLE={'CUP_TIE','INTERNATIONAL'}` | Le modèle ne doit PAS prétendre fonctionner directement pour coupe ou sélections. |

### Contre-audit C — corrections V1 livrées

| Réponse | Preuve de réalisation | Conséquence |
|---|---|---|
| Supprimer le « fait enfant » automatique | `04_MOTEUR/moteur_v1_conversation.py` exige un `child_values` avec preuve datée; 0 observation enfant indépendante dans la démo reconstruite | Plus de faux 46/710 « directs ». |
| Reprovenancer les 62 ancres | `DEMO_DOSSIER_ENTREE_GAMBA_KYOTO.json` : 44 couples famille/équipe à contexte sourcé, 66 à proxy, 10 simulés, hors domaine séparé | Les statuts reflètent davantage le niveau réel de connaissance. |
| Correction orientation I10 | Règle I10 du dossier : `AWAY/GK_DEFENSE × HOME/SHOT_CONVERSION` | L'interaction « gardien Kyoto × finition Gamba » a désormais les bonnes équipes. |
| Dédupliquer avantage terrain | Baseline du nouveau runner non multipliée par +3,5 % / −3,5 % fixes, NEUTRAL_VENUE conservée | Correction structurale; impact chiffré non qualifié de gain prédictif. |
| Contrer la réutilisation invisible | `--dossier` obligatoire, validation intégrale, pas de fichier chargé par défaut | Nouveau match = nouveau dossier; pas de valeurs Gamba dans une rencontre étrangère. |
| Interactions conditionnelles typées | Les 12 règles sont sorties du noyau et fournies par dossier avec `a_team`, `b_team`, poids et prémisses; atténuation avec qualité | Permet de reconstruire les règles par adversaire et d'auditer le branchement. |
| Bloquer le temporel | `available_at <= asof < kickoff`; historique `played_at < asof`; preuve enfant après cutoff rejetée | Réduit la fuite postmatch, y compris à J−3. |
| Bloquer hors domaine | `competition_type='league_clubs'` seul admis; autres compétitions refusées explicitement | Interdit un IC fallacieux en coupe avec 24 règles neutralisées. |
| Fiches individuelles | 62 dossiers + 355 enfants + 12 interactions, chacun avec objectifs, questions, repli et calcul témoin | Continuité de travail vérifiable au lieu de nombres seuls. |

### Ré-audit D — résultats reproduits

- D079 témoin conservé **82,609048 %** ; V1 améliorée **82,023276 %**. Écart **−0,585772 point**, sans prétention d'amélioration statistique.
- Couverture structurelle V1 **710/710**, 24 N/A ; **686 cases familiales ou individuelles dérivées**, 60 familles applicables.
- **30 tests V1 passent** : forme des 62 familles, temporalité, historique, sources futures rejetées, valeurs enfants, réemploi d'un nouvel historique, aucune interaction recopiée quand absente, domaine refusé, sensibilité individuelle et reproduction du calcul.
- **60/60 ablations de famille applicables** changent IC numériquement; 2 hors domaines restent à 0. Cela prouve une voie dans les équations, **pas** la validité mécanique de l'ensemble.
- **12/12 règles** du match exemple ont une influence numérique marginale contre-factuelle; I10 a changé de sens après correction.
- Les fiches de sous-paramètres contiennent les valeurs D079 et les statuts plus honnêtes V1. Le **journal de collectes enfant indépendantes est nul sur ce dossier de démonstration** : ne pas le cacher.

### Verdict du contre-audit

**ACCEPTÉ COMME :** première version documentaire, calculatoire, reproductible, avec moteur conversationnel à entrée JSON, fiches et mécanismes explicités. **NON ACCEPTÉ COMME :** système d'enquête entièrement autonome déjà éprouvé sur un nouveau match ou mécanisme causal 355/355 scientifiquement prouvé. La prochaine preuve exigée est une recherche fraîche en conversation ChatGPT sans recyclage de Gamba–Kyoto.


## Ré-audit supplémentaire après 30 tests

Le contrôle final a découvert une hypothèse implicite : 12 interactions déclarées « conditionnelles » restaient toutes activées numériquement sans statut formel de preuve de leurs prémisses. La V1 finale exige un statut et applique une atténuation supplémentaire aux scénarios. Deux bornes scénarios 0,98 étaient inférieures à la valeur centrale 0,99; elles ont été corrigées. Un historique renommé sans modifier son propriétaire était accepté; l’identité par côté est maintenant obligatoire. **40/40 tests** vérifient ces règles. Résultat final du dossier démonstratif : **81.993294630 %**. Ces corrections ne prouvent pas la causalité individuelle ni l’aptitude autonome à rechercher 355 éléments.