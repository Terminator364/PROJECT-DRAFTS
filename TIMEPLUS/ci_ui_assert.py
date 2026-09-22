#!/usr/bin/env python3
import re
import sys
import xml.etree.ElementTree as ET

xml_path, width_s, height_s, label = sys.argv[1:5]
width, height = int(width_s), int(height_s)
root = ET.parse(xml_path).getroot()

violations = []
clickables = 0
texts = 0

for node in root.iter("node"):
    if node.attrib.get("package") != "com.terminator364.timeplus":
        continue
    bounds = node.attrib.get("bounds", "")
    m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
    if not m:
        continue
    x1, y1, x2, y2 = map(int, m.groups())
    if x1 < 0 or y1 < 0 or x2 > width or y2 > height or x2 <= x1 or y2 <= y1:
        violations.append(f"out-of-bounds {bounds} text={node.attrib.get('text','')!r}")

    if node.attrib.get("clickable") == "true":
        clickables += 1
        # At density 320, 40dp ~= 80px. Keep a small tolerance for nested semantics.
        if (x2 - x1) < 72 or (y2 - y1) < 72:
            violations.append(f"small-click-target {x2-x1}x{y2-y1} text={node.attrib.get('text','')!r}")

    if node.attrib.get("text"):
        texts += 1

if clickables == 0:
    violations.append("no clickable app nodes found")
if texts == 0:
    violations.append("no visible app text nodes found")

if violations:
    print(f"TIMEPLUS_UI_ASSERT_FAIL label={label}")
    for item in violations[:30]:
        print(item)
    raise SystemExit(1)

print(f"TIMEPLUS_UI_ASSERT_PASS label={label} clickables={clickables} texts={texts}")
