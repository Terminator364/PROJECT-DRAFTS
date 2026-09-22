#!/usr/bin/env python3
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

target = sys.argv[1]
subprocess.run(["adb", "shell", "uiautomator", "dump", "/sdcard/ui.xml"], check=True, stdout=subprocess.DEVNULL)
subprocess.run(["adb", "pull", "/sdcard/ui.xml", "/tmp/timeplus-ui.xml"], check=True, stdout=subprocess.DEVNULL)
root = ET.parse("/tmp/timeplus-ui.xml").getroot()
for node in root.iter("node"):
    if node.attrib.get("text") == target or node.attrib.get("content-desc") == target:
        match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", node.attrib.get("bounds", ""))
        if match:
            x1, y1, x2, y2 = map(int, match.groups())
            subprocess.run(["adb", "shell", "input", "tap", str((x1+x2)//2), str((y1+y2)//2)], check=True)
            subprocess.run(["sleep", "2"], check=True)
            sys.exit(0)
print(f"UI target not found: {target}", file=sys.stderr)
sys.exit(2)
