# LINK2HP — Android + Windows HP (développement v1.1)

Deux produits distincts : **téléphone = envoi des liens** ; **HP = réseau + téléchargement**. L'interface Android est conçue pour se limiter à partager/coller → envoyer, avec appairage par validation unique sur le HP. La connexion locale HTTPS est authentifiée et l'identité du HP est vérifiée par empreinte TLS.

Le HP effectue le scan Wi-Fi, privilégie Starlink 5 GHz puis 2,4 GHz, et peut recevoir un ordre authentifié de connexion à un autre réseau Wi-Fi déjà sauvegardé dans Windows. L'application affiche les réseaux détectés par le HP, pas une simple liste Wi-Fi du téléphone. Si les appareils ne sont plus joignables, aucun faux pilotage distant n'est prétendu.

**Preuves disponibles** : tests unitaires locaux Windows de classification, SQLite et politiques Wi-Fi, compilation APK GitHub à confirmer pour cette version. Tests réels téléphone ↔ HP, téléchargement public réel et auto-mise à jour signée durable non acquis tant que des reçus ne les démontrent pas. Ne pas confondre code produit et release qualifiée.

Voir `windows/README.md` et `android/README.md`. Dépôt de développement public : ne jamais y publier secrets, mots de passe Wi-Fi, tokens ou clé de signature APK.
