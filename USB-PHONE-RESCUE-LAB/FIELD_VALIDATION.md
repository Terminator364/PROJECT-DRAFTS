# Real Android, USB, audio and Windows field gates

This file is a **manual executable protocol**, not field certification. Tests MUST report the hardware/software IDs, actual command output, approvals and logs before a result is labelled FIELD_PROVEN.

## Stage A — Synthetic fast test (works anywhere)
- Run `python -m unittest -v test_lab`
- Run `python run_all.py --out reports/latest.json`
- Confirm `all_passed=true`, and confirm `field_gates` remain NOT_RUN / NOT_IMPLEMENTED.

## Stage B — Real Android Emulator (AVD)
Android Emulator (SDK platform tools + image installed; sufficient disk/RAM and virtualization required):
1. Run `python tools/avd_probe.py` to inventory adb and connected emulators (read-only).
2. Start a compatible Android Virtual Device with Android Studio, then install a **separately built** B-Edge APK by `adb install -r <apk-path>` *only after checking application ID and signing continuity*.
3. Validate B-Edge app boot and lifecycle, notification permission, background restrictions, service stop/restart, airplane mode, mobile data, battery saver, TLS certificate pinning.
4. In extended controls, explicitly enable host mic if needed; test muted/unmuted mic, virtual headset and playback. Confirm app permission prompts and audio integrity using recordings and timestamps.
5. Test Android app state survives emulator process death and OS restart, including persistent job idempotency.
6. Do not claim that an AVD reproduces the USB tether stack of the physical Samsung phone; AVD is software-side evidence only.

## Stage C — Real Windows + Android via USB
Prerequisites: screen unlocked, user consent, reliable data cable, Windows companion agent actually installed, and a named/verified phone. Never expose development listener on public network.
1. Run `tools/windows_probe.ps1` read-only on PC.
2. Confirm Windows sees Samsung/Android USB device and **USB tethering** network adapter while the cable is plugged in. Android's **File transfer (MTP)** does NOT by itself create a TCP link.
3. Obtain local IPs from Windows and Android; prove bidirectional reachability to the **single authenticated local service**; do not mistake successful ping for an application handshake.
4. Test paired TLS handshake, signed device binding, explicit consent for consequential actions, rate limiting, disconnect and reinstall recovery.
5. Simulate Desktop Commander agent down without shutting down the new independent guardian. Validate diagnostic still works, and recovery only for explicitly allowed service.
6. Reboot PC; check automatic startup after login and after service crash, without infinite restart loops.
7. Remove cable; charge-only cable; change Android USB mode; deny USB permission; toggle mobile data; disable phone Internet; phone low-battery; suspend laptop; observe exact reason codes.
8. Transfer test-only files of 0 B / 1 KB / 1 MB and corrupt bytes intentionally. Verify SHA-256, idempotency, reassembly, retry after interruption, and no directory traversal.
9. Test voice: mic off/on, gain, clipping, Bluetooth headset, speaker route, interruptions and user permissions. Do not record private conversations.
10. Test screen path separately with a fake desktop first; if remote interactive desktop is added, validate session lock/UAC/user consent and never bypass Windows security boundaries.

## Stage D — ChatGPT ingress
Do NOT call this operational until the ChatGPT-side interface is proven:
- Authorized path to create a mission from ChatGPT (supported connector or user-mediated Drive file).
- Phone sees that mission, validates identity and expiry.
- PC executes only within allowed sandbox with local authorization.
- Signed result and audit event return to the same user-visible conversation/authorized storage.
- ChatGPT independently reads back the result and distinguishes simulated receipt from real Windows evidence.
- Force a remote-connector outage; show the fallback has no single shared point of failure.

## Promotion acceptance
Only promote after ALL stages have receipts: exact device builds, timestamped hashes, true OS and USB APIs, authorization tests, no public listener, rollback, and 3 repeated successful unplug/replug/reboot recoveries on MBMPC. On failure, preserve raw evidence and create a regression test. Never mark Android field proof on a pure Python/AVD success.

## Safety / battery / practicality
Do not leave USB debugging enabled unnecessarily; prefer OS-supported USB tethering without ADB for production. Avoid always-on Bluetooth scanning or background high-power networking. Do not automatically modify firewall/security profiles or install drivers without explicit permission. Never treat a physical cable alone as permission to execute arbitrary commands.
