# MOTEUR BLESSING — Projet officiel dans PROJECT-DRAFTS

> **Commande de reprise : `MOTEUR|CONTINUE`** (alias `MOTEUR BLESSING|CONTINUE`).
> Dernier checkpoint fiable : **MB-1 V3 (16 octobre 2026)**, sur socle **V1.1.2**. [État vérifié](ETAT_MB1_V3_20261016.md) · [Checkpoint structuré](mb1/CHECKPOINT_MB1_V3_20261016.json).
> **Projet distinct du flux général MATRICE|CONTINUE**, mais respectant l'ADN MATRICE R8 pour l'IC Over 1,5.

## Objet et point de départ
Moteur Blessing est la branche de conception/implémentation du moteur de calcul mathématique qui transforme les données pré-match ("farine") en **IC = P(au moins deux buts sur les 90 minutes, arrêts de jeu compris)**. Le nom propre "Moteur Blessing" ne signifie pas qu'un second moteur a été réinventé : le socle est MATRICE R8, versions V16 > V1.1 > V1.1.1 > V1.1.2.

**Livraisons :** source d'origine V1.1.2 reçue via Delivery `R-9YPJ87CMENDW` (12 241 975 octets, originale intacte). **Dernier paquet** : `MOTEUR_BLESSING_V1_1_2_MB1_V3_2026-10-16.zip` (12 298 556 octets), sauvegardé dans le [dossier Google Drive privé](https://drive.google.com/drive/folders/1t_53nvyzLAD_wmPCo8AKwB21QgDuKGaX) et la bibliothèque ChatGPT. GitHub contient les **checkpoints et la documentation**, pas les 12 Mo du moteur. MB-1 V3 ajoute le plan des 372 exigences et un coffre de preuves, sans activer de nouveaux scores.

## Lire, dans cet ordre
1. [CONTINUITE.md](CONTINUITE.md) : protocole exécutable de reprise d'une nouvelle conversation ;
2. [ETAT_MB1_V3_20261016.md](ETAT_MB1_V3_20261016.md) : **état actuel** ; puis [ETAT_V112.md](ETAT_V112.md) : baseline historique ;
3. [FEUILLE_ROUTE.md](FEUILLE_ROUTE.md) : travaux suivants et portes de validation ;
4. [LIVRAISONS.md](LIVRAISONS.md) : preuve de livraison et références ;
5. [JOURNAL.md](JOURNAL.md) : journal des interventions et observations ;
6. [MANIFEST.json](MANIFEST.json) : état structuré pour automatisation.

## Autorités scientifiques, séparées
- ADN MATRICE R8 : [source R8](https://github.com/Terminator364/ChatGPT-PC/blob/research/matrice-r4-universal-2026-10-10/MATRICE/GOUVERNANCE/FEUILLE_DE_ROUTE_DIRECTRICE_MATRICE_ADN_2026_10_14_R8.md).
- Catalogue gelé de **62** mondes : [catalogue canonique 62 (branche R8 G3)](https://github.com/Terminator364/ChatGPT-PC/blob/research/matrice-r8-g3-depth-audit-2026-10-14/MATRICE/R8_G3_DEEP_20261014/parameter_v1_freeze_20261015/CATALOGUE_PARAMETRES_MONDES_V1_FIGE_62.json). La liste `GOUVERNANCE/CATALOGUE_PARAMETRES_R8.json` d'une autre branche ne contient que **30 mondes** et ne doit pas remplacer le canonique 62.
- Gouvernance GitHub et budget : [AGENTS.md](../AGENTS.md), [NEW_PROJECT_BOOTSTRAP.md](../NEW_PROJECT_BOOTSTRAP.md). Aucune Actions automatique, aucun service payant nécessaire.

## Espace de travail local
Dossier demandé et créé via Desktop Commander : `C:\Users\Lenovo\Documents\Moteur Blessing`.
La copie du code de production sur ce PC **ne doit pas être déduite** de la création du dossier ; l'archive se trouve dans ChatGPT Delivery. Un téléchargement local et une extraction ne sont à déclarer faits qu'après constat et contrôle des empreintes.

## Principe de sincérité
Des **formules codées** ou des **tests verts** ne prouvent ni la calibration ni la performance du moteur sur des matchs réels. Le candidat V1.1.2 perd sur une épreuve synthétique contre la baseline ; il reste `EXPERIMENTAL_NOT_APPROVED`.

## Vérification du bootstrap (2026-10-16)
GitHub publié et relu. Sur MBMPC, création de `Documents/Moteur Blessing`, **7 documents synchronisés**, deux scripts PowerShell de gestion présents ; synchronisation terminée avec code de sortie zéro. Archive **non extraite sur Windows**. Côté environnement ChatGPT, ZIP vérifié et **169/169 tests** relancés. Voir `MANIFEST.json` et `JOURNAL.md`.

## Reprise post-MB-1 V3 (16 octobre 2026)
- [Plan et coffre MB-1 V3](mb1/README_V3_20261016.md) : 11 voies de preuves candidates, 12 familles de doubles usages, 372 sous-paramètres non promus.
- Tests effectivement relancés dans l'environnement ChatGPT : **215/215 PASS** (169 moteur d'origine + 18 MB-1 V2 + 28 MB-1 V3). **Aucun test Windows du ZIP complet**.
- **Mise à jour ultérieure confirmée** : Google Drive pour ordinateur était monté en G: sur MBMPC. ZIP V3 copié dans un dossier versionné (SHA-256 conforme), extrait, **215/215 tests Windows/Python 3.12.10 réussis**. Journaux et reçu Windows accessibles dans le Drive privé. La validation sportive PIT/OOS reste ouverte.
