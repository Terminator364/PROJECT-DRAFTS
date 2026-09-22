# ChatGPT Delivery

Canal canonique de livraison de fichiers vers Telegram, indépendant de BCP.

## Principe
1. Une conversation ChatGPT chiffre le fichier avec la clé publique du relais.
2. Elle dépose le job chiffré dans `CHATGPT-DELIVERY/outbox/<job_id>/`.
3. GitHub Actions déchiffre côté runner avec une clé privée stockée en secret, vérifie SHA-256 et envoie le fichier au bot Telegram.
4. Après succès, le payload chiffré est supprimé et un reçu est conservé.

## Secrets GitHub requis
Dans **Settings → Secrets and variables → Actions** du dépôt :
- `TELEGRAM_BOT_TOKEN`
- `DELIVERY_X25519_PRIVATE_KEY`

Le chat Telegram est détecté automatiquement depuis le dernier `/start` privé.

## Catégories
Applications/APK, PDF, Documents, Images, Archives, Autres.

## Future conversation
Lire `CHATGPT-DELIVERY/FUTURE_CHATGPT_INSTRUCTIONS.md`.

Le token Telegram n'est jamais écrit dans Git. BCP n'est pas utilisé.
