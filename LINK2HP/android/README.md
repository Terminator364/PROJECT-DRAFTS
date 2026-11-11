# LINK2HP pour Android — v1.4.0

1. L'application recherche le HP automatiquement au lancement et au retour du Wi-Fi. Le bouton « Connecter au HP » donne toujours un état visible pendant l'action.
2. À la première association, ouvrir LINK2HP sur le HP et cliquer une seule fois « Autoriser ce téléphone » ; aucun code n'est à copier.
3. Partager un lien depuis le navigateur ou le coller dans LINK2HP, puis « Envoyer au HP ». Une demande hors ligne est sauvegardée et renvoyée lorsque le HP redevient joignable.
4. Le réseau Wi-Fi du téléphone peut rester sur Starlink 2,4 GHz (extender) si le HP sur Starlink 5 GHz est joignable. Ne pas forcer la migration du Wi-Fi du téléphone.
5. Les options avancées permettent de voir les réseaux du HP, puis d'en choisir un si Windows connaît ses identifiants.

L'application nécessite un réseau commun joignable. Une installation Android sans Play Store ne peut se mettre à jour sans permission système. Une signature APK stable et sécurisée reste nécessaire aux mises à jour incrémentales.

## Nouveauté v1.3

Lorsque le routeur/extender bloque les messages de découverte, le téléphone tente des messages UDP directs vers le réseau privé courant, puis une vérification TLS directe de la présence de LINK2HP. Le téléphone reste sur son réseau 2,4 GHz : aucun changement Wi-Fi n'est imposé. La progression distingue recherche Wi-Fi et recherche directe. Le HP doit rester joignable par une route IP locale et le pare-feu doit autoriser 17642/TCP et 17644/UDP.

Compilation [GitHub Actions #42983673353](https://github.com/Terminator364/PROJECT-DRAFTS/actions/runs/42983673353), APK debug v1.3. Les changements de signature empêchent l'installation par-dessus v1.2 ; la signature stable pour mises à jour futures reste un chantier ouvert.

## Android 1.4 — réseau libre

Après la première association sur le réseau local (autorisation par un seul clic sur le HP), LINK2HP conserve le jeton et l'empreinte du certificat. Il reçoit sur HTTPS authentifié l'adresse Tailscale privée du HP, sans publier le serveur sur Internet. Si Tailscale est actif sur le téléphone (même tailnet), il utilise cette connexion via données mobiles ou Wi-Fi externe. Sinon il revient au LAN local, puis recherche le HP sur le même certificat en cas de changement DHCP.

- Le téléphone **n'a pas à rejoindre le même SSID que le HP** pour l'utilisation distante, mais il doit pouvoir joindre son tailnet privé.
- Les petits liens peuvent être transmis sur réseau mobile. En cas de coupure ils restent stockés en local.
- Android 1.4 affiche la raison d'échec enregistrée par le HP lorsqu'elle est connue, au lieu d'afficher seulement `FAILED`.
- VersionCode = 5 ; versionName = 1.4.0, build GitHub Actions n° 42988418154.
- APK **RELEASE** avec signature de publication stable à conserver pour les versions suivantes ; une rupture initiale avec les versions DEBUG impose éventuellement une réinstallation et une seule nouvelle approbation. Aucune mise à jour silencieuse hors Play Store n'est autorisée sans mécanisme de gestion de l'appareil.
- **Limites encore ouvertes** : test réel sur ton smartphone/Tailscale et moteur de mise à jour intégré.
