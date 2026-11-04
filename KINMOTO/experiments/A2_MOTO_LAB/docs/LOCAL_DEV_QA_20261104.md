# KIN MOTO — QA local et budget hébergement, 4 novembre 2026

## Décision gelée

- Vercel Hobby officiel : **100 déploiements par période de 24 heures**, **32 builds par heure**, mais état de consommation du compte **inconnu**.
- Le propriétaire demande **aucun nouveau déploiement Vercel** pendant la conception et les correctifs ; pas de nouvel hébergeur sans feu vert.
- Aucun déploiement Vercel ni GitHub Actions hébergée n'a été déclenché pour les modifications décrites ici.
- Sources, scripts et rapport dans GitHub ; backups des anciennes versions inchangés.

## Tests locaux vérifiés

| Vérification | Preuve | Statut |
|---|---|---|
| Source VS HTML autonome | `python build.py` → 81 006 octets, 8 modules inline | PASS |
| Code JavaScript | `npm run check` | PASS |
| Physique, missions, trafic, bordures et budget | `npm test` → **54/54** | PASS |
| Serveur Python local | `python tools/test_local_delivery.py` : index, SW, manifest, SVG, PNG, HTTP headers, URL hors racine refusée | PASS |
| Build PowerShell Windows | HP Windows 11, sans Python/Node utilisés pour le build ; index de 79 143 octets puis 80 998 octets après corrections précédentes | PASS pour compilation PowerShell |
| Serveur PowerShell local | `http://localhost:8789` servi depuis le HP, requêtes HTML/SW HTTP 200 ; Opera ouvre le rendu WebGL | PASS pour serveur et démarrage |
| Défaut de pénétration façade | Capture précédente montrait moto en façade à `x=-14.5` ; `keepOverStreet` contraint désormais l'axe le plus proche à **8,1 m** ; caméra à **7,5 m** | PASS en tests numériques ; visuel après changement à consolider |
| Android Galaxy A21s physique | Pas de session Android capturée | NOT_TESTED |
| iPhone physique | Hors périmètre immédiat | NOT_TESTED |
| FPS/RAM sur 15 min avec Opera foreground | Aucun relevé fiable complet | NOT_TESTED |
| Ressenti de conduite validé par joueur | Non évalué après cette correction | NOT_TESTED |

## Pourquoi le mode local est utile

- Une compilation PowerShell sans installation supplémentaire est possible sur le HP.
- Le serveur ne bind que la boucle locale (`127.0.0.1`) par défaut, aucune exposition Internet.
- Le service worker fonctionnera seulement dans un contexte sécurisé (localhost reconnu, HTTPS en ligne). Le téléphone via HTTP LAN ne valide pas PWA hors ligne.
- Sur une machine à pression RAM élevée, ne pas faire tourner le jeu, les tests graphiques et les gros logiciels inutilement en parallèle.
- **Aucun compteur FPS obtenu par une scène masquée/onglet background ne doit être utilisé comme mesure de performance réelle.**

## Défauts restant à traiter avant V1

1. Mesures réelles sur Android, et retour qualitatif sur la moto.
2. Suspension 2-roues encore simplifiée (surface heightfield, pas raycasts Rapier complets).
3. Graphismes et véhicules moins bons que l'ambition déclarée ; assets CC0 à sélectionner et intégrer avec licences/poids vérifiés.
4. Caméra et environnement à vérifier par captures comparables en conduite prolongée.
5. Missions interactives et trafic à évaluer pendant une session complète.

## Protection anti-publication

`KINMOTO/PROJECT_STATE.json`: `hosting_policy.vercel_deploy_allowed = false`; `other_public_deploy_allowed = false` ; la publication reste gelée jusqu'à un nouvel ordre explicite.
