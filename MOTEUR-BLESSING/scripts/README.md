# Outils Windows locaux

Ces scripts sont **optionnels**, ne sont exécutés par aucun GitHub Actions. Ils servent au dossier `C:\Users\Lenovo\Documents\Moteur Blessing`.

- `SYNCHRONISER_CONTINUITE.ps1` télécharge uniquement les 7 petits documents depuis GitHub main. Il n'installe pas le code.
- `INSTALLER_ARCHIVE_LOCALE.ps1 -Archive "chemin_du_zip"` vérifie le SHA-256 indiqué par Delivery et extrait en `versions/V1.1.2` uniquement si le dossier n'existe pas.

Ne jamais confondre synchronisation de documentation et installation réelle du moteur. Aucun script ne déclenche d'Actions hébergées GitHub.
