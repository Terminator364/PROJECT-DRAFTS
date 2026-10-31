# ORIGIN — Réconciliation sans redémarrage (R4.12 → R4.12a)

**Le même téléphone, deux générations de recherche, un seul cap : L3 natif.**

## Sources conservées
1. Ancien laboratoire avancé **ORIGIN OS / microexec C0** (dans le paquet local `ORIGIN_OS_L3_PLAN_DIRECTEUR_APOLLO_AZ_20261031.zip`) : noyau C11 de recherche, 16 slots P0–P3, sérialisation, contrôles d'état; recompilé et **32/32 tests réussis** à nouveau le 31/10/2026; 120 SIGKILL simulés (34 kills, 86 achèvements naturels), zéro corruption constatée.
2. Branche GitHub antérieure `research/origin-os-l3-masterplan-20261031`, doc `ORIGIN-NODE/docs/PLAN_DIRECTEUR_NIVEAU_3_20261031.md`, conserve le plan A–Z d'origine et double piste kernel; le code C0 n'était pas présent à l'emplacement attendu sur cette branche, il ne faut pas le prétendre.
3. Prototypes Python `ORIGIN-NODE/origin/` dans la branche actuelle: banc d'API/SQLite, **56/56 tests** revérifiés localement le 31/10/2026. C'est un laboratoire d'intégration et d'outillage, **pas** le coeur natif N3.
4. R4.12 `PLAN_DIRECTEUR_ORIGIN3_APOLLO_R4_12.md` et `registry/WBS_GATES_R4_12.json` = **registre directeur canonique pour les étapes futures**, sans effacer l'historique A–Z antérieur.

## Arbitrage architecture
**APOLLO C0 natif (C11) est le candidat principal pour L3**, car il est borné et indépendant de la JVM/Framework Android. Le C0 actuel ne satisfait pas encore durabilité externe, migration de snapshot, supervision hiérarchique, identité des effets hors processus, isolation de processus, sécurité et tests ARM64. Le Python existant reste oracle/prototype analytique; toute réécriture doit être justifiée par tests d'équivalence et mesure RAM/CPU.

## Passage des anciens lots A–Z aux lots R4.12
| Lot historique | Sujet ancien | Nouveau lot R4 | Règle de migration |
|---|---|---|---|
| A | Identification | A | inventaire appareil absent |
| B | Santé batterie | D | aucun test physique déjà acquis |
| C | Sauvegardes | B | ne pas compter comme validé |
| D | Firmware/boot | C/S | carte boot et plan rescue requis |
| E | Banc hôte | G/H/I/M | réutiliser 32 C0+56 Python avec preuve et limites |
| F | Télémétrie réelle | J/N | capteurs smartphone non testés |
| G | C0 Android | N | pas de preuve A21s |
| H | Fin niveau 1 | G1 | incomplète |
| I | Contrat C0 | F/G/H | prototype C0 à promouvoir après audit |
| J | Journal durable | I | journal durable encore incomplet |
| K | Modules C1..C7 | H/X | interfaces à construire |
| L | Gouverneur | J | Python consultatif uniquement |
| M | Rootfs | T | Buildroot reste à intégrer |
| N | ROM et Knox | C/P/Q/S | recherche seulement |
| O | Sécurité | L/X | labo ≠ durcissement système |
| P | Chaos | M/Y | SIGKILL n'est pas coupure électrique réelle |
| Q | RC pour L3 | U | aucune image qualifiée |
| R | Boot Samsung | C/S | aucun flash autorisé |
| S | Kernel et RAM | P/Q/R/W | 3 Go DTS ≠ 4 Go physique |
| T | Initramfs/rootfs | T/V | pré-déploiement |
| U | Charge/thermique/réseau | R/W | BLOQUANT G3 |
| V | Supervision | K/X | non vérifiée Linux natif |
| W | Restauration physique | B/S/Y | pas de preuve matérielle |
| X | Interface | L/X | pas de production |
| Y | Endurance | Y | pas de banc 30 jours |
| Z | Remise clé | Z | toujours non réalisée |

## Mesures locales de reprise réellement faites
- C11 compilé sous GCC `-O2 -Wall -Wextra -Werror -pedantic` (hôte x86_64), 32/32 tests, 120 SIGKILL.
- Python ORIGIN 0.2, 56/56 tests, sans téléphone.
- Fichier `origin_c0.c` local SHA256: `4807b09f96c5e3769a8700ecd51c24fe569d4860a03de13e12879c6dae0fde4a`.
- Fichier `origin/core.py` local SHA256: `f3246baac9027fb2edebb2430cd7ee842767e5cbe56cd9bd57901880cc0ced42`.
- Aucun de ces résultats ne valide un pilote ou une image kernel a21s.

## En cas d'écart
Ne pas supprimer les anciens plans ni déduire qu'un statut LAB équivaut à VALIDE. Reprendre depuis le dernier artefact avec empreinte et preuve; ouvrir un ticket pour toute divergence et faire évoluer le registre R4.12a. La présentation A–Z est une convention du plan; le contenu d'un lot peut évoluer sans changer la destination.
