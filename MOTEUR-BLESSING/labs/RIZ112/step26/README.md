# Step26 — échelle de preuve des 112 rubriques

Cet audit réconcilie les preuves écrites Steps17/19/20/24 et le projet de protocole Q Step25, **sans attribuer de coefficients de qualité**.

Les 112 rubriques sont réparties de manière exclusive pour orienter la prochaine recherche : 9 grandeurs avec réponse d'un modèle physique simplifié, 29 chemins de plan/ressource contrôlés sans preuve physique nouvelle (30 routes examinées au Step19, dont 035 figure aussi parmi les neuf grandeurs physiques), 14 cibles mesurables post-T0 (qui ne sont pas des entrées), et 60 autres rubriques dont l'effet physique/qualité réel n'est pas prouvé. Cette classification résume la preuve disponible, pas la vraie pertinence causale universelle. Les 30 chemins contrôlés ne prouvent pas 30 effets physiques ou sur la qualité. Les 36 interactions théoriques entre les 9 grandeurs sont référencées.

Pour chaque rubrique, `REGISTRE_TRANSVERSAL_112.json` conserve son nom, son rôle, les résultats documentés, le prochain test et les fichiers sources. `scientific_ic_percent` reste `null` et aucun mécanisme n'est artificiellement déclaré validé.

L'étape est exclusivement documentaire/mathématique. Elle ne remplace pas un protocole Q approuvé ou des cuissons indépendantes. Tester : `python -m unittest discover -s step26 -p 'test_*.py' -q`.


**Windows offline** : `step26/LANCER_RIZ112_STEP26.cmd` réutilise le Step24, rejoue le projet Q, la fiche vide et le registre des 112, puis lance les tests 25/26. Le résultat affiché précise explicitement que Q est non approuvé et que l’IC réel est nul. Aucun clic de l’utilisateur n’est nécessaire pour un test à distance.
