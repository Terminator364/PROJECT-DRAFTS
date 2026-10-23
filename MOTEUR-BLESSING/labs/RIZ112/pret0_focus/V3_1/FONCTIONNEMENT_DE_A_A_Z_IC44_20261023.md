# MOTEUR RIZ112 — Explication opérationnelle de A à Z (23 octobre 2026)

**Contrat A confirmé D050 / reprise `Moteur/continue`.** Le MOTEUR est un laboratoire de conception d'architecture prédictive pour **MATRICE pré-match**, pas une application de recettes. Les sorties sont **synthétiques non calibrées**, `IC scientifique = null`.

## Entrées, contrôle temporel et génération

Le générateur `RIZ112_IC44_V3_1/generate_v3.py` utilise la graine `20261023` et produit **1000 scénarios différents** répartis d'avance en cinq familles, 200 chacune : `controlled, standard, low_water, low_heat, damaged_rice`. Chaque scénario est un vecteur complet de **44 valeurs pré-T0** (R001…R042, R045, R047), soit **44000 valeurs**. Certaines sont corrélées, p. ex. foyer/source d'énergie, masse/eau, longueur/variété : ces valeurs ne sont pas 44000 tirages indépendants. **Les 37 plans d'action et 13 politiques conditionnelles supplémentaires sont gelés** et ne comptent pas parmi les 44 valeurs. Le paquet porte un instantané `freeze_utc` strictement antérieur au début fictif `start_utc`, ainsi que provenance/état/contrôles de doublons, UNKNOWN et temps.

## Chaîne numérique réelle

1. `bridge44.evaluate44` vérifie les 44 champs et leurs liens, le gel temporel, les données inconnues et la cohérence des copies.
2. `ic44.run` lit les **44 valeurs** et les fait interagir dans un bilan hydrique et thermique simplifié. Exemples de dépendances : masse (R001), eau disponible (R002), eau planifiée (R035), eau retenue pré-estimée (R036), amidon (R030), absorption (R033), évaporation (R045), couvercle (R013–R015), géométrie et matériau (R008–R011), énergie/fiabilité (R006–R007), puissance (R041), durée (R047), rendement (R042). Les entrées de planification peuvent être dormantes lorsqu'une action n'est pas prévue. Il ne s'agit pas de 44 bonus artificiels.
3. `ic44_v3.grade_physics` convertit les sorties physiques en **7 domaines** hypothétiques de qualité : hydratation **27 %**, thermique **21 %**, séparation **15 %**, intégrité **13 %**, hygiène **11 %**, goût **8 %**, service **5 %**. Elle applique des **plafonds critiques non compensatoires** en cas de sous-cuisson, manque d'eau, brûlure, contamination, etc. Le résultat est **Q* nominal /100**, pas un IC.
4. `ic44_v3.simulate` évalue une distribution d'incertitudes **définies avant T0** (dosage, puissance, évaporation, propriétés du riz, fiabilité électrique, etc.). Pour la campagne initiale, il a **128 tirages internes** par scénario, uniquement méthode numérique d'estimation. Sur chaque monde virtuel, il recalcule Q* et relève le succès `Q*>=85`; le **seul IC global du scénario** vaut `100 × succès / 128`, arrondi à trois décimales. L'IC n'est **pas** une probabilité réelle calibrée : les lois, profils et seuils sont hypothétiques. 128 est un réglage interne remplaçable.
5. `diagnostic_44_contributions.py` réalise ensuite **44 comparaisons conditionnelles** : pour chaque `j`, remplacer uniquement `x_j` par une alternative explicitée, conserver les 43 autres entrées ainsi que le modèle et la graine, recalcule l'IC global de la situation altérée, produit `delta_IC_j = IC_alt - IC_global`. **Ce ne sont pas 44 IC autonomes par paramètre**. Ils ne s'additionnent pas (interactions) et peuvent être nuls sans que le programme ait oublié de lire le champ.

## Rejeu exact du scénario archivé S0001

Entrées sélectionnées (R001…R047, 44 valeurs renseignées au total) :

| Paramètre | Valeur |
|---|---:|
| R001 masse riz | 180,35 g |
| R002 réserve eau | 546,27 mL |
| R006 énergie | électricité |
| R007 fiabilité | 0,9788 |
| R008 casserole | 2849,28 mL |
| R013 couvercle | présent |
| R024 variété | medium_white_hypothesis |
| R030 amidon surface | 0,1441 |
| R033 capacité absorption | 1,6393 g/g |
| R035 eau prévue | 306,90 g |
| R041 puissance | 541,60 W |
| R042 rendement thermique | 0,7237 |
| R045 évaporation référentielle | 2,11 g/min |
| R047 durée prévue | 19,97 min |

Le modèle `_nominal_if_power_operates` et `grade_physics` retournent **eau réellement utilisable ~306,90 g**, **eau retenue estimée ~11,85 g**, **évaporation ~31,42 g**, **eau restante ~287,33 g**, **cible d'hydratation ~283,95 g**, **hydratation ~1,012**, **Q* nominal 93,841885/100**. Les sept canaux valent (sur 100) : hydratation 100, thermique 77,47114, séparation 100, intégrité 100, hygiène 100, goût 93,54881, service 81,7808. Pas de plafond critique nominal.

En 128 variations internes avec graine `20261023*100000`, **83 réussites** Q*>=85 et **45 échecs** => `IC global = 100×83/128 = 64,84375 %, affiché 64,844 %`. Qualité moyenne des essais, pannes incluses : **85,752/100**, distincte de Q* nominal.

**Contrefactuels du même S0001** (même graine et budget numérique, autre valeur d'un seul paramètre) :

| R | Valeur alternative | IC global recalculé | Delta vs 64,844 % |
|---|---|---:|---:|
| 001 masse riz | 190 g | 65,625 % | +0,781 pt |
| 002 eau disponible | 250 mL | 33,594 % | −31,250 pts |
| 003 sel disponible | 0,6 g | 54,688 % | −10,156 pts |
| 004 matière grasse | 0 g | 64,062 % | −0,782 pt |
| 005 eau de rinçage | 90 mL | 64,844 % | 0 pt |

**Nuance des interventions :** « garder les 43 autres paramètres fixes » représente un **test mathématique de sensibilité**, pas forcément une intervention physiquement réalisable si une relation de génération est rompue. L'IC varie par pas de 0,78125 point à 128 tirages; un delta nul peut être un effet absent, saturé ou sous le seuil de résolution.

## Avancement vérifié D050

- **1000 scénarios différents × 44 valeurs** = 44000 entrées pré-T0 archivées; **1000 IC globaux historiques calculés et rejoués**.
- **44000 variations conditionnelles de Q* nominal** terminées. Elles ne sont **PAS** 44000 IC conditionnels.
- **17 scénarios × 44 = 748 véritables IC contrefactuels calculés** ; 202 deltas non nuls, 546 neutres. **43 252 IC conditionnels restent à calculer** sur 983 scénarios. Aucune continuation automatique en arrière-plan n'est revendiquée.
- Le résultat de la campagne MC contient **95 nombres d'IC distincts** pour **1000 IC individuels** (dont 798 IC=0/128). Cela traduit le choix du seuil de réussite et la faible résolution/discrimination dans les classes difficiles, **pas 798 calculs manquants**.
- **Pas de validation par cuissons réelles** : les profils de lots, lois d'incertitude, pondérations et seuil Q* sont des hypothèses qui doivent être auditées avant tout transfert méthodologique à MATRICE.

**Fichiers témoins :** `RIZ112_IC44_V3_1/generate_v3.py`, `ic44.py`, `ic44_v3.py` et `output/combined/INPUTS_1000x44.csv`, `RESULTATS_1000_IC_V3.csv` dans l'archive `RIZ112_CONTRAT_A_1000_SCENARIOS_44_PARAMETRES_20261023.zip`. Rapport D050 : `D050_CONTRAT_A_RECU_1000x44_20261023.md`.
