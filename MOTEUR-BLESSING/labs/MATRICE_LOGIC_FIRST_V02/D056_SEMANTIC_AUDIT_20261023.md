# D056 — Audit contradictoire sémantique de MATRICE Logic First V0.2
Date : 2026-10-23. Reprise `Moteur/continue`. Laboratoire isolé, pas MATRICE 2.0.

## Pourquoi le premier audit V0.2 ne suffisait pas
Les 31 IDs sont reliés à des règles, mais un ID L3 est un **contrat documentaire**, pas la preuve qu'un niveau HIGH/LOW exprime une direction causale positive ou négative. 19 tests antérieurs utilisaient un double V0.1 local; le code réel et les contrats R8 ont été lus sur GitHub dans la reprise D056. Aucune exécution intégrée Python de V0.2 D056 n'est encore prouvée, et `IC_calibrated=null`.

## Contre-audit de quatre règles (mise en quarantaine active)
1. `R-WIDE-02`: `WIDE_AERIAL_ATTACK.AERIAL_CONTEST_CONTEXT` exige une opposition événementielle attestée et `ONE_V_ONE_DUELS.AERIAL_PRIMARY` exige identité d'opposants. HIGH pour l'existence / fréquence du duel ne signifie pas compétence aérienne supérieure ; LOW n'établit pas faible défense. **Bloquer l'inférence favorable et garder la traçabilité.**
2. `R-PRESS-ERROR-02`: le contrat `UNFORCED_MISTAKE_RISK.PASS_MISCONTROL` définit une **passe manquée non contrainte**, séparée explicitement de l'erreur sous pressing. Assimiler « erreur non forcée HIGH » à « pressing adverse crée erreur » est une contradiction de catégorie. **Bloquer.**
3. `R-SECOND-02`: `SECOND_BALL_RECOVERY.CLEARANCE_SECOND` et `SETPIECE_REBOUND` sont des contrats de second contact / deuxième phase, avec un événement propriétaire commun et une exigence d'identification de l'équipe ; ils ne deviennent pas automatiquement des chances indépendantes. **Bloquer l'activation jusqu'à la définition des incidents et dédoublonnage.**
4. `R-TRAIL-BENCH-02`: `GAME_STATE_POLICY.CONDITIONAL_SCORE_STATE_MAP` et `SUBSTITUTION_IMPACT.ELIGIBLE_BENCH_ASOF` sont des états conditionnels et d'éligibilité, pas des notes ordinales de compétence dont HIGH démontrerait un impact sur buts. **Bloquer l'activation anticipée du banc.**

## Correction appliquée
- `logic_engine_v02.py` contient `SEMANTIC_HOLDS` et force `SEMANTIC_HOLD_REVIEW_REQUIRED` pour ces quatre règles des deux équipes; il conserve `pre_semantic_hold_status`, les entrées, les lignes PIT et les motifs pour audit et contre-factuels.
- `test_v02.py` contient deux nouveaux tests de régression, et l'attente du banc a été corrigée; **résultat des tests de la nouvelle révision : NON EXÉCUTÉ**, à ne pas confondre avec les anciens 19/19.
- Six règles nouvelles demeurent dans le graphe explicatif, **quatre en suspension**; deux restent potentiellement activables sous les hypothèses strictes du laboratoire. Le noyau ancien V0.1 reste intact.
- Total des IDs **traçables par code** : 31/355; restants à relier : 324; niveau de preuve causal / prédictif : aucun. Il serait incorrect de qualifier les 31 de mécanismes causaux validés.

## Sources originelles consultées
- [V0.2](https://github.com/Terminator364/PROJECT-DRAFTS/tree/main/MOTEUR-BLESSING/labs/MATRICE_LOGIC_FIRST_V02)
- [Contrats R8 Run A, 18/10/2026](https://github.com/Terminator364/ChatGPT-PC/blob/research/matrice-r8-g3-depth-audit-2026-10-14/MATRICE/R8_G3_DEEP_20261014/L3_RUN_A_7_WORLDS_20261018/CONTRACTS_RUN_A.json)
- [Contrats R8 lot 23, 17/10/2026](https://github.com/Terminator364/ChatGPT-PC/blob/research/matrice-r8-g3-depth-audit-2026-10-14/MATRICE/R8_G3_DEEP_20261014/L3_BATCH23_PASSING_WIDE_AERIAL_20261017/L3_BATCH23_CONTRACTS.json)
- [Compilateur R8 V22](https://github.com/Terminator364/ChatGPT-PC/blob/research/matrice-r8-g3-depth-audit-2026-10-14/MATRICE/R8_G3_DEEP_20261014/L3_RUN_B_8_WORLDS_20261018/compile_v22.py)

## Prochaine porte (sans demander une nouvelle validation utilisateur)
1. Exécuter `python -m unittest -v test_v02.py test_registry.py` **avec le vrai `base_v01.py`** depuis la source GitHub relue; ne jamais revendiquer PASS avant résultat.
2. Exécuter `registry_builder.py` avec R8 V22 complet pour matérialiser le reçu des 355; signer statut, rôles, sources.
3. Revoir systématiquement les 17 interprétations HIGH/LOW et choisir entre mesure d'aptitude réelle, rôle contextuel/garde, ou rejet de l'ordinal.
4. Lot 02 : traiter de nouveaux enfants par familles sans scores inventés, garder `IC_théorique=null` faute de loi quantitative des issues et `IC_calibré=null` faute d'entraînement hors échantillon.

**Lecture sécurité : la quarantaine D056 corrige un défaut logique démontré dans les contrats source; ce n'est pas une performance prédictive.**
