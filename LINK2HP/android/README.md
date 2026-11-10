# LINK2HP Android 1.1 — transfert et choix du Wi-Fi du HP

LINK2HP sert à envoyer un lien/magnet depuis Android vers l'ordinateur HP. **Seul le HP effectue les téléchargements.** Aucune connexion de cloud n'est nécessaire pour transférer des liens sur le réseau local.

- Partager dans Opera/Chrome → LINK2HP, ou coller un lien.
- Appairage sans code recopié : rechercher le HP sur le Wi-Fi, puis cliquer une fois « Autoriser ce téléphone » dans l'interface Windows sur le HP. La relation est sauvegardée de façon chiffrée dans Android Keystore.
- Sous « Réseau de mon HP », ouvrir la liste des **réseaux vus par l'ordinateur**. Les profils déjà enregistrés sont sélectionnables. Un réseau inédit doit d'abord être configuré dans Windows, sans envoyer de mot de passe à l'application.
- LINK2HP Windows choisit en priorité le Starlink 5 GHz visible et déjà configuré, puis le Starlink 2,4 GHz. Si un seul SSID couvre les deux bandes, Windows/la carte réseau contrôle le choix de bande.
- La bascule peut couper temporairement la liaison locale. Android tente de retrouver le HP authentifié sur le nouveau sous-réseau. Si le téléphone n'est pas sur un réseau qui peut joindre le HP, l'application l'indique : une liaison externe préalablement configurée serait nécessaire pour une commande à distance.
- Réseau Wi-Fi du téléphone : Android garde la maîtrise du changement, et présente si besoin le panneau Wi-Fi système.

## Build et mises à jour

Projet Kotlin natif, SDK 35, JDK 17, Gradle 8.7. `gradle :app:assembleDebug` produit un APK de développement. **Attention** : la signature debug générée par un runner GitHub Actions peut varier, et ne permet pas de garantir une mise à jour au-dessus de l'ancienne version. Pour les mises à jour durables sans perte de données, utiliser une clé de signature privée stable, hors dépôt public, ainsi qu'un mécanisme de distribution validé. L'auto-mise à jour complète n'est pas encore qualifiée ; ne pas la présenter comme opérationnelle.
