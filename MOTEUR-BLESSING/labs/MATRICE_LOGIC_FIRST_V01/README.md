# MATRICE R8 — MOTEUR LOGIQUE AVANT DONNÉES, V0.1

**Livraison : 23 octobre 2026.** Prototype Python standard-library, exécutable **sans cloud ni abonnement**. Développement lié au projet MOTEUR et à la direction ADN R8 de MATRICE. Version expérimentale **NON PROMUE** dans MATRICE 2.0.

## Le vrai objectif

Prendre des **valeurs d'avant-match** (les paramètres et sous-paramètres de MATRICE), les propager dans des mécanismes logiques, confronter attaque/défense et dépendances et expliquer quelles **issues hypothétiques** deviennent plausibles. **Calculer les probabilités et l'IC numérique seulement ensuite**, avec des relations quantitatives justifiées et une validation sur des rencontres indépendantes.

Ce n'est **pas** un programme de « +5 points si attaquant, -7 si gardien ». Une valeur peut activer, contredire, rendre incertain ou laisser inchangé un mécanisme, selon les autres valeurs. La neutralité conditionnelle n'est pas une erreur.

## Provenance réelle de MATRICE

- Dépôt source : `Terminator364/ChatGPT-PC`, branche `research/matrice-r8-g3-depth-audit-2026-10-14`.
- Hiérarchie authentique : **paramètre/monde > sous-paramètre > variables, anticipations et scénarios**, sous provenance et horizon pré-match.
- Source : `MATRICE/R8_G3_DEEP_20261014/parameter_v1_freeze_20261015/CATALOGUE_PARAMETRES_MONDES_V1_FIGE_62.json` : **62 familles** gelées (SHA blob GitHub `3a82746f649bd820f5c0cec671ca88205133f92d`).
- Source : `MATRICE/R8_G3_DEEP_20261014/CHECKPOINT_TWO_RUNS_L3_62_1902_VERIFIED_20261018.json` : **355 sous-paramètres L3 candidats**, 62 familles avec fiches; **aucun poids d'IC calibré**, aucun entraînement nouveau. La CI historique indiquée dans ce reçu a réussi 1902 tests. Le module d'anticipation documentaire postérieur en indique 1920. Ces tests ne sont **pas des preuves de prédiction correcte**.
- Première implémentation du noyau : **14 sous-paramètres authentiques**, chacun rattaché à une de **14 familles existantes**; **7 mécanismes logiques × 2 équipes**, avec hypothèses contradictoires et contributions explicitement tracées.
- Couverture **logique exécutable actuelle : 14/355 enfants et 14/62 familles**. Les 341 autres enfants **NE SONT PAS calculés**; ils devront être raccordés avec leurs mécanismes ou gardes. Un champ non câblé est **rejeté** au lieu de contribuer fictivement.

## Structure

- `logic_engine.py` : modèle logique, validateur pré-T0, 7 règles de mécanismes, branches de résultats, comparateur conditionnel.
- `build_examples.py` : trois situations entièrement **fictives**, sans clubs ou résultats réels.
- `examples/*.json` : profils illustratifs aux états `HIGH`, `MEDIUM`, `LOW`, `UNKNOWN`.
- `audit_input_effects.py` : teste 3 alternatives par valeur saisie (et pas une variation de points inventée).
- `output/*.json` : résultat de trois situations.
- `output/*_contrafacts/` : examens des variations par paramètre, reçus et CSV.
- `test_logic_engine.py` : **22 tests** de règles, dépendances, protection temporelle, absence de pourcentage inventé, reproductibilité et contrefactuel joint.
- `COUVERTURE_62_MONDES.json` : couverture par famille, distinction documentaire vs consommé par le noyau.
- `AUDIT_RECETTE.json` : bilan des tests et du contenu avec SHA256.

## Démarrer

Depuis le dossier extrait :

```bash
python -m unittest -v test_logic_engine.py
python logic_engine.py examples/open_pressing_counter.json
python logic_engine.py examples/compact_defense.json
python logic_engine.py examples/insufficient_data.json
python audit_input_effects.py examples/open_pressing_counter.json --out output/open_contrafacts
python logic_engine.py examples/open_pressing_counter.json \
  --counterfactual B.ATTACK_BUILDUP.BALL_SECURITY_PRESSURE --state HIGH
```

Aucune dépendance pip.

## Exemple d'interaction sans +points

1. A présente un **pressing historiquement élevé** ; B est **historiquement fragile** en possession sous pression. Le chemin `A:HIGH_REGAIN` est soutenu *conditionnellement*.
2. A défend historiquement haut et couvre mal derrière ; B possède des transitions rapides. Le chemin `B:COUNTER` est soutenu *conditionnellement*.
3. A possède historiquement un volume et une qualité de tir élevés face à B qui empêche peu les tirs. Chemin `A:POSITIONAL` soutenu *conditionnellement*.
4. **Si B améliore sa sécurité du ballon à HIGH**, le même moteur ne soutient plus la chaîne `A:HIGH_REGAIN`, sans modifier les autres valeurs ni fabriquer un écart de « -15 % d'IC ».
5. Dans l'exemple de deux défenses compactes, changer un seul facteur ne suffit parfois pas : il faut **modifier simultanément** le pressing de A et la fragilité de relance de B pour activer une nouvelle chaîne. C'est une preuve d'**interaction logique non additive**.

Ces chaînes ne prétendent pas que des occasions ou buts auront lieu. On ne dispose ici d'aucune fréquence statistique fiable permettant d'en déduire `IC Over 1.5 = n%`.

## Signification des entrées

Les états `HIGH/MEDIUM/LOW` représentent **des appréciations hypothétiques normalisées**, pas des nombres bruts ni des scores inventés. Pour brancher une valeur réelle comme « 14 tirs/90 min », il faudra documenter : fenêtre temporelle, adversaires, statistique exacte, dénominateur, unité, origine éditoriale, instant de disponibilité et une règle de conversion **apprise ou validée** vers un état. **Le prototype refuse les données non reconnues ou arrivées après le coup d'envoi.**

Le champ `assessment_status = DOCUMENTED_SYNTHETIC` accompagne les trois exemples : ce n'est **pas une preuve réelle**. `VERIFIED_BEFORE_T0` dans le format exige un indicateur de publication vérifiée, qui reste insuffisant, à lui seul, pour une attestation indépendante d'éditeur; un contrôle externe reste à implémenter.

## Contrat d'issue

Le noyau renvoie une **qualification de chemins plausibles** :

- `MULTIPLE_PLAUSIBLE_GOAL_PATHWAYS` : au moins deux chemins primaires activés parmi les deux équipes ; ne veut **pas** dire deux buts attendus avec certitude ni même probable sans calibration.
- `ONE_PLAUSIBLE_GOAL_PATHWAY` : un chemin primaire identifié.
- `INDETERMINATE_MISSING_CRITICAL_VALUES` : inconnus empêchant la conclusion.
- `NO_ACTIVE_PATHWAY_IDENTIFIED_NOT_UNDER15_PREDICTION` : aucune chaîne entièrement soutenue dans cet ensemble de règles ; **pas une prédiction Under 1,5**.

Les hypothèses de score `2-0`, `1-1`, `0-2` etc. indiquent la règle **réglementaire** de réussite Over1.5. **Les probabilités sont toutes `null`** ; la version V0.1 n'est pas habilitée à chiffrer l'IC.

## Conditions pour atteindre le moteur fiable souhaité

**Porte logique (travail commencé)** : connecter les 355 enfants candidats à des mécanismes, indicateurs, contextes, gardes ou résultats; contre-auditer les doubles comptes, contradictions, interactions et causalité plausible. Les 14 premiers sont un essai de méthode, **pas** la couverture du projet.

**Porte des valeurs observées** : définir la signification des valeurs quantitatives, recueillir les données avant leur horodatage de coup d'envoi (J-6/J-3/H-1), vérifier droit de source et publication réelle, remplir UNKNOWN sans le transformer en 0.

**Porte de calcul probabiliste** : apprendre ou justifier les transitions statistiques d'attaques/occasions/tirs/buts **en tenant compte des deux équipes et des états hypothétiques du score**; ne pas additionner 355 probabilités sans graphe de dépendances. Comparer une baseline simple (modèle de buts historiques ajusté) au graphe enrichi.

**Porte scientifique** : tests chronologiques hors apprentissage, calibration des probabilités, Brier/log-loss, couverture/abstention, dérive de championnat, tests adversariaux. **Pas de promesse de 85 % ni de modèle officiel avant ces étapes.**

**État MATRICE préservé :** G3 ouvert, G4/G5 non validées au checkpoint R8 consulté, MATRICE 2.0 gelée. Aucun score officiel, aucune probabilité sportive produite ni déploiement du moteur de production par ce laboratoire.