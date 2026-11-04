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
