# Step24 — audit d'interactions physiques croisées

Pour les neuf grandeurs physiquement reliées au Step20, le script calcule **36 paires** de perturbations simultanées (5 %), ainsi que les deux perturbations isolées. On estime la différence d'ordre deux `f(a+b)-f(a)-f(b)+f(base)` sur six sorties physiques théoriques ; c'est un test de **non-additivité locale**, pas une estimation de la contribution réelle à la cuisson ou à l'IC.

Dans le dossier synthétique A, **7/36 paires** présentent une non-additivité physique sous les hypothèses déclarées. Les autres ne montrent pas de non-additivité à ce point ; cela ne prouve pas leur indépendance universelle. Aucun des autres couples des 112 rubriques n'est promu au rang d'effet physique vérifié. La qualité réelle et les probabilités restent `null`.

Commande : `python step24/interaction_matrix.py --packet step6/examples/A_couvercle_ajuste_112.json --assumptions step20/ASSUMPTIONS_SYNTHETIQUES_NON_CALIBREES.json --out step24/INTERACTIONS_36_PHYSIQUES_A.json`.
