# Livraison de 1 000 scénarios calculables × 112 rubriques (18 octobre 2026)

**Archive Drive vérifiée :** https://drive.google.com/file/d/1GQMDD5LgU31TYSKsAwrbRwzMWZKcS6Bm/view?usp=drivesdk

- 1 000 lignes, 1 000 valeurs numériques **IC_DEMO** et 112 emplacements de rubriques par ligne (108 fiches explicites et 4 rôles dérivés).
- Fichier CSV 120 colonnes : 8 colonnes de métadonnées et 112 rubriques. Chaque cellule contient une valeur numérique d'entrée ou un **état explicite**. Le JSONL détaillé expose groupe, unité, état et valeur de chaque rubrique.
- Neuf grandeurs pré-T0 seulement ont été perturbées cohérentement, identifiants 001/033/035/036/037/038/041/042/047 ; 103 autres rubriques sont **présentes mais non perturbées**. Les sorties 099–112 restent nulles et quatre rôles dérivés ne sont pas des entrées indépendantes.
- Pour obtenir exactement 1 000 IC_DEMO, 1 448 candidats Latin hypercube sur 9 dimensions ont été étudiés ; 448 abstentions préalables ont été conservées dans les comptes, et 1 000 scénarios H3 calculables retenus. **Échantillon conditionnel biaisé : non représentatif**.
- 22 des 1 000 IC_DEMO atteignent au moins 85 % ; maximum 92,5 %. Ce sont des scores de modèle, **jamais des probabilités validées** sur du riz réel. Aucun réel Q, aucune cuisson mesurée ni effet causal réel validé.
- Script reproductible et rapport local dans ce dossier ; le ZIP cloud comprend la table CSV, JSONL, catalogue, guide, rapport et script.
- SHA-256 vérifié après re-téléchargement Drive : `bb53e428da33e84f546843adaa3f63398e10a4438179769a61fbf0a048887032`, ZIP CRC PASS, 300 864 octets.

**Continuité :** ce dossier complète sans remplacer l'expérience initiale de 1 000 scénarios (690 IC et 310 abstentions). Pour MATRICE, ne transposer que la discipline de simulation, l'abstention, la provenance et les contre-épreuves pré-match.
