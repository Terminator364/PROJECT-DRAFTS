# R3: user-first UX revision, sources + 42-test suite, APK NOT COMPILED, REAL USB NOT TESTED

See UX_AUDIT_R3.md and reports/qa_cycles.json.

# BCP USB RESCUE R2 — evidence gate (2026-10-12)

## Achieved
- Android Java sources (native Activity, USB-network client, AndroidKeyStore pairing, HMAC protocol).
- Windows Python bounded agent, persisted SQLite anti-replay, audit log and atomic test-workspace writes.
- Current-user Windows installer/USB-tether guardian script with circuit-breaker.
- Three local QA cycles, 32 tests per cycle: 96/96 passed after correcting package/manifest mismatch.
- JVM/Python protocol interoperability, 50 signed status calls, 20 Unicode file round-trips and refusal tests.
- Source ZIP built, SHA-256 recorded separately.

## Not achieved; must not be described as installed, validated or 'ready'
- APK binary compile (no Android SDK / Gradle in local runtime).
- Android emulator launch or actual physical Android install.
- Real USB cable / Windows RNDIS/NCM transport verification.
- Desktop GUI control, arbitrary Windows command execution, direct ChatGPT plugin integration.
- Production TLS, certificate pinning, and permissions review.

## Security condition
The v0.1 network route is plaintext HTTP + HMAC. It does not conceal data. USB private link only, no sensitive real files. Do not expose port 8766 to Internet. Do not claim production security.

## Follow-on acceptance gates
1. Build APK with Android SDK 35 (manual GitHub Actions recipe), sign with stable key for app updates.
2. Install APK on Android 16 phone, record permission/network UX evidence.
3. Install Windows agent on MBMPC as current user, prove clean Windows login/autostart.
4. Enforce private USB interface bind and scoped firewall policy with explicit user approval.
5. Run 3 unplug/replug cycles and 3 reboot cycles on real hardware with signed receipts.
6. Integrate cloud ingress with explicitly supported authorization, not by assuming ChatGPT can invoke arbitrary app sockets.