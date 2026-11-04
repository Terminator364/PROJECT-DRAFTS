# KIN MOTO — LABORATOIRE MOTO A2 (préversion non validée)

Projet expérimental isolé de la V1 et des anciennes URLs publiques. N'est **pas** une V1 commercialisable ni une version STABLE. Les tests valident l'intégrité de certains comportements, **pas** la qualité perceptuelle sur tous les appareils.

## Ouvrir et essayer

- Site laboratoire distinct : https://kin-moto-a2-moto-lab.vercel.app/
- Sur PC : W/↑ accélérer, S/↓/Espace freiner, A/← vers la gauche, D/→ vers la droite, E récupérer ou déposer un client, C caméra, P/Echap pause.
- Sur Android : boutons tactiles, qualité économique recommandée. Android physique **non vérifié**.
- Les commandes tactiles sont masquées quand un pointeur souris de bureau est détecté ; elles restent sur les appareils tactiles.
- Sauvegardes sur une origine et clé spécifiques au laboratoire (pas de migration automatique depuis la V1).
- Page de contrôle interne : ?qa=1&autoplay=1&autodrive=left ou right (le scénario redémarre à zéro dans la source actuelle).

## Ce qui est amélioré par rapport à l'ancienne V1

1. Un module de dynamique moto distinct `src/bike_physics.js` : direction lissée, rotation dépendant de l'empattement, grip latéral, inertie limitée, inclinaison selon accélération latérale, décélération, rotation des roues liée à la distance.
2. Un modèle de moto géométrique plus détaillé : pneus avec jantes et rayons, cadre tubulaire, réservoir arrondi, moteur/échappement, phare, guidon et rétroviseurs, conducteur et passager.
3. Roues animées séparément : rotation des deux roues et braquage visuel de l'avant.
4. Réaction des voitures après choc : freinage temporaire ; pas de collisions fantômes multiples par la même fenêtre de contact.
5. Occlusion de caméra : ne pas dessiner une voiture lorsqu'elle engloutirait la caméra derrière la moto.
6. Interface PC allégée : touches tactiles masquées pour souris et clavier ; aucun passage de la 3D en 2D dégradée.

## Limitations techniques explicites

- La roue est projetée sur une **chaussée plane**, sans raycast de collision des pneus. Les booléens `frontGrounded/rearGrounded=true` sont des simplifications. Les bosselures réelles et une suspension physique de deux-roues restent à traiter.
- Le corps dynamique est un modèle semi-physique : pas de transfert précis de charge, pas de simulation du contact pneumatique complète et pas de chute du pilote. Le terme « physique réaliste » ne serait pas justifié.
- Les voitures suivent encore les anciennes boucles et leurs réactions sont limitées. Les missions et le monde restent ceux de l'ancienne V1, qui n'est pas validée artistiquement.
- Le comparatif Costa Vista/Neon Mayhem n'est pas clos : il reste des tests de conduite physique et des droits sur certains modèles 3D à éclaircir.
- Aucune certification Android physique ou iPhone, et aucune mesure fiable de la mémoire propre au jeu.

## Exécution depuis le code source

Pré-requis de développement : Python 3 et Node.js modernes (gratuits). Aucun `npm install` requis pour le jeu.

```bash
python3 build.py
node --test tests/*.test.mjs
python3 -m http.server 8000 -d dist
```

Le dossier `dist/` comprend l'HTML autonome, les icônes, le manifest PWA et le service worker.

## Confidentialité et licences

Ce laboratoire contient du code créé pour KIN MOTO et l'ancien prototype détenu par l'utilisateur. Aucun code, modèle ou texture de Neon Mayhem, Costa Vista ou Poly Pizza n'a été copié dans le jeu. Leurs projets ont été **étudiés** séparément. Pas de dépendance réseau nécessaire au gameplay après installation ; aucune télémétrie incluse.

Code de continuité : `KINMOTO|SYNC`. La source canonique est GitHub `Terminator364/PROJECT-DRAFTS/KINMOTO/experiments/A2_MOTO_LAB/` une fois enregistrée.


## A2 LAB 0.5 — contact de route et trafic réactif
- Source déterministe de profil de chaussée commune à la géométrie et à la physique (`src/road_surface.js`).
- Échantillons de contact avant et arrière, amortissement ressort, différence de pente et compensation des roues pour l'inclinaison et l'assiette. Petite bosse visible sur trois axes (ce n'est PAS une vraie suspension rigide Rapier).
- Freinage du trafic pour obstacles proches et priorité déterministe à l'intersection, sans créer d'objets temporaires pour calculer le créneau.
- Tests dédiés (`tests/road_contact.test.mjs`, `tests/traffic_reactivity.test.mjs`).
- Situation de test `?qa=1&autoplay=1&autodrive=straight`: affiche les hauteurs des pneus, la réaction maximale du châssis et le FPS instantané en 3D ; les commandes réelles demeurent nécessaires pour la recette utilisateur.
- Toujours en LABORATOIRE : pas de V1 certifiée, Android physique non encore testé et direction artistique encore insuffisante.
