# KINMOTO — Mode production locale, hébergement gelé (2026-11-04)

## Décision propriétaire

**Arrêt immédiat de tout nouveau déploiement Vercel** jusqu'à une autorisation explicite. Aucun agent, conversation Work, script de test ou action GitHub ne doit créer ni redéployer un site Vercel pendant les lots de développement. Les anciennes URLs restent intactes. Cette décision ne supprime pas les projets historiques.

## Pourquoi

Documentation officielle Vercel Hobby, consultée le 4 novembre 2026 : plafond **100 déploiements par tranche de 24 h**, et **32 builds par heure**. Un site statique sans construction ne consomme pas nécessairement le quota de builds, mais **chaque déploiement consomme son plafond journalier**. D'autres limites de transfert, CPU et stockage existent. Source : https://vercel.com/docs/limits et https://vercel.com/docs/plans/hobby.

**Les quotas réels consommés sur le compte ne sont PAS connus** ; aucune supposition sur le nombre de déploiements restants ne doit être émise. L'utilisateur n'autorise ni formule Pro ni crédit API ni dépassement facturable.

## Workflow 0 FC / 0 build hébergé

1. **Source :** GitHub public `Terminator364/PROJECT-DRAFTS/KINMOTO/`, avec licence des ressources vérifiée.
2. **Compilation :** localement avec Python 3 `python build.py`, ou Windows PowerShell 5.1+ `powershell -NoProfile -ExecutionPolicy Bypass -File tools/build_offline.ps1`. Ces deux modes n'imposent aucune installation npm.
3. **Tests :** `node --test tests/*.test.mjs` lorsque Node existe, plus validations locales sans GitHub Actions. Ne jamais présenter une absence de tests physiques Android comme PASS.
4. **Site de test PC :** `python tools/serve_local.py` sur `http://127.0.0.1:8789/` ou `powershell -NoProfile -ExecutionPolicy Bypass -File tools/serve_local.ps1`. Aucune connexion Internet nécessaire après disponibilité des sources.
5. **Windows un clic :** `tools/START_LOCAL_PC.cmd` reconstruit puis ouvre localhost. La fenêtre est volontairement visible pour permettre l'arrêt (Ctrl+C) du serveur local ; pas de service permanent ni autostart Windows.
6. **Android sur Wi-Fi privé :** possible à tester en mode LAN **uniquement après activation volontaire** du serveur via `--lan`/`-Lan`, et en veillant au pare-feu et au réseau privé. Le jeu 3D sur HTTP LAN est envisageable, mais **service worker et installation PWA non garantis** : ces fonctions exigent un contexte sécurisé (HTTPS ou localhost sur le même appareil). Ne pas ouvrir automatiquement de ports ni exposer le PC à Internet.
7. **QA :** captures comparables, direction gauche/droite, trajectoire, freinage, roues chaussée, collisions, durée ≥15 min, FPS et RAM ; documenter PASS / FAIL / NOT_TESTED séparément.
8. **Livraison :** build ZIP/HTML à partir de sources figées, SHA-256, stockage Drive si nécessaire. Ne pas envoyer chaque itération sur Telegram ni mettre en ligne chaque commit.

## Publication future (non activée)

À examiner seulement au gel d'une vraie release candidate : Cloudflare Pages Free (500 builds/mois, max 25 MiB/fichier) ; GitHub Pages (source publique, soft limit 10 builds/heure, 100 Go/mois) ; Vercel si quota et licence d'usage le permettent. Choisir sur critères licence, coût, quotas et publication manuelle. Sources : https://developers.cloudflare.com/pages/platform/limits/ ; https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits.

## Invariants d'automatisation

- `VERCEL_DEPLOY_ALLOWED=false`, `PUBLIC_RELEASE_ALLOWED=false` jusqu'à nouveau mandat.
- Pas de `vercel deploy`, création de projet Vercel, appel API `create_deployment`, ni script de promotion dans les commandes de routine.
- Pas de workflows GitHub Actions hébergés automatiques (`push`, `pull_request`, `schedule`).
- Aucun secret ni donnée personnelle dans le dépôt public ; archives privées dans Drive.
- Tout code modifié est testé localement et fusionné dans GitHub avec rapport.
- On n'efface pas les vieilles releases.
