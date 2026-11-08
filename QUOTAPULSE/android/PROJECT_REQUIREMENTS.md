# QuotaPulse: règles du projet (8 novembre 2026)
- Chaque application, PC ou Android, possède son vrai logo personnalisé, visible dans l'application, dans le lanceur et la barre des tâches (pas de lettre Q générique ni de robot Android).
- Interfaces visuelles modernes, compactes, lisibles immédiatement, sans grand anneau vide ni énorme bouton Compte. Compte: action discrète en haut à droite.
- Android: connexion complète e-mail + code, sans timer qui ferme la WebView ni redirection à chaque page; cookies persistants et saisie une seule fois lorsque session valide.
- Android et Windows affichent réellement les chiffres dans leur propre fenêtre. Aucune simple redirection au site comme fonction principale.
- Windows : fermer Edge ne doit pas empêcher un relevé nouveau; un lecteur indépendant est nécessaire, chargé seulement pendant la connexion/lecture puis libéré pour préserver la RAM. Aucun service permanent.
- Quota Remote commercial : 0 appel pour la consultation. Pas de Cloudflare. Pas de dépendance ChatGPT à l'exécution.
- Mise à jour Windows au même chemin, mise à jour Android avec applicationId et signature constants.
- L'utilisateur veut supprimer les anciennes versions Windows APRÈS validation de la version remplaçante, tout en conservant uniquement l'exécutable final et les données.
- QA: tests hors ligne de parsing + tests de parcours login + test réel appareil, lecture sans Edge, écran Windows, mesures de RAM.
