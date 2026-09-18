# DIRECTIVE À COLLER DANS CHAQUE CONVERSATION PROJET

MATRICE BUILD HUB — INTÉGRATION OBLIGATOIRE

Le système central de production est maintenant :
Terminator364/PROJECT-DRAFTS/MATRICE-BUILD-HUB

Objectif utilisateur permanent :
je décris un bug ou une amélioration dans cette conversation -> tu modifies le projet -> tu prépares la nouvelle bêta/version -> MATRICE BUILD HUB fabrique l’artefact -> je reçois le lien.

Je suis profane en informatique. Ne transforme pas le workflow quotidien en tutoriel Gradle/Android SDK/SSH/PowerShell. L’automatisation doit absorber la complexité.

RÈGLES :
1. GitHub Actions hébergé reste exceptionnel et manual-only. Ne pas le réactiver pour produire les bêta ordinaires.
2. Pour une nouvelle production, préparer le dépôt et la branche pour MATRICE BUILD HUB.
3. Le Hub central utilise GitHub Codespaces comme builder cloud principal et doit viser 0 minute GitHub Actions.
4. Si la recette de build de ce projet change, mettre à jour l’adaptateur correspondant dans PROJECT-DRAFTS/MATRICE-BUILD-HUB/adapters/ ou fournir un script compatible .matrix-build/build.sh.
5. Si la branche de production change, mettre à jour PROJECT-DRAFTS/MATRICE-BUILD-HUB/projects.json.
6. Conserver strictement l’identité/signature canonique des applications existantes. Ne jamais générer silencieusement une nouvelle clé.
7. Avant d’annoncer qu’une bêta est livrable, vérifier package/application ID, version, signature, artefact et hash.
8. Ne pas créer une CI parallèle qui recommence à brûler des quotas.
9. Centraliser les artefacts finaux via GitHub prerelease/release afin que l’utilisateur reçoive un lien.
10. Si Codespaces est temporairement indisponible, rechercher d’abord un fallback gratuit qui préserve le même UX centralisé; ne pas demander à l’utilisateur d’exécuter une longue suite de commandes.

ACTION IMMÉDIATE DANS CE PROJET :
- lire l’état actuel du dépôt et de la branche en cours ;
- identifier la prochaine vraie bêta/version ;
- vérifier que la recette MATRICE BUILD HUB correspond encore à cette version ;
- corriger l’adaptateur central si nécessaire ;
- NE PAS déclencher GitHub Actions ;
- préparer le projet pour qu’un lancement depuis hub.cmd suffise à produire le prochain artefact.

Cette directive est permanente tant que je ne la révoque pas explicitement.
