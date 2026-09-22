#!/usr/bin/env bash
set -euo pipefail

PKG="com.terminator364.timeplus"
APK="ci-apk/app-debug.apk"
mkdir -p ui-evidence

adb install -r "$APK"
adb shell pm grant "$PKG" android.permission.POST_NOTIFICATIONS 2>/dev/null || true

dump_ui_retry () {
  local OUT="$1"
  local OK=0
  for ATTEMPT in 1 2 3 4 5 6 7 8; do
    adb shell rm -f /sdcard/timeplus-ui.xml >/dev/null 2>&1 || true
    if adb shell uiautomator dump /sdcard/timeplus-ui.xml >/dev/null 2>&1; then
      if adb pull /sdcard/timeplus-ui.xml "$OUT" >/dev/null 2>&1; then
        if python3 - "$OUT" <<'PY'
import sys, xml.etree.ElementTree as ET
root=ET.parse(sys.argv[1]).getroot()
if root is None:
    raise SystemExit(1)
PY
        then
          OK=1
          break
        fi
      fi
    fi
    sleep 1.25
  done
  test "$OK" -eq 1
}

capture () {
  local NAME="$1"
  local WIDTH="$2"
  local HEIGHT="$3"
  echo "CAPTURE_START name=$NAME"
  sleep 0.6
  adb exec-out screencap -p > "ui-evidence/${NAME}.png"
  dump_ui_retry "ui-evidence/${NAME}.xml"
  python3 TIMEPLUS/ci_ui_assert.py "ui-evidence/${NAME}.xml" "$WIDTH" "$HEIGHT" "$NAME"
  echo "CAPTURE_PASS name=$NAME"
}

config_run () {
  local NAME="$1"
  local SIZE="$2"
  local FONT="$3"
  local WIDTH="${SIZE%x*}"
  local HEIGHT="${SIZE#*x}"

  adb shell wm size "$SIZE"
  adb shell wm density 320
  adb shell settings put system font_scale "$FONT"
  adb shell am force-stop "$PKG"
  adb shell am start -W -n "$PKG/.MainActivity" >/dev/null
  sleep 3

  capture "${NAME}-calc" "$WIDTH" "$HEIGHT"

  python3 TIMEPLUS/ci_click.py "Heure choisie"
  capture "${NAME}-time-picker" "$WIDTH" "$HEIGHT"
  python3 TIMEPLUS/ci_click.py "Annuler"

  python3 TIMEPLUS/ci_click.py "Roues"
  capture "${NAME}-duration-wheels" "$WIDTH" "$HEIGHT"
  adb shell input keyevent KEYCODE_BACK
  sleep 1

  python3 TIMEPLUS/ci_click.py "Différence"
  capture "${NAME}-difference" "$WIDTH" "$HEIGHT"

  python3 TIMEPLUS/ci_click.py "Paramètres"
  capture "${NAME}-settings" "$WIDTH" "$HEIGHT"

  adb shell input swipe "$((WIDTH/2))" "$((HEIGHT*4/5))" "$((WIDTH/2))" "$((HEIGHT/5))" 450
  sleep 1
  capture "${NAME}-settings-bottom" "$WIDTH" "$HEIGHT"
}

# Phone classes: very narrow, common 360dp-ish, and taller 412dp-ish.
config_run narrow 640x1280 1.00
config_run narrow-large-font 640x1280 1.30
config_run compact 720x1600 1.00
config_run compact-large-font 720x1600 1.30
config_run tall 824x1830 1.00
config_run tall-large-font 824x1830 1.30

# Crash-smoke after deterministic visual states.
adb shell wm size 720x1600
adb shell wm density 320
adb shell settings put system font_scale 1.0
adb shell am force-stop "$PKG"
adb shell monkey -p "$PKG" --pct-syskeys 0 --pct-appswitch 0 --pct-anyevent 0 --throttle 3 500 > ui-evidence/monkey.log 2>&1 || {
  cat ui-evidence/monkey.log
  exit 1
}

COUNT="$(find ui-evidence -name '*.png' | wc -l)"
test "$COUNT" -eq 36

echo "TIMEPLUS_V2_VISUAL_GATE_PASS screenshots=$COUNT configurations=6 monkey_events=500"
