# RIZ-112 — Étape 6 : participation réelle des 112 cases, sans faux IC

**Mandat utilisateur (16 octobre 2026)** : « veille à la synchronisation [...] j'insiste notamment sur les faits que réellement les 112 contribue et non seulement 15 ».

## Critère d'acceptation honnête

L'exigence « 112 contribuent » a deux interprétations distinctes qu'il ne faut jamais confondre :

1. **Couverture opérationnelle vérifiable : 112/112**. Chaque case possède une opération de traitement exécutable et traçable, avec validation, formule, scénario, contrat ou garde-fou de cible. Un numéro absent est bloquant. Le reçu détaille le rôle, le statut, les dépendances et la provenance.
2. **Contribution quantitative prédictive validée : NON**. Le noyau physique d'origine exploite **15 cases** dans ses 16 nœuds de calcul (constantes simplifiées), et l'étape 6 expose **deux résultats calculés explicitement, 043 (montée à température) et 048 (bilan hydrique)** qui réutilisent les mêmes calculs, sans créer deux influences indépendantes supplémentaires. La case 046 n'est qu'un proxy de couvercle, la case 044 est **non modélisée**. Les autres cases influencent la complétude, le contrôle de cohérence, la description du protocole, les branches ou l'évaluation future — aucune ne reçoit un effet de texture/qualité inventé.

**Il serait faux de dire « les 112 cases influencent numériquement l'IC »** : les 14 cases 099–112 sont des résultats *futurs*, pas des facteurs pré-T₀ ; l'IC ne peut pas être calculé avant observations réelles et calibration.

## Contrat JSON strict

`step6/examples/A_couvercle_ajuste_112.json` contient :
- `prestart` : paquet horodaté existant du calcul étape 4 ;
- `case_inputs` : **44** fiches pré-T₀ (connues, hypothétiques ou `UNKNOWN`) ;
- `action_plans` : **37** décisions annoncées, **pas les actions réellement effectuées** ;
- `correction_policies` : **13** branches conditionnelles déclarées ou manquantes ;
- `target_contract` : **14** définitions de qualité future, non exploitées comme entrées ;
- **4 cases dérivées** 043/044/046/048 calculées ou explicitement non modélisées par le programme.

`case_inputs.014` (couvercle), `.035` (eau), `.041` (puissance) et les autres drivers sont confrontés à la valeur exacte du `prestart` du noyau physique : on ne peut pas déclarer inconnue une case calculée comme observée. Sources et dates déclarées **ne constituent pas une attestation tierce**.

Sortie : **112 lignes de trace**, un bilan de données manquantes, de contradictions et de mécanismes, mais **`validated_success_IC_percent: null`**.

## Reproduction locale hors ligne

Depuis le répertoire racine extrait :

```sh
python step6/engine112.py step6/examples/A_couvercle_ajuste_112.json
python -m unittest discover -s step6 -p 'test_*.py'
```

Le programme utilise seulement la bibliothèque standard et les fichiers étape 4/5 inclus. Les traces d'exemples A/B/C sont dans `step6/examples`.

## Contre-audit et engagements

- 112/112 : une case retirée de chaque famille fait échouer les validations ; statut de chaque action/politique transmis à la trace ; sources modifiées changent le digest d'entrée.
- Les 14 sorties finales sont **interdites comme prédicteurs**. Une entrée `quality_score_100` préstart est rejetée.
- Un couvercle physiquement absent mais prévu dans le plan génère `CONTRADICTORY_PLAN` ; une réserve d'eau insuffisante génère `RESOURCE_SHORTAGE` sans malus numérique arbitraire.
- Les hypothèses non mesurées restent signalées, et les 42 tests V6 ajoutés couvrent ces exigences.
- **Aucun classement, IC ou probabilité 112/100 n'a été présenté comme validé.**

## Suite de travail réellement nécessaire

L'étape 7 doit rechercher les liens **physiques ou statistiques justifiables** pour les cases contextuelles et planifiées, en conservant les dépendances et la non-additivité. Des expériences réelles et une métrique Q préenregistrée sont nécessaires. L'architecture du graphe et le reçu d'exécution peuvent ensuite être adaptés aux **62 mondes MATRICE** : un rapport qui dit « 62 mondes disponibles » sans preuves de mécanismes calculés sera explicitement refusé.
