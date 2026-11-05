# A2 — Décision conditionnelle d'import de la Road Sportbike (CC0)
Date : 2026-11-05. **Étude de source publiée, pas acquisition du fichier.**
Moteur courant : WebGL maison `src/render.js`, `src/geom.js`, modèle moto 3D géométrique + commandes physiques indépendantes. Cible : Galaxy A21s, HP Windows (faible coût RAM), iPhone ensuite.

## Preuves publiques, sans prétendre avoir le binaire
- Éditeur original : https://3dassets.dev/assets/motorcycle-racing-and-street-bikes-road-sportbike-e1418015 (consulté le 05/11).
- URL GLB directe indiquée par l'éditeur : https://cdn.3dassets.dev/assets/15424/v1/model.glb.
- Caractéristiques annoncées : 254,7 Ko ; 5 156 triangles ; 15 468 sommets ; 8 matériaux ; 3 clips `wheel-roll`, `steer`, `side-stand-up` ; dimensions 0,76 × 1,20 × 2,135 m ; +Y vertical, moto vers +Z, essieux X ; pivots nommés ; animation sans squelette.
- Éditeur : licence **CC0 1.0** déclarée, contribution indiquée comme générée avec outil IA ; aucune marque/sponsor voulu. **Aucune copie du modèle n'a été intégrée dans ce projet** ; vérifier fichier exact, licence, provenance, taille et hash après téléchargement.
- Documentation de l'éditeur : `KHR_mesh_quantization` et textures WebP peuvent apparaître ; GLTFLoader Three.js n'exige pas Draco/Meshopt/KTX2 supplémentaires.
- Une page tierce https://meshcrate.vip/examples/assets3d-road-sportbike liste **0 images embarquées et 8 matériaux**, alors que la documentation générique de l'éditeur vante des textures WebP. Ce ne sont pas des preuves binaires contradictoires tranchées : **inspecter le vrai fichier**, ne pas présumer la présence ou l'absence de textures.

## Choix de conception à respecter
1. Ne pas copier un jeu complet ni la moto propriétaire du projet Costa Vista ; la licence MIT du code n'étend pas les droits sur ses assets.
2. La moto procédurale actuelle est légère, intégrée au tampon de géométrie; une GLB PBR animée n'est pas « remplacement direct ». Le WebGL maison ne possède pas de décodeur glTF ni de gestion de textures/matériaux/hiérarchie/animations.
3. **Éviter d'ajouter une deuxième pile de rendu Three.js par-dessus WebGL en production sans benchmark**, car cela rajouterait un contexte, de la duplication mémoire et des problèmes de synchronisation de caméra/profondeur.
4. Choix technique provisoire : inspecter d'abord la GLB exacte, puis réaliser une scène étalon A/B isolée. Comparer import léger via un pipeline glTF précompilé (avec validation des matériaux/animations) vs éventuelle migration de rendu plus large. Ne pas convertir silencieusement une vraie moto texturée en couleurs plates : cela irait à l'encontre du gate qualité du propriétaire.
5. **Offline-first obligatoire** : intégrer localement les fichiers explicitement audités dans le paquet et éviter les téléchargements CDN au runtime du joueur, même si l'éditeur autorise le hotlink. Les téléchargements pour la préparation ne sont pas une dépendance de gameplay.

## Gates obligatoires pour une sélection
- G0 hash SHA-256 du binaire, réponse licence/identité/version sauvegardée; pas de fichiers externes implicites.
- G1 `python tools/audit_glb.py candidate.glb --out ...` sur fichier réel ; budget <2 MB et <=12 000 triangles, vérifier quantization, matériaux/images, rotations/pivots, animations, éventuels avertissements.
- G2 captures vraie 3D, roues/sol, direction des pivots, éclairage, passager, changement de caméra ; contrôle de non-régression contre la moto précédente.
- G3 FPS/RAM/thermique sur HP et Galaxy A21s, essai >=15min, pas de dépendance réseau après installation.
- G4 décision utilisateur : aucun merge STABLE ni publication avant son accord.

## Blocage actuel
Tentative de téléchargement via URL officielle : refus/échec réseau DNS dans environnement d'exécution. **Fichier absent, hash absent, aucune intégration**, ni claim de conformité ou droit du binaire exact. La priorité suivante reste le test matériel de A2 0.5.6 et le benchmark A1-D.
