# ORIGIN L3 — double piste Linux et heritage Apollo

## Decision technique
Le but n'est PAS d'avoir Linux a l'interieur d'Android, ni du root, ni une application Termux. La destination est un OS Linux ARM64 natif ou Android n'est plus l'espace utilisateur.

Deux voies sont etudiees en parallele, avec exactement le meme rootfs, C0, sauvegardes, API et tests :

**L3-V — Linux constructeur :** noyau Linux vendor 4.19 du SM-A217F avec espace utilisateur Linux independant. On evaluera si pilotes/firmwares fonctionnent sans init Android ni ses HAL. Si oui, c'est un OS Linux natif, meme si le noyau n'est pas mainline. Aucune garantie pour charge, Wi-Fi, modem, thermiques ou securite.

**L3-M — Linux mainline :** Linux Exynos850 + DTB SM-A217F. Le patch accepte en septembre 2026 reste initial : SimpleFB, boutons, 3 Go configures par defaut, ramoops, GPU declare, MMC, USB, watchdog. Charge/PMIC, Wi-Fi et RAM reelle de 4 Go sont a qualifier.

Les deux convergent dans la meme architecture C0 et la meme recette R-Z. L3-PRODUCTION exige stockage, energie, recovery et un transport d'administration reels, pas seulement un boot.

## Les six lois ORIGIN-APOLLO
1. Complexite sur eMMC, minimum charge dans la RAM.
2. Priorites P0 securite / P1 controle / P2 service / P3 facultatif.
3. Modules lourds hors micro-executif C0, invoques a la demande.
4. Slots memoire bornes et files avec rejet explicite en surcharge.
5. Snapshot + futur journal append-only, acknowledgements apres commit.
6. Degradation des fonctions secondaires en cas d'alarme, inspiree de l'executif Apollo 11.

## Mesures de laboratoire C0 31 octobre 2026
- executable C11 Linux x86_64 : 17112 octets ;
- fichier d'etat : 796 octets ;
- sections ELF : text 5730, data 736, bss 992 octets ;
- 32 tests unitaires/adversariaux passes ;
- 3000 operations aleatoires cumulees dans deux bancs ;
- 120 interruptions SIGKILL : 33 processus tues, 87 termines, zero corruption de snapshot detectee ;
- 32/32 sous UBSan ;
- corrections : verrou multi-ecrivain flock et accusé de reussite apres commit.

**Limites :** le C0 est un executable en espace utilisateur, pas un noyau ni un init de production. Snapshot unique sans journal transactionnel, pas de ledger idempotent pour effets externes, aucune demonstration ARM64, Android ou Samsung. Les tests ne simulent pas fidelement une coupure physique.

## Gouvernance
N1 A-H: caracteriser appareil et recuperation; N2 I-Q: construire logiciel complet et images; N3 R-Z: boot natif, pilotes vitaux, services, securite, endurance, remise de cle.
Aucun flash sans sauvegarde testee, batterie saine et plan recovery fiable.
Aucune CI GitHub automatique, budget AGENTS.md.
Aucune donnee privee/medicale ou cle en depot public.

## Sources
- https://github.com/LineageOS/lineage_wiki/blob/main/_data/devices/a21s.yml
- https://lists.openwall.net/linux-kernel/2026/09/16/2949
- https://lists.openwall.net/linux-kernel/2026/09/18/1455
- https://github.com/exynos850-mainline
- https://nasa.gov/wp-content/uploads/static/history/alsj/a11/a11.1201-fm.html
