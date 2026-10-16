# V8 — audit des 62 routes D014 en cinq cycles

1. **Construction.** Reprendre exactement les 62 cas du fichier RESTANT_62_REGISTRE.json, sans ajout de nouveaux coefficients. Construire 22 routes source/ressource, 3 prévisions, 26 contrôles des plans et 11 politiques conditionnelles.
2. **Audit.** Contrôler les 62 ID, chaque traitement, la provenance pré-T0 via V6-V7 et l'absence de label poststart dans la prédiction. Tester absence/contradiction de ressources, formule géométrique, bilan de masse sur base humide *hypothétique*, déclenchements de politiques.
3. **Contre-audit.** Déceler : (a) quantité d'eau de rinçage positive non traçable en cas de modification ; (b) séquences optionnelles initialement traitées comme contraintes dures ; (c) une prévision 044 sans formule indépendante ; (d) relation Q non validée.
4. **Correction.** Rendre le montant de l'eau observable, marquer les liens de séquence comme hypothèses, exposer explicitement 044 = `NO_FORMULA`, refuser toute probabilité Q ou score artificiel.
5. **Ré-audit.** Vérifier les 22 mutations de sources, 26 mutations d'actions, 11 mutations de politiques, 043/046 variables sur le noyau, absence de fuite poststart. **19 nouveaux tests V8 passent** ; les tests précédents 22+31+10+42+36 sont rejoués et passent en emplacement d'origine. Total = **160 tests**.

**Statut :** prototype de routage D014 cohérent dans les limites indiquées ; AUCUNE VALIDATION de causalité, de texture ou d'IC. L'exécution de 62 routes de contrôle ne constitue pas la clôture du chantier de prédiction.
