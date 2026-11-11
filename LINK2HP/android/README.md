# LINK2HP pour Android — v1.3.0

1. L'application recherche le HP automatiquement au lancement et au retour du Wi-Fi. Le bouton « Connecter au HP » donne toujours un état visible pendant l'action.
2. À la première association, ouvrir LINK2HP sur le HP et cliquer une seule fois « Autoriser ce téléphone » ; aucun code n'est à copier.
3. Partager un lien depuis le navigateur ou le coller dans LINK2HP, puis « Envoyer au HP ». Une demande hors ligne est sauvegardée et renvoyée lorsque le HP redevient joignable.
4. Le réseau Wi-Fi du téléphone peut rester sur Starlink 2,4 GHz (extender) si le HP sur Starlink 5 GHz est joignable. Ne pas forcer la migration du Wi-Fi du téléphone.
5. Les options avancées permettent de voir les réseaux du HP, puis d'en choisir un si Windows connaît ses identifiants.

L'application nécessite un réseau commun joignable. Une installation Android sans Play Store ne peut se mettre à jour sans permission système. Une signature APK stable et sécurisée reste nécessaire aux mises à jour incrémentales.

## Nouveauté v1.3

Lorsque le routeur/extender bloque les messages de découverte, le téléphone tente des messages UDP directs vers le réseau privé courant, puis une vérification TLS directe de la présence de LINK2HP. Le téléphone reste sur son réseau 2,4 GHz : aucun changement Wi-Fi n'est imposé. La progression distingue recherche Wi-Fi et recherche directe. Le HP doit rester joignable par une route IP locale et le pare-feu doit autoriser 17642/TCP et 17644/UDP.

Compilation [GitHub Actions #42983673353](https://github.com/Terminator364/PROJECT-DRAFTS/actions/runs/42983673353), APK debug v1.3. Les changements de signature empêchent l'installation par-dessus v1.2 ; la signature stable pour mises à jour futures reste un chantier ouvert.
