# LINK2HP — vérification v1.2 (10 novembre 2026)

## Version suivie
- Branche : `link2hp/ux-simple-v1-2-20261110`.
- GitHub Actions : [exécution 42916001476](https://github.com/Terminator364/PROJECT-DRAFTS/actions/runs/42916001476), compilation APK Android 1.2.0 **SUCCEEDED**, SHA du code `770eeeee68c9cfb0cf8be1f9579a1329dc0c70c3`.
- Archive du runner récupérée ; APK ZIP structure valide, taille 851501 octets ; SHA-256 `7b90e1496d0fff9495eaf709640bcf125cece74d0fc2b8b11be06f9c33430f4a`.
- Tests locaux Node `agent.test.cjs` + `wifi.test.cjs` : **8/8 PASS**, pas d'échec.
- APK transmise au dossier privé « ChatGPT Delivery / À envoyer / Applications-APK » ; **aucun reçu de livraison Telegram confirmé** au moment du contrôle.

## Décisions ergonomiques
- Écran Android limité à état de connexion HP, action « Envoyer au HP », historique ; options réseau facultatives repliées par défaut.
- La recherche du HP ne doit pas ouvrir les réglages Wi-Fi Android ; les confirmations d'appui, une jauge et les états doivent être explicites.
- Un téléphone sur extender Starlink 2,4 GHz et un HP sur 5 GHz peuvent communiquer **uniquement** si leur réseau local est routable. Le téléphone ne pilote pas un HP déjà injoignable.
- Association initiale : approbation explicite d'un clic sur le tableau de bord local du HP, pas de code à recopier.

## Non-conformités restant ouvertes
- Les certificats de signature d'APK v1.0, v1.1 et v1.2 diffèrent (v2 signer certificate SHA-256 respectivement `68d01d4d360f086578214cc6ce9c428bcd6a85348cbcf608b9beaa4a68ac376b`, `d910995d1892581071c0772aa0afcbc56e53d927209a66a7300b66d6f01da1ce`, `8977c41274c9dea262034ab6eabb1b2270fdb98b32ae9c636c9c3afcdc0f3e1a`). **Mise à jour Android par-dessus l'ancien APK non possible** sans clé originale, ni auto-installation fiable. Ne pas revendiquer d'auto-update tant qu'une clé de signature stable et privée, le protocole de publication et l'autorisation Android d'installation ne sont pas en place.
- Un vrai test téléphone Android → HP → récupération de fichier public n'a **pas été démontré**. Le contrôle HP par PCRC a rendu `RECONCILIATION_REQUIRED` / `TimeoutError` ou `RuntimeError` ; **ne pas** prétendre le PC joignable aujourd'hui.
- Ne pas télécharger de nouveaux binaires sur le HP ni modifier PCRC/qBittorrent tant que le canal n'est pas rétabli. Aucune publication 1.2 « production qualifiée ».
- ChatGPT Delivery : le simple dépôt Drive vaut « en attente », pas « livré Telegram », jusqu'au reçu `DELIVERED` avec identifiant de message.

## Suite prioritaire
1. Réparer et vérifier le canal PCRC, lire l'installation HP existante, auditer pare-feu/ports et poursuivre un test réel avec petit fichier public autorisé.
2. Fixer une seule signature Android stable et un mécanisme de mise à jour consenti par Android ; prévenir l'utilisateur de la migration initiale potentiellement destructive.
3. Qualifier l'appairage et le transport réel sur le téléphone, corriger le retour visuel d'après observation.
4. Obtenir un reçu ChatGPT Delivery avant d'affirmer Telegram livré.
