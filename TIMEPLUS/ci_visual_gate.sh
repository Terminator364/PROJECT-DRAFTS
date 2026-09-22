#!/usr/bin/env bash
set -euo pipefail
adb install -r ci-apk/app-debug.apk
mkdir -p ui-screenshots

capture_set () {
  local NAME="$1"
  local SIZE="$2"
  local FONT="$3"
  adb shell wm size "$SIZE"
  adb shell wm density 320
  adb shell settings put system font_scale "$FONT"
  adb shell am force-stop com.terminator364.timeplus
  adb shell am start -n com.terminator364.timeplus/.MainActivity >/dev/null
  sleep 2
  adb exec-out screencap -p > "ui-screenshots/${NAME}-now.png"
  python3 TIMEPLUS/ci_click.py "Départ"
  adb exec-out screencap -p > "ui-screenshots/${NAME}-manual.png"
  adb shell input keyevent KEYCODE_BACK || true
  adb shell am start -n com.terminator364.timeplus/.MainActivity >/dev/null
  sleep 1
  python3 TIMEPLUS/ci_click.py "Paramètres"
  adb exec-out screencap -p > "ui-screenshots/${NAME}-settings.png"
}
capture_set compact 720x1600 1.0
capture_set compact-large-font 720x1600 1.25
capture_set tall 824x1830 1.0
capture_set tall-large-font 824x1830 1.25
test "$(find ui-screenshots -name '*.png' | wc -l)" -eq 12
echo "TIMEPLUS_VISUAL_GATE_PASS screenshots=12"
