#!/usr/bin/env bash
set -euo pipefail
echo "[MBH] ChatGPT-PC cloud adapter V0.1"
ROOT="$(pwd)"
OUT="$ROOT/.matrix-build-output"
rm -rf "$OUT"
mkdir -p "$OUT"
command -v python3 >/dev/null 2>&1 || { sudo apt-get update && sudo apt-get install -y python3; }
python3 -m compileall -q chatgpt-pc
if [ -d chatgpt-pc/vnext/tests ]; then
  python3 -m unittest discover -s chatgpt-pc/vnext/tests -p "test_*.py" -v 2>&1 | tee "$OUT/VNEXT_TESTS.log"
fi
if [ -d chatgpt-pc/g6 ]; then
  python3 -m compileall -q chatgpt-pc/g6
fi
SHA="$(git rev-parse --short=12 HEAD)"
tar -czf "$OUT/ChatGPT-PC-${SHA}-source-validation.tar.gz" chatgpt-pc README.md AGENTS.md 2>/dev/null || tar -czf "$OUT/ChatGPT-PC-${SHA}-source-validation.tar.gz" chatgpt-pc
sha256sum "$OUT/ChatGPT-PC-${SHA}-source-validation.tar.gz" > "$OUT/ChatGPT-PC-${SHA}-source-validation.tar.gz.sha256"
cat > "$OUT/result.json" <<EOF
{"publish":true,"tag":"buildhub-chatgpt-pc-${SHA}","title":"ChatGPT-PC ${SHA} — MATRICE BUILD HUB validation bundle"}
EOF
echo "[MBH] ChatGPT-PC validation bundle complete"
