# D071C — Le MOTEUR logique R8, avant les données et Windows

## Correction de priorité — 24 octobre 2026

Le but convenu est de composer les paramètres et sous-paramètres en **règles logiques**, non de commencer par des millions de matchs, une optimisation de poids ou l'installation Windows.

**Prototype autonome implémenté :** `moteur_logique_v1.py`, `generer_entree_demo.py` et tests; Python standard, sans réseau ni API. L'algorithme accepte le vrai graphe R8 (62 mondes, 355 enfants, 1088 liens documentaires, dont un lien `to_child`), sépare HOME et AWAY (710 emplacements), vérifie la date pré-T0, applique TRUE/FALSE/UNKNOWN/CONTRADICTED, et synthétise 5 familles de règles logiques conditionnelles pour les deux équipes.

Les règles combinent les prémisses portant sur la capacité de l'équipe, les occasions, les facteurs extérieurs, la défense adverse et la conversion des occasions. Elles rendent une *possibilité logique expliquée*, sans attribuer de signe ou coefficient imaginaire à des paramètres non certifiés. Les relations originales R8 sont documentaires, pas des causalités démontrées.

**Tests :** 12/12 tests locaux réussis (données de laboratoire à structure R8), dont refus de fuite temporelle, identité, doublons, contradictions, interdiction de faux taux, test de la particularité originale R8 `each_goals_effect_human_signed=0` et d'un lien `to_child`. Le code public initial avait auparavant aussi passé 11 tests sur une exécution cloud. Le code a été corrigé pour les types réels du graphe source.

**Contrôle direct sur le graphe original privé en lecture seulement :** 355 identifiants, 62 mondes, 1088 liens d'origine; 710 emplacements de deux équipes instanciés dans un essai fictif. Une démonstration indépendante des règles en mémoire a établi 6 cooccurrences documentaires et 9 parcours conditionnels satisfaits sur 10 tests de prémisses. Il s'agit d'une **vérification par l'interpréteur du contrôle**, pas d'un reçu Python complet exécuté sur le dépôt privé.

Le résultat Over1.5 **numérique** demeure `null` si aucune loi quantitative n'est déclarée. Si l'utilisateur fournit explicitement des taux hypothétiques domicile/extérieur, la formule mathématique Poisson produit un **IC théorique sous hypothèses**, non appris des 355 champs, jamais une précision sportive validée. Le cheminement logique ne dépend pas de cette option.

## Ce qui est livré

- Code : `MATRICE_LOGIC_FIRST_V03/moteur_logique_v1.py`
- Générateur d'un exemple sur de vrais ID du graphe : `generer_entree_demo.py`
- Tests : `test_moteur_logique_v1.py` (12 tests locaux, 11 dans la première version publique)
- Paquet indépendant de code et tests : `MOTEUR_R8_LOGIQUE_V1_CODE_ET_TESTS_2026-10-24.zip` dans la Bibliothèque ChatGPT `/MOTEUR_LOGIQUE_V1/`.
- Graphe original reste privé dans `Terminator364/ChatGPT-PC` sur branche `research/moteur-logic-first-d057-2026-10-23`, fichier `SOURCE_GRAPH_355_D060.json`.

## Frontières conservées

- Tous les 355 paramètres sont instanciés, mais **aucun n'obtient un coefficient sportif fabriqué**.
- Les 1088 relations sont des liens d'examen, pas automatiquement des mécanismes de buts.
- Les tests sur structure fictive sont PASS; le test Python authentique en environnement privé **n'a pas de reçu PASS**.
- La maturation des règles causalement orientées pour chaque sous-paramètre et les preuves réelles seront une étape ultérieure; **pas nécessaire pour disposer d'une première version du moteur logique opérationnel**.

## Continuité
Reprise universelle : `Moteur/continue`. **Prochaine priorité : enrichir et contre-auditer les règles logiques individuellement, puis exécuter Python sur source R8 privée; la calibration empirique est secondaire.** Ne pas redémarrer D070, ne pas remplacer la logique par un moteur de statistiques.
