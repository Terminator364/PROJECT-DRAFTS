# KIN MOTO — QA A2 LAB 0.5.2-CLOUD : collisions orientées

**Date :** 4 novembre 2026. **Nature :** expérimentale. **Distribution :** sources GitHub + build offline, **aucun déploiement Vercel**.

## Modifications

- Nouveau module `src/collision.js` : empreinte voiture/bus orientée selon l'axe et les dimensions réelles de la géométrie du laboratoire, puis intersection avec un disque de contact moto (rayon 0,58 m).
- Correction des faux contacts lors d'un dépassement parallèle, des sorties de carrosserie et des chocs contre un véhicule en mouvement lorsque la moto est immobile.
- Réponse par normale de contact et vitesse de rapprochement relative ; dommages déclenchés seulement au-dessus du seuil d'impact ; délai anti-double impact préservé.
- Tampon `g._contactScratch` réutilisé par véhicule (pas de nouveau tableau/objet par comparaison), géométrie simplifiée maintenue pour appareil modeste.
- `build.py` rassemble maintenant 9 modules ; aucune dépendance additionnelle et aucune ressource externe.

## Résultats vérifiés sur environnement isolé

| Test | Résultat |
|---|---|
| Ancienne suite automatisée (54 tests) | PASS |
| Empreinte et contact orientés (8 tests) | PASS |
| Simulation prolongée (6 minutes virtuelles, 16 voitures) et moto arrêtée percutée | PASS (2 tests) |
| **Total** | **64 PASS / 64** |
| Vérification syntaxique Node.js | PASS |
| Construction HTML autonome Python | PASS · 83 895 octets · 9 modules |
| Serveur HTTP local / ressources statiques | PASS |
| Essai automatisé WebGL headless | **BLOCKED — GPU WebGL indisponible dans le conteneur ; aucun rendu graphique validé ici** |
| Android physique / iPhone / GPU HP | **NOT_TESTED dans ce lot** |
| Sensations de conduite / direction artistique | **NOT_VALIDATED** |

SHA-256 du HTML : `fd3ae3031ff167624143eae3bbb8a9fae957760c7241eda2cf6de4a0313fb78d`.

## Risques conservés

1. Contrôleur moto semi-physique : pas encore une suspension de moto intégralement réaliste.
2. Modèles 3D encore procéduraux et peu détaillés ; un modèle externe CC0 doit être audité puis intégré si son poids et son rendu sont acceptables.
3. Les voitures suivent des boucles limitées ; réactions secondaires simples et absence de véritable réseau de conducteurs urbains.
4. Cette version est un **laboratoire A2** et ne constitue pas une V1 de jeu validée.
5. L'absence de tests de rendu ne doit pas être compensée par une affirmation de qualité visuelle.

## Décision de production

Conserver le code dans une branche isolée puis fusion après QA et diff uniquement `KINMOTO/`. Ne pas toucher à `Vercel`, au domaine public, à l'ancienne V1 ni à l'ordinateur personnel. Le prochain lot doit cibler la **présentation visuelle et la sensation de contact roue/route**, avec une source d'asset clairement autorisée, et préparer un benchmark Android de fin de jalon.
