# RIZ-112 V12 — Données qui changent ≠ 112 effets de Q prouvés

**Cas :** 100 paquets complets, avec les 44 observations/conditions disponibles avant T0 diversifiées ; 4 sorties recalculées ; 37 actions et 13 politiques pouvant varier ; 14 résultats définissant Q gelés pour rester comparables.

## Mesures exécutées

- 100 dossiers ; 500 tirages de proxy Monte Carlo par dossier admissible.
- Statuts : {"ABSTAIN_UNSUPPORTED_VESSEL": 47, "DEMONSTRATION_ASSUMPTIONS_ONLY_NOT_REAL_Q": 30, "ABSTAIN_PRESTART_CONTRADICTION": 11, "ABSTAIN_CONTRADICTION": 12}.
- 112 interventions sur 2 situations de référence : {"CHANGES_ASSUMED_DEMO_IC_FOR_TESTED_PERTURBATION": 12, "CHANGES_OPERATIONAL_GATES_NOT_CALIBRATED_Q": 52, "NOT_DEMONSTRATED_TO_CHANGE_IC_OR_GATE": 26, "CHANGES_ELIGIBILITY_OR_INVALIDATES_ASSUMPTIONS": 4, "DERIVED_OUTPUT_NOT_INDEPENDENT_RANDOM_INPUT": 4, "TARGET_DEFINITION_LOCKED_NOT_INPUT": 14}.
- **26** cas sans influence démontrée localement : voir `GAPS_26_UNRESOLVED.json`.
- Étiquette de marmite métal vs céramique (tous autres paramètres gelés) : 71.4 % contre 71.4 %, **même IC**, aucune loi de transfert liée au matériau établie.
- Le rendement thermique 42, s'il change comme valeur explicite, affecte le proxy (0,45 → 44,60 % ; 0,75 → 68,77 % sur dossier A). Cela **n'établit pas** que le matériau cause cet écart.

## Interprétation stricte

Le modèle ne peut pas légitimement produire 112 influences quantitatives : 14 définitions du résultat ne sont pas des données pré-T0 ; 4 variables sont dérivées, et des actions/politiques conditionnelles ont besoin de données de réponse de processus. La dernière version V11 modifiait en réalité moins de champs d'entrée que son registre de 112 rôles pouvait le suggérer. V12 diversifie les 44 champs et publie des dossiers complets.

**Statut :** IC calculé uniquement pour Q* DEMO, non probabilité réelle de réussite. `scientific_ic_percent=null`.

## Cinq cycles

1. **Construction :** diversification forte 44/44, 37 plans, 13 politiques sur 100 scénarios ; 14 définitions non tirées au hasard.
2. **Audit :** 112 contre-interventions croisées sur A et B (224 tests d'effet).
3. **Contre-audit :** la simple catégorie `material=ceramic_rated` n'influence pas les équations ; manque vérifié, et lacunes restantes 26.
4. **Correction :** trois champs manquants du catalogue initial corrigés (001, 002, 017) ; ancien test V4 repris dans son arborescence historique, et pas dans un chemin reconstruit erroné.
5. **Réaduit et preuve :** 241/241 tests réussis, CRC et empreintes ZIP à produire lors de livraison ; aucune promotion scientifique.
