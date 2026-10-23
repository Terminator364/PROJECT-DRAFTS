# MOTEUR — Rapport de livraison logicielle D068 (23 octobre 2026)

## Périmètre exécuté et vérifié

- Source R8 canonique : 62 mondes, 355 enfants identifiés ; graphe documentaire de 1 088 arcs et 7 étapes conceptuelles. Un lien non canonique reste isolé.
- CI privée D062 : **55/55** tests réussis sur registre réel R8; 1 000 cas d'hypothèse Poisson indépendants, tous SYNTHÉTIQUES.
- CI privée D063 : **67/67** tests réussis sur le calcul de buts conditionnel aux occasions projetées. Aucune calibration sportive.
- D064/D065 : extracteur original des 355 dossiers, projet de point d'entrée unique, manifeste SHA-256; versions source R8 anciennes/récentes désormais prises en charge pour les horizons. **Premier reçu D065 76 tests unitaires réussis MAIS exécution de bout en bout échouée ; nouvelle validation toujours non constatée.**
- D066 : nouveau moteur de référence historique Poisson à information bornée par date de publication/première observation, compétition isolée, abstention en cas d'historique insuffisant et mesure Brier/logloss chronologique. **Code + tests + workflow enregistrés, nouveau résultat CI non vérifié.**
- D067 : contre-audit concret d'un corpus de **313 matchs** retrouvé sur Google Drive; **308 historiques** (181 train / 72 validation / 55 test) + **5 replays après match**. Les 313 fiches de score sont conservées dans la **branche GitHub privée**, exclues de l'entraînement pré-T0 tant que preuves originales, heure de match/fin à 90 minutes et droits ne sont pas établis. Pas d'export brut dans le dépôt public.
- D068 : lanceur Windows pour un checkout local R8 et Python3, avec logs et export dans AppData, **non testé sur le PC MBMPC actuellement hors ligne**. Protection logicielle contre l'écriture de contrats R8 privés dans le dépôt public.

## Résultat de l'ancien test V12 recalculé

Sur les **55 matchs test** sélectionnés :
- **49/55** avaient au moins 2 buts (**89,09 %**), ce qui constitue un échantillon très orienté Over.
- Le modèle retenu **C1_LEAGUE_POISSON** a un Brier rétrospectif de **0,1146655**; la référence V12 a **exactement le même score et les mêmes probabilités** sur les 55.
- Avec le seul taux observé **135/181 = 74,59 %** des matchs d'entraînement, un prédicteur constant aurait eu un Brier test d'environ **0,1182304** : amélioration historique apparente de **0,003565**, sans preuve statistique de généralisation.
- Le modèle prédit en moyenne **76,73 %**, contre **89,09 % observés** sur le test. Écart de **-12,36 points** à investiguer.
- Sur **19 406 cases famille×match**, **16 555 (85,31 %)** étaient `UNOBSERVED`. Aucun poids sportif mesuré pour tous les 62, encore moins les 355.
- Le classeur prévient lui-même que les snapshots éditeur antérieurs au coup d'envoi et les scores à 90 minutes ne sont pas intégralement certifiés.

**Le chiffre 0,1147 est une erreur quadratique moyenne de probabilité, pas une fiabilité de 88,53 %, ni une précision de 85 %.**

## État de livraison

**Livré :** composants logiques et calculateurs théoriques vérifiés, source de 355 paramètres traçable, estimateur historique intégré au code, audit ancien V12, scripts d'entrée et checkpoint.

**Non démontré :** exécution de bout en bout du dernier D065/D066, 324 effets individuels causalement signés, collecte pré-T0 originale de vrais matchs, calibration et validité sportive hors échantillon. Un programme qui renvoie un IC mathématique **sous hypothèses** ne donne pas pour autant un IC match fiable.

**Prochaine action exacte au code `Moteur/continue` :** confirmer D065b ou exécuter le moteur unique depuis une copie privée complète R8, lire les nouveaux journaux D066, corriger tout E2E; sécuriser les horaires/éditeurs de l'archive V12, revalider les matchs et comparer D066 au vrai benchmark; seulement ensuite calibrer les mécanismes R8 sur observations pré-match et geler le modèle.
