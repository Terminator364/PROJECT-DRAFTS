# Candidats moto 3D gratuits — statut d'acquisition, 04/11/2026

## Candidat prioritaire (page officielle lue, fichier non téléchargé)

- **Road sportbike (Motorcycle Racing and Street Bikes)**, fournisseur 3DAssets.dev.
- Fiche originale : https://3dassets.dev/assets/motorcycle-racing-and-street-bikes-road-sportbike-e1418015
- Fichier annoncé : https://cdn.3dassets.dev/assets/15424/v1/model.glb
- Fournisseur annonce **CC0 1.0 Universal**, 254,7 Ko, 5 156 triangles, +Y haut, trois animations `wheel-roll`, `steer`, `side-stand-up`, textures WebP embarquées, extension `KHR_mesh_quantization`. **Aucune redevance d'achat annoncée**.
- **Statut : CANDIDATE_SOURCE_PAGE_VERIFIED, FILE_NOT_ACQUIRED**. L'accès HTTP binaire au CDN a échoué depuis notre environnement isolé ; pas de hash réel, pas de rendu du modèle ni licence extraite du fichier. Aucune intégration dans le jeu.
- La présence de textures WebP et d'animations par nœuds implique un **véritable pipeline glTF/GLB texturé** ou un convertisseur fiable. Notre rendu WebGL artisanal n'en dispose pas encore. Nous devons éviter d'adopter un modèle pour le dégrader lors de la conversion.

## Autres pistes

- Kenney Car Kit : https://kenney.nl/assets/car-kit — véhicules 3D sous CC0 selon l'auteur.
- Kenney City Kit Roads : https://kenney.nl/assets/city-kit-roads — éléments routiers CC0 selon l'auteur.
- Innerscene Road motorcycle : https://www.innerscene.com/tools/library/3d-parts/road-motorcycle-f2519759 — GLB 627 Ko, CC0 déclaré, modèle statique.

## Contrôle technique obligatoire

Lancer `python tools/audit_glb.py modele.glb --out docs/ASSET_AUDIT.json` sur le **fichier exact**. Le script n'accorde jamais de licence tout seul et rejette un modèle avec buffers externes, au-delà de 2 Mo ou de 12 000 triangles. Il signale les textures, animations et pivots dont le renderer doit tenir compte.

Puis ajouter source URL, auteur, SHA-256 réel, nombre de triangles, taille du download, mémoire GPU observée, niveau de détail, essai 15 minutes et pièce justificative de licence au registre `docs/ASSET_LICENSES.csv`. Seulement après cela, remplacer le modèle géométrique en jeu.
