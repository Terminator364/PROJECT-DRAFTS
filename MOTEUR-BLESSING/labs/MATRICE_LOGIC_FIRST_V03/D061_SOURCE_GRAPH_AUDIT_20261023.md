# D059 → D061 — Audit d'intégration des relations R8 et des schémas originaux
**Date : 23 octobre 2026 — MOTEUR/CONTINUE**  
**Périmètre : moteur logique expérimental ; MATRICE 2.0 et branche canonique R8 inchangées.**

## Résultats observés, non présumés

L'exécution GitHub Actions privée du laboratoire R8 a confirmé :
- D059 : vérification indépendante du journal `JOURNAL_EVENEMENTS.jsonl` (168 événements, chaîne de hachage valide) et du point de reprise `continuity/resume.py` (**PASS/PASS**).
- D060 : compilation de 355 sous-paramètres authentiques / 62 mondes; récupération **des 12 contrats sources archivés en octets authentifiés**; **355 nœuds**, **1 088 liens documentaires** après normalisation des références.
- Parmi ces liens : **997 relations vers un monde**, **1 relation vers un sous-paramètre existant**, **90 relations de recouvrement d'incidents**. Une relation vers un ID hors catalogue a été conservée comme **référence orpheline non résolue**, jamais transformée en influence inventée.
- D061 : champ `definition_du_sous_parametre` authentique présent dans **306/355** originaux; **49/355** ne l'ont pas. Pour 12 de ces 49, un champ textuel alternatif (`question`) est disponible ; pour **37**, aucun champ textuel descriptif parmi ceux explicitement reconnus n'est trouvé. Un intitulé `name_fr` n'est PAS traité comme définition.
- Dernière CI D061 : **40/40 tests PASS**, audit des sources et compilation intégrée R8 `all_pass=true`. Résultats privés : `CI_READBACK_D061.json`, `FIELD_AUDIT_355_D061.json`, `SOURCE_GRAPH_355_D060.json`, `SEMANTIC_ALL_355_ARCHIVE_D060.json` sur branche `research/moteur-logic-first-d057-2026-10-23` de `Terminator364/ChatGPT-PC`.

## Contre-audit des relations

L'audit a révélé que `related_worlds` dans les contrats R8 peut contenir :
1. un ID de monde canonique (ex. `WEATHER`);
2. un ID d'enfant du catalogue 355 (ex. `PITCH_STADIUM.SURFACE_PHYSICAL_PROPERTIES`);
3. une référence à un ID **absent** du catalogue (ex. `PITCH_STADIUM.STADIUM_SPATIOTEMPORAL_MATCH`).

Le premier prototype D060 bloquait sur les types 2 et 3. Après réparation, le type 2 est un lien `RELATED_CHILD`, le type 3 une anomalie `NONCANONICAL_SOURCE_REFERENCE_NO_INFERENCE`. Aucun n'est une preuve de causalité sportive.

## Ce que couvrent les 355 exactement

- 355/355 enfants : contrat source / métadonnées / rôle provisoire / graphe de dépendances **documentaires** disponible.
- 31 enfants : déjà raccordés à des hypothèses expérimentales V0.2. **10 gardés en retenue sémantique**. Les 21 autres restent des hypothèses **non calibrées**.
- Les **324 autres** : reconnus dans le graphe et la chaîne PIT ; ils ne possèdent toujours pas de mécanisme causal validé à effet signé vers les buts. Les 1 088 arcs ne sont pas 1 088 lois physiques/statistiques.
- Aucune loi quantitative commune `P(buts | entrées pré-match)` validée, aucun jeu d'événements pré-match indépendamment datés, ni validation hors échantillon. **IC théorique probabilisé = null ; IC calibré = null.**

## Travaux non clos et prochaine porte D062

Réaliser une **revue sémantique humaine/source par enfant**, en commençant par les 37 sans champ descriptif reconnu et l'unique référence orpheline, et documenter le mécanisme propre à son monde, les dépendances de l'équipe A et B, la temporalité, la concurrence de causes, l'anticompte et les états de données. Distinguer formellement `unknown`, `non applicable`, `insuffisant`, `hypothèse discutée` et `mécanisme validé`. Ne calculer d'IC que lorsque des lois probabilistes explicites et des données chronologiquement admissibles le justifieront.

**Statut : phase d'intégration documentaire complète, phase causale/prédictive non terminée.**
