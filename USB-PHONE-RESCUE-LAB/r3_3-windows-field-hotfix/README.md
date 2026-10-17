# R3.3 Windows field hotfix — tested on MBMPC
Date: 2026-10-17
Canonical Android binary: BCP-USB-Rescue-R3.3-SIGNED.apk
Android versionCode: 5 / package com.blessing.rescuebridge.
Private signing key stays only on user's MBMPC.
USB Rescue agent TCP: 8876; discovery UDP: 8767; reverse TCP phone: 8768.
Existing unrelated BCP TLS proxy on TCP 8766 is preserved.
Changes: Windows UTF-8 tests, bounded concurrent tests with socket cleanup, peer disconnect tolerant HTTP response, correct listener ownership detection.
Windows tests: 67 run, 0 failures, 0 errors, 1 skipped. Tests rerun after alignment to the actual Android build.
Installed live on MBMPC; backup of prior Windows agent stored under local backups.
Field reality: Windows USB Android adapter count 0 in last probe; no Samsung-to-PC end-to-end certification.
Initial one-time pairing and USB tether enablement are not silent/fully automated.
Transport is unencrypted HTTP + HMAC; restrict to trusted physically-connected private USB network.
This folder is a **Windows-only compatibility overlay** for the already compiled R3.3 Android APK. It does not replace the immutable CI source used to build the APK. Do not mislabel these PC-side changes as included in the original Android APK.
