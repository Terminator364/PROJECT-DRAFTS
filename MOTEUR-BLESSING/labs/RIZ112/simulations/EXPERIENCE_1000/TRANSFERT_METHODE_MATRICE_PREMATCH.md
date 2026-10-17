# RIZ-112 → MATRICE | Transfert méthodologique pré-match (sans transfert de coefficients)

## Origine et autorité
Le Cahier mère RIZ-112 et le journal GitHub forment la preuve durable de la campagne. Ce document est un **contrat méthodologique de transfert**, pas une modification des 62 familles sportives de MATRICE R8, pas un remplacement de son ADN/feuille directrice, ni une validation de pronostics sportifs.

La campagne contrôlée : 1 000 scénarios synthétiques de riz via Latin hypercube sur 9 grandeurs couplées ; H3 a calculé 690 dossiers et refusé 310 ; 20 dossiers ont IC_DEMO ≥ 85 % et 664 ont des bilans physiques théoriquement favorables ; 18 perturbations univariées ±15 % sur l'ancre SYN_0821 choisie après simulation. Ces résultats reposent sur Q* fictif et **ne se transposent à aucune probabilité sportive réelle**.

## 1. Correspondances de méthode, pas de domaine

| RIZ-112 (laboratoire) | MATRICE (application à concevoir sous son ADN R8) | Ne PAS transférer |
|---|---|---|
| Gel des entrées pré-T0 | Captures horodatées J-6, J-4, J-3, H-9, H-0 **avant le coup d'envoi**, jamais après | Observations live, blessure/line-up révélé après snapshot |
| 112 rubriques hétérogènes | Familles et sous-paramètres **distincts** définis dans la matrice sportive, actuellement 62 familles dans son propre chantier | Identité 112 = 62, nombres d'effets supposés |
| Bilans énergétiques et marge hydrique | Constraints sportives propres : disponibilité effectifs, repos, déplacements, composition et cohérence des sources | Constantes thermodynamiques du riz |
| 310 abstentions H3 | Motif d'abstention explicite selon qualité/ancienneté des sources et couverture | Affecter 0 %, imputer « sûr » |
| 18 variations ±15 % | Contrefactuels pré-enregistrés sur variables sportives réellement manipulables ou scénarios d'information | Inférer causalité réelle d'un score qui réagit |
| 20 IC_DEMO au-dessus de 85 % | Tests de seuil pour **scores purement simulés** ; classement contrôlé et falsification | « 2 % des matchs dépassent 85 % de confiance » |
| Chaîne SHA-256, CSV, graines fixées | Reproduction locale de chaque snapshot et preuve de version (puis backtests sportifs historiques séparés) | Présumer d'un horodatage tiers ou d'une certification |

## 2. Sept portes obligatoires pour toute expérimentation MATRICE

**P1 – Date d'information** : chaque champ possède `observed_at`, `available_at`, `snapshot_cutoff`, `source_id`, `status`, `age` et `units`. `available_at <= cutoff < kickoff`. `UNKNOWN` ≠ `0`.

**P2 – Provenance et intégrité** : tous les snapshots J-6/J-4/J-3/H-9/H-0 enregistrent les sources et empreintes ; les mises à jour n'altèrent jamais rétroactivement une prévision antérieure.

**P3 – Couplages sémantiques** : deux représentations du même fait (joueur, équipe, calendrier, météo, etc.) doivent coïncider, ou le dossier échoue explicitement. Ne pas compter deux fois la même influence.

**P4 – Stress multi-régimes** : explorer 500–1 000 configurations hypothétiques et contre-exemples selon un plan fixé (pas seulement des cas favorables) ; varier ± petites et grandes amplitudes adaptées aux unités. Les intervalles synthétiques sont étiquetés `SYNTHETIC`.

**P5 – Diagnostics causaux modestes** : distinguer réponse d'une variable dérivée, changement d'une décision, corrélation historique, interaction et effet causal validé. Aucune obligation de faire varier chaque famille dans chaque scénario.

**P6 – Évaluation post-match séparée** : le résultat final sert **uniquement** de label dans le jeu de validation. Aucun score ou état de match live ne doit contaminer une prévision pré-match gelée.

**P7 – Calibration et falsification** : comparer les probabilités **prévues avant kickoff** aux résultats historiques réels tenus à l'écart, par saison/ligue/date : fiabilité, Brier/log-loss, sous-groupes, couverture et abstention. Un score synthétique ou une étude sur riz ne vaut aucune calibration.

## 3. Protocole de simulation à reprendre

1. Charger le dernier ADN/feuille de route **du dépôt MATRICE**, ses 62 familles et les paramètres L2/L3 existants. Règle `REUSE/ADAPT/BUILD ONLY IF GAP` : pas de nouveau moteur concurrent.
2. Construire un journal d'expérience par match, date de gel, fenêtre pré-match et source ; garder **les données finales post-match** dans un registre séparé.
3. Produire d'abord 500–1 000 scénarios **de stress purement hypothétiques** : vieillissement de blessure, absence de titulaire, météo incertaine, déplacement, repos, composition non confirmée, conflit de sources. Marquer `NOT_ESTIMABLE` plutôt que créer de faux matches.
4. Répliquer les perturbations de chaque cas avec graines communes ; distinguer paires et interactions de véritables gains statistiques. Corriger le biais de SYN_0821 : choisir les ancrages **avant** de regarder les meilleurs résultats.
5. Pour tester l'anticipation J-6/J-4/J-3, reconstruire séparément l'état de l'information disponible **à chaque heure de gel** ; H-0 peut contribuer aux labels d'apprentissage historique sans fuite dans J-6.
6. Valider ensuite sur matches historiques **réels, hors échantillon temporel**, puis contre-auditer par championnat, saison, équipes et sources ; les simulations précédentes restent uniquement des tests structurels.

## 4. Interdictions et conclusion

- Aucun transfert de Q*, du seuil de qualité du riz à 85, de l'IC_DEMO ou de coefficients du riz vers une probabilité de match.
- Aucun changement automatique dans le dépôt sportif sans inspecter l'ADN R8, les branches et les checkpoints qui peuvent avoir avancé indépendamment.
- Les 112 rôles RIZ-112 et les 62 familles MATRICE sont des taxonomies propres ; toute analogie est documentée, pas copiée.
- Ne pas exiger que l'utilisateur réalise 1 000 cuissons : **ce sont des scénarios simulés**, déjà exécutés comme maquette.

**Décision méthodologique** : simulation → falsification structurale → sources historiques sportives → calibration temporelle. L'avancement du laboratoire RIZ-112 est un résultat de conception pour MATRICE, pas une preuve de qualité prédictive sportive. La documentation de référence est `RAPPORT_FR.md`, `results/RAPPORT_1000.json`, `results/CONTREFACTUELS_18.json` et `CAHIER_MERE.md`.
