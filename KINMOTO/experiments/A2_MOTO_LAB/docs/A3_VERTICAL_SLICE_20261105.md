# A3 — Micro-quartier Bandal / École / Victoire — 05/11/2026

**A3 intégration laboratoire :** candidate *vertical slice*, non acceptation V1. Fille de la branche A2-COLLISION (#43).

## Critères du cahier FACTORY V3 / §16
- Une zone reconnaissable, non pas une extension infinie : quartier de départ proche de Bandal, École des Arts, Place Victoire. Géométrie urbaine déjà existante et modeste ; ajout d'un abri de station wewa à x=-11,2,z=85 et voies de stationnement comme un unique lot de mesh statique.
- Deux missions **écrites** de bout en bout, avant rotation procédurale :
  - 01 « COURSE DU QUARTIER » : arrêt wewa de Bandal → École des Arts ; Maman Chantal ; 850 FC avant confort/pénalités.
  - 02 « COLIS POUR VICTOIRE » : École des Arts → Place Victoire ; Junior ; 1 150 FC avant ajustements.
  - Dès la troisième course, retour au système de carrière initial ; garage/upgrades, 16 voitures et sauvegardes continuent à fonctionner.
- La première prise en charge est proche du point de départ (~15 m affichés sur UI), plutôt qu'à l'autre bout de la ville. Pas de téléportation.
- Les fichiers du jeu restent 3D, offline-first, sans appel serveur ni nouvel asset externe à licence incertaine.

## Preuves
- 5 tests `tests/a3_vertical_slice.test.mjs` : deux routes courtes/connectées, premier client accessible, deux missions complètes payées chacune une fois, sauvegarde à mi-course, géométrie créée.
- Deux tests hérités ont été **révisés sans les supprimer** : l'affirmation arbitraire « première mission >100m » est remplacée par « distance >0 et calcul déterministe » ; le refus d'interaction est testé à une position distante explicite.
- Suite locale A3 issue du baseline A1D après correction A2 : **173/173 Node PASS**, 22/22 Python (historique, non relatif aux nouvelles images).
- Visuel logiciel WebGL2 sera testé sur candidate A4 ; image seule non suffisante pour accepter la qualité.

## Écart restant
La charte demande une qualité visuelle crédible et une circulation maîtrisée. L'ensemble reste low-poly, les PNJ n'ont pas d'animation de montée/descente et les intersections demeurent simplifiées. Ces critères **NE SONT PAS validés**. Une route scriptée et le fonctionnement des missions ne suffisent pas pour valider une véritable zone de Kinshasa.
