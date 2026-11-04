# A1 — Sources gratuites candidates (pas sélectionnées)

| Source | URL officielle | Ce qu'il faut tester | Risque à vérifier | État |
|---|---|---|---|---|
| Neon Mayhem | https://github.com/pranshuparmar/neon-mayhem | Conduite moto, tactile, missions, taille, offline | Apache-2.0 code indiqué ; licences assets à relever ; rendu/Android inconnus | CANDIDATE |
| Costa Vista | https://github.com/fastrouter/experiments-costa-vista | Physique Rapier, moto, trafic, mission taxi | MIT code indiqué ; assets non uniformes ; repo lourd (~270 Mo déclaré) ; tactile incomplet | CANDIDATE |
| Kenney Car Kit | https://kenney.nl/assets/car-kit | Véhicules 3D, taille, niveau de détail | CC0 affiché ; cohérence visuelle à tester | CANDIDATE |
| Kenney City Kit Roads | https://kenney.nl/assets/city-kit-roads | Réseau/intersections | CC0 affiché ; conversion et précision locales | CANDIDATE |
| Prototypes KIN MOTO | `docs/HISTORICAL_ARCHIVES.md` | Éléments graphiques, UX, missions récupérables | Anciennes régressions et code non validé | ARCHIVED_REJECTED_QUALITY |

**Verdict :** aucun moteur définitivement retenu. A1 ne doit pas annoncer un vainqueur avant essais sur HP et Android, et audit des droits fichier par fichier.

## A1-S (2026-11-04)
- **Pinned** Neon `cd19f934d9088392d1f10374c3b64a1b7eb683cf` ; Costa `23e87108a281ac827e2ea23691aa7bf4b544146e`.
- Rapport : `A1_STATIC_SOURCE_AUDIT_20261104.md`, scorecard : `A1_SCORECARD_20261104.json`. Aucun score /100 attribué sans essai réel.
- Autre **bibliothèque** à examiner si utile : `AndyGura/gg-web-engine` Apache 2.0, pas de contrôle moto vérifié.
- **Bloquant juridique** : Costa Vista `LICENSE` exclut `public/assets` de MIT ; ne pas importer les modèles internes.

## A1-S+ — Candidats artistiques CC0 vérifiés publiquement (2026-11-04)

| Source | Licence annoncée | Utilité possible | Condition avant intégration |
|---|---|---|---|
| [Cartoony Purple Motorcycle / AliceCassie](https://poly.pizza/m/j20srJUjpB) | Public Domain / CC0 sur page modèle | **Moto 3D GLTF/OBJ**, plus crédible qu'un assemblage de boîtes | Télécharger le modèle source gratuitement, conserver la preuve de licence, vérifier proportions et animations de roues, retopologie si besoin |
| [Kenney Car Kit](https://kenney.nl/assets/car-kit) | CC0, page officielle | Véhicules de trafic, plusieurs types | Harmoniser les tailles, matériaux, poids et palette |
| [Kenney City Kit Roads](https://kenney.nl/assets/city-kit-roads) | CC0, page officielle | Routes, marquages, feux, carrefours | Adapter au réseau Kinshasa, ne pas copier une ville générique |
| [Quaternius Universal Base Characters](https://quaternius.com/packs/universalbasecharacters.html) | CC0 affiché pour pack gratuit | Conducteurs et passagers riggés | Sélectionner **Standard gratuit**, contrôler la taille (~13k triangles selon site) et la compatibilité rig |
| [Quaternius Universal Animation Library](https://quaternius.com/packs/universalanimationlibrary.html) | CC0 affiché pour pack gratuit | Animations d'attente, marche, assis | Sélectionner le sous-ensemble libre ; compatibilité rig et mémoire ; vérifier archive source |
| [GG Web Engine](https://github.com/AndyGura/gg-web-engine) | Apache-2.0 (fichier LICENSE du dépôt) | Référence de sous-modules de simulation/contrôles mobiles | Bibliothèque, **pas** preuve de physique de moto ; ne pas ajouter sans nécessité |

**Précision :** aucune ressource ci-dessus n'est encore intégrée au jeu. Toutes entrent comme `CANDIDATE_LICENSE_PAGE_VERIFIED`, non `APPROVED_ASSET` ; l'approbation exige le téléchargement du fichier exact, son hash, taille, format, licence et essai dans la scène de benchmark. Aucune version payante Quaternius Source/Pro n'est autorisée.

## Nouveau candidat léger pour le modèle 3D (audit web, 4 novembre 2026)

- [Road motorcycle — Innerscene](https://www.innerscene.com/tools/library/3d-parts/road-motorcycle-f2519759) : la page de la bibliothèque présente un modèle GLB original, non marqué, sous **CC0**, taille annoncée **627 Ko**, longueur environ 2,1 m, largeur 0,8 m, hauteur 1,4 m, rayon des roues de taille réaliste. **CANDIDATE_SOURCE_PAGE_VERIFIED**, PAS téléchargé ni intégré ; vérifier fichier exact, hash, nombre de triangles, textures, articulations roue/guidon et vraies performances sur A21s avant adoption. La licence CC0 de la page ne valide pas automatiquement chaque texture d'un fichier non téléchargé.
- Ce candidat est mieux dimensionné pour l'appareil Android économique que des modèles CC0 de 7 à 20 Mo, mais sa qualité réelle et sa topologie ne sont pas encore contrôlées.
- Aucune ressource GLB nouvelle n'a été importée durant la version A2-0.5.2. Interdiction de remplacer un modèle procédural par un asset sans tests et conservation de provenance.
