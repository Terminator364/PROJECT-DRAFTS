# ORIGIN-SIM R2.1 — Contre-expertise scientifique, 12 cycles

31 octobre 2026. Cible finale : Linux natif ORIGIN-3 sur Galaxy A21s SM-A217F. Cette étape est exclusivement une recherche logicielle, sans accès matériel.

## Rectification majeure

Les 107 tests R1 passaient, mais le taux de succès dépendait artificiellement du pas de temps. Sur 15 graines et 2 jours, les résultats R1 variaient de 66,7 % (1 min) à 6,7 % (60 min). Les anciens pourcentages R1 sont **invalidés comme estimation de fiabilité réelle**.

## Corrections R2.1

- Intégration interne fixe à une minute, cadence de rapport indépendante.

- Flux PRNG séparés et rejouables. Cela ne démontre pas l'indépendance physique.

- Conservation contrôlée de l'énergie (Wh), des tâches (admission/rejet/commit) et du stockage.

- Distinction secteur, port de puissance USB, USB données, Wi-Fi, Doze et service réseau réellement accessible.

- Refus de confirmer les tâches en cas de stockage épuisé; pas de promesse exactement-une-fois pour les effets externes.

- Pilotes inconnus bloquant N3; monde optimiste strictement contrefactuel.

## Essais reproduits

- Python 153/153 tests; Apollo C0 32/32; 12/12 cycles audit/contre-audit/recherche/contre-recherche/réévaluation.

- C0 SIGKILL : 120 essais, 33 tués, 87 terminaisons, 0 corruption détectée dans le banc hôte.

- 720 trajectoires de 7 jours; 5/6/8 ans; hypothèses favorables/intermédiaires/défavorables.

- Archive ZIP intégralement extraite, 153+32 tests et 12 cycles relancés avec succès.

- **Zéro boot Linux natif, zéro émulation Android/QEMU effective, zéro preuve matérielle.**

## Contre-épreuve d'incertitude

Âge virtuel 6 ans, N3 avec pilotes **supposés tous fonctionnels** : respect des règles du modèle 39/40 en conditions favorables, 32/40 intermédiaires, 0/40 défavorables. Ces fréquences sont des réponses aux coefficients supposés, **PAS** des probabilités réelles.

## Défaut persistant Apollo C0

Le moteur C0 peut évincer une tâche de fond P3 précédemment acceptée lorsqu'une tâche critique P0 arrive dans les 16 slots saturés. Test : EVICT id=1 P3; ACCEPT id=17 P0. La fiabilité exactement-une-fois reste non satisfaite. Le chiffre 796 octets décrit une structure d'état C, non la RAM totale du système.

## Décision

GO pour V&V conceptuelle et expérimentation; HOLD pour toute prédiction de fiabilité; NO-GO pour flash et certification N3. Exiger mesures physiques distinctes pour charge, PMIC, Wi-Fi, eMMC, USB, température, RAM, watchdog et restauration.

## Sources

- NASA-STD-7009B : https://standards.nasa.gov/node/263

- NIST VVUQ 2026 : https://www.nist.gov/publications/methods-uncertainty-quantification-computational-modeling-and-simulation-harmonizing

- NREL BLAST : https://docs.nrel.gov/docs/fy15osti/63246.pdf

- DTS Exynos850 A21s : https://lists.openwall.net/linux-kernel/2026/09/16/2949

- QEMU virt : https://www.qemu.org/docs/master/system/arm/virt

- Android Doze : https://developer.android.com/training/monitoring-device-state/doze-standby

- SQLite WAL : https://www.sqlite.org/wal.html

Le code complet et les rapports détaillés de R2.1 sont livrés dans une archive de cette conversation. Ce fichier GitHub ne prétend PAS synchroniser tous les fichiers. GitHub Actions : aucun déclenché.