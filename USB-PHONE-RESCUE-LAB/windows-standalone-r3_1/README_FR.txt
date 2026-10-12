BCP USB Rescue PC R3.1 (Windows 10 / Windows 11)
================================================

Le fichier BCP-USB-Rescue-PC.exe contient :
- l'installateur graphique Windows,
- l'agent de diagnostic et de fichiers limité,
- le superviseur Windows qui reste disponible après connexion USB,
- les outils de diagnostic USB et de correction du pare-feu avec autorisation.

Aucun Python, GitHub ou programme séparé à installer sur Windows.

A faire UNE fois sur MBMPC :
  1. Ouvrir BCP-USB-Rescue-PC.exe.
  2. Cliquer sur « Installer et activer sur ce PC ».
  3. Brancher le Samsung par câble USB de données.
  4. Activer « Partage de connexion USB » dans les réglages Samsung.
  5. Dans la fenêtre Windows, cliquer « Actualiser le diagnostic ».
  6. Copier l'adresse IP détectée et la clé d'appairage, à saisir sur le téléphone
     dans BCP USB Rescue → Réglages (port 8766).
  7. Sur le téléphone : « Enregistrer l'appairage » puis « Diagnostiquer maintenant ».

IMPORTANT : la clé et l'adresse IP doivent être saisies une première fois dans
l'APK R3.1. L'interface Android actuelle ne sait pas détecter automatiquement
l'adresse du PC ou scanner un QR. Ne jamais transmettre la clé dans ChatGPT.

Si le téléphone n'atteint pas le PC :
- Vérifier que le partage de connexion USB est activé.
- Utiliser le bouton Windows dédié au pare-feu USB, et accepter la demande
  Windows uniquement si nécessaire. La règle est limitée à l'interface USB.

Sécurité : ce prototype utilise HTTP avec authentification HMAC mais sans TLS.
Ne pas l'utiliser sur Wi-Fi public ou avec des données sensibles. Ce n'est pas
un remplacement complet de Desktop Commander et ChatGPT ne gagne pas l'accès
au PC automatiquement. L'installateur peut être signalé comme non signé par
Windows SmartScreen (compilation pilote sans certificat éditeur commercial).

État : binaire Windows produit en environnement CI ; installation et liaison USB
à confirmer sur le vrai MBMPC.