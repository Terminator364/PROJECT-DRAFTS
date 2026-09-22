# Instructions pour toute future conversation ChatGPT

Quand l'utilisateur demande « envoie-moi le fichier sur Telegram » :

1. utiliser le relais `Terminator364/PROJECT-DRAFTS/CHATGPT-DELIVERY` ;
2. ne jamais demander ni exposer les secrets Telegram ou la clé privée ;
3. générer ou matérialiser le fichier localement ;
4. récupérer `client/encrypt_delivery.py` ;
5. produire un job chiffré ;
6. pousser ce job sous `CHATGPT-DELIVERY/outbox/<job_id>/` ;
7. attendre le workflow `ChatGPT Delivery → Telegram` ;
8. confirmer la livraison uniquement après succès du workflow et création du reçu.

Catégories : Applications/APK, PDF, Documents, Images, Archives, Autres.

BCP ne fait pas partie de ce système.
