#!/data/data/com.termux/files/usr/bin/sh
# ORIGIN 0.2: Termux user-mode supervisor; not immune to Android kills.
set -eu
cd "$HOME/origin-node"
if command -v termux-wake-lock >/dev/null 2>&1; then termux-wake-lock || true; fi
exec python -m origin.supervisor --port 8789
