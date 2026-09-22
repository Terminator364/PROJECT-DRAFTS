#!/usr/bin/env python3
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

target = sys.argv[1]

def dump_ui(out_path="/tmp/timeplus-ui.xml"):
    for attempt in range(1, 9):
        subprocess.run(["adb", "shell", "rm", "-f", "/sdcard/ui.xml"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        proc = subprocess.run(
            ["adb", "shell", "uiautomator", "dump", "/sdcard/ui.xml"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if proc.returncode == 0:
            pull = subprocess.run(
                ["adb", "pull", "/sdcard/ui.xml", out_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if pull.returncode == 0:
                try:
                    root = ET.parse(out_path).getroot()
                    if root is not None:
                        return root
                except Exception:
                    pass
        time.sleep(0.8)
    raise RuntimeError("Unable to obtain stable UIAutomator hierarchy after retries")

def find_and_tap():
    root = dump_ui()
    for node in root.iter("node"):
        if node.attrib.get("text") == target or node.attrib.get("content-desc") == target:
            match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", node.attrib.get("bounds", ""))
            if match:
                x1, y1, x2, y2 = map(int, match.groups())
                subprocess.run(
                    ["adb", "shell", "input", "tap", str((x1 + x2) // 2), str((y1 + y2) // 2)],
                    check=True,
                )
                time.sleep(1.0)
                return True
    return False

if find_and_tap():
    sys.exit(0)

# Search farther down the current scrollable screen.
for _ in range(6):
    subprocess.run(["adb", "shell", "input", "swipe", "320", "1050", "320", "350", "350"], check=True)
    time.sleep(0.5)
    if find_and_tap():
        sys.exit(0)

# Search back toward the top as well. This lets the same helper find top tabs/app-bar actions
# after a previous interaction left a LazyColumn scrolled down.
for _ in range(7):
    subprocess.run(["adb", "shell", "input", "swipe", "320", "330", "320", "1050", "350"], check=True)
    time.sleep(0.5)
    if find_and_tap():
        sys.exit(0)

print(f"UI target not found after bidirectional scroll search: {target}", file=sys.stderr)
sys.exit(2)
