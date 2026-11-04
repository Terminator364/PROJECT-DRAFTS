# Architecture cible — non gelée avant A1

- Jeu web statique/PWA, même code Android/PC/iPhone ; mode offline après préchargement vérifié.
- Candidate Three.js/TypeScript/Vite **ou** adaptation d'un moteur libre ; évaluer le benchmark A1.
- Découpler logique/simulation (tick fixe) du rendu/animations et des entrées (clavier/tactile).
- Entrées normalisées `steer [-1,+1]`, `throttle [0,1]`, `brake [0,1]`, `interact`, `pause`.
- Étude moto d'abord : position roues-sol, accélération, freinage, contact, inclinaison, caméra stable.
- Simulation trafic sous budget, proche détaillé / distant simplifié.
- Assets libres documentés, zéro réseau tiers obligatoire, aucune télémétrie par défaut.
- Ce document est un **point de départ**, pas un choix de moteur déjà approuvé.
