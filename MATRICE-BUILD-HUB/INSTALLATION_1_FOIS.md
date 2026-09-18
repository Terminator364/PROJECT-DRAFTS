# MATRICE BUILD HUB V0.2 — installation une seule fois

Cette procédure est volontairement courte. Les détails techniques sont automatisés.

1. Depuis GitHub, récupérer une seule fois le dépôt privé `PROJECT-DRAFTS` puis ouvrir le dossier `MATRICE-BUILD-HUB`.
2. Double-cliquer sur **`INSTALL-BUILDHUB.cmd`**. Si Windows refuse exceptionnellement le fichier `.cmd`, utiliser le secours: clic droit sur `bootstrap-pc.ps1` → **Exécuter avec PowerShell**.
3. Le bootstrap installe ou vérifie Git, GitHub CLI, JDK 17 et les outils Android locaux nécessaires à la signature.
4. Lors de la première exécution, GitHub peut ouvrir le navigateur pour l'authentification et l'autorisation Codespaces.
5. Le bootstrap installe ensuite sa copie canonique sous `%LOCALAPPDATA%\MatriceBuildHub\PROJECT-DRAFTS` et exécute le self-test.
6. Pour PhoneMouse/P2PCR95, il migre l'identité de signature canonique dans un vault Windows DPAPI **sans envoyer la clé dans Codespaces**.
7. Il demande ensuite un emplacement externe ou synchronisé hors du PC pour créer la sauvegarde catastrophe chiffrée, puis demande de la sélectionner à nouveau afin d'effectuer un vrai test de restauration: déchiffrement, vérification SHA-256, ouverture du keystore et comparaison du certificat canonique.
8. Quand `BUILD_HUB_BOOTSTRAP_PASS` apparaît, un raccourci **MATRICE BUILD HUB** est créé sur le Bureau.
9. Première action recommandée: lancer le raccourci et choisir **4 — Diagnostic cloud seulement**. Ce smoke test crée puis détruit un Codespace sans compiler d'APK.
10. Après le smoke PASS, utiliser les choix 1, 2 ou 3 pour les productions.

## Règles importantes

- Ne jamais générer une nouvelle clé Android pour remplacer une clé canonique introuvable.
- Ne jamais supprimer la sauvegarde catastrophe tant qu'une autre copie restaurée/testée n'existe pas.
- Ne pas réactiver les workflows GitHub Actions automatiques pour contourner un problème BuildHub.
- Un build Android signé est bloqué si le test de restauration catastrophe n'a pas PASS.
- Le PC ne compile pas l'application Android complète; il ne fait que l'orchestration et la signature/vérification légère. La compilation lourde reste dans Codespaces.
