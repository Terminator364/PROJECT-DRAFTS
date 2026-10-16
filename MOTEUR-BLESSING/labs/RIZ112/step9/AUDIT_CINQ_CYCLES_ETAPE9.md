# Audit contradictoire — RIZ112 IC_DEMO V9

## C1 — Construction
Réemploi exact de `reference/step4/riz112.py`, `step6/engine112.py`, `step7/graph_governor.py` et `step8/functional_routes.py`. Pas de modification des anciens fichiers. Simulateur `step9/ic_simulation_v1.py`, contrat explicite à huit distributions et quatre dimensions Q* de laboratoire, MC déterministe.

## C2 — Audit
Vérification des dates pré-T0, 112 rôles, 62 routes D014, résultats futurs absents de l'entrée, cohérence de ressources et 25 tests de référence V9. Rejet strict si échelles / distributions incomplètes ou si l'on demande de prétendre à un modèle approuvé.

## C3 — Contre-audit
La qualité réelle n'est PAS prédite : échelles, loi `surface_starch → séparation`, seuils et distributions ont été choisis sans observation. Un intervalle MC serré ne crée pas de fiabilité scientifique. Tous les critères Q ne sont pas modélisés. Le type `IC_DEMO` est séparé des champs `scientific_ic_percent` / `real_Q_probability_percent` qui restent `null`.

## C4 — Corrections et perturbations
Sensibilité sur diminution d'eau de 60 g, multiplicateur de couvercle, barème modifié, blocage par contradiction, données post-T0, même graine et graines différentes. Utilisation du *minimum* entre mécanismes plutôt que de bonus/malus cumulés. Inquiétude : la fonction de score Q* est un choix artificiel ; étiquette obligatoire.

## C5 — Ré-audit
Anciennes suites sous les bonnes arborescences : 22 + 31 + 10 + 42 + 36 + 19 = 160 ; V9 = 25 ; **185/185 tests logiciel PASS**. Les trois démonstrations JSON et deux scénarios de sensibilité sont reproduits à graine fixée. Aucune preuve empirique, aucun Windows non vérifié, moteur sportif MATRICE inchangé.

Conclusion : **calcul de probabilité simulée livrable**, mécanismes/exhaustivité statistique et statut scientifique complet toujours NON APPROUVÉS. La demande utilisateur de finir n'autorise pas à inventer une précision réelle.
