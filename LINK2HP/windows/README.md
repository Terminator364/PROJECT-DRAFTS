# LINK2HP Windows 1.0

Une application autonome Windows légère. Aucune dépendance opérationnelle à ChatGPT/PCRC : l'installation copie `node.exe` dans `%LOCALAPPDATA%\LINK2HP\app`.

## Installation sur HP
1. Décompresser le ZIP dans un dossier du HP.
2. Clic droit sur `Install-LINK2HP.ps1` → Exécuter avec PowerShell (ou depuis une console PowerShell utilisateur avec `powershell -NoProfile -ExecutionPolicy Bypass -File .\Install-LINK2HP.ps1`).
3. Ouvrir le raccourci « LINK2HP » sur le Bureau; l'interface locale s'affiche sur `http://127.0.0.1:17643`.
4. Copier le code d'appairage dans l'application Android une seule fois. Les deux appareils doivent être sur le même Wi-Fi. Ne pas envoyer le code sur un site public.
5. Si le Windows Firewall bloque le port 17642, autoriser uniquement TCP 17642 depuis le réseau local via une règle de pare-feu *LocalSubnet* (autorisation administrateur requise).

**Important :** le mode Android→HP utilise HTTPS avec un certificat auto-signé et une empreinte de certificat épinglée sur Android. Le serveur rejette les commandes sans le jeton personnel. Aucun port Internet, compte cloud ou mot de passe Windows transmis.

Les téléchargements HTTP simples sont stockés dans `%LOCALAPPDATA%\LINK2HP\Downloads`. Les magnets et .torrent sont transmis au qBittorrent installé ; l'acceptation finale par qBittorrent doit être confirmée dans son interface (la version initiale n'active pas sa WebUI ni ne touche à ses téléchargements).

Statuts : QUEUED, ANALYSING, WAIT_SELECTION, RUNNING, COMPLETED, HANDED_TO_QBITTORRENT, FAILED. Ne jamais confondre « remis au moteur » et « terminé ».

## Tests
`node --test agent.test.cjs`

## Limitations connues
- Première association nécessite la copie du code manuel depuis le HP; pas encore de caméra QR intégrée.
- Si le poste est éteint, l'application Android conserve la demande; elle la retransmet lors d'une connexion Wi-Fi disponible.
- L'agent HTTP ne télécharge pas de pages protégées, DRM, captchas ou exécutables.
- Un antivirus ou Windows Firewall peut bloquer la première écoute de l'agent; il faut autoriser sur le réseau local uniquement.
