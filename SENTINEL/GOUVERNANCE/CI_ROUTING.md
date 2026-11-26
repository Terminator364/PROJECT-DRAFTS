# SENTINEL — Circuit GitHub privé/public

Décision du propriétaire, 26 novembre 2026 : conserver Sentinel dans une branche de ChatGPT-PC, utiliser PROJECT-DRAFTS pour les travaux et validations publics admissibles, privilégier les ressources gratuites. Le déploiement HP de la mise à jour reste soumis au GO explicite.

## Références historiques vérifiées
- PROJECT-DRAFTS PR #48 : PCRC V2, laboratoire public isolé, sans accès privé.
- PROJECT-DRAFTS PR #17 : OneClick, 20 fichiers autonomes revus et copiés avec manifeste Git, CI Windows publique.
- PROJECT-DRAFTS PR #13 : BookHarvester, qualification Windows puis workflow manuel uniquement.
- Branche pcrc-v3-public-ci-isolated-20261112 : précédent de séparation public/privé.

## Circuit Sentinel
1. ChatGPT-PC privé, branche sentinel-migration-20261126 : réconciliation des sources, versions, historique, tests et documentation. Transit actuel SENTINEL_TRANSIT ; ne pas considérer les copies texte comme sauvegardes bit-à-bit.
2. PROJECT-DRAFTS public, branche sentinel-autonomie-20261126 : composants expressément déclassifiés, jeux synthétiques, tests, éventuellement compilation des composants exportables. Ne pas publier télémétrie HP, secrets, données personnelles, archives privées, ou code non revu. Pas de checkout privé depuis un runner public.
3. Vérifier identité des blobs Git des composants communs et intégrer les résultats dans la branche privée. Les résultats publics ne qualifient pas à eux seuls la version installée.
4. PCRC : tests matériels finaux, mesures d'autonomie et déploiement réversible après GO.

## Budget
Zéro minute privée par défaut. CI publique : runners standards admissibles, ciblés, manuel uniquement, aucun runner payant, aucun workflow automatique ajouté. Avant lancement vérifier règles d'éligibilité, quotas et périmètre public ; aucun contournement des limites. Le présent document ne modifie pas AGENTS.md global.

## Sécurité et état
Aucune fusion main, aucune suppression locale avant preuve de restauration, aucune installation. Migration en cours et non intégrale. Préserver huit familles et trois fichiers racine de Sentinel, ainsi que le registre de scellés historique. Un seul référentiel canonique privé après validation, la branche publique est un laboratoire dérivé.
