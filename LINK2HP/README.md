# LINK2HP — Android + Windows HP

Deux produits légers pour envoyer un lien depuis la feuille **Partager** d'Android à l'ordinateur HP, via Wi-Fi local. Pas de cloud, abonnement, publicité ou dépendance à ChatGPT/PCRC pour fonctionner une fois installé.

## Windows
`windows/`: agent autonome sous Node.js 24, HTTPS LAN certifié par une empreinte SHA-256 unique par installation, jeton 256 bits, tableau de bord local `http://127.0.0.1:17643`, file persistante SQLite. Les fichiers directs autorisés sont téléchargés vers le dossier dédié et les magnet/.torrent sont ouverts par qBittorrent.

## Android
`android/`: Kotlin natif (sans framework lourd), file d'attente chiffrée Android Keystore, partage depuis Opera/Chrome, import de `.torrent`, reprise JobScheduler et historique. Le premier appairage demande un code unique présent dans l'interface Windows ; ensuite le transfert se fait en un geste.

## Sécurité et limites
Ne jamais publier le code d'appairage ni le certificat privé. Le service HTTPS refuse les commandes sans jeton et cert pin; téléchargement de pages HTML limité aux liens directs publics identifiables ; aucun contournement DRM, compte privé, captcha ou téléchargement d'exécutables. qBittorrent peut demander confirmation ; le logiciel indique alors « transmis » et non « terminé ». Aucun serveur public Internet n'est ouvert.

## Compilation ponctuelle sur GitHub
Le workflow `.github/workflows/link2hp-build-once.yml` est limité à la branche dédiée et se déclenche une seule fois lors de l'ajout du workflow ; workflow_dispatch reste disponible. Il publie l'APK debug dans les artefacts GitHub Actions. Sans déclencheur général push/PR/schedule. Les sources ne contiennent aucun secret privé.
