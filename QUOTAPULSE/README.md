# QuotaPulse — incubation (Android + Windows)

**Statut :** sources migrées depuis `Terminator364/ChatGPT-PC` (branche de travail `quota-monitor/android-v1`), le 8 novembre 2026. Dépôt PUBLIC : aucune clé, donnée de compte, session WebView ou fichier de configuration personnel ne peut être archivé ici.

## Organisation
- `android/` : sources Android natives, tests et ressources graphiques.
- `windows/` : sources du lecteur Windows. La version exécutée sur le PC peut avoir évolué après l'archive source : respecter la comparaison avant déploiement.
- `MIGRATION_AUDIT.md` : preuve de provenance, contraintes et périmètre.

## Directives fonctionnelles
- Quota affiché dans la petite fenêtre native, non dans un site ouvert à part.
- Pourcentage à deux décimales ; variation `+N appels` fondée sur deux relevés réels ; date strictement limitée au jour/mois.
- Connexion unique et session persistée autant que le fournisseur le permet, sans sauvegarder mot de passe ou OTP.
- Compte = résumé dans l'application ; connexion web uniquement lorsque nécessaire.
- Graphique léger des relevés réels, sans animation ou service persistant.
- Windows indépendant d'Edge, zéro lancement automatique de service ; RAM minimale.
- Icône distinctive sur les deux plateformes, y compris l'icône de la fenêtre Windows.

## Construction et confidentialité
Conformément à `/AGENTS.md` et `/CI_BUDGET_POLICY.json`, **aucun workflow Actions automatique ajouté et aucun runner engagé**. Les builds de développement doivent être locaux. Les APK de mise à jour doivent être signées avec la clé persistante conservée dans un espace privé autorisé, jamais dans ce dépôt public ; un APK debug n'est pas une mise à jour compatible d'une APK release.

Les versions anciennes restent disponibles dans leur dépôt historique privé uniquement comme référence de récupération ; le projet source actif est ce dossier une fois la migration vérifiée.
