# Rapport d'exécution — RIZ-112 V9

Le moteur produit désormais un **IC de démonstration** à partir des conditions initiales des préparations A, B et C : **62,40 %, 36,83 %, 0,10 %**, après 3 000 simulations chacun (graine reproductible 20261016). Un résultat de simulation n'est pas une probabilité validée de réussite de cuisine.

## De quoi dépend ce résultat ?
- Graphes de bilan de masse/d'énergie du noyau V4 (non validés pour la cuisson réelle).
- Vérification des 112 rôles / contrats (V6), graphe V7 et 62 routes fonctionnelles V8.
- Huit incertitudes *choisies pour la démonstration*, avec dépendance partagée déclarée.
- Quatre dimensions d'un substitut `Q*_DEMO` (hydratation, temps chaud, eau libre, amidon). L'effet amidon→texture n'est pas validé et le reste des cibles de qualité n'est pas modélisé.
- Une fonction minimum entre les dimensions, non une somme de bonus ou 112 notes.

## Ce que les essais prouvent
- L'algorithme exécute un calcul de probabilité de **son propre événement fictif**, depuis des JSON sans résultat futur.
- L'effet des entrées est réel **dans les équations fictives** (moins 60 g d'eau change la sortie de 62,40 à 44,87 %).
- Le changement de l'échelle fictive du critère Q* change A de 62,40 à 38,20 %. Ce n'est donc **pas** une estimation robuste ou scientifiquement calibrée de la qualité réelle.
- Aucune preuve empirique n'identifie les paramètres de texture ; dix dimensions de résultat ne sont pas prédites.
- 185 tests logiciels réussis ; aucun test Windows V9 déclaré, aucun essai de vrai riz.

## Ce qu'il ne faut jamais transférer à MATRICE
Les valeurs 62,40/36,83/0,10, les échelles de Q* et les sigma d'incertitude du riz. **À transférer uniquement :** séparation entrée pré-T0/label futur, modèle global plutôt que somme des 112 bonus, lignée des calculs, simulation d'incertitude, abstention, vérification empirique des IC.
