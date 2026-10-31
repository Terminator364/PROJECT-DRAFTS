# ORIGIN-3 / APOLLO CORE — PLAN DIRECTEUR R3
31 octobre 2026 — **Destination obligatoire : Linux natif niveau 3**, et non Android optimisé comme solution finale.

## Mission et principes Apollo
Construire une machine Linux ARM64 autonome à partir du Galaxy A21s SM-A217F. La philosophie Apollo déjà validée par le propriétaire: **complexité froide principalement sur stockage**, **mémoire active strictement minimale**, **modules chargés à la demande puis libérés**. Ajouter tâches déterministes, ordonnancement prioritaire, journal durable, backpressure, reprise, watchdog, confinement, coûts énergétiques mesurés. Aucune promesse de quelques ko pour Linux entier.

## Architecture cible
L0 Matériel / Exynos 850 / eMMC / batterie / Wi-Fi / USB / watchdog.
L1 Chaîne boot/recovery du Samsung précisément cartographiée; images et sauvegardes, pas de flash aveugle.
L2 Noyau Linux adapté au téléphone avec pilotes validés.
L3 Userspace Linux minimal sans Android Framework; init, rootfs minimal, /data durable.
L4 APOLLO CORE: ordonnanceur événementiel, budgets, état, idempotence/fencing.
L5 Données froides: fichiers, SQLite WAL, checkpoints, archives, cache borné.
L6 Modules: réseau, indexation, bibliothèque, automatisation, sauvegarde; chargement à la demande.
L7 Console web locale/texte, authentification, aucun port public par défaut.
L8 Sécurité et résilience: journal, mesure énergie/RAM, secours, mises à jour, rollback démontré.

## Parcours cumulatif (jamais 3 options interchangeables)
**P0 / Étude préalable / G0:** identifier exact modèle, bootloader/Knox, batterie, RAM, partitions, kernel, firmware, récupération, sauvegarde restaurable; tableau sources et risques. Aucune modification destructrice.

**N1 / P1 / Laboratoire Android / G1:** construire les couches portables L4-L8; moteur jobs, scheduling prioritaire, storage froid, governors, superviseur, UI/API; tests locaux, chaos et Android Termux. Vérifier veille/Doze, pertes réseau, crash, stockage plein, reprise. Android = échafaudage, pas produit final. Gate: persistance et ressources mesurées sur téléphone, modules OS-agnostiques.

**N2 / P2 / Laboratoire kernel et matériel / G2:** explorer éventuellement LineageOS (sans flash prématuré), cartographier boot/recovery/partitions; préparer toolchain ARM64, build Linux, initramfs, kernel vendor et kernel mainline, device tree, drivers, sauvegarde/rollback. Tableau PILOTE pour boot, MMC, batterie/charge, thermique, réseau/Wi-Fi, USB, affichage console, boutons, veille/suspend, watchdog. Gate: preuve d'une image de test viable et secours; aucun flash sans décision spécifique et données sauvées.

**N3 / P3 / Linux autonome / G3:** deux voies étudiées en parallèle: **L3-V** kernel Linux vendor Samsung conservant drivers + userspace Linux sans Android Framework (prioritaire), **L3-M** noyau Linux mainline + device tree Exynos850/A21s (expérimental). N3 n'est atteint que par boot réel Linux, stockage fiable, contrôle batterie/température, réseau, USB, services APOLLO CORE et restauration démontrée. Ordre de bring-up: console → stockage → récupération → énergie → Wi-Fi → USB → veille → services. 24 h, 7 jours, 30 jours de mesures avant qualification. Si driver essentiel bloquant, statut bloqué et jamais « fini ».

**P4 / Release / G4:** image reproducible, provenance, licences, SBOM, signatures/hashes, sauvegarde et restauration, procédures de maintenance, sécurité noyau, logs, stabilité prolongée. Livrable = machine autonome maintenable, pas installation expérimentale.

## Contraintes acceptation et priorités
S0 intégrité et énergie; S1 contrôle local; S2 services vitaux; S3 requêtes interactives; S4 indexation/IA. Sous pression, S4 cède en premier. Un traitement lourd simultané; cache et files bornés; zéro WAN par défaut; récupération indépendante des services non essentiels.

Budgets **provisoires non mesurés**: 128 MiB RSS cible pour les propres démons inactifs (hors noyau), ~256 MiB actifs légers, ≤512 MiB durant indexation ordinaire, plafond paramétrable pour tâches non critiques. Ces budgets doivent être calibrés sur le vrai téléphone; ne pas les présenter comme performances acquises.

## Tests gates
T01 premier boot; T02 restart; T03 perte processus; T04 mort superviseur; T05 saturation jobs; T06 stockage plein; T07 récupération SQLite; T08 stale worker; T09 réseau absent; T10 reconnexion Wi-Fi; T11 WAN absent; T12 batterie faible; T13 chauffe; T14 mémoire saturée; T15 suspend/resume; T16 câble USB; T17 panne update; T18 rollback; T19 restauration sauvegarde; T20 tests prolongés. Un banc simulé ne remplace jamais un test matériel.

## Gouvernance de construction
Rôles d'analyse: direction, boot/kernel, core, hardware/énergie, sécurité, QA/chaos, UX. Pour chaque lot: SPEC → IMPLEMENT → TEST → AUDIT → CONTRE-AUDIT → FAILURE-INJECT → READBACK → RECEIPT. Cahier mère append-only, preuves, rapports de tests et anomalies. Échéancier par **gates techniques**, pas dates fictives.

## Compatibilité et vérité des preuves
- LineageOS officiel a21s: https://github.com/LineageOS/lineage_wiki/blob/main/_data/devices/a21s.yml : branche 23.2, noyau vendor 4.19; exige vérification du firmware Samsung et de la variante.
- Patch Linux mainline initial: https://lists.openwall.net/linux-kernel/2026/09/16/2949 : SimpleFB, boutons, 3 Go RAM par défaut, ramoops, GPU déclaré, MMC, USB, watchdog; aucune démonstration de Wi-Fi/charge complète.
- Termux:Boot https://github.com/termux/termux-boot ; Android Doze https://developer.android.com/training/monitoring-device-state/doze-standby

## Dossiers détaillés
Le plan détaillé complet est maintenu dans le livrable associé `PLAN_DIRECTEUR_ORIGIN3_APOLLO_R3_20261031.md` de cette session; ce fichier GitHub en est le document de coordination.
**État 31/10/2026**: N1 en laboratoire logiciel; N2 recherches; N3 **non construit, non installé**. Aucune mise à jour Android, root ou flash effectuée.
