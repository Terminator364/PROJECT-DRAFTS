# KIN MOTO A2 — Sécurisation du préflight GLB, 05/11/2026

**Mandat limité :** renforcer l'outil d'audit d'assets 3D sans importer un nouveau modèle, sans modifier le moteur WebGL ni les scènes. Rappel : un statut `PASS_TECHNICAL` n'est **jamais** une preuve juridique.

## Défauts adverses identifiés

La version v0.5.5 pouvait accepter un champ `POSITION:-1` en Python, parce que `-1 >= len(accessors)` est faux et `accessors[-1]` est un index légal en Python alors qu'il est illégal en glTF. Le test des index de triangles pouvait aussi ignorer silencieusement un index négatif. Il manquait un contrôle de dépassement des `bufferViews` hors `buffers`, ainsi que le rejet explicite d'un `count` négatif.

Un fichier excessivement lourd était rejeté **après** le parsing de la structure, ce qui sollicitait inutilement la mémoire.

## Correctifs de l'outil

- Refuser `POSITION` et `indices` négatifs ou hors limites.
- Vérifier les références aux `bufferViews`, leurs offsets et longueurs, et les comptes d'accessors.
- Refuser les chunks GLB non alignés à 4 octets.
- Contrôler la taille du fichier en amont de l'analyse JSON.
- Préserver les limites existantes : 2 Mo, 12 000 triangles, aucune URI externe, licence `UNVERIFIED`.

## Validation

- Un prototype local à préflight renforcé a passé **17/17 tests Python** : les 7 scénarios historiques répliqués et 10 scénarios malformés supplémentaires (index POSITION -1, indices -1, vue hors BIN, nombre de sommets négatif, taille >2 Mo). Tests synthétiques, non issus d'un véritable modèle 3D externe.
- Les dix nouveaux cas sont enregistrés dans `tests/test_glb_audit.py` sur cette branche.
- **NOT_TESTED ici :** réexécution de l'intégralité de la suite Python depuis le commit GitHub, import de la vraie moto CC0, rendu GLB texturé, iOS, Android et performances.

## Contrôle juridique et release

La page officielle du candidat Road Sportbike affiche CC0 1.0, environ 254,7 Ko, 5 156 triangles, 3 animations, URL https://cdn.3dassets.dev/assets/15424/v1/model.glb ; le binaire exact n'a pas été acquis dans cette session. Ne renseigner aucun hash fictif et ne pas marquer le modèle `APPROVED`. Aucun import sur la branche.

**Statut : DRAFT / revue indépendante requise.** Ne pas fusionner ce correctif ni publier de nouvelle V1 sur la seule base des tests synthétiques.

## Contre-audit de la structure JSON interne

Cinq cas adverses supplémentaires testent `meshes=None`, `primitives=None`, `attributes=None`, `images=[None]` et `animations` de type chaîne. La branche rejette ces structures sans faire confiance à `.get()` sur des éléments non-dictionnaires. Prototype local : **17/17 tests Python PASS** (7 scénarios hérités répliqués + 10 cas adverses). Une exécution dans l'environnement du dépôt GitHub demeure obligatoire avant fusion ; aucun fichier GLB externe réel n'a été importé.
