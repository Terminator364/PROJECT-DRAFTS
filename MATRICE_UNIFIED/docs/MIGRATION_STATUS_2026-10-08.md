# Matrice — statut du nettoyage documentaire (2026-10-08)

Statut : **PHASE DOCUMENTAIRE LIVRÉE / GATE OPÉRATIONNEL OUVERT**.

## Résultats prouvés
- Le hub historique Drive reste l'autorité opérationnelle du projet ; un centre unique de consolidation y est rattaché.
- L'arborescence accessible depuis les zones de départ définies a été recensée récursivement ; toutes les branches incluses sont clôturées dans un registre privé.
- La bibliothèque ChatGPT a une racine unique pour les archives Matrice/ISI/MAXV. Les documents isolés ont été regroupés et un tableau privé de provenance a été créé.
- Cinq familles de doublons ont été vérifiées par empreinte SHA-256. Leurs copies supplémentaires sont isolées, **pas effacées**.
- Les modèles statistiques, les checkpoints scientifiques et les dossiers de contrôle vivants ne sont pas fusionnés ni modifiés.

## Alertes / gates
- Huit anciens dossiers Library présentés comme vides par la lecture standard ont **refusé une suppression non récursive** car le stockage indique des contenus. Ils sont protégés, aucune suppression forcée n'a eu lieu.
- La structure opérationnelle du worker local dépend d'un dossier et d'un chemin configuré dans Windows. Le poste est joignable, mais la configuration effective et un redémarrage sain n'ont pas été certifiés. L'ancien chemin Drive reste une exception de compatibilité.
- Quelques accès rapides/systèmes actifs restent hors de l'emplacement de consolidation pour éviter de rompre les anciens automatismes.
- Le dépôt d'incubation est **public** : aucun jeu de données, identifiant privé, résultat détaillé ou code propriétaire ne doit y être ajouté. Le nettoyage du HEAD ne garantit pas l'effacement de l'historique Git public.

## Séquence de reprise
1. Inspecter l'autorité Drive privée et le registre complet d'objets/dépendances.
2. Lever l'incertitude sur les dossiers Library non lisibles. Pas de `recursive=true` tant que la liste n'est pas fiable.
3. Au dernier kilomètre seulement, vérifier la configuration worker PC, effectuer une sauvegarde, simuler les changements de chemin, prévoir le rollback et valider des heartbeats frais.
4. Fermer le gate documentaire/physique puis seulement lancer un **audit différentiel** des moteurs sous tests comparables.
5. Après accord humain, passer à la conception d'une architecture unifiée ; aucune fusion scientifique automatique pendant le nettoyage.

## CI
Règle héritée de `AGENTS.md` et `CI_BUDGET_POLICY.json`. Aucun GitHub Actions automatique ni runner hébergé demandé par ce checkpoint.
