# RIZ-112 / H4A — relier des rubriques sans inventer d'effets Q

**Statut : H4A PARTIEL, 17 octobre 2026.** Suite du laboratoire H3, pas un nouveau moteur sportif ni une validation empirique.

## Ce qui fonctionne effectivement
- `003 + 061` : si un stock de sel daté et un dosage planifié sont connus avant T0, calcul de la faisabilité du dosage, du manque éventuel et de la quantité par gramme de riz sec. Si la case 061 n'était pas déclarée PLANNED, rejet.
- `049 + 082` : répartit **la masse de riz sec**, jamais la masse cuite, entre un nombre entier de portions déclaré avant T0.
- `029 + 030 + 054` : conserve l'identité de la masse sèche; si la fraction des grains cassés est observée **en masse sèche** (et non en nombre), calcule les masses par catégorie. Le rinçage planifié fournit un indice comptable d'amidon de surface `I_apres = I_avant × (1−fraction_retrait)`. Aucun lien avec la texture finale n'est appris.

## Contre-audits exécutés
La donnée `UNKNOWN` demeure inconnue; un zéro réellement mesuré est distinct. Rejet des dates sans fuseau et post-gel, unités incompatibles, fractions hors intervalle, plan non déclaré, portions fractionnaires, valeurs booléennes/infinies, incohérence des primitifs `case001`/`rice_mass_g` et `case030`/`surface_starch_index`. La fraction des grains cassés doit déclarer `basis=dry_mass_fraction`; une fraction en nombre ne peut produire une masse par simple multiplication. Les variables de qualité finales `target_contract` ne sont pas lues. Aucun champ utilisateur n'est muté.

**Preuve locale** : Python standard, `python -m unittest discover -s step15 -p 'test_h4.py' -q` depuis `labs/RIZ112/` : **29/29 PASS** (tests synthétiques locaux). Git blobs : code `4c97bdefc2b65764379cd98db6ec5e2feeb45484` et tests `726063de32e3e0bd6ab2518838ada022970b8150`, relus sur GitHub. Les 309 tests H3 sont un résultat historique et **n'ont pas été relancés dans cette session**. Les 169 tests du ZIP V1.1.2 ont été relancés séparément.

## Ce qui reste
Sur les 22 rubriques H3 non dotées d'un nouveau mécanisme quantitatif, **7 sont désormais raccordées à des diagnostics H4A**, mais **aucune ne dispose d'un effet empirique Q démontré**. Il reste **15 rubriques sans ces nouveaux diagnostics**, et les **22 liens vers Q réel** restent ouverts. `scientific_ic_percent=null` ; aucun effet ajouté à IC_DEMO, aucune validation de recette ou sécurité alimentaire.

H4B : avancer sur l'hétérogénéité thermique (018), les propriétés de variété (024), les risques opérationnels (071/077/094) et le transfert/maintien (023/081/083/084/085) selon faisabilité réelle et contrat PIT. Ne jamais chercher un changement artificiel de l'IC.

**Synchronisation** : sources + journal + checkpoint sur GitHub ; H4A non testé sur le PC Windows et non envoyé via Drive/Delivery à ce checkpoint.
