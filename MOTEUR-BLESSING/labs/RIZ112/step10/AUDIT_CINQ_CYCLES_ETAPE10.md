# RIZ-112 — Étape 10 : audit de contribution réelle, au lieu de déclarer « 112 facteurs actifs »

## Construction
Sur les 112 cases, 112 interventions unitaires ont été exécutées sur le dossier A, à **3 000 tirages Monte Carlo par cas**, graine fixée à `20261016`. Les 14 cases de qualité future restent des définitions du résultat, non des caractéristiques pré-T0. Le script `case_intervention_audit.py` et `INTERVENTIONS_112_STAGE9.json` contiennent les 112 reçus.

## Premier audit : V9
- **11/112** cas modifient numériquement `IC_DEMO` dans ce dossier précis (`001,014,033,034,036,037,038,041,042,045,047`).
- **5/112** cas déclenchent une abstention par contradiction (`013,019,020,021,035`).
- **92/112** mutations n'infléchissent PAS la sortie IC du simulateur V9, même si le traitement du cas, son statut ou sa trace change.
- **4/112** variables `043,044,046,048` sont dérivées et ne peuvent pas être directement substituées comme des entrées indépendantes ; `044` reste `NO_FORMULA`.
- Aucune intervention n'a échoué techniquement. Tous les changements sont hypothétiques, unidimensionnels et étudiés sur **une seule préparation A** ; ceci n'est ni une preuve d'absence de causalité ni une preuve d'exactitude physique.

## Contre-audit
Le V9 acceptait des modifications aux **14 définitions de qualité** tout en conservant à tort **le même `IC_DEMO`** : cela révèle un couplage manquant entre le contrat-cible et la fonction de sortie. Les actions prévues (37) et politiques conditionnelles (13) ne modifient jamais le score fictif dans ce dossier, donc la couverture 112 du V9 était un contrôle de contexte, pas un modèle à 112 facteurs.

## Correction
`ic_integrity_v10.py` lie désormais le simulateur à une empreinte exacte des **14 critères-cibles**. Toute modification des définitions, de leur version ou toute cible absente donne `ABSTAIN_TARGET_CONTRACT_CHANGED` et IC démo nul. Cela rend les critères de réussite réellement exécutoires **comme contrat d'admissibilité**, sans les convertir artificiellement en prédicteurs. Pour les trois paquets de référence inchangés, les IC démo restent A=62,40 %, B=36,83 %, C=0,10 % ; `scientific_ic_percent=null`.

## Ré-audit
**205/205 tests réussis** : 185 suites V4–V9 antérieures (dont étape 4 depuis son arborescence ZIP originale) + 20 tests de V10. La première tentative de lancer les tests V4 depuis l'arborescence de copie a échoué par mauvais chemin d'exemples; la reproduction corrigée depuis `reference/ORIGINAL_ETAPE4.zip` passe. Pas d'exécution Windows dans cette étape. Les tests prouvent le comportement du logiciel et l'effet local des perturbations sur ce modèle, **pas** la qualité de riz ou la validité d'un IC réel.

## Portée scientifique
Les **11 sensibilités numériques** concernent uniquement le modèle fictif de quatre critères. Les **14 nouvelles portes de cible** protègent la cohérence de la définition de qualité. Les **37 actions** et **13 politiques** demeurent non quantifiées dans les probabilités ; certaines sont dans le chemin de contrôle. L'échantillon réel est **n=0**. Notre état reste `IC_DEMO_ONLY__SCIENTIFIC_IC_NULL` et la directive D014 est encore ouverte.

## Transfert MATRICE
Toute affirmation « 62 mondes utilisés pour cet IC » doit être auditée de la même façon : perturber une entrée, refaire le calcul, distinguer `IC_CHANGED`, `ABSTAIN`, `UNCHANGED`, `DERIVED` et vérifier l'identité et le gel de la cible. Une case sans effet dans un scénario donné peut tout de même être pertinente dans un autre; ne jamais imposer qu'un nombre d'effets soit égal au nombre de mondes.
