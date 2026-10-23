# D070 — Livraison logicielle V1.1.2 + 1 000 IC de laboratoire

**Date :** 2026-10-23. **Suite autonome de D069**, sans modification des archives R8 originales.

## Résultat réellement produit

- Un paquet ZIP **MOTEUR_D070_LIVRAISON_AUTONOME_1000_IC_112_VARIABLES_2026-10-23.zip** (13 530 227 octets) a été créé dans le conteneur et copié dans la **Bibliothèque personnelle** de l'utilisateur au chemin `/MOTEUR_D070/`. Lien de téléchargement de conversation : `sandbox:/mnt/data/MOTEUR_D070_LIVRAISON_AUTONOME_1000_IC_112_VARIABLES_2026-10-23.zip`.
- L'archive contient **111 fichiers**, dont **100 fichiers du ZIP source original V1.1.2 vérifiés identiques octet par octet** avec SHA-256. L'archive source SHA-256 : `5ef731d6ee4b5edb8a741c59a565d4f7363be84eb9225e814345cb0a04fe89e0`. Un manifeste de livraison vérifie **110 fichiers** et le ZIP passe son test d'intégrité.
- Tests historiques V1.1.2 : **46 + 45 + 30 + 48 = 169/169 PASS**. Six nouveaux tests D070 **6/6 PASS** dans le dossier de construction. Dans un nouveau répertoire après extraction du ZIP : manifeste **PASS**, tests D070 **6/6**, tests historiques **169/169**.
- Deux générations complètes distinctes des **1 000 scénarios** ont été produites par le test D070 et comparées octet par octet avec résultats identiques. Une troisième régénération facultative après extraction a été **interrompue par une limite d'exécution** ; elle ne constitue pas une preuve de succès supplémentaire et n'annule pas les tests de génération antérieurs.
- **1 000** scénarios **100 % synthétiques**, avec **112 champs numériques changés par scénario** répartis dans **58 familles** de l'ancien moteur. **1 000 IC distincts**, compris entre **55,702838 % et 58,988920 %** (aucun résultat de match réel).
- Perturbation locale univariée sur les 112 champs : **105** modifient une ou plusieurs sorties de **formules**, **18** modifient au moins une interaction transversale candidate, mais seulement **8** modifient l'IC expérimental final de ce profil précis. Cela fait apparaître l'écart entre volume de données, mécanismes calculés et probabilités pondérées.
- Lanceur Windows **`LANCER_MOTEUR_D070.cmd`** : un double-clic après extraction, **Python 3 requis**, aucune API payante et aucun Desktop Commander. Le lanceur n'a PAS été installé/testé sur le PC MBMPC (dernier état : hors ligne).

## Domaines à distinguer

**V1.1.2** : 62 familles, 240 entrées candidates, 140 recettes et 12 interactions, 372 propositions de sous-paramètres documentaires. Les **112** champs numériques qui varient dans D070 sont prélevés dans les **240** de V1.1.2.

**R8 privé D060-D069** : **355 sous-paramètres** de source contractuelle (341 + 14 historiques et variantes selon source) répartis dans 62 familles; **cela n'a PAS été fusionné causalement avec 112 entrées**. L'intégration complète D069 n'a pas fourni de reçu privé `CI_READBACK_D069.json` vérifié. Les 324 effets causaux restants restent sans poids individuel validé. Ne pas confondre ces périmètres.

**Fiabilité sportive** : nulle calibration sportive démontrée. Le candidat V1.1.2 s'était montré inférieur à sa référence au test synthétique : Brier 0,385073 contre 0,376084. Les archives réelles V12 du Drive sont rétrospectives et non entièrement attestées avant le match. Aucune fiabilité 85 % ne peut être déduite de ces expériences.

## Fichiers de livraison

- `README_D070_A_LIRE_EN_PREMIER.md` (instructions Windows, 0 $).
- `LANCER_MOTEUR_D070.cmd` (lancement en un clic, Python 3 nécessaire).
- `code/generer_1000_scenarios_d070.py` (112 variations/simulation, 1000 calculs, graine 20261023).
- `resultats/D070/IC_1000_SCENARIOS_SYNTHETIQUES.json` (1000 IC).
- `resultats/D070/INPUTS_1000x112_SYNTHETIQUES.jsonl` (1000 jeux d'inputs).
- `resultats/D070/AUDIT_INFLUENCE_112.json` (105/18/8 étages).
- `MANIFEST_LIVRAISON_D070.json`, `VERIFIER_CODE_ET_MANIFESTE.py`, `AUDIT_FINAL_D070.md`, `tests/test_d070.py`.
- `heritage_original/` contient les 100 fichiers de la version V1.1.2 inchangés, avec les archives précédentes en héritage.

## Continuité

Le logiciel local de simulation **D070 est livré et testé**. Le **moteur scientifique de prévision R8 complet n'est pas terminé** : confirmer l'exécution privée D069 puis collecter les éléments authentiques horodatés pré-T0, corriger les lacunes des 324 mécanismes et valider hors échantillon. N'inventer ni précision ni influence pour conclure.
