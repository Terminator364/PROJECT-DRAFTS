from __future__ import annotations
import ast
from pathlib import Path

root=Path(__file__).resolve().parent
bridge=root/"bridge.py"
hub=root/"hub"
required=[
    bridge,
    hub/"hub.ps1",
    hub/"self-test.ps1",
    hub/"projects.json",
    hub/"remote-runner.sh",
]
missing=[str(p) for p in required if not p.is_file()]
if missing:
    raise SystemExit("MISSING:"+",".join(missing))
ast.parse(bridge.read_text(encoding="utf-8"),filename=str(bridge))
text=bridge.read_text(encoding="utf-8")
for forbidden in ["shell=True","cmd.exe /c","powershell -Command"]:
    if forbidden in text:
        raise SystemExit("FORBIDDEN:"+forbidden)
for op in ["doctor","build_phonemouse","build_p2pcr95","build_chatgpt_pc","last_build_status"]:
    if op not in text:
        raise SystemExit("OPERATION_MISSING:"+op)
print("MBH_MANAGED_APP_SELFTEST_PASS")
