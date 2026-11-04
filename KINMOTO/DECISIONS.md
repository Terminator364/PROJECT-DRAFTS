# Journal des décisions — KIN MOTO FACTORY

Les lignes sont typées : `E` exigence utilisateur, `C` constat vérifié, `P` proposition, `H` hypothèse, `N` interdit.

| ID | Type | Décision ou contrainte | Source / statut |
|---|---|---|---|
| D-001 | E | 0 FC de dépense supplémentaire obligatoire, aucun achat/API/crédit | Confirmée |
| D-002 | E | Jeu web/PWA commun, Android et PC en priorité, iPhone cible officielle avec validation réelle | Confirmée |
| D-003 | E | Faible RAM et CPU, profil Eco digne, pas de fallback 2D dégradé caché | Confirmée |
| D-004 | E | V1/V2/V3 majeures ; pas de publications quotidiennes improvisées | Confirmée |
| D-005 | E | Sensation moto, direction, contact roues/sol, trafic, graphismes et gameplay avant le volume de contenu | Confirmée |
| D-006 | E | Réutiliser des jeux, moteurs et modèles libres de qualité après audit légal/technique | Confirmée |
| D-007 | E | Conversation pilote naturelle + missions Work bornées + continuité explicite par fichiers | Confirmée |
| D-008 | C | Anciens prototypes livrés mais refusés en qualité ; ne pas les déclarer STABLE | Charte 2026-11-04 |
| D-009 | C | `PROJECT-DRAFTS` est l'incubateur privé par défaut ; GitHub-hosted Actions = 0 minute par défaut | Politique root du dépôt |
| D-010 | P | Démarrer KINMOTO en sous-dossier privé, migrer ultérieurement vers dépôt dédié si justifié | Application de D-009 |
| D-011 | P | Laisser Vercel et toute URL publique historique intacts pendant A0/A1/A2 | A0, approuvé |
| D-012 | H | `Neon Mayhem` ou `Costa Vista` pourraient accélérer le travail ; aucun n'est choisi avant benchmark | À tester A1 |
| D-013 | N | Pas de workflow automatique Actions, pas de publicité/analytics tierce, pas de secrets, pas de publication STABLE non approuvée | Interdit |

**Conflits :** la proposition passée de CI automatique est écartée : la politique existante `AGENTS.md` de `PROJECT-DRAFTS` prévaut et impose le calcul hébergé nul par défaut. Les validations programmées localement restent possibles.
