# RIZ-112 — Step20 : mécanismes physiques et protocole Q (17/10/2026)

**Mandat** : rendre l'influence des variables *vérifiable par un mécanisme*, sans injecter des coefficients décoratifs dans `IC_DEMO` ni affirmer une probabilité réelle. **Étape d'ingénierie expérimentale**, non validation empirique de la qualité du riz.

## Réutilisation, pas un deuxième prédicteur

- `physical_influence_envelope.py` vérifie **neuf couples de variables sémantiquement identiques**, entre `case_inputs` et `prestart.inputs` : `001/033/035/036/037/038/041/042/047`. **Toute divergence échoue explicitement.**
- Une enveloppe de premier principe estime, sous hypothèses **déclarées** et avant T0, un budget d'énergie sensible, une capacité de chauffage, une marge hydrique et un **plafond thermique** d'évaporation. Elle ne simule ni la trajectoire réelle de cuisson ni les actions effectivement réalisées. Elle ne modifie **jamais** les coefficients ou l'IC H3.
- Une variation pré-T0 de 1 % d'une de ces neuf grandeurs donne, dans le cas synthétique A, une variation d'au moins une sortie physique intermédiaire. Le calcul fait apparaître le sens de la variation, mais ne prouve pas d'effet sur le Q observé ou un « gain de X points ».
- Les sept hypothèses numériques sont dans `ASSUMPTIONS_SYNTHETIQUES_NON_CALIBREES.json` avec unités, état et date de disponibilité. **Aucune hypothèse par défaut cachée.** L'estimation est limitée : capacité thermique simplifiée, température cible théorique à 100 °C, chaleur latente, pertes uniformes optionnelles, indépendance conditionnelle hypothétique ; la capacité du récipient, la convection, la chaleur réellement captée et la cinétique sont inconnues.
- `quality_outcome_protocol.py` propose un **contrat DRAFT** des **14 rubriques de sortie** 099–112 (salubrité, quantité, tendreté, séparation, homogénéité, intégrité, eau libre, brûlure, température, goût, arôme, visuel, maintien, décision). **Aucun barème Q validé, aucune formule agrégée, aucune observation réelle**. Les rubriques post-T0 sont séparées des variables prédictives ; aucune fuite temporelle n'est permise.
- `build_register_112.py` conserve la totalité des 112 rôles et les conclusions antérieures, mais étiquette **9 réponses physiques théoriques**, **14 cibles de sortie**, **89 autres rubriques** non promues à de nouveaux effets physiques. **Effets empiriques validés sur Q : zéro.**

## Lancement Windows depuis Desktop Commander ou raccourci

`step20/LANCER_RIZ112_STEP20.cmd` relance le Step19 existant, régénère l’enveloppe physique et le registre 112, exécute 45 tests, puis retourne un code d'échec en cas de problème. Aucun clic utilisateur n'est nécessaire pour les vérifications à distance.

## Commandes hors ligne

Depuis `labs/RIZ112/` :

```bash
python -m unittest discover -s step20 -p 'test_*.py' -q
python step20/physical_influence_envelope.py --packet step6/examples/A_couvercle_ajuste_112.json --assumptions step20/ASSUMPTIONS_SYNTHETIQUES_NON_CALIBREES.json --output step20/RESULTAT_A.json
python step20/build_register_112.py --lab . --out step20/REGISTRE_STEP20_112.json
```

## Contre-audit et garde-fous

- Un changement de `035` dans le JSON des cases **sans mise à jour cohérente** de la primitive de H3 est rejeté, comme déjà fait en Step19. Step20 généralise cette protection à neuf variables.
- Une valeur `UNKNOWN` n'est jamais zéro, une valeur future n'entre jamais en entrée, `NaN` / booléens / unités et sources incohérentes sont rejetés.
- La marge « énergie suffisante dans un modèle idéal » n'est pas une garantie que le riz sera cuit ou consommable. Le plafond d'évaporation n'est **pas** l'eau effectivement évaporée. L'influence sur `Q≥85` attend un barème préalable et des essais datés indépendants.
- L'IC scientifique et le nombre d'effets empiriques prouvés restent `null` et `0`. Les 9 influences sont des **relations calculatoires conditionnelles**, pas des coefficients de réussite réels.

**Suite autorisée** : clarification du barème Q avec l'utilisateur, protocole d'acquisition de vraies expériences pour deux portions, puis identification/calibration et tests sur jeux temporellement disjoints. Les 112 fiches existantes ne sont pas à redéfinir.
