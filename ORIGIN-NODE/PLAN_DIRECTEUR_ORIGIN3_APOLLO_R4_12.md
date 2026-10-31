# ORIGIN-3 / APOLLO CORE — PLAN DIRECTEUR R4.12

**31 octobre 2026 · Version de référence après 12 contre-audits structurés · Destination : Linux natif (niveau 3)**



> Ce plan est un contrat d'ingénierie conditionnel, pas une promesse de réussite matérielle. Les 12 cycles ci-dessous sont des revues logiques/systèmes, pas 12 essais sur le téléphone ni 12 équipes autonomes indépendantes.

## A. Définition concrète du résultat final

ORIGIN-3 est un système Linux ARM64 démarrant **réellement** sur le Samsung SM-A217F, avec PID1 et rootfs Linux natifs, **sans Android Framework en cours d'exécution**, et avec des services exécutés sous des budgets stricts de mémoire, d'énergie et de stockage. L'usage de firmware bas niveau propriétaire peut subsister, documenté; il ne sera pas présenté comme un système 100% libre.

Le produit final dispose : d'un démarrage reproductible, d'une méthode de récupération vérifiée, d'un stockage transactionnel, d'un réseau Wi-Fi local, de l'USB, d'une mesure batterie/charge/température fiable, d'une console de contrôle sécurisée, d'un ordonnanceur de modules froids, et d'une maintenance réaliste. Caméra, téléphonie et accélération GPU sont facultatives tant que le cahier des besoins ne les rend pas indispensables.

**Définition stricte de « niveau 3 atteint »** : V+W+X vérifiés sur l'appareil; **« programme livré »** : Y+Z après endurance et restauration. Aucun pourcentage de code n'équivaut à ce résultat.

## B. Principes APOLLO, avec limites physiques

1. **Complexité froide** : index, bibliothèques, composants métier et modèles restent stockés, non résidents en RAM; activation ponctuelle par besoin.

2. **Minimum actif** : S0 énergie/sécurité, S1 récupération, S2 contrôle, S3 interactions, S4 travaux lourds. Préemption/suspension de S4 si ressources insuffisantes; journaliser toute décision.

3. **Phases de reprise** : idempotence, checkpoints et fencing avant de relancer un traitement. Ne jamais promettre exactly-once pour les effets externes.

4. **Systèmes séparés** : APOLLO CORE portable (L4-L8) d'un côté, noyau/vendor + noyau mainline et HAL matériel de l'autre.

5. **Budget mesuré** : cible d'essai pour propres démons inactifs ≈128 MiB RSS, modules légers ≈256 MiB, travaux ordinaires ≈512 MiB; ces nombres sont des hypothèses à mesurer, pas une capacité acquise du Samsung.

6. **Périmètre clair** : la sobriété d'Apollo ne signifie pas fabriquer Linux en kilo-octets. Priorité à la mesure RSS/PSS, latence, énergie, endurance, récupération.

L'AGC Apollo utilisait un Executive prioritaire et une reprise par phases lors de surcharges. Nous reproduisons les propriétés, pas son matériel ni son logiciel historique.

## C. Chemin critique, niveaux et travaux parallèles

**N0 — préalables** : A→B/C/D + E. **N1 — laboratoire Android** : F→G/H/I→J/K/L→M→N. **N2 — transition kernel** : O, P+Q en parallèle, R, S et T, puis U. **N3 — Linux natif** : V→W→X→Y→Z.

L'étude P/Q commence avant N1 terminé si elle est sans danger, mais U exige la qualification N1 réelle et toutes les sauvegardes. Les dates ne prévalent jamais sur les critères matériels.

**Arbitrage V/M** : voie V = noyau Samsung downstream 4.19 + userspace Linux sans Android; voie M = kernel Linux principal + device tree A21s. Une seule peut devenir image de référence; l'autre reste recherche. La voie V n'est PAS garantie, car des drivers/HAL peuvent dépendre d'Android. La voie M n'est PAS garantie car Wi-Fi/charge/suspend ne sont pas prouvés.

## D. Travaux de A à Z : contenu, preuves, secours et dépendances

### A — Identité et patrimoine matériel (P0)

**Responsable :** Matériel. **État initial :** NON_COMMENCE. **Dépend de :** aucune.

**Construction :** Inventaire lecture seule : SM-A217F variante exacte, RAM effective, stockage, état du chargeur, santé batterie, version Android/bootloader; exclusions IMEI, MAC et secrets.

**Preuve de fin :** Rapport signé par hachage, valeurs relevées sur appareil; comparaison à 2 sources matérielles.

**Si échec :** Sans appareil: BLOQUE inventaire physique; aucune identité déduite d'une ancienne fiche.

### B — Sauvegarde réellement restaurable (P0)

**Responsable :** Données. **État initial :** NON_COMMENCE. **Dépend de :** A.

**Construction :** Sauver données personnelles, état logiciel, fichiers de service; inventaire des partitions possibles sans affirmer un dump bootloader intégral.

**Preuve de fin :** Restaurer un échantillon sur support distinct, vérifier checksums et consigner les données non sauvegardables.

**Si échec :** Si backup impossible: STOP flash et modifier le périmètre de test.

### C — Chaîne d'amorçage et partitions (P0)

**Responsable :** Boot. **État initial :** NON_COMMENCE. **Dépend de :** A.

**Construction :** Relever modes Samsung Download/recovery, partitions boot/vbmeta/vendor/system, déverrouillage; documenter image originale et procédure opérateur.

**Preuve de fin :** Carte bootloader, risque Knox, stratégie réelle de récupération vérifiée sans altérer le téléphone.

**Si échec :** Pas de supposition fastboot ou partitions A/B; plan conditionnel par matériel.

### D — Risque énergétique et santé matérielle (P0)

**Responsable :** Énergie. **État initial :** NON_COMMENCE. **Dépend de :** A.

**Construction :** Mesurer chauffe, charge USB, batterie usée, comportement Wi-Fi, état alimentation et conséquences des coupures.

**Preuve de fin :** Décision batterie sûre/inconnue/dangereuse et limites d'essai signées.

**Si échec :** Batterie gonflée/abîmée ou charge non sûre : HALT essais autonomes non supervisés.

### E — Registre des sources et licences (P0)

**Responsable :** Recherche. **État initial :** RECHERCHE. **Dépend de :** aucune.

**Construction :** Classer sources Samsung, LineageOS, Linux device tree, pilotes, Buildroot, postmarketOS, U-Boot, Knox; licences, dates, compatibilité.

**Preuve de fin :** Chaque affirmation critique porte source, statut vérifié/proposé/supposé et date; pas de mélange entre variantes.

**Si échec :** Si preuves contradictoires: ticket et arbitre, pas d'affirmation ferme.

### F — Contrat du système portable (N1)

**Responsable :** Architecture. **État initial :** NON_COMMENCE. **Dépend de :** E.

**Construction :** API stable OS-agnostique jobs, observabilité, configuration, stockage, temps monotone, communication; interfaces HAL abstraites.

**Preuve de fin :** Maquette exécutable sans appels Android obligatoires dans le cœur; versionnement schéma et API.

**Si échec :** Adapter façade Android, ne pas bifurquer logique métier.

### G — APOLLO Executive à priorités (N1)

**Responsable :** Exécution. **État initial :** RECHERCHE. **Dépend de :** F.

**Construction :** Ordonnancement S0 sécurité/énergie, S1 récupération, S2 contrôle, S3 interactif, S4 indexation/IA; files bornées.

**Preuve de fin :** Tests starvation, surcharge, famine priorités, deadlines, dégradation contrôlée, aucune tâche S4 bloquant S0.

**Si échec :** Quand capacité insuffisante: rejeter, décaler, reprendre; jamais ignorer silencieusement.

### H — Mémoire froide et modules intermittents (N1)

**Responsable :** Mémoire. **État initial :** RECHERCHE. **Dépend de :** F, G.

**Construction :** Catalogue modules sur stockage; un module lourd actif; lecture streaming, cache plafonné, charge/travail/checkpoint/libération.

**Preuve de fin :** Mesure RSS/PSS par module, heap et fuite sur 1 000 cycles; tests seuils sur ARM64.

**Si échec :** Adapter langage et compilation native si Python devient trop coûteux.

### I — Transactions et journal de reprise (N1)

**Responsable :** Données. **État initial :** RECHERCHE. **Dépend de :** F.

**Construction :** SQLite+outbox, idempotence, fencing, fsync, snapshots, sauvegarde hors téléphone, séparation état critique / cache.

**Preuve de fin :** Crash tests multiples, restauration contrôlée, preuve que les tâches validées survivent selon contrat de durabilité.

**Si échec :** Si stockage défectueux: lecture seule et récupération, jamais réécriture agressive.

### J — Gouverneur RAM/CPU/énergie/réseau (N1)

**Responsable :** Ressources. **État initial :** NON_COMMENCE. **Dépend de :** G, H.

**Construction :** Budgets hypothétiques mesurés : RSS services, CPU duty-cycle, RAM libre, espace eMMC, température, data mobile.

**Preuve de fin :** Tests limites/dégradation, lecture capteurs, états UNKNOWN traités prudemment; pas de régulation matérielle imaginaire.

**Si échec :** Seuils ajustés après mesures et contre-audit énergétique.

### K — Superviseur hiérarchique et boot temporaire (N1)

**Responsable :** Fiabilité. **État initial :** RECHERCHE. **Dépend de :** G, I.

**Construction :** Runit/Termux:Boot ou service natif de labo; supervision avec verrou crash-safe et détection de redémarrage.

**Preuve de fin :** Crash process, kill superviseur, reboot, Doze, standby: résultat réel journalisé sans promesse 24/7.

**Si échec :** Si OS supprime superviseur, l'événement nourrit N2; pas présenté comme service permanent.

### L — API sécurisée et interface minimale (N1)

**Responsable :** Sécurité. **État initial :** NON_COMMENCE. **Dépend de :** F, I.

**Construction :** Console offline-first localhost, contrôle d'accès, token rotatif, absence de shell arbitraire, journaux redigés.

**Preuve de fin :** Tests auth, injection, frontières de permissions, refus explicite d'accès internet.

**Si échec :** Aucune écoute 0.0.0.0 ni secrets sur dépôt public.

### M — Banc portable / tests adversariaux (N1)

**Responsable :** QA. **État initial :** RECHERCHE. **Dépend de :** G, H, I, J, K, L.

**Construction :** Tests unitaires, propriétés, fuzz ciblé, coupure à points de commit, saturation, thermique simulé, backpressure.

**Preuve de fin :** Matrice exigences↔tests; preuve indépendante et reproductible, chronométrage/RSS annotés par machine.

**Si échec :** Refus de convertir un test x86 en validation téléphone.

### N — Qualification Android réelle (N1)

**Responsable :** Terrain. **État initial :** NON_COMMENCE. **Dépend de :** A, B, D, M.

**Construction :** Termux ou APK laboratoire réversible; épreuves Wi-Fi veille 1/4/12/24h, coupure, charge, stockage, collecte des métriques.

**Preuve de fin :** Rapport équipement signé, logs de boot/reboot, autonomie, défaillances et correction; G1 atteint.

**Si échec :** Si téléphone indisponible: statut BLOQUE et poursuite N2 hors appareil.

### O — Atelier de compilation ARM64 (N2)

**Responsable :** Build. **État initial :** NON_COMMENCE. **Dépend de :** E, F.

**Construction :** Cross-compile C/Rust/Python AArch64, Buildroot rootfs minimal, QEMU ARM64 pour services seulement; SBOM.

**Preuve de fin :** Compilations hors Android, tests ELF ABI, reproductibilité hashes et logs; limite PC 4 Go vérifiée.

**Si échec :** Construire par paquets/caches; ne pas déclencher GitHub Actions automatiques.

### P — Voie V : noyau Samsung dérivé (N2)

**Responsable :** Kernel vendor. **État initial :** RECHERCHE. **Dépend de :** C, E, O.

**Construction :** Étudier kernel 4.19, drivers firmware, SELinux, dtbo, ramdisk, dépendances Android; patcher sans supposer compatibilité userspace non-Android.

**Preuve de fin :** Build artefact sur hôte, matrice des drivers essentiels et limites du noyau ancien.

**Si échec :** Si pilotes Android spécifiques à l'espace utilisateur: ports/shims isolés ou pause V.

### Q — Voie M : Linux mainline (N2)

**Responsable :** Kernel mainline. **État initial :** RECHERCHE. **Dépend de :** C, E, O.

**Construction :** Suivre exynos850-a217f.dts 2026, 3 Go RAM déclaré, patchsets, PMIC/charge, wifi/firmware, USB, boot.

**Preuve de fin :** Compile dtbs/checks; divergences 3/4 Go consignées, statut chaque pilote prouvé.

**Si échec :** Jamais emprunter les images A13/A12 comme compatibles A21s.

### R — Matrice des pilotes et firmware (N2)

**Responsable :** Bring-up. **État initial :** NON_COMMENCE. **Dépend de :** P, Q, D.

**Construction :** Comparer V/M: DRAM 4Go, MMC, regulators, PMIC/charge, thermiques, wifi, USB, framebuffer, veille, watchdog, RTC.

**Preuve de fin :** Chaque ligne = source, état code, état boot, état terrain, propriétaire, criticité, recours; essentiels tous TESTES avant G3.

**Si échec :** Réseau et énergie non validés = blocage G3; écran sophistiqué et caméra optionnels.

### S — Plan d'essai boot et récupération (N2)

**Responsable :** Boot. **État initial :** NON_COMMENCE. **Dépend de :** B, C, D, R.

**Construction :** Périmètre des partitions préservées, image originale vérifiée, voie de récupération Download/recovery, avertissement Knox, action opérateur explicite.

**Preuve de fin :** Test de restauration réaliste; aucune opération irréversible sans décision explicite et risques acceptés.

**Si échec :** Pas de recette générique fastboot/Odin hors variante vérifiée; conserver la voie de secours.

### T — Rootfs Linux et PID1 (N2)

**Responsable :** Userspace. **État initial :** NON_COMMENCE. **Dépend de :** O, F, I.

**Construction :** Buildroot/BusyBox (ou équivalent motivé), initramfs minimal, init/PID1, configuration fichiers système, services ORIGIN natifs.

**Preuve de fin :** Démarrage VM/test initramfs sur hôte émulateur, shell debug, fsck, service start/stop, logs.

**Si échec :** Userspace sans Android Framework ni APK, tout en acceptant firmware propriétaire si indispensable.

### U — Essais de démarrage prudents (N2)

**Responsable :** Qualification HW. **État initial :** NON_COMMENCE. **Dépend de :** N, P, Q, R, S, T.

**Construction :** Séquence host tests → boot à risque maîtrisé après autorisation → shell/console → eMMC → USB → radio/énergie; révisions réversibles.

**Preuve de fin :** Journal boot avec image précise et hachage; mode récupération opérationnel; aucune mise en production.

**Si échec :** Si boot ou restauration non prouvé: N2 BLOQUE, itérer patchsets, pas de flash à l'aveugle.

### V — Premier boot Linux autonome (N3)

**Responsable :** Linux. **État initial :** NON_COMMENCE. **Dépend de :** U.

**Construction :** Lancement d'un Linux natif sur SM-A217F (noyau V ou M), PID1, rootfs, shell/console, sans Android Framework actif.

**Preuve de fin :** Boot attesté par logs uname/PID1/mounts et version image; reboot reproductible.

**Si échec :** Sans preuve sur appareil: N3 NON ATTEINT même si QEMU fonctionne.

### W — Fonctions matérielles essentielles (N3)

**Responsable :** Matériel. **État initial :** NON_COMMENCE. **Dépend de :** V, R.

**Construction :** Pilotes fiables batterie/charge/thermique, wifi/USB, stockage et wear, watchdog, RAM 4Go, RTC et éveil.

**Preuve de fin :** Matrice PASS sur appareil pour énergie, wifi, stockage, recovery, RAM; absence de chauffe dangereuse.

**Si échec :** Si un P0 matériel manque: N3-BLOQUE, choisir V↔M/porter driver ou escalade.

### X — Intégration APOLLO CORE native (N3)

**Responsable :** Intégration. **État initial :** NON_COMMENCE. **Dépend de :** V, W, M.

**Construction :** Services sans Android, modules intermittents, authentification LAN local, sécurisation OS, isolation UID, chiffrement si faisable.

**Preuve de fin :** Boot autonome des fonctions S0-S3, offline, console fonctionnelle et résilience à une panne de service.

**Si échec :** API WAN fermée; runtime complexe supprimé sauf justification RAM/CPU mesurée.

### Y — Campagne d'endurance et incidents (N3)

**Responsable :** SRE. **État initial :** NON_COMMENCE. **Dépend de :** X, D.

**Construction :** Banc 24h puis 7j puis 30j avec mesure consommation, stockage, réseau, réveils, corrections et 3 retests des régressions.

**Preuve de fin :** SLO cible provisoire >=99% services S0-S2 pendant fenêtre de 30j (hors coupure physique), zéro perte de transactions reconnues dans tests; preuve journalisée.

**Si échec :** Chauffe / batterie dangereuse : STOP; incidents critiques réouvrent W/X et compteur test.

### Z — Release ORIGIN-3 et gouvernance (N3)

**Responsable :** Livraison. **État initial :** NON_COMMENCE. **Dépend de :** Y, S, E.

**Construction :** Image native vérifiée, hash, sources/licences/SBOM, sauvegarde, procédure recovery, maintenance, docs, statut et traçabilité.

**Preuve de fin :** Validation contre-audit indépendant, checkliste chaque gate, preuve sur téléphone; pas de faux DONE.

**Si échec :** Absence de driver essentiel ou rollback = non terminé; Android restant est seulement plan de secours.

## E. Portes de validation et interdiction du faux « fini »

- **G0 — NON_VALIDE** : tâches A, B, C, D, E. Identité+restauration+bootmap+énergie+sources documentées.

- **G1 — NON_VALIDE** : tâches F, G, H, I, J, K, L, M, N. Cœur portable et épreuves Android sur téléphone mesurées.

- **G2 — NON_VALIDE** : tâches O, P, Q, R, S, T, U. Deux noyaux qualifiés sur papier; un chemin boot réel + récupération démontrés.

- **G3 — NON_VALIDE** : tâches V, W, X. Linux natif sur A21s, sans Android Framework, tous périphériques P0 fonctionnent.

- **G4 — NON_VALIDE** : tâches Y, Z. Stabilité durée et livraison maintenable.

Une porte est VALIDÉE seulement si chaque tâche indispensable est VALIDE, liée à des preuves horodatées, à une version de matériel/firmware et à une fiche de contre-audit. Un blocage critique réouvre la porte concernée, et les phases aval ne sont plus déclarées qualifiées.

**États canoniques** : NON_COMMENCE → RECHERCHE → PROTOTYPE_LAB_NON_QUALIFIE → EN_COURS → A_CORRIGER → A_CONTRE_AUDITER → VALIDE; BLOQUE/SUSPENDU accessibles à tout moment. Toutes les transitions portent auteur, date, motif, preuve et action suivante.

## F. Scénarios d'imprévus et scénarios d'adaptation

- **Appareil absent/offline** → Bloquer A/B/N/U; développer APOLLO CORE et cross-build sans déclarer de succès HW.

- **PC 4 Go incapable de compiler AOSP** → Compiler noyau ciblé/rootfs sur environnement Linux adapté, cache/download contrôlé, zéro Actions par défaut; pas d'AOSP massif.

- **Pas de déverrouillage constructeur vérifié** → Stopper flash; recherche boot chain/partitions, explorer images de test et recours matériel distinct sans forcer.

- **Knox/bootloader irréversible** → Information et décision propriétaire à l'étape S; l'objectif N3 ne justifie pas d'effacement non consenti.

- **3 Go de RAM seulement détectés sous mainline** → Corriger noeuds mémoire, zones réservées et bootloader d'après mesures; ne pas annoncer 4 Go acquis.

- **Noyau V n'initialise pas Wi-Fi hors Android** → Décomposer HAL et pilotes; tester M; isoler firmware, cartographier modules avant port.

- **Noyau M ne gère pas charge et température** → G3 bloquée, aucun service autonome longue durée; étudier PMIC et power domains ou revenir en labo.

- **Stockage eMMC usé/corrompu** → Réduire écritures, protection lecture seule, sauvegarde externe vérifiée, endurance reportée.

- **Réseau domestique ou courant instable** → Mode déconnecté, caches froids, outbox bornée, reconnexion et UPS/batterie surveillée; enregistrer incidents.

- **Batterie dangereuse / gonflée** → Stopper tests physiques et faire contrôler/remplacer par solution appropriée; ne pas neutraliser sécurité thermique.

- **Pilote libre/licence impossible à redistribuer** → Fournir procédure d'extraction légale côté appareil ou exclure la fonctionnalité; pas de blobs privés dans GitHub.

- **Échec répété au même test** → Issue avec preuve et hypothèses; 3 tentatives distinctes avec changement matériel, puis escalade recherche; pas de boucle aveugle.

- **Après 30 jours un incident critique** → Réouvrir W/X/Y, annuler qualificatif release, reprendre endurance sur version corrigée.

- **N3 impossible matériellement à budget nul** → Statut BLOQUE-HARDWARE; conserver N1/N2 comme laboratoires et documenter les drivers manquants; changer de matériel uniquement par décision explicite.

## G. Programme de tests et preuves

**T1 logiciel** : CI locale x86, ARM64 cross-compile, QEMU (ne valide aucun périphérique A21s); unitaires, crash, corruption, contrats API, backpressure, fuites.

**T2 Android réel** : veille Doze, redémarrage, CPU/RSS/PSS, charge, Wi-Fi, stockage, température, pertes réseau et reprise.

**T3 hardware kernel** : logs de boot, PID1, eMMC lecture/écriture, USB, écran ou console de secours, Wi-Fi, battery/charger, thermique, reboot, watchdog, RAM 4 Go.

**T4 endurance** : 24 heures puis 7 jours puis 30 jours; SLO proposé ≥99% des services S0-S2 hors panne physique majeure (définition fenêtres et exclusions documentée); zéro transaction acquittée perdue durant bancs de crash spécifiés; chiffres cibles non mesurés.

Pour chaque preuve : identifiant WBS, test, matériel firmware/hash, outil/commande, date, résultat brut, écart, correctif, retest, contre-auditeur et statut. Un résultat x86 est toujours étiqueté LAB; jamais DEVICE.

## H. Ressources, temps et priorité financière

**Ressources connues** : Samsung A21s 4 Go/64 Go de référence, PC Windows/Linux 4 Go RAM, Internet mobile coûteux et intermittent, coupures de courant. Le téléphone doit rester utilisable comme matériel de test pendant N1/N2. Objectif coûts additionnels 0 USD, pas de dépenses non demandées.

**Horizon indicatif, non promesse** : P0 1–3 semaines d'inventaire; N1 4–10 semaines; N2 3–9 mois (dépend surtout pilotes/boot); N3 3–12+ mois si drivers répondent. Projet complet **potentiellement >12 mois ou matériellement bloqué**, sans délai garanti. Paralléliser N1 et recherche N2 tant que leur sécurité ne dépend pas du téléphone.

**GitHub** : dépôt public PROJECT-DRAFTS, branche isolée, lecture AGENTS.md, 0 minute Actions par défaut, aucun secret ni document personnel, pas de workflow automatique; preuves locales et artefacts versionnés.

**Travail collaboratif** : directeur arbitre seulement sur preuves; responsables boot/kernel, énergie, mémoire, données, cyber, QA et UX. Lors des revues, chaque rôle est une perspective d'analyse, sauf agent externe effectivement exécuté.

## I. Journal obligatoire : douze cycles critique → correction → validation structurelle

**R01. Hypothèse modèle non vérifiée** — *Objection :* La mémoire de conversation ne prouve pas l'état actuel du téléphone. *Révision :* Exiger A signé, référence exacte, détails des partitions physiques avant toute décision. *Lots affectés :* A, C. Contrôle de cohérence de dépendances : PASS.

**R02. Flash prématuré** — *Objection :* Un bootloader déverrouillé/Knox et une sauvegarde imparfaite rendent le retour difficile. *Révision :* Introduire B/S comme double porte indépendante; aucune action risquée si restauration non démontrée. *Lots affectés :* B, S. Contrôle de cohérence de dépendances : PASS.

**R03. 3 Go DT vs appareil 4 Go** — *Objection :* Le device tree mainline a une mémoire 3 Go par défaut; risque de masquer les 4 Go. *Révision :* Test RAM physique, noeuds mémoire, réservations et vrai /proc/meminfo sous Linux. *Lots affectés :* A, Q, W. Contrôle de cohérence de dépendances : PASS.

**R04. Wi-Fi absent** — *Objection :* Un Linux bootable sans radio réseau est inutilisable comme machine autonome locale. *Révision :* Wi-Fi+USB comme P0; chaîne firmware/antenne/power-domain, aucun G3 sans test. *Lots affectés :* R, W. Contrôle de cohérence de dépendances : PASS.

**R05. Batterie et charge** — *Objection :* Serveur permanent peut devenir dangereux sans charge sûre, thermiques et capacité réelle. *Révision :* Contrôle D et W; STOP automatique d'essai si batterie douteuse; aucun travail lourd sur charge douteuse. *Lots affectés :* D, W, Y. Contrôle de cohérence de dépendances : PASS.

**R06. Noyau vendor piégé** — *Objection :* Le noyau 4.19 peut reposer sur des composants Android non portables. *Révision :* Documenter dépendances HAL/firmware, deux voies V/M et critère mesuré de sélection. *Lots affectés :* P, Q, U. Contrôle de cohérence de dépendances : PASS.

**R07. Modèle Apollo mal transposé** — *Objection :* Quelques ko ne suffisent pas à Linux; RAM 4 Go n'autorise pas une exécution anarchique. *Révision :* Budget RSS/PSS mesuré, modules S4 froids, ordre de priorités S0-S4. *Lots affectés :* G, H, J. Contrôle de cohérence de dépendances : PASS.

**R08. Fausse exactement-une-fois** — *Objection :* SQLite ne garantit pas l'absence de double effet externe en cas de crash. *Révision :* Outbox et idempotence; tests de stale completion et crash-points; aucun effet externe non compensable. *Lots affectés :* I, M. Contrôle de cohérence de dépendances : PASS.

**R09. Test labo confondu avec test appareil** — *Objection :* Une réussite x86 ne prouve ni Android Doze ni thermiques. *Révision :* Étiquetage obligatoire LAB/ANDROID/MAINLINE_HW; gates réels exigent preuve DEVICE. *Lots affectés :* M, N, U. Contrôle de cohérence de dépendances : PASS.

**R10. Récupération insuffisante** — *Objection :* Réinitialisation peut détruire données et laisser le matériel inaccessible. *Révision :* Cartographier partitionnement réel, secours, sauvegarde externe et consignes opérateur. *Lots affectés :* B, C, S. Contrôle de cohérence de dépendances : PASS.

**R11. Budget/Réseau RDC** — *Objection :* PC 4Go, data limitée et coupures rendent builds et CI répétitifs non viables. *Révision :* Build incrémental, caches, quota Actions 0/min par défaut, binaire petit, connexion optionnelle. *Lots affectés :* O, J, Y. Contrôle de cohérence de dépendances : PASS.

**R12. Fin fictive / dérive de périmètre** — *Objection :* Un prototype ou un boot incomplet serait annoncé comme niveau 3. *Révision :* Gates stricts, statuts et preuves, replanification après chaque échec, audit indépendant de Z. *Lots affectés :* Z, Y. Contrôle de cohérence de dépendances : PASS.

Ces 12 cycles ne prouvent ni boot Linux, ni fiabilité énergétique. Ils produisent 12 corrections conceptuelles traçables, à tester expérimentalement plus tard.

## J. Critères de reprise, arrêt et état courant

**Reprise** : lire README, PLAN R4.12, JSON tracker, dernier journal; ne pas recommencer A-Z sans preuve d'invalidation. Une loi appliquée : si condition critique absente → BLOQUE, jamais substituée par une simulation non étiquetée.

**Arrêt** : danger batterie, perte de récupération, incompatibilité non maîtrisée, absence d'autorisation pour unlock/flash, désaccord sur provenance des fichiers. Documenter cause et voie alternative.

**Au 31/10/2026** : N1 dispose d'un prototype logiciel antérieur non qualifié sur appareil; P/Q font l'objet de recherche documentaire. Aucun niveau 3 physiquement atteint, aucune nouvelle modification du téléphone. Les portes G0-G4 restent NON_VALIDÉES.

## K. Sources de référence (revérifier à chaque jalon)

- [LineageOS A21s officiel](https://github.com/LineageOS/lineage_wiki/blob/main/_data/devices/a21s.yml)

- [Patch initial DTS A21s du 16 septembre 2026](https://lists.openwall.net/linux-kernel/2026/09/16/2949)

- [Linux kernel U-Boot Exynos850 boot flow](https://docs.u-boot.org/en/latest/board/samsung/e850-96.html)

- [Dépôt expérimental a21s-mainline](https://github.com/samsungexynos850/android_device_samsung_a21s-mainline)

- [Projet Exynos850 mainline](https://github.com/exynos850-mainline)

- [Buildroot documentation](https://buildroot.org/downloads/manual/manual.html)

- [postmarketOS classification kernel downstream/mainline](https://docs.postmarketos.org/pmaports/main/packaging/device-categorization.html)

- [NASA Apollo 11 executive alarms](https://nasa.gov/wp-content/uploads/static/history/alsj/a11/a11.1201-fm.html)

- [SQLite WAL et durabilité](https://sqlite.org/wal.html)

- [Samsung Knox warranty fuse](https://docs.samsungknox.com/admin/knox-platform-for-enterprise/faqs/faq-115013719548.htm/)

- [Android Doze](https://developer.android.com/training/monitoring-device-state/doze-standby)

- [Policy Actions](https://github.com/Terminator364/PROJECT-DRAFTS/blob/main/AGENTS.md)


---
**Révision R4.12 : finale pour la planification actuelle, non immuable.** Toute nouvelle preuve physique provoque une évolution contrôlée R4.13+, jamais la falsification d'une ancienne validation.