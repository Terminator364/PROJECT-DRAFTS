# LINK2HP — V1.3, contre-audit et passation du 11 novembre 2026

## Demande et preuves visuelles
L'utilisateur a signalé « HP introuvable » sur Android v1.2 et a demandé une capture réelle du tableau de bord Edge du HP ainsi qu'une APK corrigée. Capture Windows exécutée via PCRC ; la première capture visait par erreur l'écran de bienvenue Edge. Une capture déterministe via Edge en mode headless, profil isolé, a ensuite confirmé la vraie page LINK2HP : « Agent HP actif », aucune demande d'autorisation reçue, aucun téléphone associé. Ne pas confondre un simple HTTP 200 de localhost avec l'accès réseau depuis Android.

## Causes et modifications
1. v1.2 Android cherchait le HP **uniquement par diffusion UDP** 17644 sur le Wi-Fi ; l'extender peut bloquer la diffusion même si le réseau TCP est utilisable.
2. v1.3 `LanDiscovery.kt` : diffusion UDP, sondes UDP ciblées sur le sous-réseau privé /24 du téléphone, puis vérification TLS HTTPS ciblée sur TCP 17642 (au plus 254 adresses, pool de 20 concurrents, délai maximal de 9 s pour sondes TLS). Identité du HP confirmée par le certificat SHA-256 reçu, avant soumission de la demande d'appairage à approuver explicitement sur Windows.
3. `GET /api/discovery` côté Windows, accessible sans jeton **uniquement depuis une adresse privée LAN**, publie la valeur publique de l'empreinte du certificat et le port. Aucun secret, token d'association, mot de passe ou clé privée.
4. Le PC avait des règles LAN correctes mais le redémarrage du service via PCRC reprenait la variable `LOCALAPPDATA` d'un profil technique. Lancement de fond réparé avec le dossier utilisateur HP et `LINK2HP_CONFIG` explicites ; redémarrage réel vérifié HTTP 200 et 1 agent.
5. Un lancement Edge en fenêtre d'application à profil dédié a été vérifié afin de contourner l'écran de première utilisation Edge.
6. Les réseaux restent gérés par le HP et non le téléphone. Priorité Starlink principal 5 GHz puis Starlink principal 2,4 GHz, pas d'obligation de changer le Wi-Fi Android.

## Vérifications réellement exécutées
- Node Windows `agent.cjs` contrôle syntaxe : exit 0.
- HTTPS LAN `/api/discovery` via adresse Wi-Fi IPv4 du HP : `LAN_TLS_DISCOVERY_PASS=true`, HTTP 200, aucun secret renvoyé.
- Tableau de bord Windows `http://127.0.0.1:17643` : HTTP 200 après réparation.
- Nouveau lanceur Edge isolé : processus `--app=http://127.0.0.1:17643` observé.
- GitHub Actions : [run 42983673353](https://github.com/Terminator364/PROJECT-DRAFTS/actions/runs/42983673353), `success`, source à la révision `b2e3579c02cd3f51bf5facf7a819b9b1da07e0ab`. APK v1.3.0 extraite et test ZIP valide ; taille **854917** octets ; SHA256 `f636eb8948c2b529007b3d63c7ae72ec62e4ab6280f115c526ef2058a852ad32`; signature APK v2 détectée.
- Google Drive / ChatGPT Delivery : dépôt du fichier `LINK2HP-Android-v1.3.apk`, ID `1JuAhBYC8GCRQC_0Ky5Hia7n282IkxBLh`, déplacé vers la racine d'envoi (le dossier catégorisé n'est pas utilisé comme ingress brut). **Reçu Telegram durable : DELIVERED, message n° 983, code `R-A7N282IKXBLH`**, SHA256 identique.
  
## Limitations et blocages avoués
- La découverte TLS par balayage de sous-réseau ne contourne pas une **isolation Wi-Fi complète/NAT sans route** entre 2,4 GHz/extender et 5 GHz/HP.
- Pas de test réel Android v1.3 → HP → appairage → téléchargement réussi sur le téléphone de l'utilisateur : **NON QUALIFIÉ**. L'utilisateur doit installer et appuyer une fois sur « Réessayer la connexion » ; attendre sur le HP une demande d'autorisation.
- Les debug APK 1.2 et 1.3 n'ont pas de signature commune (GitHub runner). Android peut exiger de désinstaller 1.2, avec perte possible d'outbox et appairages. Le mécanisme de mise à jour automatique sûre et signature persistante reste non réalisé.
- Réseau distant (faculté, données mobiles, Wi-Fi tiers) non pris en charge par cette APK : intégration Tailscale sécurisée requise. Ne pas revendiquer un service cloud ou accès distant aujourd'hui.
- Toujours garder sauvegarde du module PC `agent.cjs.backup-v12-20261111` ; ne pas modifier PCRC et les autres projets.

**Etat final : APK 1.3 construite et livrée sur Telegram ; nouveau serveur HP rétabli et testé localement ; validation mobile de bout en bout toujours ouverte.**
