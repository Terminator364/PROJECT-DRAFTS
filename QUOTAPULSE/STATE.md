# QuotaPulse — état vérifié, 2026-11-08

## Sources et reproductibilité
- Référence active : `QUOTAPULSE/android/` et `QUOTAPULSE/windows/` dans ce dépôt public.
- Sources Windows synchronisées depuis le HP après les corrections visuelles, puis mise à jour du lecteur WebView2 et de la stratégie hybride.
- Aucun secret, mot de passe, OTP, cookie, profil utilisateur ou clé de signature dans ce dépôt.
- Ne jamais activer de workflow automatique : conserver la politique du dépôt `AGENTS.md` et `CI_BUDGET_POLICY.json`.

## Windows — vérifié / non vérifié
- **Vérifié :** C# compilé sur le HP, 3 tests de parsing réussis. Fenêtre 410 x 435 px capturée via PCRC, avec logo personnalisé, 2 décimales et date courte. Les caractères corrompus et le chevauchement visible sont corrigés.
- **Vérifié :** bouton Actualiser activable en direct ; lecture WebView2 démarre réellement. Traces locales `diagnostics/webview2-status.log` : création d'environnement puis initialisation réussies (~2–3 s), navigation vers le fournisseur, passage à une page d'authentification.
- **À valider :** obtention d'un NOUVEAU relevé WebView2 sans Edge une fois la session indépendante authentifiée. L'ancien navigateur et WebView2 ne partagent pas automatiquement leurs cookies ; ne pas promettre de réutiliser une identification établie dans un autre navigateur.
- **Existant préservé :** programme installé `QuotaPulse.exe`, cache `quota.txt`, profil `WebProfile` et raccourci Bureau. Nouvelle version candidate `QuotaPulse.next.exe` conservée pour tests. Aucune promotion sans vérification d'une lecture chiffrée réelle. Les anciennes copies `QuotaPulse.rollback.exe` et les captures temporaires obsolètes ont été supprimées par PCRC.
- **Architecture :** ouverture quasi instantanée sur le cache ; lecture Edge possible comme raccourci *facultatif*, WebView2 autonome pour les cas sans Edge. Fenêtre limitée à sa durée de vie ; actualisation toutes les 20 minutes seulement si la fenêtre est ouverte et une session valide connue.
- **Risque observé :** WebView2 charge et détecte correctement AUTH_REQUIRED ; si l'utilisateur n'achève pas l'authentification dans ce nouveau profil, le compteur n'est pas actualisé. Ne jamais confondre ce cas avec SUCCESS.
- Réduire les fenêtres en double et éviter de laisser WebView2 ouvert après fin du test.

## Android — vérifié / non vérifié
- **Vérifié :** compilation publique de la version 0.5 QA et tests Java, workflow GitHub Actions `42508662816` réussi.
- **Vérifié dans le code :** pourcentage à 2 décimales, variation `+N appels` calculée à partir de deux mesures, remise à zéro de cycle contrôlée, graphique uniquement sur points réels, onglet Compte comme résumé natif et boutons compacts.
- **À valider sur appareil :** authentification et affichage natif après login, latence réelle, réutilisation de la session et adaptation aux tailles Samsung.
- L'APK 0.5 QA est signée **debug** : elle ne peut pas remplacer l'APK 0.3 release déjà installée sans perdre la continuité de signature. NE PAS la présenter comme une mise à jour de production.
- Une véritable APK 0.5 de remplacement doit être signée avec la même clé persistante que la release précédente, conservée dans le dépôt privé `ChatGPT-PC`.

## GitHub Actions — audit de facturation
- `ChatGPT-PC` est privé ; `PROJECT-DRAFTS` est public.
- Une exécution privée a échoué avant allocation de runner ; GitHub affiche « recent account payments have failed, or spending limit needs to be increased ».
- Vérification Billing/Budgets dans le compte : Actions `$0.00 / $0.00` et `Usage blocked`. Aucun changement de dépenses autorisé.
- Un job de test public standard dans `PROJECT-DRAFTS` a effectivement fonctionné, compilé l'APK debug et publié le rapport QA.
- Le déclencheur public temporaire a été supprimé après le test. Le dépôt conserve un workflow manuel uniquement, sans clé privée.
- **Diagnostic :** blocage de runners privés lié à la politique de dépenses/facturation ; l'usage gratuit des runners publics est confirmé par le job réel.

## Conditions de validation finale
1. Windows sans Edge : relevé frais fourni par WebView2 authentifié, puis fenêtre fermée sans processus web résiduel et RAM mesurée.
2. Comparaison directe avant/après lecture du compteur et du delta, sans solliciter les outils Remote commerciaux pour chaque actualisation.
3. Capture finale montrant zéro débordement, caractères corrects, logo en barre des tâches et valeurs actualisées.
4. Une seule version Windows principale et suppression des exécutables obsolètes **après** promotion vérifiée.
5. APK Android signée par la clé persistante, remplacement sans désinstallation et test réel sur Samsung.
