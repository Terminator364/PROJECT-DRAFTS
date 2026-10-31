# ORIGIN-SIM — Etude numérique de smartphones usés (R1, 31 octobre 2026)

## Mandat et lien directeur
Cette branche du dépôt **PROJECT-DRAFTS** conserve la recherche sur un jumeau numérique du Samsung Galaxy A21s **SM-A217F** ayant servi **5 à 8 ans**. La référence 2026 correspond à environ **6 ans** depuis la sortie en 2020. Le profil « 8 ans » est un scénario contrefactuel/prospectif et non une mesure d'un A21s déjà âgé de huit ans en octobre 2026.

Le plan de construction A→Z officiel reste `ORIGIN-NODE/PLAN_DIRECTEUR_ORIGIN3_APOLLO_R4_12.md` et le registre `ORIGIN-NODE/registry/WBS_GATES_R4_12.json` (26 tâches, 83 preuves). La destination est **Linux natif N3**, non Android optimisé comme produit final.

## Architecture de simulation
- **H0 : données et hypothèses** : 35 composants documentés, tous non inspectés sur l'exemplaire réel; batterie 5000 mAh neuve, RAM 4 GiB et stockage 64 Go de *référence*.
- **H1 : moteur Python sur hôte** : simulation événementielle approximative de température, batterie, réseau, réserve eMMC, RAM, charge, coupures, reprises, accès Wi-Fi; paramètres d'usure explicites, graines reproductibles, Monte Carlo.
- **H2 : software-in-the-loop Apollo C0** : compiler le vrai démonstrateur C11 précédemment construit et exécuter priorité P0 avant P3, snapshot durable et chaos SIGKILL sur Linux x86_64.
- **H3 prévu : Android Emulator / AVD générique** : Doze, API, UX; ne simule pas le bootloader Samsung, le PMIC, l'USB exact ni Exynos 850.
- **H4 prévu : QEMU ARM64 `virt`** : rootfs, initramfs, services d'un OS Linux ARM64 générique; QEMU `virt` n'est PAS le Galaxy A21s.
- **H5 ultérieur :** vrai SM-A217F pour calibrer les modèles et valider les pilotes. Aucune mesure physique en cours.

## Répétition de construction A–Z
1. **N1/G0-G1** : les tâches de recherche/logiciel sont simulées; résultats étiquetés `SYNTHETIC`.
2. **N2/G2** : two kernel paths (Samsung vendor 4.19 vs Linux mainline). Les pilotes sont classés comme inconnus, initiaux ou supposés résolus.
3. **N3/G3-G4** : les fonctions critiques (boot, stockage, charge, thermique, Wi-Fi, USB, RAM, RTC, watchdog, PMIC, reprise) doivent toutes être satisfaites. En monde réaliste `unknown` le simulateur bloque, même si l'exécutif logiciel réussit.
4. Le monde `optimistic` n'est qu'un **contre-factuel de faisabilité** : 26 tâches simulées peuvent passer, mais **0/5 portes physiques** sont qualifiées.

## Tests réellement effectués en laboratoire logiciel
- 107/107 tests Python; 44/44 contrôles d'auto-audit logique.
- 32/32 tests du C0 C11 en local; état binaire 796 octets (hors charge de Linux); 120 scénarios SIGKILL, 0 état corrompu détecté dans ce banc.
- 15 conditions × 64 tirages = **960 trajectoires stochastiques de sept jours**; 8 scénarios de stress complémentaires.
- Construction inconnue : 18/26 lots virtuels franchissables, 8 bloqués; construction optimiste : 26/26 lots virtuels, 12 défauts de plan provoqués/corrigés par hypothèses.
- Tableau de bord HTML hors ligne passé dans un navigateur de test sans erreur JavaScript.
- **Aucun boot Samsung, aucune émulation Android/QEMU, aucune qualification électrique/batterie, aucun flash/root/ADB.**

Le paquet source et le tableau de bord complet ont été générés comme artefacts téléchargeables dans la conversation ChatGPT à l'origine de cette branche; ce README est le registre public de recherches, **pas la preuve que tous les fichiers de l'archive ont été synchronisés sur GitHub**.

## Mises en garde méthodologiques
Les taux de réussite et les percentiles de la simulation sont **des propriétés du modèle**, pas des probabilités réelles. L'état de santé réel de la batterie, les risques de gonflement, les pilotes Wi-Fi/PMIC et l'endurance ne sont pas inférables d'une fiche technique.

La comparaison des émulateurs suit la documentation officielle :
- https://www.qemu.org/docs/master/system/arm/virt
- https://developer.android.com/studio/install
- https://developer.android.com/studio/run/managing-avds
- https://lists.openwall.net/linux-kernel/2026/09/16/2949
- https://github.com/LineageOS/lineage_wiki/blob/main/_data/devices/a21s.yml
- https://standards.nasa.gov/node/263
- https://docs.samsungknox.com/admin/knox-admin-portal/kbas/kba-360039680233/

## Prochaine borne
Ne pas flasher ou promouvoir N3. Améliorer d'abord la crédibilité du simulateur, la séparation tests logiciel/émulation/mesure, et établir un plan de calibration read-only du téléphone réel. GitHub Actions = 0 minute par défaut conformément au fichier `AGENTS.md` racine.
