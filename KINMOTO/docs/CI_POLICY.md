# Politique CI / quotas — norme propriétaire existante

Cette politique locale **hérite du dépôt racine** `PROJECT-DRAFTS/AGENTS.md` et `CI_BUDGET_POLICY.json`. Elle ne les remplace pas.

- Budget GitHub-hosted par défaut pour KINMOTO : **0 minute**.
- **Aucun workflow automatique** (`push`, `pull_request`, `schedule`). Aucun workflow distant ajouté par A0.
- Ne pas autoriser de facturation, runners payants, CI automatique à chaque commit.
- Les validations déterministes doivent utiliser les scripts gratuits et locaux (`python KINMOTO/scripts/verify_factory.py KINMOTO`).
- Une CI manuelle `workflow_dispatch` ne pourra être ajoutée qu'à un checkpoint justifié et autorisé ; encore non configurée.
- Le quota ChatGPT Plus/Work/Codex est variable et non observable depuis le dépôt ; ne pas inventer son solde.
- Tout lot Work se clôt sur un commit + état, pour limiter les pertes de quota.
