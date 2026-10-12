# BCP USB Rescue R3 — APK quality and human field gates

Date: 2026-10-12. **STATE: SOURCE BUILT; APK / Android Virtual Device / REAL SAMSUNG / USB FIELD: NOT VERIFIED.**

## Evidence-based lessons from earlier first-party repos

- `Terminator364/BCP`: existing B-Edge user-first home/activity/devices/system UX, human-oriented status, advanced panels separately.
- `Terminator364/PhoneMouse/field-findings/BETA03_HUMAN_UX_2026-09-17.md`: real Samsung SM-G990E running Android 16; usability is a field criterion; do not infer success from UI-only indicators.
- `Terminator364/PhoneMouse/field-findings/BETA05_1_HUMAN_UX_2026-09-17.md`: hide calibration under settings; preserve update identity and battery-friendly behavior; real human validation still needed.
- `Terminator364/P2PCR95/docs/BETA03_OFFLINE_AIRBRIDGE_RESPONSIVE_UI.md`: prefer reliable offline pairing and user-friendly recovery; avoid horizontal overflow; text scales; no repeated reinstall/uninstall and explicit release signing.
- `Terminator364/PhoneMouse/SIGNING_IDENTITY_PUBLIC.md`: package+signing certificate are durable update identity. Never copy PhoneMouse's key into another app.

## Implemented on R3 sources

- Home-first UI **Accueil / Missions / Fichiers / Réglages** with a bottom navigation and content in scrollable cards; technical IP/port/key settings separated from primary home.
- Single prominent **Diagnostiquer maintenant** action; truthful status only after actual signed agent response, no fabricated PC online state.
- Explanations for missing setup, pairing, timeout, unreachable service, actual authenticated link; read-only local USB interface hint states uncertainty.
- Foreground-only timed status check (60 s) after pairing; stops onPause/onDestroy. Does not claim any perpetual Android background service.
- Secure pairing key unchanged Android Keystore identity; package remains `com.blessing.rescuebridge`, versionCode incremented to 2; signing continuity NOT YET established by a signed APK.
- Missions remain manual JSON import. Confirmation and secure validation for each write; constrained sandbox and no shell/desktop command.
- Use scrollable screens, non-fixed-height buttons and short bottom-tab labels for narrow phones and font scaling. Adaptive launcher icon added.
- No analytics SDK, advertising, remote telemetry, full permissions expansion, broad network scan or unapproved Windows firewall change.

## Qualification gates

1. Java syntax/JVM protocol/Windows integration tests and newly added UX-contract tests **RUN LOCALLY**, with report.
2. Android actual `assembleDebug` build **NOT RUN** without SDK + Gradle; no usable APK until artifact exists and sha256/signing identity checked.
3. Android emulator preview across dp widths 320/360/412, font scale 1.0/1.3/1.5, landscape, dark/light system UI and soft keyboard **NOT RUN**.
4. USB tether phone Samsung SM-G990E → real Windows MBMPC: **NOT RUN**.
5. Real first-run onboarding, Wi-Fi absent, USB disconnected, agent stopped, sleep/reboot/resume, KeyStore corruption, APK update with same certificate **NOT RUN**.
6. Production TLS or E2E encryption required before transmitting sensitive information; R3 still has same R2 HTTP+HMAC-only transport. Never expose it to untrusted Wi-Fi.

## No false claims

The new UI improves usability but does not automatically discover Windows IP or provide ChatGPT remote computer access; those require a safely implemented discovery service, a supported authenticated connector and physical field proof. Virtual tests are not Android tests.