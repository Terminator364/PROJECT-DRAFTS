# ORIGIN-3 — GitHub Deep Research R5 (4 novembre 2026)

**Nature : inspection documentaire des dépôts publics et fichiers source. Aucun essai A21s, flash ou test de pilote n'a été entrepris. Les dépôts, forks et patchs changent : les détails ci-dessous sont des instantanés datés.**

## Découverte 1 — uniLoader a une carte A21s spécifique
- https://github.com/ivoszbg/uniLoader/blob/master/board/samsung/board-a21s.c (SHA Git blob `3302c1ea4a543638c3ba90f12bd1f783ea9eaa75`)
- https://github.com/ivoszbg/uniLoader/blob/master/configs/a21s_defconfig (SHA `bee66cd4cb14e0c3514e1a6bae138c7c5a8d6523`)
- Source date : commit `347589d10d04` du 8 juillet 2026.
- Code : `CONFIG_EXYNOS_3830=y`, `CONFIG_SAMSUNG_A21S=y`, `CONFIG_TEXT_BASE=0x80080000`, `CONFIG_PAYLOAD_ENTRY=0x90000000`, `CONFIG_RAMDISK_ENTRY=0x84000000`; framebuffer 720x1600, adresse 0xfa000000; écrit dans un registre DECON.
- **Interprétation** : implantation bootloader au niveau source pour A21s. **NON démontré** : démarrage reproductible avec notre firmware, RAM 4 Go, sauvegarde/recovery, pilotage de batterie. Ne pas flasher un artefact de ce dépôt sans chaîne de vérification.

## Découverte 2 — kernel mainline A21s évolue au-delà du patch v3 du 16 septembre
- Source consultée : https://github.com/samsungexynos850/linux/blob/master/arch/arm64/boot/dts/exynos/exynos850-a217f.dts
- Commit initial upstream accueilli le 18 septembre 2026 : https://lists.openwall.net/linux-kernel/2026/09/18/1455
- Commits additionnels dans la branche du fork : `3ee889183cae` 30 septembre PMIC, `0c8ecfc09bf9` 1 octobre WTSR/SMPL, `9274d576bcf6` 1 octobre vibrator; touchscreen commit `8b0d498efb13` (date source pouvant ne pas suivre l'ordre de branche).
- DTS actuel : `samsung,s2mpu12-pmic`, buck/LDO, RTC, USB, MMC, watchdog, tactile, framebuffer, ramoops. **Mais** l'horloge RTC `fixed-clock` garde le commentaire de substitution en attendant l'implémentation PMIC correcte, le GPU et l'USB utilisent un `reg_dummy`, tactile aussi. Pas de démonstration dans ce fichier du Wi-Fi ni de charge complète.
- La description mémoire actuelle utilise encore une carte pour variante 3 Go. Ne pas conclure compatibilité 4 Go sans adaptation et logs.

## Découverte 3 — LineageOS 24.0 fournit une carte matérielle utile, PAS un userspace Linux mainline
- Source : https://github.com/LineageOS/android_device_samsung_a21s-common/blob/lineage-24.0/BoardConfigCommon.mk (blob `b0f0632529a48a2a7db5108133aed6451efbfb25`)
- `TARGET_KERNEL_SOURCE=kernel/samsung/exynos850`, `BOARD_KERNEL_IMAGE_NAME=Image`, `BOARD_DTB_CFG`, `BOARD_DTBO_CFG`, `BOARD_BOOTIMAGE_PARTITION_SIZE=37748736`, `BOARD_RECOVERYIMAGE_PARTITION_SIZE=55574528`, `AB_OTA_UPDATER=false`.
- Wi-Fi déclaré `BOARD_WLAN_DEVICE=slsi`, dépendances pilotes et HAL Samsung SLSI. Charger un système Linux sans Android exige de résoudre pilotes/firmware et interfaces utilisateurs correspondantes.
- Charge contrôlée dans cette ROM via `/sys/class/power_supply/battery/batt_slate_mode` (1 = charge désactivée et 0 = réactivée selon fichier). **Ne jamais écrire aveuglément dans ce chemin sur téléphone réel** : son existence, sa sémantique et sa sûreté sont limitées à cette configuration.
- Thermique : https://github.com/LineageOS/android_device_samsung_a21s-common/blob/lineage-24.0/configs/thermal/thermal_info_config.json ; seuils signalés 60°C batterie et port USB, 96/115°C CPU. Ce sont des paramètres du profil ROM, **pas des seuils de sécurité à copier dans notre contrôleur**.
- Fstab : https://github.com/LineageOS/android_device_samsung_a21s-common/blob/lineage-24.0/configs/init/fstab.exynos850 ; partitions metadata, boot, recovery, vbmeta, cache, userdata f2fs, efs, misc; zram 2 GiB; pas un script d'écriture.
- USB gadget: https://github.com/LineageOS/android_device_samsung_a21s-common/blob/lineage-24.0/configs/init/init.exynos850.usb.rc ; configfs, RNDIS et NCM existent dans la configuration Android, non prouvés sous Linux mainline.

## Découverte 4 — vrais bogues signalés, à transformer en tests
- https://github.com/LineageOS/issues/issues/351 : Wi-Fi HAL getLinkLayerStats crash, ouvert (juillet 2026).
- https://github.com/LineageOS/issues/issues/723 : Wi-Fi WPA2/WPA3 incompatibilité, clos octobre 2026 (ne pas conclure cause corrigée sans historique).
- https://github.com/samsungexynos850/atlas/issues/3 : compilation d'Image locale conduisant à Download Mode malgré image officielle démarrant (clos, n'est pas preuve d'une solution universelle).
- https://github.com/samsungexynos850/atlas/issues/6 : freezes/reboots aléatoires sous AxionOS+Atlas (clos; manifestation rapportée, non imputable définitivement au noyau seul).
- https://github.com/LineageOS/issues/issues/917 : NFC en panne sur 24.0, non bloquant pour serveur, ouvert.
- Ne pas copier la procédure de flash ni les clés de démonstration de projets A13 vers A21s.

## Découverte 5 — Apollo Executive réellement examiné
- https://github.com/virtualagc/virtualagc/blob/master/Luminary099/EXECUTIVE.agc
- Le code distingue `NOVAC`, `FINDVAC`, `JOBSLEEP`, `JOBWAKE`, `PRIOCHNG`, `ENDOFJOB`, espaces `VAC`, sept `core sets` et `BAILOUT1` avec alarme `1201` quand les zones d'exécution sont indisponibles. Il ne démontre pas un journal transactionnel exactement une fois ni la durabilité moderne; nos SQLite receipts ne proviennent pas d'Apollo.
- Héritage : admission bornée, priorités, récupération, notifications, défense contre surcharge; adapter à Linux et au stockage moderne.

## Autres projets
- https://github.com/chrislgarry/Apollo-11 : code AGC historique numérisé (référence de logique, non une bibliothèque moderne).
- https://github.com/virtualagc/virtualagc : émulateur + sources historiques.
- https://github.com/Bry50/Old-Smartphone-as-a-server : cas Nexus 5 en serveur postmarketOS, matériel et contexte différents.
- https://github.com/fernandomcrsilva/Phone-as-a-homelab : serveur Galaxy S10+ rapporté à 0,39 W; non transposable quantitativement.
- https://github.com/funkybooboo/pmos-toolkit : pipeline inventaire/backup/portage Samsung, à auditer avant réemploi de scripts.
- https://github.com/exynos850-mainline/releases : images *A13/A135F* expérimentales, **non compatibles A21s** et explicitement non adaptées à un usage quotidien.
- https://github.com/samsungexynos850/atlas : noyau downstream Samsung/Android, utile pour pilotes, non assimilable à un port Linux natif.
- postmarketOS pmaports central est administré via son infrastructure actuelle (souvent GitLab), ne pas inventer un GitHub miroir officiel.

## Politique de preuves et décision
1. **G0** : appareil exact, batterie, partitions, sauvegardes, récupération sans écriture.
2. **N1** : Apollo C2 sur Android réversible, observer thermiques et Wi-Fi; ajouter tests inspirés #351/#723.
3. **N2** : reconstruire une *carte de dépendances* `SM-A217F → uniLoader a21s → DTS Linux fork → kernel modules → PMIC/RTC/USB/MMC/Wi-Fi`; compiler en laboratoire; vérifier RAM 4 Go.
4. **N3** : boot vrai sur téléphone, énergie/charge/Wi-Fi/USB/stockage prouvés; sinon status BLOQUÉ.
5. Une découverte dans un DTS ou BoardConfig est « CODE PRESENT ». Ne devient « FONCTION MATÉRIELLE TESTÉE » qu'après logs et mesure sur l'appareil.
6. La fidélité de ORIGIN-SIM est encore non calibrée; intégrer les bogues concrets en scénarios sans transformer leurs fréquences en probabilités de pannes.
**Ce fichier est un état de recherche, pas une nouvelle qualification matérielle.**