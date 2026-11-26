# Contrôle de migration

1. Inventaire de chaque génération et de son origine.
2. Manifestes privés SHA-256, taille, chemins relatifs, et correspondances source/binaire; distinguer sources absentes, candidates et effectivement installées.
3. Revue des secrets et des licences; aucun transfert des sources privées vers ce dépôt public.
4. Dépôt privé dédié pour l'autorité de production; import par snapshots identifiés, sans inventer de dates de commits ni filiation non établie.
5. Vérification après transfert par relecture et empreintes; conserver les archives originales et préparer le rollback.
6. Hériter de AGENTS.md et CI_BUDGET_POLICY.json; aucun déclencheur automatique ni exécution Actions par défaut.
7. Valider la compilation et l'application réelle avant bascule d'autorité. Aucun déploiement à ce stade.
