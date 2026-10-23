# MOTEUR RIZ112 / IC44 V3.1 — Nouveau moteur et campagne 1000×44

**But canonique :** laboratoire de méthodologie pour MATRICE exclusivement pré-match. Code de reprise : Moteur/continue. Les données observées après la préparation ne sont jamais utilisées comme entrées.

## État vérifié le 23 octobre 2026

Le nouveau noyau IC44 V3.1 est enregistré dans pret0_focus/V3_1/ic44_v3.py, Git blob 5cd774f2ede8c43569e2ce32437ba760381a0e1f. Ses dépendances et scripts/tests se trouvent dans le package reproductible Drive ci-dessous.

Le moteur reçoit les 44 paramètres pré-préparation R001–R042, R045 et R047. Il modélise des interactions hydriques, thermiques, de texture, d'intégrité, de faisabilité et de protocole. Q*/100 est une note de qualité hypothétique avec sept dimensions et des limites pour les défauts critiques. IC* modèle (%) représente la proportion des tirages Monte Carlo atteignant Q* ≥85. Ce n'est PAS une probabilité réelle calibrée.

**Campagne exécutée :** 1 000 mondes de 44 entrées = 44 000 valeurs synthétiques et 128 000 préparations fictives Monte Carlo (128 répétitions par monde), graine 20261023. Échantillon STRATIFIÉ AVANT résultat, cinq régimes de 200 chacun : maîtrisé, ordinaire, eau insuffisante, chauffe faible, grains dégradés. Distribution IC modèle : 0 à **95,312 %** ; sous10=843 ; 10–<40=42 ; 40–<70=53 ; 70–<85=41 ; ≥85=21. Cette distribution volontairement difficile ne décrit pas les cuisines réelles.

**44/44 chemins démontrés :** pour chacun des 44 paramètres, un contrefactuel à une seule variable, dans un contexte applicable et avec la même graine aléatoire, a effectivement modifié IC*. Une influence peut rester nulle hors contexte ; aucune variation artificielle de score n'est ajoutée. R007 représente le risque de panne de la source d'énergie ; on ne pénalise pas deux fois la puissance quand la source fonctionne.

**15/15 tests locaux Python PASS** : 44 entrées strictement datées avant T0, absence de fuite post-départ, UNKNOWN => ABSTAIN, simulations reproductibles, IC compris entre 0 et 100, scène favorable IC >80, scène dégradée, facteur énergétique, 44 témoins, intervalles Wilson MC. Les dix anciens scénarios A–J et leurs 440 valeurs restent intacts ; leurs résultats V3 ont été recalculés, non leurs entrées.

Scénario contrôlé K : Q* nominal, si la source fonctionne, 99,166/100 ; IC* modèle 85,059 % avec 1 024 tirages ; intervalle MC Wilson [82,744 ; 87,111]. Le scénario M réduit la fiabilité de la source : qualité nominale conditionnelle inchangée mais IC* ~39,16 %. Il s'agit de scénarios FICTIFS.

Le modèle V2 défectueux (plafond mathématique d'IC ~60,77 %) est conservé comme témoin, ainsi que les anciennes 1000×112 simulations. IC scientifique = null, aucune observation réelle, aucun score Brier empirique ni calibration. Ne pas transférer les coefficients de cuisson vers le football.

## Artefacts et preuves

- Package complet ZIP (30 fichiers, code, 1000x44 entrées, 1000 IC et sensibilité, tests, manifeste SHA, XLSX) : https://drive.google.com/file/d/1RnLc0cQNfRtwSznlyq77vNyI0LE5cbHY/view?usp=drivesdk
- Sources Python seules : https://drive.google.com/file/d/1QLM19XjweJVq8xA9Apv0qoxCmY8C1Po9/view?usp=drivesdk
- SHA256 package complet : f28dcf6067695a77e19417727d41241b7650d2b67792edf37160549fed665047 ; taille 514606 octets.
- Fichier INPUTS_1000x44.csv dans ZIP : 1000 scénarios et 44 paramètres. RESULTATS_1000_IC_V3.csv : 1000 Q* et IC*. TEMOINS_INFLUENCE_44_SUR_IC.csv : 44 preuves d'influence sur IC.

La structure des mécanismes s'inspire des études sur diffusion hydrique et gélatinisation, effet de l'eau sur texture, temps/température de cuisson. Cela ne valide aucun coefficient du modèle : https://www.sciencedirect.com/science/article/pii/S026087741400209X ; https://www.cerealsgrains.org/publications/cc/2007/November/Pages/84_6_614.aspx ; https://pubmed.ncbi.nlm.nih.gov/29792958/ . Pour l'étalonnage des probabilités : https://stat.uw.edu/research/tech-reports/probabilistic-forecasts-calibration-and-sharpness

## Continuité

Le Cahier mère documente **tout MOTEUR**, pas seulement les risques. À Moteur/continue, lire d'abord CAHIER_MERE.md, CHECKPOINT.json, DECISIONS.md, le présent reçu et les données V3.1 ; ne pas recommencer la campagne. Suite : contre-audit des hypothèses Q* et incertitudes, puis transfert de MÉTHODE vers MATRICE avec données pré-match et résultats réels post-match. Les commits Git sont journalisables automatiquement ; les messages privés ChatGPT nécessitent une inscription explicite pendant la séance.
