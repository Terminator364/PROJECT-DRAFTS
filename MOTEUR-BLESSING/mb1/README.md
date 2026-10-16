# Moteur Blessing — MB-1 / outil d'inventaire en lecture seule

**Objet :** contrôler l'archive source exacte V1.1.2 *avant* de connecter ou de modifier la moindre recette. Ce sous-répertoire ne remplace ni le moteur, ni le registre complet des 372 pistes, ni la feuille ADN R8.

## Sources d'autorité
- `../CONTINUITE.md`, `../ETAT_V112.md`, `../FEUILLE_ROUTE.md`, `../MANIFEST.json`;
- [62 mondes figés R8](https://github.com/Terminator364/ChatGPT-PC/blob/research/matrice-r8-g3-depth-audit-2026-10-14/MATRICE/R8_G3_DEEP_20261014/parameter_v1_freeze_20261015/CATALOGUE_PARAMETRES_MONDES_V1_FIGE_62.json) : blob `3a82746f649bd820f5c0cec671ca88205133f92d`.

## Inspection lorsque l'archive est effectivement accessible
Sur une machine avec Python 3.10+ :

```powershell
python .\mb1\inspect_v112.py --archive "C:\CHEMIN\MOTEUR_BLESSING_V1_1_2_MOTEUR_ACTUEL_2026-10-16.zip" --output ".\mb1\inspection_v112.json"
python -m unittest discover -s .\mb1 -p "test_*.py" -v
```

L'outil refuse tout SHA-256 ou taille divergents du reçu `R-9YPJ87CMENDW`; vérifie CRC, chemins, doublons, symlinks et chiffrement ; inventorie les fichiers obligatoires et les *formes* JSON réelles. Il **n'extrait pas le ZIP**, **n'entraîne pas** et **ne calcule pas d'IC**. Si un fichier obligatoire est absent, statut incomplet et code de retour non nul.

## Contrôle reproductible
- Le 16 octobre 2026, 11 tests purement fictifs ont été exécutés dans le conteneur de cette reprise, **11 PASS**.
- Correspondance stricte source testée / blobs GitHub : `inspect_v112.py` blob `3fbb7028cec7d71e525937bda8abc773a0f5f67f` et `test_inspect_v112.py` blob `1add70d1eddc72fe93a9ba72722551e90b405d11`; vérifiée via `git hash-object`.
- Contrôle séparé du registre V1 GitHub : 62 entrées, 62 ID et noms uniques, 45 héritages + 17 extensions, ordres 1–62, tous `score_active=false`, effets numériques nuls.
- **Non exécuté dans cette reprise :** inspection effective du ZIP de 12 241 975 octets, suites historiques V1.1.2, validation Windows et tests PIT sur matchs réels. Les résultats antérieurs de 169 tests ne sont pas comptés dans les 11 tests nouveaux.

## Suite
Récupérer l'archive préservée auprès de ChatGPT Delivery ou son lien réellement vérifiable, inspecter les schémas et les 372 fiches sans noms inventés, puis bâtir l'audit individualisé (source, unité, horizon PIT, événement/doublon, coût réseau, incertitude, recette candidate et preuve) avec cinq cycles contradictoires. Aucun effet ne sera promu automatiquement.
