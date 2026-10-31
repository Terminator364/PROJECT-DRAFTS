#!/data/data/com.termux/files/usr/bin/sh
# Optional Termux:Boot hook. Copy to ~/.termux/boot/10-origin
cd "$HOME/origin-node" || exit 1
nohup sh "$HOME/origin-node/termux/start-origin.sh" >/dev/null 2>&1 &
