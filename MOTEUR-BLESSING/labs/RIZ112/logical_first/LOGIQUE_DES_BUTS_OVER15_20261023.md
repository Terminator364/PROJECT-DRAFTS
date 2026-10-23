# MOTEUR → MATRICE R8 — D052 : LOGIQUE D'ABORD, ANALYSE DES DONNÉES ENSUITE

**Date :** 23 octobre 2026. **Statut :** doctrine logique/conceptuelle réaffirmée, **AUCUN modèle sportif ni IC numérique nouveau**. Code RIZ : `Moteur/continue` ; code MATRICE : `MATRICE|CONTINUE`.

## 1. Cette idée vient bien de la Direction, et elle était déjà actée

La demande actuelle consiste à demander **« Qu'est-ce qui peut faire qu'un match comporte deux buts ou plus ? »** et à partir des **chaînes logiques d'événements** avant de rechercher des statistiques et d'ajuster des équations, comme dans le laboratoire du riz.

L'instruction existait déjà dans **MATRICE/R8_G3_DEEP_20261014/logical_research_20261015/ADDENDUM_DIRECTIF_ADN_R8_LOGIQUE_DABORD_20261015.md** : logique d'abord, mesures ensuite (15/10/2026). Une première recherche avait proposé 45 familles candidates, 360 sous-paramètres candidats et 180 situations logiques, sans fixer ces nombres comme quotas. Le travail R8 ultérieur a fixé un patrimoine de **62 paramètres/monde** dans la phase L3 ; **ne créer aucun monde supplémentaire automatiquement** et **ne jamais ramener MATRICE aux 44 facteurs du riz**. La taxonomie utilisateur conservée est **PARAMÈTRE/MONDE → SOUS-PARAMÈTRES → VARIABLES, ANTICIPATIONS, SCÉNARIOS**, avec sources et horizon temporel transversaux.

Cette note **réutilise et précise** la logique existante ; elle ne remplace pas la feuille de route R8, n'ouvre pas G4/G5, et ne déclare pas G3 scientifiquement acceptée.

## 2. L'événement réellement recherché

`Over 1.5` signifie **au moins deux buts réglementaires au total à 90 minutes + arrêts de jeu**. Cela comprend `2–0`, `0–2`, `1–1`, `2–1`, etc. et exclut `0–0`, `1–0`, `0–1`. **Il n'est pas nécessaire que les deux équipes marquent.** Aucun événement après le coup d'envoi du match ciblé ne peut être une donnée d'entrée réelle pré-match.

## 3. Modèle logique des mécanismes de but

`CONDITIONS AVANT MATCH`
→ `stratégies/possessions/récupérations`
→ `progressions et déséquilibres défensifs`
→ `occasions et qualité des tirs`
→ `conversion / arrêts / déviations`
→ `BUT ou non`.

Chemins supplémentaires : transitions et contre-attaques, coups de pied arrêtés, penalties, erreurs et buts contre son camp. **Les deux équipes sont prises ensemble** : chacune peut créer et concéder une chance dans le même épisode. **La réaction au score** est importante : le but à l'instant `t` peut changer les tactiques à `t+1`, puis les occasions futures; ce mécanisme doit être **déplié dans le temps**, pas représenté par une boucle causale instantanée ni injecté comme résultat réel pré-match.

Le fichier `MECANISMES_CONDITIONNELS_OVER15_20261023.json` consigne **11 modules logiques**, tous liés à des IDs de mondes déjà présents dans le catalogue historique R8 : `TACTIC_STYLE, PRESSING_TURNOVERS, TRANSITION_ATTACK/DEFENSE, SHOT_CREATION/QUALITY/CONVERSION, GK_DEFENSE, SETPIECE_ATTACK/DEFENSE, PENALTY_PATHWAYS, GAME_STATE_POLICY`, etc. Ils ne sont **pas** 11 nouveaux paramètres ni des pondérations pour l'IC. La liste reste ouverte à la recherche et la revue contradictoire.

## 4. Exemple raisonné (sans simulation numérique ni pourcentages fabriqués)

**Hypothèse pré-match :** A presse haut et laisse un espace derrière ses défenseurs ; B cherche à relancer court et peut perdre sous pression.

- **Chemin A** : B perd près de sa surface → A exploite la récupération → occasion de tir de qualité → but possible.
- **Chemin B** : B traverse le pressing → avance dans le dos du bloc haut de A → contre-attaque → occasion de tir de qualité → but possible.
- **Contrainte contraire** : si B ressort finalement par longs ballons ou si A protège efficacement sa couverture, certains chemins disparaissent ; si les tirs sont très peu dangereux, fort volume ne signifie pas beaucoup de buts.
- **Branches après le premier but** : l'équipe menée peut attaquer plus, ce qui augmente certaines occasions et expose sa défense ; ou les équipes peuvent contrôler le rythme. **Le signe ne doit jamais être fixé universellement sans données**.
- **Conclusion LOGIQUE uniquement** : rencontre potentiellement ouverte, plusieurs chemins plausibles vers 2+ buts, mais `IC Over1.5 = null` à ce stade. Les états `2–0`, `1–1`, `1–0`, `0–0` ne reçoivent aucun poids chiffré inventé.

## 5. Comment transformer la logique en moteur, sans se tromper sur l'IC

1. **Inventaire causal ouvert** : chaque grand chemin pour produire ou empêcher un but, et chaque branche après le premier but, sans forcer une quantité donnée de paramètres.
2. **Fiche par monde** : mécanisme et conséquences, sous-paramètres/variables, compatibilités, contradictions, scénarios, cas inconnus, horizons J−6/J−3/H−1, source et possibilité de mesure pré-match.
3. **Graphe de mécanismes interactifs** : chemins dirigés signés seulement lorsque justifiés, effets possiblement contraires, interactions, données dérivées, double comptage exclu. Exemple : pressing haut peut favoriser la récupération dangereuse ET exposer derrière ; absence d'attaquant impacte disponibilité → onze probable → création/conversion, pas un « −10% » gratuit.
4. **Données ensuite** : chercher des éléments historiques et des données de match gelées avant le coup d'envoi afin de confronter les mécanismes, mesurer leurs distributions et apprendre des relations numériques plutôt que les inventer.
5. **Scoring en dernier** : définir la loi conjointe des occasions et buts pour les deux équipes en tenant compte des états du match, comparer des baselines et modèles plus riches, calculer **un IC global Over1.5 par match** et des impacts conditionnels des paramètres pertinents, calibrer et auditer hors échantillon. Les futurs scores ne peuvent jamais entrer dans les prédicteurs prématch.

Cette voie prépare la structure réutilisée de RIZ : `X_avantT0 -> mécanismes -> scénarios cohérents -> IC global -> impacts conditionnels`. L'IC du riz `83/128`, ses sept pondérations et ses lois physiques **ne doivent pas être transportés vers le football**.

## 6. Contre-audit conceptuel obligatoire

- Une moyenne de ligue ou une série de buts est une **mesure passée**, pas une explication causale suffisante.
- Pressing agressif, pluie, arbitre, rotation, carton rouge probable ne sont pas **toujours** favorables aux buts ; états contradictoires et inconnus sont prévus.
- Les décompositions `tir -> xG` sont estimées historiquement, non des lois physiques ; seuls les tirs historiques sont disponibles avant le match cible.
- `2–0` et `1–1` satisfont la même cible Over1.5, mais par voies différentes.
- En cas d'absence de source critique ou de mécanisme mesurable, **ABSTAIN / NON MODÉLISÉ**, pas de bonus.
- Une chaîne plausible est une **hypothèse**, pas un IC ni un gain de précision certifié.
- Pas de régression de la doctrine pré-match ni de l'identité des 62 familles R8 ; chaque module doit réutiliser et rattacher les IDs du patrimoine avant de proposer une subdivision.

## 7. Base externe pour examen scientifique ultérieur

- Hudl StatsBomb, xG : https://statsbomb.com/soccer-metrics/expected-goals-xg-explained/ — la valeur d'une occasion dépend notamment position, angle, contexte et défenseurs/gardien selon les données disponibles.
- Eusebio et al., *Scientific Reports* (2026), transitions offensives : https://www.nature.com/articles/s41598-026-49831-2 — voies identifiables de buts sur transitions ou phases arrêtées ; **classification d'événements passés, pas coefficient prédictif universel**.
- Skripnikov et al. (2026), contexte de jeu : https://journals.sagepub.com/doi/full/10.1177/22150218261454824 — les métriques offensives sont influencées par état du score et cartons, variables à traiter comme **futures hypothétiques** avant le match.

## 8. Statut et provenance

**Travail accompli :** relecture du vrai addendum R8 et du catalogue logique historique; réconciliation de ses IDs existants; formalisation de 11 chemins et d'un contrat de tests logiques; note de transfert ajoutée au Cahier mère MOTEUR avec message utilisateur intégral. **Travail non accompli ici :** aucun nouveau coefficient, aucun IC sportif, aucune collecte G3 supplémentaire, aucun changement de score MATRICE, aucune validation prédictive nouvelle. La conception ne remplace pas les portes officielles G3→G4→G5 ni la traçabilité des 62 mondes.

**Synchronisation :** `MOTEUR-BLESSING/labs/RIZ112/CAHIER_MERE.md`, `DECISIONS.md`, `CHECKPOINT.json`, `CONTEXTE_INTEGRAL/REGISTRE_MESSAGES.jsonl`, `journal/JOURNAL_EVENEMENTS.jsonl` et `TRANSFERT_MATRICE.md`. La feuille R8 originale reste intacte.
