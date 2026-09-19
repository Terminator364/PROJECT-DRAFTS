# PROJECT-DRAFTS

Dépôt privé d’incubation par défaut pour les nouvelles idées, expériences et travaux qui nécessitent un dépôt GitHub mais n’ont pas encore leur dépôt permanent.

## Règle permanente
- Nouveau projet sans dépôt dédié → commencer ici.
- Garder chaque projet dans un sous-dossier clairement nommé.
- Dès qu’un projet devient suffisamment structuré, stable ou important → créer son dépôt privé dédié et y migrer son architecture.
- Ne pas utiliser PROJECT-DRAFTS comme autorité permanente d’un projet arrivé à maturité.

## Règle GitHub Actions — obligatoire pour tout projet actuel ou futur
La politique `AGENTS.md` + `CI_BUDGET_POLICY.json` de ce dépôt est la règle canonique pour les projets ChatGPT de Terminator364.

Avant de créer, promouvoir ou initialiser un nouveau dépôt permanent :
1. lire `AGENTS.md`;
2. lire `CI_BUDGET_POLICY.json`;
3. copier `AGENTS.md` dans la racine du nouveau dépôt;
4. partir avec **0 workflow GitHub Actions automatique**;
5. ne pas ajouter de déclencheurs `push`, `pull_request` ou `schedule` sans autorisation explicite du propriétaire;
6. considérer **0 minute GitHub-hosted Actions/jour comme l'état normal**;
7. réserver les runners GitHub aux checkpoints réellement indispensables;
8. si une conversation ChatGPT, un agent ou un projet propose une CI plus agressive, cette politique prévaut tant que le propriétaire ne l'a pas explicitement révoquée.

Aucun nouveau dépôt ChatGPT n'est considéré correctement initialisé tant que cette règle n'a pas été héritée.

Voir aussi `NEW_PROJECT_BOOTSTRAP.md`.

## Projets déjà dédiés
- `Terminator364/PhoneMouse` → PhoneMouse.
- `Terminator364/P2PCR95` → P2PCR95.
- `Terminator364/ChatGPT-PC` → ChatGPT-PC / 2003 / G6.
- `Terminator364/BROWSER4G` → dépôt dédié réservé/placeholder ; **pas encore autorité**. La source canonique reste `PROJECT-DRAFTS/BROWSER4G` jusqu'à une migration explicite avec inventaire, SHA-256, readback et mise à jour du checkpoint de continuité.

Cette règle sert de continuité externe afin que le choix du dépôt et la politique CI ne dépendent pas uniquement d'une conversation ou de la mémoire ChatGPT.
