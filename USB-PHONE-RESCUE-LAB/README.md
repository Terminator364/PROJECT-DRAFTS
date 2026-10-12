# USB PHONE RESCUE LAB — BCP / ChatGPT-PC compatibility experiment

Status: **SIMULATED / NOT FIELD VALIDATED** (2026-10-12).
Incubation: `Terminator364/PROJECT-DRAFTS/USB-PHONE-RESCUE-LAB`.
No GitHub-hosted CI; the repository-wide `AGENTS.md` cost policy applies.

## Purpose
A fault-injection laboratory for a proposed ChatGPT -> authenticated mission channel -> Android B-Edge -> USB network -> Windows rescue agent. It is NOT an Android Emulator, a Windows emulator, an APK, an installation package, or a new ChatGPT connector.

- `bridge_lab.py`: deterministic protocol model with authenticated, device-bound envelopes; anti-replay; explicit approval; virtual sandbox; linked transport and guardian failures; offline queue.
- `audio_sim.py`: synthetic PCM and optional WAV generation, mute, clipping, low volume, 20-ms packet-loss simulation.
- `display_sim.py`: synthetic RGB frames, simulated black screen, frozen desktop and dropped video frames; optional PPM. NEVER a real screenshot.
- `run_all.py`: combined structured machine-readable gate report.
- `test_lab.py`: Python standard-library unit tests.
- `remote_catalog.json`: inspected GitHub reference projects and limits. No copied vendor code.
- `FIELD_VALIDATION.md`: Android Emulator / physical Windows + Android tests and promotion criteria.
- `tools/avd_probe.py`: read-only probe of Android Debug Bridge environment.
- `tools/windows_probe.ps1`: read-only Windows local hardware/network/service inventory.

### Execute locally without installing dependencies
```bash
cd USB-PHONE-RESCUE-LAB
python -m unittest -v test_lab
python run_all.py --out reports/latest.json
python audio_sim.py --wav reports/microphone-synthetic.wav
python display_sim.py --ppm reports/virtual-screen.ppm
```

### Design decisions
1. **No remote agent shared failure domain**: a future Windows guardian runs independently of Desktop Commander; its recovery capability must be bounded and auditable.
2. **USB data != file transfer**: USB tethering (an IP network), or optional ADB port forward/reverse, is needed for a command channel. Charging-only USB is a blocking fault.
3. **Phone Internet != PC Internet**: if only the PC cloud route is down, a phone with Internet and real USB IP transport can still act as relay. If the phone has no cloud route too, a new ChatGPT instruction cannot arrive, though previously authorized local tasks might continue.
4. **No arbitrary execution**: only defined actions with pairing and an explicit grant for mutation. The real Windows agent must have OS-managed secrets, TLS, sandbox, receipts, audit trail and expiry. In-memory HMAC in this simulator is test-only, NOT production security.
5. **No fake field certification**: success of simulation/CI is not proof of Android USB interoperability, Windows service installation, ChatGPT app integration, or automated desktop operation.
6. **Reuse, don't fork a competing product**: BCP B-Edge app and PC Node should supply device-side building blocks; ChatGPT-PC is the canonical engineering architecture for the future companion bridge.
7. **Audio != speech recognition**: PCM waveforms and injected faults exercise packet framing and metrics, not Android mic permissions, ASR correctness or call audio routing.
8. **Remote desktop apps are separate fallback classes**: MeshCentral for shell/file/desktop management, RustDesk for interactive graphical support, Guacamole for RDP/VNC/SSH gateway, scrcpy for reverse phone testing, Sunshine/Moonlight for streaming; no automatic product interoperability implied.

## Provenance / pre-existing sources
- BCP phone: https://github.com/Terminator364/BCP/tree/main/android-b-edge
- BCP Windows node: https://github.com/Terminator364/BCP/tree/main/pc-node
- Existing offline bridge contract: https://github.com/Terminator364/ChatGPT-PC/blob/main/chatgpt-pc/vnext/architecture/OFFLINE_PROXIMITY_BRIDGE.json
- Existing USB policy code: https://github.com/Terminator364/ChatGPT-PC/blob/main/chatgpt-pc/vnext/runtime/proximity_orchestrator.py
- Android official emulator: https://developer.android.com/studio/run/emulator-commandline
- Android official emulator microphone: https://developer.android.com/studio/run/emulator-extended-controls

## Limits
Only Python standard-library synthetic testing is included. The simulator does not change any real PC or phone settings. No real file, account, USB, microphone, screenshot, Android app, remote desktop service, cloud sync or external connection is exercised. Real-world deployment remains a separate staged project and should be developed against the canonical BCP/ChatGPT-PC source, with field evidence and approvals.
