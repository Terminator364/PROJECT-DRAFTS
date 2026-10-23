# MOTEUR RIZ112 — Retour au mandat du Cahier mère : 1 situation → 44 entrées → 1 IC global + 44 diagnostics conditionnels

**Date :** 23 octobre 2026. **Code de reprise :** `Moteur/continue`. **Origine :** directive utilisateur contestant les « 128 trucs » et demandant « pour chaque paramètre [...] un IC ».

## Les textes d'origine tranchent la finalité

Au début de `CAHIER_MERE.md`, il est écrit qu'il s'agit d'un **laboratoire pour MATRICE ADN R8, et non d'un moteur de recettes**. Le mandat §0 prévoit exactement : `données initiales pré-T₀ sourcées → mécanismes/interactions → IC sur qualité de la situation`. L'indice final vise `P(Q≥85 | X_avantT0)` une fois calibré. Les 112 rubriques étaient le périmètre général; depuis D041/D043, le modèle prédictif utilise **44 entrées PRESTART**, R001…R042, R045 et R047.

### Clarification mathématique obligatoire : ne plus confondre les quantités

1. **Un scénario** est un vecteur **de 44 valeurs initiales** (certains paramètres peuvent dépendre les uns des autres).
2. **Un IC global par scénario** est le résultat conjoint de ces 44 entrées **et de leurs interactions** : pour 1000 scénarios, 1000 calculs IC globaux. Certains nombres peuvent être égaux.
3. Pour voir l'importance de **chacun des 44 paramètres dans CE scénario**, calculer **44 contre-factuels conditionnels** : `IC(x_1,…,x_j',…,x_44)` en gardant les 43 autres entrées fixes, puis `delta_IC_j = IC_modifié - IC_original`.
4. Cela donne **44 valeurs d'IC contrefactuels et 44 deltas par scénario**, à ne pas confondre avec 44 probabilités de réussite indépendantes. Les paramètres n'ont pas de « probabilité de bon riz » seuls.
5. **Les 128 tirages Monte Carlo** utilisés jusqu'ici sont une **méthode interne facultative d'estimation du seul IC du scénario**, et NON 128 situations demandées, NON 128 paramètres, NON 128 résultats d'IC indépendants. L'architecture externe ne doit pas dépendre de cette valeur 128. Une autre méthode d'inférence pourrait la remplacer si elle est définie et testée.
6. **Si la demande « 1 IC pour chacun des 44 paramètres » signifie littéralement 44 probabilités autonomes**, ce n'est pas encore un objet mathématique défini dans le Cahier mère ; ne pas l'inventer ni attribuer arbitrairement 44 coefficients.

### Expérience supplémentaire réellement exécutée pour éclairer la demande

Un prototype reproductible `diagnostic_44_impact_IC.py` a été écrit et exécuté avec le modèle V3.1 et **deux situations complètes** : S0001 (issue des 1000 dossiers archivés) et FAVORABLE_REFERENCE (situation témoin). Pour chacune, le même moteur calcule une fois l'IC global et ensuite **44 IC conditionnels**, en modifiant une seule des 44 entrées avec une alternative pré-déclarée, même graine et même budget numérique. Les 1000 situations historiques ne sont pas écrasées.

| Situation | IC global | Paramètres examinés | Variations de l'IC détectées | Neutres localement |
|---|---:|---:|---:|---:|
| S0001 (archive originale) | 64,844 % | 44 | 40 | 4 |
| FAVORABLE_REFERENCE | 88,281 % | 44 | 40 | 4 |

Quelques exemples sur **S0001** :

| Paramètre | Valeur initiale → hypothèse alternative | IC avant | IC si seule cette entrée est modifiée | Delta |
|---|---|---:|---:|---:|
| R001 masse de riz | 180,35 → 190 | 64,844 % | 65,625 % | +0,781 pt |
| R002 eau disponible | 546,27 → 250 | 64,844 % | 33,594 % | −31,250 pt |
| R003 sel | 1,766 → 0,6 | 64,844 % | 54,688 % | −10,156 pt |
| R004 matière grasse | 2,184 → 0 | 64,844 % | 64,062 % | −0,782 pt |
| R005 eau de rinçage | 901,45 → 90 | 64,844 % | 64,844 % | 0 pt |

Les quatre neutralités sont **correctes dans ces conditions** : changer un paramètre ne doit pas produire d'effet forcé lorsqu'il n'est pas limitant. Ces hypothèses alternatives démontrent une sensibilité **conditionnelle**, pas une mesure causale ou calibrée sur riz réel.

Le pilote contient **88 lignes de contre-factuels (44×2)**, plus **2 IC globaux**. **Il ne prétend PAS avoir exécuté 44 000 contre-factuels pour les 1000 scénarios.** La campagne V3.1 originale a, elle, bien **1000 IC globaux réellement calculés**.

### Étape suivante d'architecture

- Formaliser la sortie du moteur comme `{scenario_id, 44_inputs, mechanisms, IC_global, 44_parameter_diagnostics, provenance, uncertainty, status}`.
- Vérifier que tout diagnostic pointe vers **le même scénario et le même moteur** ; effectuer des interventions comparables (même graine ou même résolution d'incertitude) ; enregistrer les interactions qui rendent les contributions non additives.
- Étendre les diagnostics à toutes les 1000 combinaisons **avec un budget de calcul vérifié**, sans présenter les 128 tirages internes comme des scénarios ; conserver les 1000 IC globaux et les traces précédentes inchangés.
- Aucun IC scientifique réel sans données post-cuisson indépendantes et calibration.

**Implémentation additive** : `pret0_focus/V3_1/diagnostic_44_impact_IC.py`. Le ZIP pilote complet comprend le code local portable, les dépendances V3.1, les 88 lignes CSV, les deux IC et le reçu JSON. La version officielle du Cahier mère doit préserver les demandes exactes et les différences entre travail effectué et travail à étendre.
