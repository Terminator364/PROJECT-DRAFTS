# ORIGIN R&D 0.2 — Résultat final (2026-10-31)

## Résultats exécutés (Linux x86_64, pas sur téléphone)
- **56 tests unitaires sur 56 réussis** (nouvelle exécution finale).
- **2 500 tâches** traitées en **5 vagues de 500** sous une barrière de 1 000 tâches actives.
- **148 expirations de bail simulées**, récupération puis refus des résultats périmés.
- **20 000 scénarios** synthétiques de ressources (batterie, température, mémoire, stockage, data).
- Sauvegarde SQLite et réouverture vérifiées.
- `compileall` sur le code Python et tests sans erreur.
- Le ZIP local final est vérifié (test d'intégrité et SHA-256):
  `654abbc17a90b16900ff30db9f02adba972d0d32f7076873106754302be67a18`

La première tentative de 2 500 soumissions simultanées a échoué, **comme prévu**, sur le garde-fou d'occupation 1 000. L'essai a ensuite été corrigé pour traiter les charges par vagues. Aucun test sur matériel Samsung n'a été réalisé.

## Réserve de validation
- Le gouverneur est **consultatif** (aucun driver ni action batterie), seuils à recalibrer.
- Le superviseur `flock` libère son verrou après SIGKILL sur Linux, mais ne résiste pas automatiquement à une interdiction d'exécution par Android.
- La récupération assure une idempotence interne des trois tâches pures de démonstration, pas le `exactly-once` d'effets externes.
- La RAM tracée dans le laboratoire **n'est pas** la consommation de RAM du téléphone.
- Le port API reste sur `127.0.0.1` avec authentification; aucune administration distante LAN n'est implémentée.
- Aucun flash, root, ADB sur téléphone, ni GitHub-hosted Actions durant cette session.

## Decision Gate
**GO** : inventaire strictement en lecture seule + essai non-root sur stock Android.

**HOLD** : LineageOS (branche officielle 23.2) tant que le téléphone n'a pas été inventorié et sauvegardé.

**NO-GO** : Linux natif production, flash, bootloader sans essai matériel et plan de retour.

## Références
- https://github.com/LineageOS/lineage_wiki/blob/main/_data/devices/a21s.yml
- https://lkml.iu.edu/2609.2/07600.html
- https://github.com/termux/termux-app
- https://github.com/termux/termux-boot
- https://github.com/termux/termux-services
- https://developer.android.com/training/monitoring-device-state/doze-standby
- https://docs.samsungknox.com/admin/knox-admin-portal/kbas/kba-360039680233/
