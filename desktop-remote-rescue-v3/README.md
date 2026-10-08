# Desktop Commander Remote Rescue V3

**Goal:** reconnect the **existing** Remote Desktop Commander from one click on Windows 11, without downloading or reinstalling Desktop Commander.

This is a rescue utility, not the replacement project PC Command Open.

## User action

Extract the release ZIP anywhere (including Downloads) and double-click **RUN_RESCUE.cmd**.

The window shows these meaningful states:
- `PROBING_LOCAL`: opening the already-installed Desktop Commander local MCP
- `LOCAL_MCP_PASS`: actual MCP `initialize` and `tools/list` worked
- `CONNECTING`: starting the official Remote CLI
- `AUTH_REQUIRED`: genuine one-time authorization needed; existing credentials are never erased
- `ONLINE_REPORTED`: official Remote device process says online (server-side verification follows)
- `LOCAL_MCP_FAILED`: package exists but local MCP did not initialize
- `FAILED_NEEDS_INSPECTION`: retries exhausted; the program **stops**, no endless restarts

After an official online message, a small Windows Startup shortcut is created so reconnecting after login requires no manual step.

## Non-destructive

No `npm install`, no downloads, no logout, no token removal, no registry modifications, no administrator permissions, and no broad process killing. It reuses the official `@wonderwhy-er/desktop-commander` already installed globally.

Runtime requirements: Node 22.12+; observed on the target machine: Node 24.21.0, Desktop Commander 0.2.52. Run the user-facing tool from the normal Windows user account (not elevated).

Log and state: `%LOCALAPPDATA%\BlessingPC\remote-rescue-v3\`.

The program uses a single-instance lock and, if a Remote process exits during initial connection, retries at most three times with delays. If network/authorization requires intervention it stops at that gate rather than falsely declaring success.

## GitHub Actions tests

The Windows CI qualification executes:
- offline deterministic scenarios for MCP init, Remote ready, Remote stuck, authentication required
- installs the official package into a **temporary path with spaces on GitHub Windows**, not on the user's PC
- tests actual local MCP JSON-RPC handshake and discovery on Windows
- invokes official Remote CLI `--help` without network authorization
- packages the user-facing **RUN_RESCUE.cmd + rescue.mjs** as one build artifact only after checks pass

**Limits:** A hosted GitHub runner is not an exact replica of the user's Windows 11 machine or its 4 GB RAM pressure, account OAuth state, Wi-Fi, or ISP. It cannot prove *server-side Online* for MBMPC, which requires the real machine to send a successful connection. The final field gate is a single click and subsequent online verification; no claim of complete recovery before that.

Official upstream:
https://github.com/wonderwhy-er/DesktopCommanderMCP/tree/main/src/remote-device

This project must not be merged into a production branch or installed until the Windows qualification workflow passes.
