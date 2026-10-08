# MATRICE — consolidation contrôlée (incubation, 2026-10-08)

Statut : **inventaire et migration documentaire**. Aucun moteur n'est fusionné et aucun pronostic de pari n'est validé par cette branche.

## Périmètre
- Héritage Matrice V1.x (lois/IC), V2.2–V2.9 (statistique et versions opérationnelles).
- Infrastructure Matrice ISI 2.0 et lignée MAXV / MAXV4PP8 / M5X.
- Données historiques, corpus R&D, scripts de simulation, manifests, preuves et rollback.
- **Hors périmètre** : tout projet n'appartenant pas à la famille Matrice/MAXV, données privées et financières, exécution de mises, publication de modèles non validés.

## Autorité et état
- Les preuves transactionnelles Drive restent l'autorité du programme jusqu'à migration auditée.
- Reprise historique M5X : unité W5-053 (S106, acquisition lineups), non clôturée lors du dernier readback.
- Champion historique ROUTED_15 : 19 561/23 835 = 82,0683868 % de sélections gagnantes; couverture 23 835/70 939 = 33,5993 %.
- Cela **ne prouve pas** un rendement économique ni une performance future. Holdouts protégés et sélection historique restent gelés.

## Phases
1. Inventorier fichiers et dossiers sur Drive et ChatGPT Library avec IDs, tailles, empreintes quand disponibles, rôles et dépendances.
2. Référencer les sources survivantes; classer CANONICAL / ACTIVE / PRESERVE / SUPERSEDED_EXACT_DUP / REVIEW.
3. Concentrer les matériaux utiles dans le centre canonique unique, avec une arborescence fonctionnelle et un manifest de provenance.
4. Ranger les doublons exacts documentés uniquement si la copie survivante est vérifiée et les dépendances résolues.
5. Faire un **audit différentiel et scientifique**, avant tout rapprochement des moteurs.
6. Proposer ensuite une architecture cible et des expériences OOS préenregistrées. Fusion des modèles : **non autorisée à cette phase**.
7. Dépôt GitHub permanent dédié seulement après décision expresse et baseline reproductible.

## Sécurité et efficacité
- Ne pas déplacer/effacer sans preuve de récupération des fichiers d'autorité W5, règlements, datasets, modèles, snapshots, manifests et checkpoints distincts.
- Une liaison par ID doit primer sur le chemin; aucune rupture silencieuse des commandes de reprise.
- Ne jamais publier ici des données privées, corpus propriétaires, cotes historiques sensibles ou artefacts du patrimoine Drive. Cette branche appartient à un dépôt **public**.
- Zéro dépense supplémentaire; zéro parieur automatique; zéro GitHub Actions hébergé par défaut (voir AGENTS.md et CI_BUDGET_POLICY.json à la racine).
- Tests statiques et locaux avant toute dépense de CI. Aucune configuration de workflow automatique.

## Critères de sortie de la migration
- Un dossier racine visible par surface, sans perte de pièces distinctes.
- Registre fichier ID → rôle → décision → survivant → hash/contrôle → emplacement et restauration.
- W5-053 non manipulée tant que son statut exact n'a pas été réconcilié.
- Portefeuille Matrice/ISI/MAXV présent, sans fusion prématurée ni promotion scientifique.
