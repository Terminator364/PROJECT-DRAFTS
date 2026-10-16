# MOTEUR|CONTINUE — contrat de reprise obligatoire

## Déclencheur
Quand l'utilisateur écrit **`MOTEUR|CONTINUE`** ou **`MOTEUR BLESSING|CONTINUE`**, le nouvel assistant **doit reprendre au dernier checkpoint fiable**, sans repartir à zéro ni demander un long récapitulatif.

## Démarrage (dans l'ordre)
1. Lire `MOTEUR-BLESSING/README.md`, **ce fichier**, `ETAT_MB1_V3_20261016.md`, `ETAT_V112.md`, `MANIFEST.json`, `FEUILLE_ROUTE.md`, `JOURNAL.md` sur `Terminator364/PROJECT-DRAFTS` branche `main`. Si GitHub est indisponible, chercher la copie dans `Documents/Moteur Blessing`, puis les pièces jointes de la conversation. **Indiquer quelle source a réellement été lue.**
2. Vérifier si la branche / le répertoire / le manifeste ont reçu un **checkpoint ultérieur à V1.1.2**. Utiliser alors le dernier checkpoint dont les preuves sont complètes ; les demandes utilisateur les plus récentes priment.
3. Lire la **feuille directrice R8** et son catalogue avant toute proposition modifiant le sens des 62 paramètres. Conserver le périmètre *pré-match exclusivement*.
4. **Préférer le dernier ZIP MB-1 V3** : `MOTEUR_BLESSING_V1_1_2_MB1_V3_2026-10-16.zip`, SHA-256 `3c1bd3369309101ffdb11f41b4e62270c65f028ff138935b4058e35cf3042baa`, dans le [Drive privé](https://drive.google.com/drive/folders/1t_53nvyzLAD_wmPCo8AKwB21QgDuKGaX) ou dans la bibliothèque ChatGPT `/MOTEUR_BLESSING/MB1_V3_2026-10-16/`. Sinon rechercher la source intacte `MOTEUR_BLESSING_V1_1_2_MOTEUR_ACTUEL_2026-10-16.zip` du reçu `R-9YPJ87CMENDW`. **Ne pas confondre les documents GitHub avec les fichiers ZIP du moteur.**
5. À réception du code, **avant modification**, lire `00_LIRE_EN_PREMIER.md`, `01_AUDIT_CINQ_CYCLES.md`, `02_REPRISE_COLLAB_MATRICE.md`, puis `mb1/RELEASE_NOTES_V3_20261016.md` et `mb1/CHECKPOINT_V3_20261016.json`. Exécuter les suites `tests`, `tests_v11`, `tests_v111`, `tests_v112` et `mb1/test_mb1*.py` ; ne jamais reprendre les résultats historiques pour des tests relancés.
6. Rapporter en une phrase la **version réelle**, le **dernier commit GitHub**, le statut du **PC**, le statut **Delivery**, les **tests effectivement relancés** et la **prochaine lacune à résoudre**. Si une source manque, le signaler ; ne pas inventer de preuve.
7. Continuer directement le travail demandé ; avant chaque modification, écrire un journal DÉBUT puis FIN, avec fichiers, preuves, contre-audit et suite. Mettre à jour GitHub + manifeste de continuité ; relivrer via Delivery **lorsque l'utilisateur le demande ou lorsqu'une règle de livraison qu'il vient d'approuver le prévoit**. Ne pas programmer d'automations.

## Décisions de projet à préserver
- **Une seule mission :** produire l'IC Over 1,5 des **90 minutes réglementaires**, exclusivement à partir de données disponibles **avant le coup d'envoi**. Pas de moteur live, pas de prédiction 1X2 comme sortie principale.
- **62 mondes canoniques** et leurs sous-paramètres ; ne pas réduire les 62 à 55 en supprimant 7 éléments de gouvernance/synthèse. Des contrôles ne sont pas des effets offensifs indépendants.
- Un **paramètre est un monde** : contrat, calcul mathématique propre, sous-variables, incertitude, scénarios, relations, provenance, horizon et validations.
- Modèle hybride : mathématiques spécialisées + graphe de mécanismes + apprentissage statistique **conditionné par la preuve**, calibration temporelle, comparaison à des baselines.
- Les données manquantes sont `UNKNOWN`, non zéro. Les scénarios corrélés restent joints ; pas de valeurs post-match, pas de double comptage d'une blessure ou d'un événement.
- Aucun coefficient de "bonus" intuitif et aucune promotion d'un modèle sans validation réelle hors échantillon. Une baseline meilleure doit rester meilleure.
- Répéter des tests sur des données **fictives** prouve la mécanique logicielle, pas la compétence sportive. Exiger la provenance et disponibilité PIT des vraies archives.
- Ressources modestes : Python et bibliothèque standard quand possible, **offline-first**, budget **0 $**, pas d'API payante obligatoire, cache, transferts réseau mesurés.
- Différencier explicitement **[FAIT]**, **[TESTÉ]**, **[EXPÉRIMENTAL]**, **[BLOQUÉ]**, **[PROPOSÉ]**.
- Ne pas remplacer **MATRICE 2.0** ni proclamer G3/G4/G5 achevées sur la seule base de V1.1.2 ; décisions de promotion séparées.
- La commande **`MATRICE|CONTINUE`** conserve son propre usage global ; **`MOTEUR|CONTINUE`** reprend le sous-projet moteur uniquement.

## Questions critiques à auditer constamment
1. Chaque sous-paramètre a-t-il une **formule** et une **entrée observée** pertinentes, ou n'est-il qu'un nom dans le registre ?
2. Quel serait le résultat d'un scénario alternatif plausible et **à quelle date** cette hypothèse pouvait-elle être formée ?
3. L'interaction est-elle causale / dépendante / doublonnée avec d'autres mondes ?
4. Les données d'entraînement et de test sont-elles identifiables, **réelles**, indépendantes et temporellement valides ?
5. Quelle baseline est battue, avec quelle métrique, quel effectif et quel intervalle d'incertitude ?
6. Le code tourne-t-il sur matériel modeste, et la reproduction a-t-elle été observée, sans coût caché ?

## Règle de fin de session
Actualiser `JOURNAL.md`, `MANIFEST.json`, `ETAT_V112.md` ou son successeur, et le dossier local si accessible ; conserver les anciennes versions et les preuves négatives. Une nouvelle conversation doit pouvoir répondre **"nous en étions exactement ici"** sans fouiller des heures de conversation.

## État d'autorité constaté le 16 octobre 2026 — MB-1 V3
- **Checkpoint** : `mb1/CHECKPOINT_MB1_V3_20261016.json` via `MANIFEST.json.latest_specialized_checkpoint`.
- **Moteur baseline** : V1.1.2 (100 fichiers). MB-1 V2 : 8 ajouts. MB-1 V3 : 6 ajouts. **114 membres ZIP**, les 108 précédents inchangés, empreinte ZIP complet `3c1bd3369309101ffdb11f41b4e62270c65f028ff138935b4058e35cf3042baa`.
- **Tests** : 169 +18 +28 = **215 tests réussis** sur ChatGPT/Linux, pas Windows ; pas de preuve de performance réelle.
- **372 exigences** : 25 correspondances directes de conception, 50 contextuelles, 297 non reliées ; 11 voies d'acquisition candidates et 12 groupes de partage de primitives. **Aucune correspondance = validation sportive**.
- **Synchronisation** : Drive privé + bibliothèque ChatGPT pour les ZIP, GitHub pour l'autorité documentaire, PC MBMPC pour la continuité et le checkpoint. **L'archive ZIP complète n'est pas encore installée sur Windows** ; téléchargement Drive privé direct depuis le terminal Windows renvoie à une connexion Google.
- **Scientifique** : score uniquement pré-match 90 minutes ; `EXPERIMENTAL_NOT_APPROVED`; aucune vraie archive PIT tierce authentifiée. Préserver exactement cet état et continuer vers les données historiques authentifiées, pas vers l'activation prématurée des coefficients.
