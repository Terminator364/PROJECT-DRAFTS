# MATRICE R8 — Logic First V0.2 / Lot 01 (23 octobre 2026)

**Statut : laboratoire logique expérimental ; aucun IC sportif calculé.** Mandat D054 : mécanismes avant données/calibration. Dépôt autonome `PROJECT-DRAFTS`, sans modification du moteur sportif MATRICE 2.0 ni du dépôt `ChatGPT-PC`.

## Réutilisation, sans remise à zéro

- `base_v01.py` est une **copie Git blob strictement identique** du noyau V0.1 (`83fa4e00ff405d8d07fd8c5aeb066014802e7f8e`) ; l'original reste intact.
- `logic_engine_v02.py` maintient les sept règles historiques par équipe et relie **17 nouveaux IDs L3 exacts** (source R8, batches 12/16/17/22/23 et Run A). Au total : **31/355 IDs raccordés aux règles**, **324/355 non exécutables**.
- Nouvelles voies : progression centrale, flanc/aérien, secondes phases. De nouveaux modificateurs : erreur en possession sous pressing, défense antagoniste au contre, banc conditionnel si retard ultérieur.
- **Groupement anti-double compte** : progression centrale, flanc et attaque placée peuvent décrire des accès au même processus ; `SETTLED_OPEN_PLAY` n'est compté qu'une fois comme *famille* de chemins. Une famille de chemins n'est pas un but, ni une probabilité.
- `registry_builder.py` convertit **l'inventaire original complet V22** en un registre de 355 identifiants, 62 familles et provenance de chaque contrat, **à condition que le dépôt source R8 soit présent localement**. Les 324 autres ne reçoivent qu'un rôle candidat de tri, **pas une classification causale signée**. L'exécution du compilateur réel V22 n'a pas été vérifiée durant cette séance.

## Exécution

Python 3.10+ standard-library :

```bash
python -m unittest -v test_v02.py test_registry.py
python logic_engine_v02.py examples/scenario_synthetique_v02.json
python registry_builder.py --r8-repo-root /chemin/vers/ChatGPT-PC --output registre_355.json
```

Le dernier script exige la branche R8 source `research/matrice-r8-g3-depth-audit-2026-10-14` de `Terminator364/ChatGPT-PC` contenant tous ses contrats archivés. Il refuse un corpus incomplet ou des ids non conformes. Aucun téléchargement automatisé, API payante ou installation pip.

## Ce qui a été effectivement testé

- **19/19 tests locaux** sur le module V0.2 et la génération de registre, avec *double de compatibilité* V0.1 local. Cas : rejet hors T0, fuite du score cible, faux marqueur de provenance, inconnus ≠ zéro, contestation contradictoire, regroupement anti-double compte, score futur exclusif, absence d'IC chiffré, déterminisme, unicité/parents/absence de scoring des 355.
- **Les fichiers Python publiés ont été relus depuis GitHub** et leurs Git blob SHA sont égaux aux copies testées.
- **Limite de preuve : les 19 tests ne constituent pas une exécution intégrée avec le vrai `base_v01.py`**, car PC MBMPC déclaré OFFLINE durant la reprise. Le compilateur réel R8 n'a pas non plus été exécuté ici. Ces deux tests sont la prochaine porte technique.

## Contrat épistémique

`HIGH/MEDIUM/LOW` = hypothèses qualitatives sur des propriétés historiques **pas** seuils de mesure validés. L'interprétation de certains champs (en particulier duel aérien, contexte aérien et banc) doit être auditée par rapport au protocole de mesure avant données réelles. Les 3 scénarios d'état futur (nul/équipe A menée/équipe B menée) sont **exclusifs et non probabilisés**. Ils ne prétendent pas couvrir toutes les trajectoires d'un match.

`numeric_IC_theoretical_under_hypotheses = null` et `numeric_IC_calibrated = null` sans loi numérique justifiée et distribution jointe documentée. Aucune garantie de 85 %.

## Prochaine exécution

1. Exécuter les 19 tests avec la **vraie base V0.1** et le compilateur R8 V22 complet, vérifier le reçu de 355 IDs uniques ;
2. Contre-auditer les 17 nouvelles règles : direction exacte des états, double compte, limites d'interprétation et conditions d'applicabilité ;
3. Poursuivre **324 sous-paramètres restants par lots mécanistiques**, donner des rôles contextuels/gardes explicites et refuser leur activation arbitraire ;
4. Garder le code de reprise unique `Moteur/continue` (Cahier mère, D054/D055 et NEXT_ACTION), sans collecte massive sportive avant le moteur logique.

Statut MATRICE : G3 ouvert, G4/G5 non approuvées, MATRICE 2.0 gelée, aucune prédiction réelle promue.
