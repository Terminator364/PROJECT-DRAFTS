# LINK2HP — v1.4, correctifs du torrent et du pilotage à distance (11 novembre 2026)

## Besoin confirmé
Le téléphone ne doit soumettre que des liens, en utilisant son Wi-Fi ou ses données mobiles **indépendamment** de la connexion Internet du HP. Le HP choisit sa connexion principale Starlink 5 GHz, éventuellement Starlink 2,4 GHz, et effectue réellement les téléchargements. L'appairage reconnu doit survivre aux mises à jour ; les erreurs doivent être explicites et les tests exécutés sur le matériel réel.

## Reproduction de la défaillance signalée
- Sur le vrai HP : **1 téléphone déjà associé**, **1 URL reçue**, état **FAILED**, raison **ERR_INVALID_IP_ADDRESS**.
- Une requête HTTP vers un site public de contrôle échouait elle aussi avec `TypeError [ERR_INVALID_IP_ADDRESS]: Invalid IP address: undefined`.
- Cause exacte : `network.cjs` déployé était une ancienne version avec callback DNS `lookup:(_h,_opt,cb)=>cb(null,ip,4)`, incompatible avec Node.js 24 lorsque `autoSelectFamily` demande `lookup({all:true})`. Le source GitHub avait déjà `pinnedLookup` corrigé mais n'avait pas été déployé.
- Ancien réseau sauvegardé sur HP, puis source corrigée installée. Tests `secureGet` vers deux hôtes publics : **réussis**, contrôle syntaxe : **réussi**. Aucune modification d'autres projets.

## Vérification sur le lien fourni
- Il s'agissait d'une **page HTML**, non d'un magnet direct ; la page contient **exactement un** candidat magnet valide détecté par `parseCandidates`. Le contenu et l'URL ne sont pas publiés.
- `agent.cjs` v1.4 transmet automatiquement un candidat magnet unique à qBittorrent, au lieu d'exiger de choisir un élément.
- La réutilisation d'un identifiant de tâche ou d'une empreinte d'URL pour un état `FAILED` demande désormais une **reprise dans la même tâche**. Le travail n'est pas prétendu terminé lorsque qBittorrent a seulement été lancé.
- L'ancienne tâche personnelle reste `FAILED` en base jusqu'à ce que l'utilisateur la renvoie ; nous n'avons pas lancé automatiquement le magnet de son ancienne page.

## Test de téléchargements réels
- Sur le vrai HP, demande authentifiée de `https://www.rfc-editor.org/rfc/rfc1149.txt` reçue puis exécutée avec succès : `COMPLETED`, **3 215 octets** enregistrés sur le disque, `E2E_EXIT=0`.
- Test BitTorrent légal et isolé : torrent original fabriqué localement (152 octets), qBittorrent lancé dans une configuration distincte avec `--add-stopped=true` ; un fichier `.torrent` et un `.fastresume` ont été observés : **acceptation réelle d'un torrent démontrée**. Pas de téléchargement de charge utile. L'instance de test a été fermée et l'ancienne configuration qBittorrent préservée.
- **Non démontré** : un torrent personnel réel téléchargé complètement, qBittorrent lancé de façon permanente en arrière-plan ou une remontée API de sa progression.

## Contrôle privé depuis n'importe quel réseau
- Le HP possède Tailscale déjà configuré et actif. Un service `tailscale serve --bg --tcp=17645 tcp://127.0.0.1:17642` a été ajouté **dans le tailnet privé**, pas en Funnel public. Les anciennes règles de Serve/Funnel étrangères à LINK2HP ont été préservées ; configuration précédente sauvegardée sur le HP.
- Test sur le HP : GET /api/health avec jeton préalablement autorisé par l'utilisateur sur le HTTPS LAN : 200. Même requête vers l'adresse Tailscale privée : 200, **certificat SHA-256 identique**, `remote.version=1.4.0`.
- Android v1.4 : sauvegarde de l'adresse Tailscale reçue depuis un HP déjà associé, pin de certificat inchangé, jeton Bearer conservé dans le stockage chiffré. Utilise le VPN Tailscale sur les données mobiles, avec fallback Wi-Fi ou réassociation au même certificat après changement DHCP. Les tâches en attente ne sont plus bloquées par l'exigence de Wi-Fi non mesuré.
- **Non démontré sur smartphone** : Tailscale Android actif dans le même tailnet et transfert réel depuis réseau cellulaire / faculté. Android doit être connecté à ce VPN privé ; sans VPN il n'existe pas de connexion distante autorisée.

## APK Android et pérennité de signature
- Source v1.4 compilé sur GitHub Actions, run [42988418154](https://github.com/Terminator364/PROJECT-DRAFTS/actions/runs/42988418154) : **SUCCESS**.
- APK produite re-signée sur machine de confiance avec **clé de publication RSA-3072 créée pour LINK2HP** ; `apksigner verify` valide schémas **v2** et **v3**. Certificat public SHA-256 `f003c6e220873ec2a5599e4a729d8eaa2049634499517458484b19e32dc490e6`.
- Empreinte APK RELEASE SHA256 `137b00fcb5e77e66d307a60db41c9ef3e22ca6b98b8ff4be2078fb08ad97f267`. VersionCode 5 ; versionName 1.4.0.
- Clé PKCS12 chiffrée conservée dans un **dossier Drive privé** hors ChatGPT Delivery et hors dépôt GitHub. Son mot de passe est scellé dans le compte Windows HP via DPAPI CurrentUser, sans publication de clé privée ou de mot de passe. Index privé sur HP `%LOCALAPPDATA%\LINK2HP\signing\README_PRIVATE_SIGNING.md`.
- **Il reste une rupture de signature** entre l'ancienne APK de développement v1.3 et la nouvelle première APK de publication v1.4 : Android peut exiger la désinstallation, qui efface l'appairage et la file du téléphone. Une seule nouvelle autorisation d'appareil pourra donc être nécessaire. Les futures versions devront être signées avec **exactement** ce même certificat. Le mécanisme d'installation automatique contrôlée par l'utilisateur n'est pas encore implémenté et ne doit pas être annoncé comme opérationnel.

## Livraison et jalons
- APK `LINK2HP-Android-v1.4-RELEASE.apk` placée dans la file officielle `ChatGPT Delivery/À envoyer` via Google Drive. **Ne marquer Telegram DELIVERED qu'après reçu durable** incluant identifiant de message et empreinte correspondante.
- Sources sur [la branche de travail](https://github.com/Terminator364/PROJECT-DRAFTS/tree/link2hp/v14-torrent-remote-20261111/LINK2HP).
- Etat : **Windows direct-download E2E PASS**, **import qBittorrent d'essai PASS**, **VPN privé HP PASS**, **APK RELEASE signée PASS**, **test réel distant sur téléphone non prouvé**, **mises à jour Android entièrement automatiques non livrées**.
