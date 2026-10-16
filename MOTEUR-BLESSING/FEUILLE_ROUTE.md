# Moteur Blessing — feuille de route de continuation

## Porte MB-0 — intégrer l'espace de projet [À vérifier]
- Conserver l'archive V1.1.2 intacte, reçu `R-9YPJ87CMENDW`.
- Créer/contrôler `Documents/Moteur Blessing` sur MBMPC ; placer `README.md`, `CONTINUITE.md`, `MANIFEST.json` et `JOURNAL.md`.
- Mettre à jour l'état PC séparément des états GitHub et Delivery ; n'inférer aucune extraction locale sans constat.
- Sur GitHub, dossier `PROJECT-DRAFTS/MOTEUR-BLESSING` ; aucune Actions CI automatique.

## Porte MB-1 — vérité des recettes [PRIORITÉ]
- Extraire les 62 fiches, 240 entrées, 140 formules et les 372 idées.
- Pour les 348 non mappées : matrice d'utilité/faisabilité avec unité, source potentielle, horizon de disponibilité PIT, dérivation, événement partagé, facteur de confusion, tests et politique d'inconnu.
- Traiter d'abord les sous-variables à plus grande valeur informationnelle, pas viser 348 "formules" décoratives.
- Définir le type de sortie de chaque module : observation, diagnostic, garde ou **candidate predictor**. Ne pas attribuer d'effet de but sans apprentissage.

## Porte MB-2 — collecte gratuite vérifiable
- Petit échantillon **réel**, saisons et compétitions choisies selon disponibilité des archives *pré-match* ; football-data CSV / openfootball JSON à étudier avec licences et dates, sans présumer couverture de toutes les variables.
- Identité de fixture, publication source, `published_at`, `as_of`, hash, incertitude ; date du résultat séparée ; embargo temporel.
- Cache/reprise, aucune collecte intensive sur Wi-Fi non autorisé ou données mobiles ; pas d'API payante.

## Porte MB-3 — confrontation contradictoire
- Baselines : taux de compétition, modèles simples, éventuellement Poisson régularisé ; entraînement sur saisons passées, test chronologique jamais réutilisé pour choisir des hyperparamètres.
- Metrics : Brier, log loss, calibration, couverture, performance par compétition et par qualité source ; intervalle de confiance et cas Over **et** Under.
- Ablation des mécanismes, tests de scénarios joints, validation sans double comptage. Les gains doivent résister à des contrôles négatifs.

## Porte MB-4 — produit local et livraison
- CLI Python 3.10+ reproductible ; manifeste du code, du modèle, des données et de la date de prévision.
- Sortie principale `domicile — extérieur : IC Over 1,5 XX,X %`, avec diagnostics consultables ; `EXPERIMENTAL` clairement distingué.
- Sur PC Windows faible RAM : tests légers / lots / reprise / cache ; installation explicite uniquement.
- Reçu Delivery et checksum après validation ; promotion seulement avec approbation.

## À chaque porte
Construction → audit → contre-audit → correction → réaudit, preuve enregistrée. Ne pas redémarrer le projet ; *REUSE/ADAPT/BUILD ONLY IF GAP*. Aucun budget CI Github Hosted automatique.
