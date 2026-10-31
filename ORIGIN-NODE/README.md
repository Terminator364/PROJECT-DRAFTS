# ORIGIN NODE — R&D (Galaxy A21s SM-A217F)

**Status:** software laboratory, not deployed to any Android device.
**Date:** 2026-10-31.
**Scope:** independent smartphone repurposing; no root, no flash, no default internet listeners.

## Evidence and decision
- Official [LineageOS A21s device specification](https://github.com/LineageOS/lineage_wiki/blob/main/_data/devices/a21s.yml) lists `current_branch: 23.2` (check current firmware/region on the *physical device* before considering changes).
- Accepted [Linux device-tree patch](https://lkml.iu.edu/2609.2/07600.html) adds *initial* SM-A217F support. It does **not** demonstrate a stable Linux phone with Wi-Fi, modem, charging, and suspend fully working.
- [Termux README](https://github.com/termux/termux-app) explicitly warns about Android 12+ phantom process killing. [Android Doze documentation](https://developer.android.com/training/monitoring-device-state/doze-standby) explains network and scheduling limits.
- [Termux:Boot](https://github.com/termux/termux-boot) and [termux-services](https://github.com/termux/termux-services) provide supported boot/service approaches, but no guarantee of 24/7 uptime.
- Samsung [Knox warranty bit](https://docs.samsungknox.com/admin/knox-admin-portal/kbas/kba-360039680233/) can be irreversible when unofficial firmware is installed.

## Preferred path
1. **Phase 0: read-only physical inventory.** Confirm model, bootloader, Android version, battery safety, Wi-Fi sleep behavior, local hardware and firmware.
2. **Phase 1: non-root prototype** on existing firmware, with only loopback HTTP, local SQLite jobs, restart/recovery and thermal logging.
3. **Phase 2: week-long stability trial** with measured system uptime, temperature, charge and actual access/network conditions.
4. **Phase 3: decide whether an alternative ROM is justified.** LineageOS is a candidate, not a required step.
5. **Phase 4: independent Linux-mainline laboratory** with hardware-specific drivers. No production flash until essential peripherals are validated.

## R&D findings — local simulation
The companion **ORIGIN NODE v0.2** code bundle (not yet installed on an Android phone) passed **56 Python unittest cases** on Linux x86_64. A deterministic benchmark exercised:
- 2,500 bounded jobs in five 500-job waves;
- 148 forced lease-expiry recoveries with stale-result rejection;
- persistent SQLite backup verification and fresh-handle restart;
- 20,000 synthetic resource-governor snapshots;
- local SQLite integrity check.

**Limit:** these are software tests, not device thermal, battery, Wi-Fi, boot, Android Doze, OTA or uptime tests. Bench timings depend on the lab machine; they are not A21s performance forecasts.

The separate `governor.py` and `test_governor.py` in this directory are self-contained reproducible modules with no third-party dependencies. Python 3.10+ is recommended.

```sh
cd ORIGIN-NODE
python -m unittest discover -s tests -v
```

## Safety gates
- Do not flash or unlock bootloader during discovery. Backup and contingency plan are mandatory first.
- Never expose development HTTP endpoints on 0.0.0.0 or internet; do not commit tokens, device IDs or medical/personal files.
- A battery swelling, poor charger, unusual heat, or unreliable supply blocks unattended long-duration tests.
- No automatic GitHub Actions: root AGENTS.md budget policy applies; 0 hosted runner minutes used for this work.
- All scripts and thresholds are prototypes, not verified safety features or root-level power controls.

## Review
See [DECISION_20261031.md](DECISION_20261031.md) for technical alternatives, evidence, acceptance criteria and go/no-go matrix. This R&D branch is intentionally isolated from `main`.
