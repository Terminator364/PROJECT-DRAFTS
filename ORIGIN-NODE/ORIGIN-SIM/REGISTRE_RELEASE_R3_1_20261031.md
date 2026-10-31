# ORIGIN-SIM R3.1 — Registre final de vérification logicielle
31 octobre 2026 — **Objectif stratégique maintenu : ORIGIN-3 Linux natif sur SM-A217F.**

## Livrable numérique réellement créé
- Archive complète et testée depuis extraction vierge : `ORIGIN_SIM_R3_1_COMPLET_AUDITE_20261031.zip` (livrée dans la conversation ChatGPT, **non téléversée sur GitHub**).
- Taille : **200 740 octets**. SHA-256 : `b03f67b8dbe5b2580fce160ea87fd2bc1cf614ad9d7a98701ba90f186a849af5`.
- 68 fichiers source et rapports, 3 Makefiles C0/C1/C2, JSON des preuves et interface HTML autonome.
- ZIP testé CRC, sommes SHA-256 des 68 fichiers, sécurité des chemins, extraction dans un dossier neuf.

## Preuves d'exécution après extraction
- Python : **207/207** tests PASS.
- C0 : **32/32**; C1 : **20/20**; C2 + SQLite : **25/25** tests PASS. Total des quatre suites : **284/284**.
- C1 : **120 interruptions SIGKILL**, état cohérent, mais ACK ambigu après `rename`.
- C2 : **120 SIGKILL après commit**, 120 rejouements identifiés sans nouvelle admission, 120 reçus accessibles.
- 12 cycles audit → contre-audit → recherche → contre-recherche → réévaluation : 12/12; 24 tests ciblés rejoués (inclus dans les 284).
- **432 trajectoires synthétiques** de deux jours, 35 composants, 26 lots de construction, **83 preuves** requises; 0 violation des invariants de conservation dans cette campagne.
- HTML hors ligne : 6 onglets, navigateur Chromium mobile/desktop, sans erreur JS.
- ELF générique AArch64 cross-compilé et identifié; **jamais exécuté**.
- 11 vérifications indépendantes après extraction ZIP : **11/11 PASS**.
- **0 mesure physique, 0 AVD, 0 QEMU invité, 0 flash, 0 boot Linux natif.**

## Corrections fondamentales
C1 refuse les requêtes en surcharge sans évincer les travaux précédemment acceptés; garde 2 places pour P0/P1. C2 adopte une admission persistante avec clé de requête et reçu rejouable sous SQLite WAL; résolution de l'ambiguïté de commit pour **opérations pures internes**, pas exactly-once des actions externes. Modèle de charge avec pertes de conversion et découplage USB données/charge; Wi-Fi local relié à l'électricité du routeur avec option de batterie de secours. Les anciens taux R1 restent invalidés scientifiquement.

## Décision
**R3.1 = banc de simulation logiciel achevé et reproductible.** Pas de certification d'un jumeau numérique physiquement fidèle. **N3/G0–G4 restent NON VALIDÉS.** Il faut calibrer sur le smartphone et tester les pilotes énergie/Wi-Fi/USB/eMMC/boot avant toute intervention risquée. Aucun GitHub Actions ni coût API déclenché par cette publication.

## Sources de méthode
- NASA-STD-7009B : https://standards.nasa.gov/node/263
- Linux DTS A21s 2026 : https://lists.openwall.net/linux-kernel/2026/09/16/2949
- QEMU virt : https://www.qemu.org/docs/master/system/arm/virt
- Linux fsync : https://man7.org/linux/man-pages/man2/fsync.2.html
- SQLite WAL : https://www.sqlite.org/wal.html

**Limitations de synchronisation :** l'intégralité des sources R3.1 est uniquement dans le ZIP vérifié de la conversation; le présent registre Github ne remplace pas ce livrable et n'implique pas un `git push` du code.