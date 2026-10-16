# État vérifié — version V1.1.2 (16 octobre 2026)

## Livré, codé, déclaré dans la V1.1.2
- 62 ID de paramètres canoniques, sans suppression ;
- 240 entrées numériques définies ;
- 140 formules mathématiques **candidates** exécutables ;
- 12 interactions transversales candidates ;
- 169 tests logiciels (46 + 45 + 30 + 48), vérifiés dans la production de V1.1.2 ; **ne pas dire "relancés aujourd'hui" sans relance** ;
- 372 propositions documentaires de sous-paramètres : **24 liens partiels au code** et **348 encore non mappées**.
- Moteur expérimental avec scénarios corrélés, contrôles d'alignement des périodes/équipes, embargo temporel et interprétation restreinte d'expressions.

## Résultat négatif à conserver
Sur données **entièrement synthétiques**, 230 rencontres fictives d'entraînement et 20 de test : Brier candidat **0,385073** versus baseline **0,376084**. Aucun gain : `EXPERIMENTAL_NOT_APPROVED`. Des profils fictifs obtiennent des pourcentages distincts ; il ne s'agit pas de prédictions certifiées.

## Restant à prouver / à coder
- 348 pistes non mappées : classifier faisabilité, sources gratuites, coût, horizon, conception du calcul, dépendances, preuve de source ; ne pas prétendre pouvoir collecter les 372 gratuitement ;
- 24 liens partiels non synonymes d'extracteurs opérationnels ;
- 313 dossiers historiques hérités **non validés indépendamment** comme photographies disponibles au temps T ;
- absence de calibration sur matchs réels vérifiés et de preuve d'amélioration contre baselines ;
- asymétrie des compétitions et limites de couverture ; mécanismes seulement candidats ;
- cinq cycles de revue à chaque porte ; tests adversariaux, contrôle de contamination et reproductions sur Windows modeste.

## Source et chemins dans l'archive
`00_LIRE_EN_PREMIER.md`; `01_AUDIT_CINQ_CYCLES.md`; `02_REPRISE_COLLAB_MATRICE.md`;
`config/RECETTES_62_EXECUTABLES.json`;
`config/REGISTRE_372_RECETTES_ACQUISITION_V112.json`;
`config/ETAT_REEL_62_MONDES_V112.csv`;
`code/moteur_v112.py`;
`code/mecanismes_v112.py`;
`code/entrainer_mecanismes_v112.py`;
`tests_v112/test_v112.py`.

## Garde-fou
Ne jamais présenter V1.1.2 comme "MATRICE complètement terminée". L'objectif est un moteur pré-match vrai, auditable, capable d'apprendre de résultats Over et Under ; les unités et volumes de code ne sont pas des preuves sportives.
