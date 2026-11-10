# LINK2HP — V1.2, ergonomie minimale Android

## Fonctionnement attendu

**Téléphone** : 1) ouverture et recherche automatique du HP ; 2) confirmation de l'association une fois dans le navigateur local du HP (sans code ni mot de passe à copier) ; 3) coller/partager un lien, puis « Envoyer au HP ». Une demande envoyée hors ligne reste dans la file locale chiffrée.

**HP** : agent autonome via HTTPS LAN, télécharge ou transmet à qBittorrent les liens autorisés. Le téléphone peut être connecté à un Wi-Fi 2,4 GHz et le HP à un Wi-Fi 5 GHz **si les deux réseaux sont effectivement bridgés et routables**. Le SSID n'est pas un identifiant fiable de la bande radio. Le réseau se change depuis le HP, avec liste optionnelle des réseaux détectés par Windows.

## Corrections V1.2

- Suppression du renvoi automatique aux paramètres Wi-Fi et de la fenêtre de choix Wi-Fi non demandée.
- Écran réduit à connexion, partage d'un lien, activité ; options réseau repliées par défaut.
- Feedback immédiat à l'appui, Ripple + vibration système, jauge d'attente pendant les recherches, messages d'états explicites.
- Verification API `/api/health` **réelle** avant d'afficher « HP connecté » : interdiction des faux états connectés même sans demande dans la file.
- Décalage sous la barre d'état corrigé par les `WindowInsets` Android 15/16.
- Respect des identifiants d'appareil existants et de la base chiffrée pour une mise à niveau signée avec la même clé.

## Limites honnêtes

- Une première autorisation sur le HP est indispensable pour ne pas appairer un téléphone inconnu.
- Sans chemin IP entre le téléphone et le HP (extender en mode NAT isolé, isolation des clients), aucun code ne peut faire passer le contrôle LAN ; un réseau commun / mode bridge est requis.
- Android requiert l'autorisation de l'utilisateur pour installer une nouvelle APK hors Play Store. Les APK de développement générées par GitHub Actions peuvent ne pas avoir la même clé de signature : ne pas promettre de mise à jour par écrasement de l'ancienne application sans validation du certificat.
- Les tests du récepteur Windows et un build GitHub ne remplacent pas une validation réelle sur téléphone + HP.

Sources publiques sans secrets dans `Terminator364/PROJECT-DRAFTS` ; service Windows installé sur le HP conserve secrets et certificats **localement**.
