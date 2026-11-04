# KIN MOTO · A2 LAB 0.5.5 — Bilan cumulatif, 04/11/2026

Statut : **laboratoire expérimental**, non certifié V1. Aucun nouveau déploiement public, aucun usage Desktop Commander ni GitHub Actions hébergées dans cette série. Anciennes URLs intactes.

## Checkpoints enchaînés

1. **0.5.3 — Navigation sur rues réelles du laboratoire** : chemin sur graphe de neuf carrefours, distance le long des segments, consignes GPS gauche/droite/tout droit/arrivée, petit panneau de guidage qui ne masque pas la moto. Correction des distances affichées pour qu'elles se réfèrent au même trajet. 69/69 tests au jalon.
2. **0.5.4 — Qualité de service** : passager/colis sensible au freinage brusque, aux virages, aux bosses et impacts ; rémunération et étoiles modulées. Jauge confort au cours de la mission ; comportement déterministe, pas de facturation en ligne. 76/76 tests au jalon.
3. **0.5.5 — Optimisation de rendu** : adaptation prudente de la résolution WebGL selon FPS soutenus, sans changer les règles de physique ni supprimer la 3D ; 82 tests au jalon.
4. **Contre-test du build** : découverte d'un bug de collision de noms JavaScript (deux variables `clamp`) dans le HTML autonome qui n'était pas détecté par les tests de modules. Renommage des symboles, vérification du JS concaténé via Node VM, comparaison automatique de l'ordre des 12 modules dans les builders Python et PowerShell (l'ancien builder PowerShell oubliait le module collision). 85/85 tests finaux.
5. **Contrôle graphique de bureau et émulation tactile** : WebGL 2 et démarrage réel dans Chromium + SwiftShader sous Xvfb ; mission récupérée par hook QA, nouvel état visible, consigne de navigation, confort à 100 %, aucune erreur JS pendant la capture. Captures `A2_v055_desktop_webgl.png` et `A2_v055_mobile_emulated_webgl.png` dans ce ZIP, **non** prises sur un Samsung ou iPhone réel.
6. **Contrôle d'interface portrait 393×852** : rectangles HUD mesurés ; carte et mission ne se chevauchent plus, compteur et commandes ne se recouvrent pas. Alertes replacées au-dessus de l'aire de conduite.
7. **Stress CPU** : 72 000 pas simulant 20 minutes, collisions gérées, états finis, historique limité à 35 messages, variation mémoire Node approximative ~224 Ko après GC ; pas une mesure des buffers GPU ni du navigateur complet.
8. **Audit GLB CC0** : inspecteur hors ligne sans dépendances Python ; budgets taille/triangles, binaires intégrés, fragments externes interdits, animations/pivots et textures signalés. 7 tests unitaires supplémentaires **Python** indépendants des 85 tests Node.

## Résultats QA 
- `node --test tests/*.test.mjs`: **85/85 PASS**.
- `python -m unittest discover -s tests -p 'test_*.py'`: **7/7 PASS**.
- `python build.py`: **PASS**, HTML inline de 12 modules ; aucun téléchargement au runtime.
- `xvfb-run ... tools/visual_smoke.py`: **PASS** sur Chromium logiciel WebGL 2 (desktop + format mobile ém ulé), aucune erreur JS. FPS instantané 11–15 à cause du rendu CPU logiciel sous Xvfb, non comparable à Android/PC avec GPU.
- `node --expose-gc tools/stress_run.mjs`: **PASS**, 72 000 pas.
- Import du modèle CC0 original : **NON FAIT** (fichier GLB binaire non récupérable dans l'environnement ; licence web vérifiée mais fichier individuel et performance non vérifiés). Le moteur WebGL artisanal n'a pas encore de rendu glTF texturé : il serait contreproductif de dégrader un vrai asset en le convertissant à des couleurs plates sans validation.
- Tests physiques Android et PC HP sur cette version : **NON FAITS** ; ne pas les confondre avec l'émulation ou les anciens essais du HP.
- Durée de jeu, stabilité batterie/thermique et satisfaction joueur : **NON VALIDÉES**.

## Critères bloquants avant nouvelle V1

1. Moto réellement agréable sur Android et PC, plus de sensation de glisse.
2. Modèle/animation 3D libre de qualité supérieure, avec licence du fichier exact, format adapté et performances mesurées.
3. Contrôle 15 min de RAM/FPS sur Galaxy A21s et HP.
4. Pas de collision fantôme ni de rendu 2D dégradé ; sauvegarde et missions testées sur appareils réels.
5. Accord utilisateur avant toute publication Vercel ou autre hébergeur.

**Continuité :** `KINMOTO|SYNC`, dépôt canonique `Terminator364/PROJECT-DRAFTS/KINMOTO`, zéro frais.
