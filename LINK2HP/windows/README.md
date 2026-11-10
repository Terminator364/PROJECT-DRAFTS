# LINK2HP Windows 1.1 — agent de téléchargement du HP

L'agent Node.js 24 fonctionne localement sous le compte HP. Le HP télécharge lui-même les liens directs publics autorisés; les magnets/torrents sont délégués à qBittorrent avec statut de passation (pas de téléchargement déclaré fini sans preuve). Tableau de bord : `http://127.0.0.1:17643`. HTTPS local authentifié : port 17642. Découverte Wi-Fi : UDP 17644. Aucun secret/certificat privé dans le dépôt public.

## Choix intelligent du Wi-Fi du HP

`wifi.cjs` interroge **Windows** (`netsh wlan show networks mode=bssid`, `show profiles`, `show interfaces`) sans exporter les mots de passe. L'API authentifiée `GET /api/wifi/networks` donne au téléphone les SSID visibles par le HP, les bandes détectées, la disponibilité d'un profil enregistré et le réseau actif. `POST /api/wifi/connect` connecte uniquement à un profil Wi-Fi déjà connu de Windows, à la suite d'un choix explicite sur le téléphone. Une bascule interrompt parfois temporairement le canal de contrôle ; la réponse HTTP est envoyée avant la demande `netsh`.

Au démarrage et toutes les 10 min (hors téléchargement actif), la politique privilégie le Starlink 5 GHz sauvegardé et visible; sinon le Starlink 2,4 GHz. Une temporisation de 5 min empêche les bascules en boucle. Sans profil enregistré, une configuration manuelle initiale sur le HP est nécessaire. Sans liaison de contrôle préexistante, un téléphone sur un autre réseau ne peut pas commander le changement Wi-Fi du HP. Aucun contournement de Windows, des mots de passe ou de restrictions de pare-feu.

## Installation

Exécuter `Install-LINK2HP.ps1` sur le HP. Les fichiers `wifi.cjs`, `pairing.cjs`, `agent.cjs`, `network.cjs` sont copiés vers `%LOCALAPPDATA%\LINK2HP\app`. Après mise à jour de l'agent, le processus Node doit être relancé pour charger le nouveau code. La configuration et la base de tâches restent dans `%LOCALAPPDATA%\LINK2HP`. Le setup ne doit pas être exécuté sans contre-vérifier pare-feu et statut du processus. Le script de désinstallation est fourni.
