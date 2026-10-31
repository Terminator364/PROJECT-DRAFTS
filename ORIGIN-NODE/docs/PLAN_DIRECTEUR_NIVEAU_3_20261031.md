# ORIGIN OS — PLAN DIRECTEUR NIVEAU 3 (31 octobre 2026)

> **Destination :** transformer le Galaxy A21s SM-A217F (Exynos 850, 4 Go dans le dossier matériel) en une **appliance autonome Linux ARM64 native**, hors ligne, pilotée par un petit exécutif C « Apollo », avec reprise des tâches, contrôle des ressources et services chargés à la demande.
>
> **Contrainte de vérité :** aucun boot Linux natif ni changement de firmware n'a été validé physiquement sur le Samsung lors de cette livraison. Les tests de laboratoire ne valent pas recette matérielle.

## Le concept final avant toute opération

ORIGIN n'est pas une application Termux améliorée. Termux est uniquement une plate-forme de test du runtime. Le niveau 3 comprend : chaîne de boot vérifiée du Samsung → kernel Linux ARM64 et DTS SM-A217F → initramfs diagnostic → rootfs minimal lecture seule → init/superviseur système → exécutif C0 peu gourmand → modules C1..C7 à la demande → état persistant/sauvegardes → console locale authentifiée (Wi-Fi ou USB seulement si pilotes validés).

**Périmètre personnalisé :** ordinateur personnel autonome pour recherche/documentation médicale hors ligne, automatisations, laboratoire IA légère, relais LAN privé et stockage — usages optionnels indépendants. Le téléphone ne doit dépendre d'aucun ancien projet applicatif. Il doit rester utile avec Internet coupé, données mobiles désactivées et PC éteint.

### Les six lois Apollo adaptées

1. Stockage abondant et mémoire vive active strictement limitée : le code, les bases et les documents restent sur eMMC.
2. Priorités P0/P1/P2/P3 : P0 sécurité/intégrité, P1 contrôle/récupération, P2 service utile, P3 tâche facultative. Dégrader P3 avant P2.
3. Allocation statique et files bornées dans C0 ; aucun travail lourd dans le chemin chaud.
4. Journal/checkpoint/recovery ; idempotence ou réconciliation pour chaque effet externe.
5. Modularité : C0 orchestrateur ; C1 documents ; C2 rendu ; C3 réseau ; C4 capteurs/énergie ; C5 indexation ; C6 console/API ; C7 sauvegardes.
6. En cas de surcharge ou capteur suspect : mode dégradé conservant l'intégrité, pas de course aux performances.

La NASA documente un exécutif avec ordonnancement par priorité et suppression de tâches de faible priorité lors des alarmes Apollo 11 1201/1202. La comparaison porte sur le **modèle de décision**, pas sur la taille totale d'un Linux moderne.
Sources : https://nasa.gov/wp-content/uploads/static/history/alsj/a11/a11.1201-fm.html

## Trois niveaux, un seul objectif

### N1 — Etablir la vérité matérielle (A-H)
| Lot | Travail et livrable | Critère de passage |
|---|---|---|
| **A** | Inventaire ADB lecture seule : modèle/variante, firmware, patch, RAM, ABI, stockage | modèle confirmé, rapport anonymisé |
| **B** | Santé batterie, charge, chaleur, écran/ports, chargeur et câble | appareil physiquement sain |
| **C** | Sauvegardes indépendantes, inventaire des partitions, restauration d'un échantillon | restauration prouvée |
| **D** | Cartographie boot/recovery/download/verified boot/Knox | procédure de retour documentée, pas de flash |
| **E** | Bancs CPU/IO/SQLite/scheduler C, profils réseau et corruption | tests reproductibles |
| **F** | Mesures écran éteint, autonomie, Wi-Fi, pertes réseau, température et mémoire | traces brutes datées |
| **G** | Même C0 sur Android stock sans root, comme banc, jamais comme destination | reprises, restrictions Doze et quotas |
| **H** | Comité de revue N1, blocages, sécurité, risques | GO vers N2 documenté |

### N2 — Construire le véritable logiciel de niveau 3 (I-Q)
| Lot | Travail et livrable | Critère de passage |
|---|---|---|
| **I** | C0 : priorités, slots fixes, messages de taille bornée | mémoire / surcharge mesurées |
| **J** | Etat durable : journal append-only, CRC, snapshots, acquittement après fsync | reprise cohérente + test corruptions |
| **K** | Modules C1..C7 séparés par processus/permissions, chargement sur demande | aucun module ne bloque P0 |
| **L** | Politique énergie/data : profils offline, batterie, secteur, réseau limité | tests scénarios |
| **M** | Toolchain ARM64 + rootfs BusyBox/musl ou Alpine, initramfs, init | image reproductible + boot émulateur compatible |
| **N** | Comparaison ROM stock/LineageOS officielle comme outil de qualification | coûts/Knox/documentation complets |
| **O** | Modèle de menace, authentification, chiffrement, signatures, mises à jour | audit sécurité réussi |
| **P** | Chaos : SIGKILL, disk-full, partitions corrompues, coupures, saturation, rollback | journal des FAIL/PASS/retests |
| **Q** | Candidate L3 intégrée et dossier de retour arrière | GO uniquement si chemin de boot réel identifié |

**N2 n'est pas obligatoirement un flash root ou une ROM définitive**. La ROM alternative peut servir de matériel d'essai ; toute l'ingénierie prépare le boot natif de N3.

### N3 — Faire tourner ORIGIN à la place d'Android (R-Z)
| Lot | Travail et livrable | Critère de passage |
|---|---|---|
| **R** | Étude et démonstration d'une chaîne de boot A21s réellement récupérable | aucune opération risquant brick sans recovery prouvée |
| **S** | Linux ARM64 natif + DTS du SM-A217F, prise en charge RAM 4 Go/horloges | logs de démarrage réels sans corruption |
| **T** | Initramfs et rootfs indépendant d'Android, console secours | Linux démarre seul, sans Android |
| **U** | Alimentation, charge, température, stockage, USB et transport local | pilotes vitaux testés physiquement |
| **V** | Supervision native de C0, watchdog, quotas, reprise | tests kill/reboot/restart sur appareil |
| **W** | Journal, snapshots, stockage sécurisé et restauration | reprise après interruption physique contrôlée |
| **X** | Console/API locale sécurisée (Wi-Fi ou USB si démontré) | aucun service Internet entrant |
| **Y** | Qualification 7/14/30 jours : dérive mémoire, chauffe, autonomie, débit, stabilité | rapport réel avec preuves |
| **Z** | Remise de clé : image figée, manifeste, SHA256, licences, sauvegarde/recovery, manuel | L3-PRODUCTION déclaré seulement après recette |

## Architecture mémoire — valeurs-cibles, pas de résultats obtenus

- État statique C0 : **<=64 KiB** dans le logiciel final, avec objectif expérimental plus faible.
- RSS C0 : **<=8 MiB** à vide sur ARM64 après mesure.
- OS headless : objectif de départ **<=256 MiB** de mémoire active utilisateur au repos, à recalibrer.
- Modules lourds : **1 à la fois par défaut** ; stockage/eMMC et RAM surveillés.
- P0 et P1 ne doivent pas être confiés à une application Android susceptible d'être tuée : en N3, supervision Linux native.
- **Linux entier ne peut pas tenir dans quelques kilo-octets.** Apollo inspire l'orchestration et le chargement, non une promesse impossible de RAM totale.

## Trois niveaux de preuve L3

- **L3-BOOT :** noyau natif lancé + console/logs.
- **L3-CORE :** rootfs + C0 + state + récupération + stockage + supervision réellement fonctionnels.
- **L3-PRODUCTION :** L3-CORE + charge/thermique sûres, administration locale, mises à jour/retour arrière, endurance et sécurité vérifiées.
**Le projet vise L3-PRODUCTION.**

## Risques dominants et interdictions

1. La prise en charge du Galaxy A21s en Linux mainline est **initiale** (patch du 18 septembre 2026) : SimpleFB, boutons, 3 Go configurés par défaut, ramoops, GPU déclaré, MMC, USB, watchdog. **Cela ne démontre ni Wi-Fi, ni charge, ni modem, ni veille profonde.** La déclaration 3 Go impose une adaptation et des tests pour la variante 4 Go.
2. Aucun conseil générique pour flasher Samsung sans correspondance de modèle/firmware/bootloader et preuve de restauration. Knox peut devenir irréversiblement affecté.
3. La batterie non amovible et âgée interdit de prétendre à une sécurité 24/7 sans inspection et tests.
4. Pas de secrets/tokens/données de santé privées dans le dépôt public ; pas de port Internet entrant ; aucun tunnel ou accès tiers non autorisé.
5. GitHub Actions : 0 minute par défaut, aucune CI automatique, conformément au `AGENTS.md` racine.
6. Aucun appareil n'a été modifié ni branché dans cette livraison.

## Registres de validation obligatoires

- **BM01** taille binaire/état C0 + RSS réel ARM64.
- **BM02** P0/P1 sous surcharges P3 ; rejet explicite et accusés de réception durables.
- **BM03** récupération de 1 000 crashs simulés ; effets externes réconciliés.
- **BM04** coupures physiques surveillées sans corruption après qualification batterie.
- **BM05** usure eMMC, quota journal, taille snapshots.
- **BM06** politique offline/data ; zéro trafic mobile imprévu.
- **BM07** sécurité et authentification, ports exposés.
- **BM08** boot natif + device-tree mémoire correct.
- **BM09** surveillance batterie/température/charge et arrêt conservateur.
- **BM10** restauration firmware et secours.
- **BM11** endurance réelle 7/14/30 jours.
- **BM12** performance sous charge utile et qualité des modules optionnels.

Chaque banc doit conserver machine, version exacte, protocole, trace, résultat, cause, correction et contre-test. La simulation n'est jamais une preuve matérielle.

## Exécution parallèle et dépendances
- **Matériel :** A→B→C→D→H→R→S→U→Y→Z.
- **Apollo :** E→I→J→K→L→P→Q→V→W→Y→Z.
- **Linux :** E→M→O→Q→R→S→T→V→Y→Z.
- **Usages :** K→modules→X→Y→Z.

Le logiciel N3 doit être construit **dès maintenant** hors téléphone, mais aucune installation dangereuse n'est autorisée sans les preuves des lots A–D. Si le noyau Linux natif ne fournit pas transport local + sécurité de charge, le niveau 3 reste **bloqué** : Android/LineageOS peut être un système de travail, sans être abusivement déclaré N3.

## Faits techniques / liens
- Galaxy A21s officiel LineageOS : https://github.com/LineageOS/lineage_wiki/blob/main/_data/devices/a21s.yml
- Patch initial Linux mainline : https://lists.openwall.net/linux-kernel/2026/09/16/2949
- Acceptation du 18 septembre : https://lists.openwall.net/linux-kernel/2026/09/18/1455
- Apollo NASA : https://nasa.gov/wp-content/uploads/static/history/alsj/a11/a11.1201-fm.html
- Exynos850 mainline : https://github.com/exynos850-mainline
- Termux : https://github.com/termux/termux-app

## Statut
**PLAN DEFINI / N1 PARTIEL EN LABO / N2 C0 PROTOTYPE EN LABO / N3 NON DEMONTRE.**
Les fichiers de recherche déjà présents dans `ORIGIN-NODE/` sur cette branche restent intacts et conservent leurs essais Python v0.2. La branche de travail n'est pas fusionnée dans main.
