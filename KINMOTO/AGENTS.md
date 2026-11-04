# KINMOTO — consignes d'exécution

**Héritage obligatoire :** `../AGENTS.md` et `../CI_BUDGET_POLICY.json` à la racine de `PROJECT-DRAFTS` prévalent. L'allocation GitHub Actions de ce sous-projet est **0 minute par défaut** ; pas de déclencheur automatique push/PR/schedule, pas de facturation.

## Mandat
- Ne jamais modifier un jeu ou déploiement PUBLIC/STABLE sans autorisation explicite.
- Aucun paiement, API payante, bibliothèque sous licence incompatible, collecte de données ou secrets dans Git.
- Tester les véritables sensations moto (roues/sol, caméra, direction, collisions) et l'usage RAM Android/PC ; les tests Node ne suffisent pas.
- Favoriser **réemploi de code/assets libres audités** avant toute reconstruction.
- Une mission = un ticket ; une branche ; un commit ; une preuve ; une note de reprise.
- Incréments internes possibles, mais **V1 / V2 / V3** seules versions publiques majeures approuvées par l'utilisateur.
- Interdiction de qualifier une ancienne V1 ou V2 de base produit validée.
- Aucun déclenchement d'une CI hébergée n'est autorisé à ce stade. Utiliser les scripts locaux.
